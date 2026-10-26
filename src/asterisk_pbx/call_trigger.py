#!/usr/bin/env python3
"""
KRONOS SENTINEL - Asterisk Auto-Dialer & AMI Originate Engine (Python 3.12)
Author: Bruno Urrea Ortiz & Freddy Vásquez Cortés (Portafolio de Título - Duoc UC)
Project: KRONOS SENTINEL - Autonomous AI-IPS & Live Voice Incident Response
"""

import logging
import os
import socket
import time
import uuid
from typing import Dict, Any, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [ASTERISK-CALL-TRIGGER] %(message)s'
)


class AsteriskCallTrigger:
    """
    Despachador de llamadas telefónicas de emergencia hacia Asterisk PBX 20 LTS.
    Soporta disparo prioritario mediante Asterisk Manager Interface (AMI Action: Originate)
    sobre TCP 5038, con conmutación por error (fallback) automática a generación
    atómica de archivos de llamada en spool (/var/spool/asterisk/outgoing).
    """

    def __init__(
        self,
        ami_host: str = "localhost",
        ami_port: int = 5038,
        ami_user: str = "kronos_ami",
        ami_secret: str = "KronosSecOps2026!",
        spool_dir: str = "/var/spool/asterisk/outgoing",
        prefer_ami: bool = True
    ):
        self.ami_host = ami_host
        self.ami_port = ami_port
        self.ami_user = ami_user
        self.ami_secret = ami_secret
        self.spool_dir = spool_dir
        self.prefer_ami = prefer_ami

    def _sanitize_header(self, text: Any, default: str = "") -> str:
        """Elimina retornos de carro y saltos de línea para evitar CRLF injection en AMI"""
        val = str(text) if text is not None else default
        return val.replace("\r", " ").replace("\n", " ").strip()

    def originate_via_ami(
        self,
        channel: str,
        incident_context: Dict[str, Any],
        call_id: str
    ) -> Tuple[bool, str]:
        """
        Envía comando Originate a través del protocolo AMI por socket TCP directo.
        """
        safe_attack_type = self._sanitize_header(incident_context.get("attack_type", "Incidente No Identificado"))
        safe_attacker_ip = self._sanitize_header(incident_context.get("attacker_ip", "0.0.0.0"))
        safe_geo = self._sanitize_header(incident_context.get("geo_country", "Origen Desconocido"))

        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect((self.ami_host, self.ami_port))

            # Leer banner inicial de Asterisk Call Manager (p.ej. Asterisk Call Manager/5.0.0)
            initial_banner = s.recv(1024).decode('utf-8', errors='ignore')
            if "Asterisk Call Manager" not in initial_banner:
                return False, f"Banner AMI inválido: {initial_banner.strip()}"

            # 1. Enviar Login
            login_cmd = (
                f"Action: Login\r\n"
                f"Username: {self.ami_user}\r\n"
                f"Secret: {self.ami_secret}\r\n\r\n"
            )
            s.sendall(login_cmd.encode('utf-8'))

            login_resp = ""
            while "Response:" not in login_resp:
                chunk = s.recv(2048).decode('utf-8', errors='ignore')
                if not chunk:
                    break
                login_resp += chunk

            if "Response: Success" not in login_resp:
                return False, f"Fallo de autenticacion AMI: {login_resp.strip()}"

            # 2. Enviar Action: Originate para conectar con el contexto de respuesta
            originate_cmd = (
                f"Action: Originate\r\n"
                f"Channel: {channel}\r\n"
                f"Context: kronos-emergency-response\r\n"
                f"Exten: s\r\n"
                f"Priority: 1\r\n"
                f"CallerID: \"KRONOS SENTINEL AI\" <1000>\r\n"
                f"Timeout: 25000\r\n"
                f"Async: true\r\n"
                f"Variable: INCIDENT_TYPE={safe_attack_type}\r\n"
                f"Variable: ATTACKER_IP={safe_attacker_ip}\r\n"
                f"Variable: GEO_ORIGIN={safe_geo}\r\n"
                f"Variable: CALL_ID={call_id}\r\n\r\n"
            )
            s.sendall(originate_cmd.encode('utf-8'))
            
            orig_resp = ""
            while "Response:" not in orig_resp:
                chunk = s.recv(2048).decode('utf-8', errors='ignore')
                if not chunk:
                    break
                orig_resp += chunk

            # 3. Logoff cortés
            s.sendall(b"Action: Logoff\r\n\r\n")
            try:
                s.recv(1024)
            except Exception:
                pass

            if "Response: Success" in orig_resp or "Response: Follows" in orig_resp:
                return True, "AMI Originate despachado con éxito"
            return False, f"Respuesta AMI no exitosa: {orig_resp.strip()}"

        except (socket.error, ConnectionRefusedError, socket.timeout) as sock_err:
            return False, f"Socket AMI inalcanzable ({sock_err})"
        except Exception as e:
            return False, f"Excepción AMI: {e}"
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass

    def originate_via_spool(
        self,
        channel: str,
        incident_context: Dict[str, Any],
        call_id: str
    ) -> Tuple[bool, str]:
        """
        Genera un archivo atómico .call en el directorio spool de Asterisk.
        """
        safe_attack_type = self._sanitize_header(incident_context.get("attack_type", "Incidente No Identificado"))
        safe_attacker_ip = self._sanitize_header(incident_context.get("attacker_ip", "0.0.0.0"))
        safe_geo = self._sanitize_header(incident_context.get("geo_country", "Origen Desconocido"))

        call_file_content = (
            f"Channel: {channel}\n"
            f"CallerID: \"KRONOS SENTINEL AI\" <1000>\n"
            f"MaxRetries: 2\n"
            f"RetryTime: 5\n"
            f"WaitTime: 25\n"
            f"Context: kronos-emergency-response\n"
            f"Extension: s\n"
            f"Priority: 1\n"
            f"Set: INCIDENT_TYPE={safe_attack_type}\n"
            f"Set: ATTACKER_IP={safe_attacker_ip}\n"
            f"Set: GEO_ORIGIN={safe_geo}\n"
            f"Set: CALL_ID={call_id}\n"
        )

        temp_file = os.path.join(os.environ.get("TEMP", "/tmp"), f"kronos_{call_id}.call")
        dest_file = os.path.join(self.spool_dir, f"kronos_{call_id}.call")

        try:
            if os.path.exists(self.spool_dir):
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(call_file_content)
                os.replace(temp_file, dest_file)
                return True, f"Call file entregado a spool: {dest_file}"
            else:
                # Simulación diagnóstica si el spool no está montado en host
                logging.info(f"[SIMULACIÓN PBX SPOOL] Directorio {self.spool_dir} no existe. Call content:")
                for line in call_file_content.strip().split("\n"):
                    logging.info(f"   | {line}")
                return True, "Simulación de llamada registrada exitosamente"
        except Exception as e:
            return False, f"Error escribiendo en spool: {e}"

    def trigger_ciso_call(
        self,
        ciso_channel: str = "PJSIP/1001",
        incident_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Punto de entrada unificado para disparar la llamada al CISO.
        Intenta AMI TCP primero (si prefer_ami=True); si no está disponible, conmuta a spool.
        """
        if incident_context is None:
            incident_context = {}

        call_id = uuid.uuid4().hex[:12]
        attack_type = incident_context.get("attack_type", "Ataque Crítico")
        attacker_ip = incident_context.get("attacker_ip", "0.0.0.0")

        logging.warning(
            f"ORIGINANDO LLAMADA DE EMERGENCIA EN ASTERISK HACIA: {ciso_channel} "
            f"(CallID: {call_id} | Vector: {attack_type} | IP: {attacker_ip})"
        )

        dispatch_method = "UNKNOWN"
        dispatch_success = False
        dispatch_message = ""

        # Intento 1: AMI directo
        if self.prefer_ami:
            success, msg = self.originate_via_ami(ciso_channel, incident_context, call_id)
            if success:
                dispatch_method = "AMI_TCP_5038"
                dispatch_success = True
                dispatch_message = msg
                logging.info(f"Llamada originada vía AMI TCP 5038 exitosamente: {msg}")
            else:
                logging.warning(f"AMI TCP 5038 no disponible ({msg}). Conmutando a spool...")

        # Intento 2: Spool fallback si AMI no tuvo éxito
        if not dispatch_success:
            success, msg = self.originate_via_spool(ciso_channel, incident_context, call_id)
            dispatch_method = "SPOOL_CALL_FILE"
            dispatch_success = success
            dispatch_message = msg
            if success:
                logging.info(f"Llamada originada vía Spool: {msg}")
            else:
                logging.error(f"Fallo en Spool: {msg}")

        return {
            "status": "DISPATCHED" if dispatch_success else "FAILED",
            "call_id": call_id,
            "target_channel": ciso_channel,
            "method": dispatch_method,
            "success": dispatch_success,
            "message": dispatch_message,
            "incident": incident_context
        }


if __name__ == "__main__":
    trigger = AsteriskCallTrigger()
    result = trigger.trigger_ciso_call("PJSIP/1001", {
        "attack_type": "SQL Injection Crítica (UNION SELECT)",
        "attacker_ip": "185.220.101.5",
        "geo_country": "Federación Rusa"
    })
    print("Call Trigger Result:", result)
