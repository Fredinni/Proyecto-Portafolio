"""Offline regression tests. No production calls, API keys or firewall changes."""

import asyncio
import base64
import contextlib
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
for folder in ("ai_voice_agent", "asterisk_pbx", "pfsense_pfctl_engine"):
    sys.path.insert(0, str(ROOT / "src" / folder))

import websockets
from call_trigger import AsteriskCallTrigger
from dispatcher import make_server
from gemini_audio_bridge import register_context
from gemini_live_client import GeminiLiveVoiceClient
from geoip_lookup import GeoIPLookup
from live_audio_server import Playback, consume_context, handle_call, packet, read_packet
from pfctl_wrapper import PfctlWrapper
from soar_tools_executor import SoarToolsExecutor
from voice_policy import VoiceActionPolicy

IP = "203.0.113.45"
INCIDENT = {"attacker_ip": IP, "operator_extension": "1004", "attack_type": "SQL_INJECTION",
            "signature": "SQLi UNION SELECT", "target_service": "test-service:443",
            "geoip": {"status": "found", "country": "Chile", "source": "fixture.mmdb"}}


class FakeFirewall:
    simulation_mode = False
    table_name = "test_table"

    def __init__(self, blocked=True, query_ok=True, mutate_ok=True):
        self.blocked = blocked
        self.query_ok = query_ok
        self.mutate_ok = mutate_ok
        self.changes = []

    def get_ip_status(self, ip):
        return {"success": self.query_ok, "verified": self.query_ok,
                "is_blocked": self.blocked if self.query_ok else None, "ip": ip}

    def unblock_ip(self, ip):
        self.changes.append(("unblock", ip))
        if self.mutate_ok:
            self.blocked = False
        return self.mutate_ok

    def block_ip(self, ip):
        self.changes.append(("block", ip))
        if self.mutate_ok:
            self.blocked = True
        return self.mutate_ok


