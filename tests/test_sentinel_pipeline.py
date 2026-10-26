#!/usr/bin/env python3
"""
KRONOS SENTINEL - Comprehensive Pipeline Test Suite (A6 & A7 End-to-End)
Authors: Bruno Urrea Ortiz & Freddy Vásquez Cortés (Portafolio de Título - Duoc UC)
Project: KRONOS SENTINEL - Autonomous AI-IPS & Live Voice Incident Response
"""

import json
import os
import socket
import sys
import threading
import time
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler

# Inyectar rutas de módulos KRONOS
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGINE_DIR = os.path.join(PROJECT_ROOT, "src", "pfsense_pfctl_engine")
PBX_DIR = os.path.join(PROJECT_ROOT, "src", "asterisk_pbx")
VOICE_DIR = os.path.join(PROJECT_ROOT, "src", "ai_voice_agent")

for p in [ENGINE_DIR, PBX_DIR, VOICE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from false_positive_filter import FalsePositiveFilter
from pfctl_wrapper import PfctlWrapper
from log_correlator import PfctlLogCorrelator
from call_trigger import AsteriskCallTrigger


class MockAMIServer:
    """Servidor TCP simulado de Asterisk Manager Interface (AMI) en puerto 5038 o dinámico"""

    def __init__(self, port: int = 0):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', self.port))
        self.port = self.sock.getsockname()[1]
        self.running = False
        self.received_actions = []
        self.thread = None

    def start(self):
        self.running = True
        self.sock.listen(5)
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        while self.running:
            try:
                client, _ = self.sock.accept()
                client.settimeout(2.0)
                # Enviar banner de bienvenida Asterisk Call Manager
                client.sendall(b"Asterisk Call Manager/5.0.0\r\n")

                buffer = ""
                while self.running:
                    try:
                        data = client.recv(1024).decode('utf-8')
                        if not data:
                            break
                        buffer += data
                        if "\r\n\r\n" in buffer:
                            parts = buffer.split("\r\n\r\n")
                            for part in parts[:-1]:
                                if not part.strip():
                                    continue
                                self.received_actions.append(part.strip())
                                if "Action: Login" in part:
                                    client.sendall(b"Response: Success\r\nMessage: Authentication accepted\r\n\r\n")
                                elif "Action: Originate" in part:
                                    client.sendall(b"Response: Success\r\nMessage: Originate successfully queued\r\n\r\n")
                                elif "Action: Logoff" in part:
                                    client.sendall(b"Response: Goodbye\r\nMessage: Thanks for all the fish\r\n\r\n")
                            buffer = parts[-1]
                    except socket.timeout:
                        break
                client.close()
            except Exception:
                break

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass
        if self.thread:
            self.thread.join(timeout=1.0)


class MockVoiceDispatcherHandler(BaseHTTPRequestHandler):
    received_incidents = []

    def do_POST(self):
        if self.path == "/incident":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            incident = json.loads(body.decode('utf-8'))
            MockVoiceDispatcherHandler.received_incidents.append(incident)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "SUCCESS", "received": True}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silenciar logs HTTP durante el test runner


