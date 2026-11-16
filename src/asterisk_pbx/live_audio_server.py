#!/usr/bin/env python3
"""Full duplex Asterisk AudioSocket <-> Gemini Live PCM transport."""

import asyncio
import audioop
import json
import logging
import os
from pathlib import Path
import socket
import struct
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai_voice_agent"))
from gemini_live_client import GeminiLiveVoiceClient
from soar_tools_executor import SoarToolsExecutor

log = logging.getLogger("kronos.live")


def packet(kind, payload=b""):
    return struct.pack("!BH", kind, len(payload)) + payload


async def read_packet(reader):
    header = await reader.readexactly(3)
    kind, size = struct.unpack("!BH", header)
    if size > 16384:
        raise ValueError("Oversized AudioSocket packet")
    return kind, await reader.readexactly(size)


class Playback:
    """Pace 20ms frames; never dump a whole synthesized sentence into TCP."""
    def __init__(self):
        self.buffer = bytearray()
        self.rate_state = None
        self.complete = False

    async def feed(self, pcm):
        converted, self.rate_state = audioop.ratecv(pcm, 2, 1, 24000, 8000, self.rate_state)
        if len(self.buffer) + len(converted) > 8000 * 2 * 45:
            raise RuntimeError("Audio playback backlog exceeds 45 seconds")
        self.buffer.extend(converted)
        self.complete = False

    async def interrupt(self):
        self.buffer.clear()
        self.rate_state = None
        self.complete = False

    async def finish_turn(self):
        self.complete = True

    async def run(self, writer):
        while True:
            start = asyncio.get_running_loop().time()
            if len(self.buffer) >= 320 or (self.complete and self.buffer):
                frame = bytes(self.buffer[:320]).ljust(320, b"\x00")
                del self.buffer[:320]
            else:
                frame = b"\x00" * 320
            writer.write(packet(0x10, frame))
            await writer.drain()
            # Reset after any scheduling delay instead of bursting old frames.
            await asyncio.sleep(max(0, .020 - (asyncio.get_running_loop().time() - start)))


async def microphone(reader):
    state = None
    while True:
        kind, payload = await read_packet(reader)
        if kind == 0x00:
            return
        if kind == 0xff:
            raise RuntimeError("Asterisk AudioSocket error")
        if kind == 0x10:
            if len(payload) % 2:
                raise ValueError("Unaligned PCM16 audio")
            pcm, state = audioop.ratecv(payload, 2, 1, 8000, 16000, state)
            yield pcm
        elif kind not in {0x03}:
            raise ValueError("Unexpected AudioSocket packet type")


def consume_context(session_id, directory):
    session_id = str(uuid.UUID(session_id))
    path = Path(directory) / (session_id + ".json")
    # A single consumer can claim a call; failed or replayed UUIDs are rejected.
    claimed = path.with_suffix(".active")
    path.rename(claimed)
    try:
        if claimed.is_symlink() or claimed.stat().st_size > 32768:
            raise ValueError("Invalid call context")
        context = json.loads(claimed.read_text(encoding="utf-8"))
        age = time.time() - context["created_at"]
        if not 0 <= age <= 60:
            raise ValueError("Expired call context")
        context["session_id"] = session_id
        return context
    finally:
        claimed.unlink(missing_ok=True)


async def handle_call(reader, writer, config, call_directory, client_factory=GeminiLiveVoiceClient):
    session_id = "unregistered"
    playback_task = None
    try:
        writer.get_extra_info("socket").setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        kind, payload = await asyncio.wait_for(read_packet(reader), timeout=5)
        if kind != 0x01 or len(payload) != 16:
            raise ValueError("AudioSocket must start with a UUID")
        session_id = str(uuid.UUID(bytes=payload))
        incident = consume_context(session_id, call_directory)
        extension = incident.get("operator_extension", "")
        operator = config.get("operators", {}).get(extension, {})
        incident.update({"operator_name": operator.get("name", "operador"),
                         "operator_role": operator.get("role", "no identificado")})
        tools = SoarToolsExecutor(config=config, incident=incident)
        if incident.get("attacker_ip"):
            incident["sensor_pfctl_blocked_at_alert"] = incident.get("pfctl_blocked")
            current = await asyncio.to_thread(tools.execute_tool_call, "get_firewall_states",
                                             {"ip": incident["attacker_ip"]})
            incident["firewall_state_at_call"] = current
            incident["pfctl_blocked"] = current.get("is_blocked") if current.get("verified") else None
        playback = Playback()
        playback_task = asyncio.create_task(playback.run(writer))
        session_task = asyncio.create_task(client_factory().start_voice_session(
            incident, microphone(reader), playback.feed, tools,
            playback.interrupt, playback.finish_turn))
        try:
            done, _ = await asyncio.wait([session_task, playback_task],
                                        timeout=int(config.get("max_call_seconds", 300)),
                                        return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            session_task.cancel()
            await asyncio.gather(session_task, return_exceptions=True)
    except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
        if session_id != "unregistered":
            log.info("caller_hangup session=%s", session_id)
    except Exception as error:
        # Log only the exception class: external connection errors may contain
        # a WebSocket URL whose query includes the API credential.
        log.error("call_failed session=%s error_type=%s", session_id, type(error).__name__)
    finally:
        if playback_task:
            playback_task.cancel()
            await asyncio.gather(playback_task, return_exceptions=True)
        try:
            writer.write(packet(0x00))
            await writer.drain()
        except (ConnectionError, OSError):
            pass
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass
        if session_id != "unregistered":
            log.info("call_closed session=%s", session_id)


def load_config():
    path = Path(os.getenv("KRONOS_VOICE_CONFIG", "/etc/kronos/voice/config.json"))
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("simulation_mode") is not False:
        raise ValueError("Set simulation_mode=false explicitly for live telephone calls")
    if not config.get("use_ssh") or not config.get("pfsense_host"):
        raise ValueError("Configure the real SSH firewall connection")
    if not config.get("authorized_extensions"):
        raise ValueError("Configure authorized_extensions")
    return config


async def main():
    config = load_config()
    # Fail on missing credentials at startup, before answering any call.
    GeminiLiveVoiceClient()
    directory = os.getenv("KRONOS_CALL_DIR", "/run/kronos/calls")
    Path(directory).mkdir(mode=0o750, parents=True, exist_ok=True)
    # Remove abandoned contexts, never incident records or log evidence.
    for path in Path(directory).glob("*.json"):
        if time.time() - path.stat().st_mtime > 60:
            path.unlink()
    server = await asyncio.start_server(
        lambda r, w: handle_call(r, w, config, directory), "127.0.0.1",
        int(os.getenv("KRONOS_AUDIO_PORT", "9092")))
    log.info("audiosocket_listening address=%s", server.sockets[0].getsockname())
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())