class VoicePolicyTests(unittest.TestCase):
    def executor(self, **kwargs):
        fw = FakeFirewall(**kwargs)
        return SoarToolsExecutor({"authorized_extensions": ["1004"]}, INCIDENT, pfctl=fw), fw

    def test_explicit_unblock_is_executed_once_and_verified(self):
        tools, fw = self.executor()
        tools.observe_input("Desbloquéame la IP, por favor")
        result = tools.execute_tool_call("unblock_ip", {"ip": IP, "reason": "QA autorizado"})
        self.assertTrue(result["verified"])
        self.assertFalse(result["is_blocked"])
        self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])
        self.assertEqual(len(fw.changes), 1)

    def test_yes_requires_previous_question(self):
        tools, fw = self.executor()
        tools.observe_input("Sí")
        self.assertIsNone(tools.policy.confirmed_unblock_target())
        self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])
        tools.observe_output("¿Quieres que desbloquee esta IP o la mantenemos bloqueada?")
        tools.finish_turn()
        tools.observe_input("Sí, por favor.")
        self.assertEqual(tools.policy.confirmed_unblock_target(), IP)
        self.assertTrue(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])

    def test_interrupted_question_preserves_explicit_input_but_cancels_bare_yes(self):
        tools, fw = self.executor()
        tools.observe_output("¿Quieres que desbloquee esta IP?")
        tools.observe_input("Desbloquea esa IP")
        tools.interrupt_output()
        self.assertTrue(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])
        tools, fw = self.executor()
        tools.observe_output("¿Quieres que desbloquee esta IP?")
        tools.finish_turn()
        tools.interrupt_output()
        tools.observe_input("Sí")
        self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])

    def test_negations_qa_details_and_questions_never_authorize(self):
        for phrase in ["No la desbloquees", "Déjala bloqueada", "Espera, desbloquea después",
                       "Soy Kevin y estaba probando", "¿Qué tipo de ataque fue?",
                       "¿Cómo se desbloquea?", "Gracias", "El desbloqueo falló"]:
            with self.subTest(phrase=phrase):
                tools, fw = self.executor()
                tools.observe_input(phrase)
                self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])
                self.assertEqual(fw.changes, [])

    def test_model_output_cannot_authorize(self):
        tools, fw = self.executor()
        tools.observe_output("[ACTION:UNBLOCK] Ya te desbloqueé")
        self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])
        self.assertEqual(fw.changes, [])

    def test_polite_explicit_requests_are_actions(self):
        for phrase in ["¿Puedes desbloquear esa IP, por favor?", "¿Podrías liberar la IP?"]:
            tools, fw = self.executor()
            tools.observe_input(phrase)
            self.assertTrue(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])

    def test_block_status_question_is_not_a_block_order(self):
        tools, fw = self.executor()
        tools.observe_input("¿Está bloqueada esa IP?")
        self.assertFalse(tools.execute_tool_call("block_ip_permanently", {"ip": IP})["success"])
        self.assertEqual(fw.changes, [])

    def test_ip_substring_cannot_change_target(self):
        tools, fw = self.executor()
        tools.observe_input("Desbloquea 203.0.113.990")
        self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": "203.0.113.99"})["success"])
        self.assertEqual(fw.changes, [])

    def test_wrong_ip_unknown_extension_subnets_and_injection_denied(self):
        tools, fw = self.executor()
        tools.observe_input("Desbloquea la IP")
        for ip in ["203.0.113.99", "0.0.0.0/0", "1.1.1.1; reboot", None]:
            self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": ip})["success"])
        unknown = SoarToolsExecutor({"authorized_extensions": ["1004"]},
                                    {**INCIDENT, "operator_extension": ""}, pfctl=fw)
        unknown.observe_input("Desbloquea la IP")
        self.assertFalse(unknown.execute_tool_call("unblock_ip", {"ip": IP})["success"])

    def test_remote_failure_and_failed_verification_never_claim_success(self):
        for kwargs in [{"mutate_ok": False}, {"query_ok": False}]:
            tools, fw = self.executor(**kwargs)
            tools.observe_input("Desbloquea la IP")
            result = tools.execute_tool_call("unblock_ip", {"ip": IP})
            self.assertFalse(result["success"])
            self.assertFalse(result["verified"])

    def test_incident_details_preserve_firewall_geoip(self):
        tools, _ = self.executor()
        result = tools.execute_tool_call("get_incident_details", {})
        self.assertEqual(result["incident"]["geoip"], INCIDENT["geoip"])
        self.assertEqual(result["incident"]["signature"], "SQLi UNION SELECT")

    def test_simulation_cannot_execute_live_change(self):
        tools, fw = self.executor()
        fw.simulation_mode = True
        tools.observe_input("Desbloquea la IP")
        self.assertFalse(tools.execute_tool_call("unblock_ip", {"ip": IP})["success"])
        self.assertEqual(fw.changes, [])

    def test_protected_incident_or_config_never_mutates_infrastructure(self):
        for config, incident in [({"protected_ips": [IP]}, INCIDENT),
                                 ({}, {**INCIDENT, "source_protected": True})]:
            with self.subTest(config=config):
                fw = FakeFirewall()
                tools = SoarToolsExecutor({"authorized_extensions": ["1004"], **config}, incident, pfctl=fw)
                tools.observe_input("Desbloquea esa IP")
                result = tools.execute_tool_call("unblock_ip", {"ip": IP})
                self.assertFalse(result["success"])
                self.assertIn("protegido", result["error"])
                self.assertEqual(fw.changes, [])
                self.assertTrue(tools.execute_tool_call("get_firewall_states", {"ip": IP})["success"])


