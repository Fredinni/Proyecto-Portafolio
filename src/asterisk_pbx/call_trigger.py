#!/usr/bin/env python3
"""
KRONOS SENTINEL - Asterisk Auto-Dialer & Call File Generator (Hardened)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import os
import uuid
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [ASTERISK-CALL-TRIGGER] %(message)s')

class AsteriskCallTrigger:
    def __init__(self, spool_dir: str = "/var/spool/asterisk/outgoing"):
        self.spool_dir = spool_dir

    def trigger_ciso_call(self, ciso_channel: str = "PJSIP/1001", incident_context: Dict[str, Any] = None) -> bool:
        """
        Genera un Asterisk .call file atómico con UUID para originar una llamada inmediata al CISO (Anexo 1001)
        y conectar el canal de audio con el agente de voz Gemini Live.
        """
        if incident_context is None:
            incident_context = {}
            
        call_id = uuid.uuid4().hex[:12]
        safe_attack_type = str(incident_context.get('attack_type', 'SQLi')).replace('\n', ' ')
        safe_attacker_ip = str(incident_context.get('attacker_ip', '0.0.0.0')).replace('\n', ' ')
        safe_geo = str(incident_context.get('geo_country', 'Unknown')).replace('\n', ' ')

        call_file_content = f"""Channel: {ciso_channel}
CallerID: "KRONOS SENTINEL AI" <1000>
MaxRetries: 2
RetryTime: 5
WaitTime: 25
Context: kronos-emergency-response
Extension: s
Priority: 1
Set: INCIDENT_TYPE={safe_attack_type}
Set: ATTACKER_IP={safe_attacker_ip}
Set: GEO_ORIGIN={safe_geo}
Set: CALL_ID={call_id}
"""
        temp_file = f"/tmp/kronos_{call_id}.call"
        dest_file = f"{self.spool_dir}/kronos_{call_id}.call"
        
        logging.warning(f"ORIGINANDO LLAMADA DE EMERGENCIA EN ASTERISK HACIA: {ciso_channel} (CallID: {call_id})")
        
        try:
            if os.path.exists(self.spool_dir):
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(call_file_content)
                os.rename(temp_file, dest_file)
                logging.info(f"Archivo de llamada movido a {dest_file} -> Asterisk procesando llamada...")
            else:
                logging.info(f"[SIMULACIÓN PBX LOCAL] Spool no montado en host. Contenido del .call file:")
                for line in call_file_content.strip().split("\n"):
                    logging.info(f"   | {line}")
            return True
        except Exception as e:
            logging.error(f"Error generando llamada en Asterisk: {e}")
            return False

if __name__ == "__main__":
    trigger = AsteriskCallTrigger()
    trigger.trigger_ciso_call("PJSIP/1001", {
        "attack_type": "SQL Injection Crítica (UNION SELECT)",
        "attacker_ip": "185.220.101.5",
        "geo_country": "Federación Rusa"
    })