class TestSentinelPipeline(unittest.TestCase):
    """Batería de pruebas unitarias y de integración end-to-end para A6 y A7"""

    def setUp(self):
        self.config = {
            "pfctl_table": "snort2c",
            "simulation_mode": True,
            "confidence_threshold": 0.75,
            "enable_auto_pfctl_drop": True,
            "dispatcher_webhook_url": "http://127.0.0.1:8899/incident",
            "asterisk": {
                "host": "127.0.0.1",
                "port": 5038,
                "user": "kronos_ami",
                "secret": "KronosSecOps2026!",
                "ciso_extension": "PJSIP/1001"
            }
        }
        self.filter = FalsePositiveFilter(self.config)
        self.pfctl = PfctlWrapper(self.config)

    def test_01_ast_tautology_analyzer(self):
        """A6: Verifica que el analizador AST detecte tautologías reales y descarte parámetros normales"""
        # Tautología numérica clásica 1=1
        taut_numeric = self.filter.evaluate_ast_tautologies("id=1' OR 1=1 --")
        self.assertGreater(len(taut_numeric), 0, "AST debe identificar 1=1 como tautología")
        self.assertTrue(taut_numeric[0]["is_tautology"])
        self.assertEqual(taut_numeric[0]["operands"], ("1", "1"))

        # Tautología de cadenas '1'='1'
        taut_string = self.filter.evaluate_ast_tautologies("username=admin' OR '1'='1")
        self.assertGreater(len(taut_string), 0, "AST debe identificar '1'='1' como tautología")
        self.assertEqual(taut_string[0]["operands"], ("1", "1"))

        # Tautología con letras 'a'='a'
        taut_alpha = self.filter.evaluate_ast_tautologies("user' OR 'a'='a' #")
        self.assertGreater(len(taut_alpha), 0, "AST debe identificar 'a'='a' como tautología")
        self.assertEqual(taut_alpha[0]["operands"], ("a", "a"))

        # Parámetro benigno normal (Submit=Submit) NO debe ser tautología maliciosa
        taut_benign = self.filter.evaluate_ast_tautologies("/index.php?Submit=Submit&page=home")
        self.assertEqual(len(taut_benign), 0, "Parámetros HTTP normales no deben generar falsas tautologías")

    def test_02_false_positive_noise_suppression(self):
        """A6: Verifica la supresión de firmas de escaneo ruidosas con score < 0.75"""
        noise_events = [
            {"src_ip": "198.51.100.1", "alert": {"signature": "ET SCAN Potential SSH Scan"}},
            {"src_ip": "198.51.100.2", "alert": {"signature": "GPL SCAN PING *NIX"}},
            {"src_ip": "198.51.100.3", "alert": {"signature": "ET POLICY Suspicious inbound to MSSQL port"}},
            {"src_ip": "198.51.100.4", "alert": {"signature": "SURICATA HTTP suspicious User-Agent"}},
        ]

        for ev in noise_events:
            res = self.filter.analyze(ev)
            self.assertFalse(res["is_real_attack"], f"Firma ruidosa no debe clasificarse como ataque: {ev}")
            self.assertLess(res["confidence_score"], 0.75, "Confianza debe ser menor al umbral (0.75)")
            self.assertIn("SUPPRESSED", res["attack_type"])

    def test_03_high_fidelity_attack_detection(self):
        """A6: Verifica detección de SQLi y RCE con confianza >= 0.75"""
        # Ataque SQLi con AST Tautology
        sqli_ev = {
            "src_ip": "185.220.101.5",
            "dest_ip": "192.168.20.50",
            "alert": {"signature": "SURICATA HTTP SQL Injection Attempt"},
            "http": {"url": "/vulnerabilities/sqli/?id=1%27%20OR%20%271%27%3D%271%20--&Submit=Submit"}
        }
        res_sqli = self.filter.analyze(sqli_ev)
        self.assertTrue(res_sqli["is_real_attack"])
        self.assertTrue(res_sqli["ast_verified"])
        self.assertGreaterEqual(res_sqli["confidence_score"], 0.75)

        # Ataque SQLi con UNION SELECT
        union_ev = {
            "src_ip": "185.220.101.6",
            "dest_ip": "192.168.20.50",
            "alert": {"signature": "SURICATA HTTP SQL Injection Attempt"},
            "http": {"url": "/vulnerabilities/sqli/?id=1%27%20UNION%20SELECT%20null%2Cuser%20FROM%20users--"}
        }
        res_union = self.filter.analyze(union_ev)
        self.assertTrue(res_union["is_real_attack"])
        self.assertGreaterEqual(res_union["confidence_score"], 0.75)

        # Ataque RCE
        rce_ev = {
            "src_ip": "185.220.101.7",
            "dest_ip": "192.168.20.50",
            "alert": {"signature": "SURICATA HTTP Command Injection"},
            "http": {"url": "/vulnerabilities/exec/?ip=127.0.0.1%3B%20cat%20%2Fetc%2Fpasswd"}
        }
        res_rce = self.filter.analyze(rce_ev)
        self.assertTrue(res_rce["is_real_attack"])
        self.assertGreaterEqual(res_rce["confidence_score"], 0.75)

    def test_04_pfctl_kernel_state_management(self):
        """A6: Verifica adición atómica a tabla <snort2c>, verificación y purga de estados"""
        target_ip = "185.220.101.99"
        self.assertFalse(self.pfctl.is_ip_blocked(target_ip))

        # Bloquear IP
        block_ok = self.pfctl.block_ip(target_ip)
        self.assertTrue(block_ok)
        self.assertTrue(self.pfctl.is_ip_blocked(target_ip))
        self.assertIn(target_ip, self.pfctl.list_blocked_ips())

        # Desbloquear IP
        unblock_ok = self.pfctl.unblock_ip(target_ip)
        self.assertTrue(unblock_ok)
        self.assertFalse(self.pfctl.is_ip_blocked(target_ip))

    def test_05_batch_correlation_suppression_rate(self):
        """A6: Demuestra que la supresión de falsos positivos supera el 50% requerido por rúbrica"""
        correlator = PfctlLogCorrelator()
        correlator.config["simulation_mode"] = True
        correlator.pfctl.simulation_mode = True

        dataset = [
            # 6 Eventos de ruido/escaneo
            {"event_type": "alert", "src_ip": "10.0.0.1", "alert": {"signature": "ET SCAN Potential SSH Scan"}},
            {"event_type": "alert", "src_ip": "10.0.0.2", "alert": {"signature": "GPL SCAN PING *NIX"}},
            {"event_type": "alert", "src_ip": "10.0.0.3", "alert": {"signature": "SURICATA HTTP suspicious User-Agent"}},
            {"event_type": "alert", "src_ip": "10.0.0.4", "alert": {"signature": "ET SCAN Nmap Scripting Engine"}},
            {"event_type": "alert", "src_ip": "10.0.0.5", "alert": {"signature": "ET POLICY Suspicious inbound to MSSQL port"}},
            {"event_type": "alert", "src_ip": "10.0.0.6", "alert": {"signature": "SURICATA HTTP Request to root directory"}},
            # 2 Ataques reales
            {"event_type": "alert", "src_ip": "185.220.101.10", "alert": {"signature": "SQLi"}, "http": {"url": "/?id=1%27%20OR%201%3D1"}},
            {"event_type": "alert", "src_ip": "185.220.101.11", "alert": {"signature": "RCE"}, "http": {"url": "/?cmd=%3B%20whoami"}}
        ]

        batch_result = correlator.correlate_batch(dataset, trigger_dispatch=False)
        self.assertEqual(batch_result["total_processed"], 8)
        self.assertEqual(batch_result["suppressed_count"], 6)
        self.assertEqual(batch_result["confirmed_count"], 2)
        # 6 / 8 = 75% de supresión de ruido
        self.assertGreater(batch_result["suppression_rate"], 0.50)
        self.assertTrue(batch_result["meets_rubric_gt_50pct"])

    def test_06_asterisk_ami_originate(self):
        """A7: Verifica disparo de llamadas mediante socket TCP AMI (Action: Originate)"""
        mock_ami = MockAMIServer()
        mock_ami.start()
        time.sleep(0.1)

        try:
            trigger = AsteriskCallTrigger(
                ami_host="127.0.0.1",
                ami_port=mock_ami.port,
                ami_user="kronos_ami",
                ami_secret="KronosSecOps2026!",
                prefer_ami=True
            )

            res = trigger.trigger_ciso_call(
                ciso_channel="PJSIP/1001",
                incident_context={
                    "attack_type": "SQL Injection (AST Tautology)",
                    "attacker_ip": "185.220.101.5",
                    "geo_country": "Federación Rusa"
                }
            )

            self.assertEqual(res["status"], "DISPATCHED")
            self.assertEqual(res["method"], "AMI_TCP_5038")
            self.assertTrue(res["success"])

            # Validar que el servidor AMI recibió Login, Originate y Logoff
            received_str = " --- ".join(mock_ami.received_actions)
            self.assertIn("Action: Login", received_str)
            self.assertIn("Action: Originate", received_str)
            self.assertIn("Channel: PJSIP/1001", received_str)
            self.assertIn("INCIDENT_TYPE=SQL Injection (AST Tautology)", received_str)
            self.assertIn("ATTACKER_IP=185.220.101.5", received_str)
            self.assertIn("Action: Logoff", received_str)

        finally:
            mock_ami.stop()

    def test_07_asterisk_spool_fallback(self):
        """A7: Verifica conmutación automática por error (fallback) a .call file si AMI está apagado"""
        # Puerto 59999 no existe, forzará fallback inmediato a spool
        trigger = AsteriskCallTrigger(
            ami_host="127.0.0.1",
            ami_port=59999,
            prefer_ami=True
        )

        res = trigger.trigger_ciso_call(
            ciso_channel="PJSIP/1001",
            incident_context={
                "attack_type": "Command Injection RCE",
                "attacker_ip": "185.220.101.7",
                "geo_country": "Nodo Hostil"
            }
        )

        self.assertEqual(res["status"], "DISPATCHED")
        self.assertEqual(res["method"], "SPOOL_CALL_FILE")
        self.assertTrue(res["success"])

    def test_08_end_to_end_sentinel_pipeline(self):
        """End-to-End: Alerta EVE -> Correlador -> AST -> pfctl drop -> Webhook de Voz -> Asterisk AMI"""
        # 1. Iniciar Mock AMI
        mock_ami = MockAMIServer()
        mock_ami.start()
        time.sleep(0.1)

        # 2. Iniciar Mock Voice Dispatcher HTTP Server en puerto dinámico
        MockVoiceDispatcherHandler.received_incidents = []
        httpd = HTTPServer(('127.0.0.1', 0), MockVoiceDispatcherHandler)
        dispatcher_port = httpd.server_address[1]
        dispatcher_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        dispatcher_thread.start()

        try:
            # 3. Configurar Correlador
            correlator = PfctlLogCorrelator()
            correlator.webhook_url = f"http://127.0.0.1:{dispatcher_port}/incident"
            correlator.pfctl.simulation_mode = True

            # 4. Inyectar evento de ataque crítico
            attack_event = {
                "event_type": "alert",
                "src_ip": "185.220.101.50",
                "dest_ip": "192.168.20.50",
                "alert": {
                    "signature": "SURICATA HTTP SQL Injection Inbound",
                    "severity": 1
                },
                "http": {
                    "url": "/vulnerabilities/sqli/?id=1%27%20OR%20%271%27%3D%271%20--&Submit=Submit",
                    "http_method": "GET"
                }
            }

            diag = correlator.process_single_event(attack_event, trigger_dispatch=True)

            # Validar diagnóstico inmediato
            self.assertEqual(diag["status"], "CONFIRMED_AND_MITIGATED")
            self.assertTrue(diag["is_real_attack"])
            self.assertTrue(diag["pfctl_blocked"])
            self.assertTrue(correlator.pfctl.is_ip_blocked("185.220.101.50"))

            # Esperar despacho HTTP asíncrono
            time.sleep(0.5)

            # Validar que el despachador de voz recibió el incidente
            self.assertEqual(len(MockVoiceDispatcherHandler.received_incidents), 1)
            rec = MockVoiceDispatcherHandler.received_incidents[0]
            self.assertEqual(rec["attacker_ip"], "185.220.101.50")
            self.assertEqual(rec["attack_type"], "SQL_INJECTION (AST_TAUTOLOGY)")
            self.assertTrue(rec["ast_verified"])
            self.assertTrue(rec["pfctl_blocked"])

        finally:
            mock_ami.stop()
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