class FirewallAndMetadataTests(unittest.TestCase):
    def test_pfctl_error_is_unknown(self):
        fw = PfctlWrapper({"simulation_mode": False})
        with patch.object(fw, "_exec_command", return_value=subprocess.CompletedProcess([], 1, "", "permission denied")):
            result = fw.get_ip_status(IP)
        self.assertFalse(result["success"])
        self.assertIsNone(result["is_blocked"])

    def test_table_membership_includes_network_entries(self):
        fw = PfctlWrapper({"simulation_mode": False})
        with patch.object(fw, "_exec_command", return_value=subprocess.CompletedProcess([], 0, "203.0.113.0/24\n", "")):
            self.assertTrue(fw.get_ip_status(IP)["is_blocked"])
            self.assertFalse(fw.get_ip_status("198.51.100.10")["is_blocked"])

    def test_no_implicit_firewall_simulation(self):
        self.assertFalse(PfctlWrapper().simulation_mode)

    def test_outbound_identity_is_endpoint_not_bot_callerid(self):
        values = dict(value.split("=", 1) for value in AsteriskCallTrigger._context_variables(INCIDENT))
        with tempfile.TemporaryDirectory() as directory:
            sid = register_context({"agi_channel": "PJSIP/1004-000000ff", "agi_callerid": "1000"},
                                   "INCIDENT", lambda name: values.get(name, ""), directory)
            context = consume_context(sid, directory)
            self.assertEqual(context["operator_extension"], "1004")
            self.assertEqual(context["geoip"], INCIDENT["geoip"])
            with self.assertRaises(FileNotFoundError):
                consume_context(sid, directory)

    def test_large_context_survives_short_ami_headers(self):
        incident = {**INCIDENT, "http_endpoint": "/?payload=" + "x" * 7000}
        values = dict(value.split("=", 1) for value in AsteriskCallTrigger._context_variables(incident))
        self.assertTrue(all(len(value) < 500 for value in values.values()))
        with tempfile.TemporaryDirectory() as directory:
            sid = register_context({"agi_channel": "PJSIP/1004-000000ff"}, "INCIDENT",
                                   lambda name: values.get(name, ""), directory)
            self.assertEqual(consume_context(sid, directory)["http_endpoint"], incident["http_endpoint"])

    def test_direct_call_does_not_invent_incident(self):
        with tempfile.TemporaryDirectory() as directory:
            sid = register_context({"agi_channel": "PJSIP/1002-000000ab"}, "DIRECT_CALL",
                                   lambda _: self.fail("Direct call requested incident variables"), directory)
            self.assertNotIn("attacker_ip", consume_context(sid, directory))

    def test_expired_context_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            sid = str(uuid.uuid4())
            (Path(directory) / (sid + ".json")).write_text(json.dumps({"created_at": time.time() - 90}))
            with self.assertRaises(ValueError):
                consume_context(sid, directory)

    def test_no_spool_is_a_real_failure(self):
        trigger = AsteriskCallTrigger(spool_dir="/path/that/does/not/exist", prefer_ami=False)
        self.assertFalse(trigger.trigger_ciso_call("PJSIP/1004", INCIDENT)["success"])

    def test_geoip_does_not_invent_location(self):
        geo = GeoIPLookup({"db_path": "/no/database.mmdb"})
        self.assertEqual(geo.lookup("8.8.8.8")["status"], "unavailable")
        self.assertIsNone(geo.lookup("194.1.1.1")["country"])
        self.assertEqual(geo.lookup("192.168.30.50")["status"], "non_public")

    def test_geoip_reads_pfsense_mmdb_fields(self):
        class Reader:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def get(self, ip):
                return {"country": {"iso_code": "CL", "names": {"es": "Chile"}},
                        "city": {"names": {"en": "Santiago"}}}
        geo = GeoIPLookup({"db_path": "/pfsense/installed/GeoLite2-City.mmdb"}, opener=lambda _: Reader())
        result = geo.lookup("8.8.8.8")
        self.assertEqual(result["source"], "GeoLite2-City.mmdb")
        self.assertEqual(result["country"], "Chile")


