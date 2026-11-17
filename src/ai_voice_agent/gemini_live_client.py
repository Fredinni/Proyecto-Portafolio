"""One stateful Gemini Live WebSocket for speech, listening and tool use."""

import asyncio
import base64
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode

import websockets

from prompts import SOAR_FUNCTION_TOOLS, build_live_system_prompt
from audio_activity import AudioActivityGate

log = logging.getLogger(__name__)
INITIAL_AUDIO_TIMEOUT_SECONDS = 8


class InitialAudioTimeout(TimeoutError):
    """No model audio and no mutation attempt; a fresh session is safe."""


class RecoverableLiveDisconnect(ConnectionError):
    """Read-only session disconnected or stalled; no command may be replayed."""


def read_secret(name, default_path=None):
    value = os.getenv(name)
    if value:
        return value
    path = os.getenv(name + "_FILE", default_path)
    if path and Path(path).is_file():
        return Path(path).read_text(encoding="utf-8").strip()
    raise ValueError(f"Configure {name} or {name}_FILE")


class GeminiLiveVoiceClient:
    def __init__(self, api_key=None, model=None, connect=None):
        self.api_key = api_key or read_secret("GEMINI_API_KEY", "/etc/gemini.key")
        self.model = model or os.getenv("GEMINI_LIVE_MODEL", "gemini-3.1-flash-live-preview")
        self.connect = connect or websockets.connect

    @asynccontextmanager
    async def open_session(self, url, incident):
        """Retry only before setup succeeds, never replay an authorized action."""
        for attempt in range(2):
            ws = None
            started = time.monotonic()
            try:
                ws = await self.connect(url, open_timeout=5, close_timeout=1,
                                        max_size=4 * 1024 * 1024, max_queue=32)
                await ws.send(json.dumps(self.setup_message(incident), ensure_ascii=False))
                ack = json.loads(await asyncio.wait_for(ws.recv(), timeout=6))
                if "setupComplete" not in ack:
                    raise RuntimeError("Gemini Live setup rejected")
            except (OSError, TimeoutError):
                if ws is not None:
                    await ws.close()
                log.warning("live_setup_retry session=%s attempt=%s elapsed=%.3f",
                            incident.get('session_id'), attempt + 1, time.monotonic() - started)
                if attempt == 1:
                    raise
                continue
            except BaseException:
                if ws is not None:
                    await ws.close()
                raise
            try:
                yield ws
            finally:
                await ws.close()
            return

    def setup_message(self, incident):
        declarations = [dict(tool) for tool in SOAR_FUNCTION_TOOLS]
        if self.model.startswith("gemini-3.8"):
            for tool in declarations:
                tool["behavior"] = "BLOCKING"
        return {"setup": {
            "model": "models/" + self.model.removeprefix("models/"),
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {
                    "voiceName": os.getenv("GEMINI_VOICE", "Aoede")}}},
            },
            "systemInstruction": {"parts": [{"text": build_live_system_prompt(incident)}]},
            "inputAudioTranscription": {},
            "outputAudioTranscription": {},
            "realtimeInputConfig": {"automaticActivityDetection": {
                "disabled": False, "prefixPaddingMs": 120, "silenceDurationMs": 500}},
            "tools": [{"functionDeclarations": declarations}],
        }}

    @staticmethod
    def opening_instruction(incident):
        base = "Saluda brevemente al operador, distingue origen y victima segun la evidencia. No ejecutes cambios todavia. "
        if not incident.get('attacker_ip'):
            return "Es una llamada directa: saluda y pregunta que necesita revisar. No inventes un incidente."
        if incident.get('source_protected'):
            return base + "Explica que el IPS descarto el ataque desde infraestructura protegida. No ofrezcas modificar esa IP."
        state = incident.get('firewall_state_at_call') or {}
        if state.get('verified') and state.get('is_blocked'):
            return base + ('Resume la alerta en dos frases y termina EXACTAMENTE con esta pregunta: '
                           '«¿Quieres que desbloquee esta IP?». No la reemplaces por una pregunta abierta.')
        return base + "Resume el incidente sin asegurar un bloqueo desconocido; pregunta que informacion quiere revisar."

    async def start_voice_session(self, incident_data, audio_input_stream, audio_output_stream,
                                  tools, on_interrupt, on_turn_complete=None):
        """Input: async PCM16/16kHz iterator. Output: async PCM16/24kHz sink.

        Keep receiving across turns. Run tool I/O separately so the microphone
        and interruption events keep flowing during firewall I/O.
        """
        url = ("wss://generativelanguage.googleapis.com/ws/"
               "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?"
               + urlencode({"key": self.api_key}))
        tool_queue = asyncio.Queue(maxsize=8)
        cancelled_ids = set()
        transcription = {"updated": 0.0, "finished": False}
        started = time.monotonic()
        timing = {"first_audio": False, "speech_end": None, "mutation_attempted": False,
                  "response_active": False, "last_audio": None, "pending_tools": 0,
                  "response_has_output": False, "completion_notified": False,
                  "input_generation": 0, "receipt": None, "last_input_end": None}
        mutation_lock = asyncio.Lock()
        async with self.open_session(url, incident_data) as ws:
            async def send(message):
                await ws.send(json.dumps(message, ensure_ascii=False))

            log.info("live_connected model=%s session=%s setup_seconds=%.3f", self.model,
                     incident_data.get("session_id"), time.monotonic() - started)
            await send({"clientContent": {"turns": [{"role": "user", "parts": [{
                "text": self.opening_instruction(incident_data)
            }]}], "turnComplete": True}})
            greeting_at = time.monotonic()

            async def startup_watchdog():
                while True:
                    await asyncio.sleep(.25)
                    if (not timing["first_audio"] and not timing["mutation_attempted"] and
                            time.monotonic() - greeting_at > INITIAL_AUDIO_TIMEOUT_SECONDS):
                        raise InitialAudioTimeout("No initial model audio")
                    if (timing["speech_end"] is not None and not timing["mutation_attempted"] and
                            time.monotonic() - timing["speech_end"] > 10):
                        raise RecoverableLiveDisconnect("No model response after speech")
                    if (timing["response_active"] and not timing["mutation_attempted"] and
                            time.monotonic() - timing["last_audio"] > 10):
                        raise RecoverableLiveDisconnect("Model audio stalled mid-response")

            async def microphone():
                gate = AudioActivityGate(threshold=int(os.getenv("KRONOS_VAD_RMS_THRESHOLD", "64")))
                async for pcm in audio_input_stream:
                    chunks, speech_end = gate.feed(pcm)
                    for chunk in chunks:
                        await send({"realtimeInput": {"audio": {
                            "mimeType": "audio/pcm;rate=16000",
                            "data": base64.b64encode(chunk).decode("ascii")}}})
                    if speech_end:
                        timing["speech_end"] = time.monotonic()
                        timing["last_input_end"] = timing["speech_end"]
                        log.info("live_speech_end session=%s", incident_data.get("session_id"))
                        await send({"realtimeInput": {"audioStreamEnd": True}})

            async def run_tool(name, arguments):
                if name not in {"unblock_ip", "block_ip_permanently"}:
                    return await asyncio.to_thread(tools.execute_tool_call, name, arguments)
                async with mutation_lock:
                    receipt = timing["receipt"]
                    key = (timing["input_generation"], name, arguments.get("ip"))
                    if receipt and receipt[0] == key:
                        return {**receipt[1], "already_executed": True}
                    timing["mutation_attempted"] = True
                    result = await asyncio.to_thread(tools.execute_tool_call, name, arguments)
                    if result.get("verified"):
                        timing["receipt"] = (key, result)
                    return result

            async def confirmation_controller():
                while True:
                    await asyncio.sleep(.05)
                    ended = timing["last_input_end"]
                    if (ended is None or not transcription["updated"] or
                            time.monotonic() - ended < .3 or
                            time.monotonic() - transcription["updated"] < .3):
                        continue
                    ip = tools.policy.confirmed_unblock_target()
                    if ip:
                        result = await run_tool("unblock_ip", {"ip": ip, "reason": "Confirmacion de la pregunta de desbloqueo por el operador"})
                        log.info("voice_confirmation_action session=%s verified=%s", incident_data.get("session_id"), result.get("verified"))
                        await send({"clientContent": {"turns": [{"role": "user", "parts": [{"text":
                            "KRONOS_ACTION_RESULT: el controlador ya proceso la confirmacion del operador. "
                            "Informa este resultado sin volver a pedir confirmacion ni repetir la operacion: " + json.dumps(result, ensure_ascii=False)}]}], "turnComplete": True}})
                        timing["last_input_end"] = None

            async def execute_calls(calls):
                responses = []
                for call in calls:
                    if call.get("id") in cancelled_ids:
                        continue
                    if call.get("name") in {"unblock_ip", "block_ip_permanently"}:
                        timing["mutation_attempted"] = True
                        # Input transcription can trail the tool call. Continue
                        # receiving while waiting briefly for the complete text.
                        deadline = time.monotonic() + 1.5
                        while time.monotonic() < deadline:
                            if transcription["updated"] and (transcription["finished"] or
                                    time.monotonic() - transcription["updated"] >= .25):
                                break
                            await asyncio.sleep(.02)
                        if call.get("id") in cancelled_ids:
                            continue
                    try:
                        tool_started = time.monotonic()
                        result = await run_tool(call["name"], call.get("args", {}))
                        log.info("live_tool session=%s name=%s elapsed=%.3f", incident_data.get("session_id"),
                                 call["name"], time.monotonic() - tool_started)
                    except Exception:
                        log.exception("tool_execution_failed name=%s", call.get("name"))
                        result = {"success": False, "error": "No se pudo verificar la operación."}
                    if call.get("id") not in cancelled_ids:
                        responses.append({"id": call.get("id"), "name": call["name"], "response": result})
                if responses:
                    await send({"toolResponse": {"functionResponses": responses}})

            async def tool_worker():
                while True:
                    calls = await tool_queue.get()
                    try:
                        await execute_calls(calls)
                    finally:
                        timing["pending_tools"] -= 1

            async def receive():
                async for raw in ws:
                    message = json.loads(raw)
                    if "error" in message:
                        raise RuntimeError("Gemini Live returned an error")
                    if message.get("goAway"):
                        log.warning("live_go_away session=%s", incident_data.get("session_id"))
                    content = message.get("serverContent", {})
                    if content.get("interrupted"):
                        if timing["response_active"]:
                            tools.interrupt_output()
                            timing["response_has_output"] = False
                        timing["response_active"] = False
                        await on_interrupt()
                    text = content.get("inputTranscription", {}).get("text", "")
                    if text:
                        if not transcription["updated"]:
                            timing["completion_notified"] = False
                            timing["input_generation"] += 1
                        tools.observe_input(text)
                        transcription["updated"] = time.monotonic()
                        transcription["finished"] = content["inputTranscription"].get("finished", False)
                    output_text = content.get("outputTranscription", {}).get("text", "")
                    if output_text:
                        timing["response_has_output"] = True
                        tools.observe_output(output_text)
                    for part in content.get("modelTurn", {}).get("parts", []):
                        inline = part.get("inlineData", {})
                        if inline.get("data") and inline.get("mimeType", "").startswith("audio/pcm"):
                            if not timing["response_active"]:
                                timing["completion_notified"] = False
                            timing["response_has_output"] = True
                            timing["response_active"] = True
                            timing["last_audio"] = time.monotonic()
                            if not timing["first_audio"]:
                                timing["first_audio"] = True
                                log.info("live_first_audio session=%s elapsed=%.3f", incident_data.get("session_id"),
                                         time.monotonic() - started)
                            if timing["speech_end"] is not None:
                                log.info("live_reply_audio session=%s after_speech=%.3f", incident_data.get("session_id"),
                                         time.monotonic() - timing["speech_end"])
                                timing["speech_end"] = None
                            await audio_output_stream(base64.b64decode(inline["data"], validate=True))
                    for call_id in message.get("toolCallCancellation", {}).get("ids", []):
                        cancelled_ids.add(call_id)
                    calls = message.get("toolCall", {}).get("functionCalls", [])
                    if calls:
                        timing["pending_tools"] += 1
                        tool_queue.put_nowait(calls)
                    if content.get("generationComplete") or content.get("turnComplete"):
                        timing["response_active"] = False
                        if (timing["response_has_output"] and not timing["completion_notified"] and
                                not timing["pending_tools"]):
                            timing["completion_notified"] = True
                            timing["response_has_output"] = False
                            tools.finish_turn()
                            transcription.update(updated=0.0, finished=False)
                            if on_turn_complete:
                                await on_turn_complete()

            tasks = [asyncio.create_task(microphone()), asyncio.create_task(receive()),
                     asyncio.create_task(tool_worker()), asyncio.create_task(startup_watchdog()),
                     asyncio.create_task(confirmation_controller())]
            try:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    task.result()
            except websockets.exceptions.ConnectionClosedError as error:
                log.warning("live_remote_disconnect session=%s received_code=%s sent_code=%s ping_timeout=%s",
                            incident_data.get('session_id'), getattr(error.rcvd, 'code', None),
                            getattr(error.sent, 'code', None), 'keepalive ping timeout' in str(error))
                if not timing["mutation_attempted"]:
                    raise RecoverableLiveDisconnect("Read-only session disconnected") from error
                raise
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
