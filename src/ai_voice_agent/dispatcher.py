#!/usr/bin/env python3
"""Authenticated incident dispatch with bounded input and call deduplication."""

import hmac
import ipaddress
import json
import logging
import os
from pathlib import Path
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "asterisk_pbx"))
from call_trigger import AsteriskCallTrigger

log = logging.getLogger(__name__)


class IncidentDispatcherHandler(BaseHTTPRequestHandler):
    def reply(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"status": "listening", "voice_e2e_verified": False})
        self.reply(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/incident":
            return self.reply(404, {"error": "not_found"})
        supplied = self.headers.get("Authorization", "")
        if not hmac.compare_digest(supplied, "Bearer " + self.server.dispatch_token):
            return self.reply(401, {"error": "unauthorized"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16000:
                return self.reply(413, {"error": "invalid_body_size"})
            self.connection.settimeout(5)
            incident = json.loads(self.rfile.read(size))
            if not isinstance(incident, dict) or not incident.get("attack_type"):
                raise ValueError("Missing attack type")
            incident["attacker_ip"] = str(ipaddress.ip_address(incident["attacker_ip"]))
        except (ValueError, KeyError, TypeError, OSError):
            return self.reply(400, {"error": "invalid_incident"})
        key = incident["attacker_ip"]
        now = time.monotonic()
        with self.server.dispatch_lock:
            self.server.recent = {k: t for k, t in self.server.recent.items()
                                  if now - t < self.server.cooldown}
            if key in self.server.recent:
                return self.reply(202, {"status": "DUPLICATE_SUPPRESSED", "call_initiated": False})
            self.server.recent[key] = now
        try:
            result = self.server.trigger.trigger_ciso_call(self.server.target_channel, incident)
        except Exception:
            log.error("dispatch_failed")
            result = {"success": False, "status": "FAILED"}
        if not result["success"]:
            with self.server.dispatch_lock:
                self.server.recent.pop(key, None)
        self.reply(200 if result["success"] else 503, {
            "status": result["status"], "call_initiated": result["success"],
            "target_channel": self.server.target_channel, "call_id": result.get("call_id")})


def make_server(address, token, target_channel, trigger=None, cooldown=120):
    if not token or len(token) < 24:
        raise ValueError("Configure KRONOS_DISPATCH_TOKEN with at least 24 characters")
    if not re.fullmatch(r"PJSIP/[A-Za-z0-9_]+", target_channel):
        raise ValueError("Configure KRONOS_CALL_CHANNEL")
    server = ThreadingHTTPServer(address, IncidentDispatcherHandler)
    server.dispatch_token = token
    server.target_channel = target_channel
    server.trigger = trigger or AsteriskCallTrigger()
    server.cooldown = cooldown
    server.dispatch_lock = threading.Lock()
    server.recent = {}
    return server


def run_dispatcher(port=None):
    server = make_server((os.getenv("KRONOS_DISPATCH_BIND", "127.0.0.1"),
                          port or int(os.getenv("KRONOS_DISPATCH_PORT", "8080"))),
                         os.getenv("KRONOS_DISPATCH_TOKEN", ""),
                         os.getenv("KRONOS_CALL_CHANNEL", ""))
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_dispatcher()