class DispatcherTests(unittest.TestCase):
    def test_auth_dedup_and_failure_reporting(self):
        class Trigger:
            success = True
            def trigger_ciso_call(self, channel, incident):
                return {"success": self.success, "status": "DISPATCHED" if self.success else "FAILED"}
        trigger = Trigger()
        token = "test-only-dispatch-token-123456"
        server = make_server(("127.0.0.1", 0), token, "PJSIP/1004", trigger=trigger, global_cooldown=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/incident"
        def request(auth=token, ip=IP):
            req = urllib.request.Request(url, data=json.dumps({**INCIDENT, "attacker_ip": ip}).encode(),
                                         headers={"Authorization": "Bearer " + auth})
            return urllib.request.urlopen(req, timeout=3)
        try:
            with self.assertRaises(urllib.error.HTTPError) as error:
                request("wrong")
            self.assertEqual(error.exception.code, 401)
            with request() as response:
                self.assertTrue(json.load(response)["call_initiated"])
            with request() as response:
                self.assertEqual(response.status, 202)
            trigger.success = False
            with self.assertRaises(urllib.error.HTTPError) as error:
                request(ip="203.0.113.99")
            self.assertEqual(error.exception.code, 503)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


class AudioIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_barge_in_discards_queued_audio(self):
        playback = Playback()
        await playback.feed(b"\x10\x00" * 2400)
        self.assertGreater(len(playback.buffer), 0)
        await playback.interrupt()
        self.assertEqual(len(playback.buffer), 0)
        self.assertIsNone(playback.rate_state)

    async def test_packet_handles_fragmented_tcp(self):
        reader = asyncio.StreamReader()
        data = packet(0x10, b"\x01\x00" * 160)
        for chunk in [data[:1], data[1:2], data[2:10], data[10:]]:
            reader.feed_data(chunk)
        kind, payload = await read_packet(reader)
        self.assertEqual((kind, len(payload)), (0x10, 320))

    async def test_real_tcp_and_websocket_voice_tool_roundtrip(self):
        completed = asyncio.Event()
        failure = []
        fw = FakeFirewall()
        tool_results = []

        async def fake_gemini(ws, *args):
            try:
                setup = json.loads(await ws.recv())["setup"]
                self.assertEqual(setup["generationConfig"]["responseModalities"], ["AUDIO"])
                self.assertIn("get_incident_details", [f["name"] for f in setup["tools"][0]["functionDeclarations"]])
                await ws.send(json.dumps({"setupComplete": {}}))
                await ws.recv()  # Initial greeting instruction.
                await ws.send(json.dumps({"serverContent": {
                    "outputTranscription": {"text": "¿Quieres que desbloquee esta IP?"}, "generationComplete": True}}))
                await ws.send(json.dumps({"serverContent": {"turnComplete": True}}))
                # Real bidirectional microphone frames reach the WebSocket.
                while True:
                    incoming = json.loads(await ws.recv())
                    if "realtimeInput" in incoming:
                        self.assertEqual(incoming["realtimeInput"]["audio"]["mimeType"], "audio/pcm;rate=16000")
                        break
                await ws.send(json.dumps({"serverContent": {"inputTranscription": {"text": "Sí, por favor."}}}))
                await ws.send(json.dumps({"toolCall": {"functionCalls": [{"id": "unblock-1", "name": "unblock_ip", "args": {"ip": IP, "reason": "QA"}}]},
                                          "serverContent": {"generationComplete": True}}))
                while True:
                    incoming = json.loads(await ws.recv())
                    if "toolResponse" in incoming:
                        tool_results.extend(incoming["toolResponse"]["functionResponses"])
                        break
                pcm = base64.b64encode(b"\x20\x00" * 2400).decode()
                await ws.send(json.dumps({"serverContent": {"modelTurn": {"parts": [{"inlineData": {
                    "mimeType": "audio/pcm;rate=24000", "data": pcm}}]}, "turnComplete": True}}))
                await asyncio.sleep(.16)  # Let the real 20ms telephone pacer play.
            except Exception as error:
                failure.append(error)
            finally:
                completed.set()

        async with websockets.serve(fake_gemini, "127.0.0.1", 0) as fake:
            ws_url = f"ws://127.0.0.1:{fake.sockets[0].getsockname()[1]}"
            client_factory = lambda: GeminiLiveVoiceClient(api_key="test-key", connect=lambda url, **kw: websockets.connect(ws_url, **kw))
            with tempfile.TemporaryDirectory() as directory:
                sid = str(uuid.uuid4())
                (Path(directory) / (sid + ".json")).write_text(json.dumps({**INCIDENT, "created_at": time.time()}))
                factory = lambda **kw: SoarToolsExecutor(**kw, pfctl=fw)
                with patch("live_audio_server.SoarToolsExecutor", side_effect=factory):
                    server = await asyncio.start_server(lambda r, w: handle_call(r, w,
                        {"authorized_extensions": ["1004"]}, directory, client_factory), "127.0.0.1", 0)
                    async with server:
                        reader, writer = await asyncio.open_connection("127.0.0.1", server.sockets[0].getsockname()[1])
                        writer.write(packet(1, uuid.UUID(sid).bytes))
                        for _ in range(10):
                            writer.write(packet(0x10, b"\x00\x04" * 160))
                        await writer.drain()
                        await asyncio.wait_for(completed.wait(), timeout=5)
                        heard_audio = False
                        while True:
                            kind, payload = await asyncio.wait_for(read_packet(reader), timeout=3)
                            if kind == 0:
                                break
                            if any(payload):
                                heard_audio = True
                        self.assertTrue(heard_audio)
                        writer.close()
                        await writer.wait_closed()
        if failure:
            raise failure[0]
        self.assertTrue(tool_results[0]["response"]["verified"])
        self.assertEqual(fw.changes, [("unblock", IP)])


if __name__ == "__main__":
    unittest.main()
