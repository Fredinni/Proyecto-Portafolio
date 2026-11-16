"""One stateful Gemini Live WebSocket for speech, listening and tool use."""

import asyncio
import base64
import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import websockets

from prompts import SOAR_FUNCTION_TOOLS, build_live_system_prompt

log = logging.getLogger(__name__)


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

    def setup_message(self, incident):
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
            "tools": [{"functionDeclarations": SOAR_FUNCTION_TOOLS}],
        }}

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
        async with self.connect(url, open_timeout=12, close_timeout=3,
                                max_size=4 * 1024 * 1024, max_queue=32) as ws:
            async def send(message):
                await ws.send(json.dumps(message, ensure_ascii=False))

            await send(self.setup_message(incident_data))
            ack = json.loads(await asyncio.wait_for(ws.recv(), timeout=15))
            if "setupComplete" not in ack:
                raise RuntimeError("Gemini Live setup rejected")
            log.info("live_connected model=%s session=%s", self.model, incident_data.get("session_id"))
            await send({"clientContent": {"turns": [{"role": "user", "parts": [{
                "text": "Inicia la llamada con el saludo y la pregunta indicados. No ejecutes cambios todavía."
            }]}], "turnComplete": True}})

            async def microphone():
                async for pcm in audio_input_stream:
                    await send({"realtimeInput": {"audio": {
                        "mimeType": "audio/pcm;rate=16000",
                        "data": base64.b64encode(pcm).decode("ascii")}}})

            async def execute_calls(calls):
                responses = []
                for call in calls:
                    if call.get("id") in cancelled_ids:
                        continue
                    if call.get("name") in {"unblock_ip", "block_ip_permanently"}:
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
                        result = await asyncio.to_thread(
                            tools.execute_tool_call, call["name"], call.get("args", {}))
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
                    await execute_calls(calls)

            async def receive():
                async for raw in ws:
                    message = json.loads(raw)
                    if "error" in message:
                        raise RuntimeError("Gemini Live returned an error")
                    if message.get("goAway"):
                        log.warning("live_go_away session=%s", incident_data.get("session_id"))
                    content = message.get("serverContent", {})
                    if content.get("interrupted"):
                        await on_interrupt()
                    text = content.get("inputTranscription", {}).get("text", "")
                    if text:
                        tools.observe_input(text)
                        transcription["updated"] = time.monotonic()
                        transcription["finished"] = content["inputTranscription"].get("finished", False)
                    output_text = content.get("outputTranscription", {}).get("text", "")
                    if output_text:
                        tools.observe_output(output_text)
                    for part in content.get("modelTurn", {}).get("parts", []):
                        inline = part.get("inlineData", {})
                        if inline.get("data") and inline.get("mimeType", "").startswith("audio/pcm"):
                            await audio_output_stream(base64.b64decode(inline["data"], validate=True))
                    for call_id in message.get("toolCallCancellation", {}).get("ids", []):
                        cancelled_ids.add(call_id)
                    calls = message.get("toolCall", {}).get("functionCalls", [])
                    if calls:
                        tool_queue.put_nowait(calls)
                    if content.get("turnComplete"):
                        tools.finish_turn()
                        transcription.update(updated=0.0, finished=False)
                        if on_turn_complete:
                            await on_turn_complete()

            tasks = [asyncio.create_task(microphone()), asyncio.create_task(receive()),
                     asyncio.create_task(tool_worker())]
            try:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    task.result()
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
