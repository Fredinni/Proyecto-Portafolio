#!/usr/bin/env python3
"""
KRONOS SENTINEL - Voice Incident Dispatcher & Asterisk PBX Trigger Server (Hardened)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import os
import json
import uuid
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# Añadir ruta del PBX para invocar call trigger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'asterisk_pbx')))
from call_trigger import AsteriskCallTrigger

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [VOICE-DISPATCHER] %(message)s')

# Almacenamiento en memoria de sesiones de incidentes por UUID
ACTIVE_INCIDENT_SESSIONS = {}

class IncidentDispatcherHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/incident":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            
            try:
                incident_data = json.loads(post_body.decode('utf-8'))
                session_id = uuid.uuid4().hex
                incident_data["session_id"] = session_id
                ACTIVE_INCIDENT_SESSIONS[session_id] = incident_data
                
                logging.info(f"==> INCIDENTE VALIDADO RECIBIDO EN DISPATCHER <==")
                logging.info(f"SessionID: {session_id} | Vector: {incident_data.get('attack_type')} | IP: {incident_data.get('attacker_ip')}")
                
                # Disparar llamada telefónica a Bruno Urrea (CISO / Anexo 1001)
                trigger = AsteriskCallTrigger()
                call_success = trigger.trigger_ciso_call(
                    ciso_channel="PJSIP/1001",
                    incident_context=incident_data
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    "status": "SUCCESS",
                    "session_id": session_id,
                    "target_channel": "PJSIP/1001",
                    "call_initiated": call_success
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                logging.error(f"Error procesando incidente en dispatcher: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def run_dispatcher(port: int = 8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, IncidentDispatcherHandler)
    logging.info(f"KRONOS Voice Dispatcher activo en puerto HTTP {port} (Llamadas a PJSIP/1001)...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run_dispatcher()
