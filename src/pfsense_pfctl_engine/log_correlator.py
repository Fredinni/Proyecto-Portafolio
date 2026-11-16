#!/usr/bin/env python3
"""
KRONOS SENTINEL - FreeBSD pfctl & Suricata EVE Log Correlation Engine (Python 3.12)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
Project: KRONOS SENTINEL - Autonomous AI-IPS & Live Voice Incident Response
"""

import json
import ipaddress
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Dict, Any, List, Optional

# Carga de YAML con fallback a parser ligero si PyYAML no está disponible
try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

# Asegurar importaciones locales
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from false_positive_filter import FalsePositiveFilter
from pfctl_wrapper import PfctlWrapper
from incident_identity import describe_network_identity

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [KRONOS-CORRELATOR] %(message)s'
)


class PfctlLogCorrelator:
    """
    Motor central de correlación SOAR.
    Ingesta telemetría EVE JSON de Suricata, discrimina falsos positivos con AST,
    aplica aislamiento en kernel FreeBSD via pfctl y despacha llamadas de voz al CISO.
    """

    def _load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        """Carga configuración con PyYAML o parser nativo mínimo"""
        if HAVE_YAML:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}

        # Fallback para entornos minimalistas sin paquete PyYAML
        data: Dict[str, Any] = {}
        current_section = None
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                raw = line.rstrip()
                stripped = raw.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if raw.startswith("  ") and current_section:
                    if ":" in stripped:
                        k, v = stripped.split(":", 1)
                        data[current_section][k.strip()] = self._parse_val(v.strip())
                elif ":" in stripped:
                    k, v = stripped.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if not v:
                        current_section = k
                        data[current_section] = {}
                    else:
                        current_section = None
                        data[k] = self._parse_val(v)
        return data

    @staticmethod
    def _parse_val(v: str) -> Any:
        # Remover comentarios en línea (p.ej. 'PJSIP/1001 # Comentario')
        if "#" in v and not (v.startswith('"') and v.endswith('"')) and not (v.startswith("'") and v.endswith("'")):
            v = v.split("#", 1)[0].strip()
        elif "#" in v:
            # Si está entrecomillado con comentario posterior
            for q in ['"', "'"]:
                if v.startswith(q) and q in v[1:]:
                    idx = v[1:].index(q) + 2
                    v = v[:idx].strip()
                    break

        if v.lower() == "true":
            return True
        if v.lower() == "false":
            return False
        if v.isdigit():
            return int(v)
        try:
            return float(v)
        except ValueError:
            pass
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            return v[1:-1]
        return v

    def __init__(self, config_path: str = "config.yaml"):
        # Cargar configuración YAML
        resolved_config = os.path.join(BASE_DIR, config_path)
        if os.path.exists(resolved_config):
            self.config = self._load_yaml_config(resolved_config)
        else:
            self.config = {}

        self.eve_log_path = self.config.get("suricata_eve_path", "/var/log/suricata/eve.json")
        self.confidence_threshold = self.config.get("confidence_threshold", 0.75)
        self.enable_auto_pfctl_drop = self.config.get("enable_auto_pfctl_drop", True)
        self.webhook_url = os.getenv("KRONOS_DISPATCH_URL", self.config.get("dispatcher_webhook_url", "http://localhost:8080/incident"))

        self.filter = FalsePositiveFilter(self.config)
        self.pfctl = PfctlWrapper(self.config)

        # Cache LRU para deduplicación atómica de eventos idénticos
        self.processed_alerts = OrderedDict()
        self.max_cache_size = 1000

        # Pool de hilos para despacho asíncrono sin bloquear ingesta
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _is_duplicate(self, event_id: str) -> bool:
        """Verifica y gestiona deduplicación con política FIFO/LRU"""
        if event_id in self.processed_alerts:
            return True
        self.processed_alerts[event_id] = time.time()
        if len(self.processed_alerts) > self.max_cache_size:
            self.processed_alerts.popitem(last=False)
        return False

    def process_single_event(
        self,
        event: Dict[str, Any],
        trigger_dispatch: bool = True
    ) -> Dict[str, Any]:
        """
        Procesa un único evento de alerta Suricata.
        Retorna el diagnóstico completo de la acción tomada.
        """
        if event.get("event_type") != "alert":
            return {
                "status": "SKIPPED",
                "reason": "event_type is not alert",
                "is_real_attack": False,
                "suppressed": True
            }

        src_ip = event.get("src_ip", "")
        dest_ip = event.get("dest_ip", "")
        alert = event.get("alert") or {}
        signature = alert.get("signature", "")
        severity = alert.get("severity", 3)
        http_data = event.get("http") or {}
        timestamp = event.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%S.000000Z")

        # Manejo de X-Forwarded-For en DMZ para identificar la IP real tras HAProxy
        if src_ip in self.config.get("trusted_proxy_ips", []):
            request_headers = http_data.get("request_headers", {})
            if not isinstance(request_headers, dict):
                request_headers = {}
            real_ip = (event.get("xff") or alert.get("xff") or http_data.get("xff") or
                       request_headers.get("X-Real-IP", ""))
            if isinstance(real_ip, str) and real_ip:
                src_ip = real_ip.split(",")[0].strip()

        try:
            src_ip = str(ipaddress.ip_address(src_ip))
        except ValueError:
            return {"status": "INVALID_SOURCE_IP", "suppressed": True, "is_real_attack": False}
        source_protected = src_ip in self.config.get("protected_ips", [])
        ips_dropped = alert.get("action") == "blocked" or (event.get("verdict") or {}).get("action") == "drop"
        if source_protected and not ips_dropped:
            return {"status": "PROTECTED_INFRASTRUCTURE_SOURCE", "src_ip": src_ip,
                    "suppressed": True, "is_real_attack": False}

        event_id = f"{src_ip}_{signature}_{timestamp}"
        if self._is_duplicate(event_id):
            return {
                "status": "DUPLICATE_SUPPRESSED",
                "event_id": event_id,
                "src_ip": src_ip,
                "is_real_attack": False,
                "suppressed": True
            }

        logging.info(f"Analizando evento Suricata: [{signature}] de {src_ip} -> {dest_ip}")

        # 1. Filtro heurístico y analizador sintáctico AST
        analysis = self.filter.analyze(event)
        is_real_attack = analysis.get("is_real_attack", False)
        attack_type = analysis.get("attack_type", "UNKNOWN")
        confidence = analysis.get("confidence_score", 0.0)
        classification_source = "HEURISTIC"
        if ips_dropped and not is_real_attack:
            # An IPS-enforced drop is important evidence even if EVE has no
            # HTTP body for the optional AST analysis. Do not invent a payload
            # or a numerical confidence score the sensor did not provide.
            is_real_attack = True
            attack_type = "IPS_BLOCK: " + (alert.get("category") or signature or "Tipo no informado")
            classification_source = "IPS_DROP"

        # Si el score no supera el umbral, se suprime como ruido de escaneo
        if not ips_dropped and (not is_real_attack or confidence < self.confidence_threshold):
            logging.info(
                f"-> [RUIDO SUPRIMIDO] Score: {confidence:.2f} | Tipo: {attack_type} - Sin escalamiento."
            )
            return {
                "status": "SUPPRESSED",
                "event_id": event_id,
                "src_ip": src_ip,
                "attack_type": attack_type,
                "confidence": confidence,
                "is_real_attack": False,
                "suppressed": True,
                "pfctl_action": "NONE",
                "dispatch_triggered": False,
                "analysis": analysis
            }

        logging.warning(f"-> [ATAQUE REAL CONFIRMADO] Tipo: {attack_type} | Confianza: {confidence:.2f}")

        # 2. Correlación atómica con kernel FreeBSD pfctl (tabla snort2c y kill states)
        try:
            is_blocked_in_pfctl = self.pfctl.is_ip_blocked(src_ip)
        except (RuntimeError, OSError):
            # An unavailable firewall query must not silence a sensor alert.
            logging.exception("No se pudo consultar pfctl; se notificara el estado desconocido")
            is_blocked_in_pfctl = None
        action_taken = ("IP YA SE ENCUENTRA BLOQUEADA EN KERNEL" if is_blocked_in_pfctl else
                        "ESTADO DE BLOQUEO DESCONOCIDO" if is_blocked_in_pfctl is None else
                        "SIN BLOQUEO CONFIRMADO")

        if source_protected:
            action_taken = "IPS DESCARTO EL ATAQUE; ORIGEN PROTEGIDO, SIN CAMBIOS AUTOMATICOS EN LA TABLA"
            logging.warning("Alerta IPS desde infraestructura protegida %s; solo notificacion", src_ip)
        elif is_blocked_in_pfctl is False and self.enable_auto_pfctl_drop:
            logging.warning(
                f"-> IP hostil {src_ip} no aislada en {self.pfctl.table_name}. "
                f"Ejecutando DROP perimetral y purga de estados..."
            )
            try:
                block_success = self.pfctl.block_ip(src_ip)
            except (RuntimeError, OSError):
                logging.exception("Fallo al bloquear; el incidente se notificara igualmente")
                block_success = None
            is_blocked_in_pfctl = block_success
            action_taken = ("DROP & BLOCK en Firewall pfSense (Kernel pfctl State Kill)" if block_success else
                            "ESTADO DE BLOQUEO DESCONOCIDO" if block_success is None else "FALLO AL BLOQUEAR")

        # 3. Construcción del payload estructurado del incidente
        incident_payload = {
            "timestamp": timestamp,
            "attacker_ip": src_ip,
            "target_ip": dest_ip,
            "attack_type": attack_type,
            "signature": signature,
            "severity": severity,
            "confidence_score": confidence if classification_source == "HEURISTIC" else None,
            "classification_source": classification_source,
            "sensor_action": alert.get("action"),
            "sensor_dropped": ips_dropped,
            "source_protected": source_protected,
            "observed_source_ip": event.get("src_ip"),
            "source_identity": ("UNRESOLVED_PROXY" if source_protected and
                                src_ip in self.config.get("trusted_proxy_ips", []) else
                                "PROTECTED_INFRASTRUCTURE" if source_protected else "ACTOR_IP"),
            "signature_id": alert.get("signature_id"),
            "category": alert.get("category"),
            "http_endpoint": http_data.get("url"),
            "target_service": f"{dest_ip}:{event.get('dest_port', 'puerto no informado')}",
            "protocol": event.get("proto"),
            "http_method": http_data.get("http_method"),
            "ast_verified": analysis.get("ast_verified", False),
            "tautologies": analysis.get("tautologies", []),
            "pfctl_table": self.pfctl.table_name,
            "pfctl_blocked": is_blocked_in_pfctl,
            "action_taken": action_taken,
            "geoip": self.filter.geoip.lookup(src_ip),
            "geo_country": self.filter.get_geoip(src_ip)
        }
        incident_payload.update(describe_network_identity(incident_payload))

        # 4. Despacho asíncrono al agente de voz Asterisk / Gemini Live
        if trigger_dispatch:
            self.executor.submit(self.dispatch_voice_alert, incident_payload)

        return {
            "status": ("CONFIRMED_AND_MITIGATED" if is_blocked_in_pfctl else
                       "CONFIRMED_BLOCK_STATUS_UNKNOWN" if is_blocked_in_pfctl is None else
                       "CONFIRMED_NOT_MITIGATED"),
            "event_id": event_id,
            "src_ip": src_ip,
            "dest_ip": dest_ip,
            "attack_type": attack_type,
            "confidence": confidence,
            "is_real_attack": True,
            "suppressed": False,
            "pfctl_action": action_taken,
            "pfctl_blocked": is_blocked_in_pfctl,
            "dispatch_triggered": trigger_dispatch,
            "incident": incident_payload
        }

    def process_event(self, event: Dict[str, Any]):
        """Punto de entrada compatible con streaming de logs"""
        self.process_single_event(event, trigger_dispatch=True)

    def correlate_batch(
        self,
        events: List[Dict[str, Any]],
        trigger_dispatch: bool = False
    ) -> Dict[str, Any]:
        """Procesa una colección de eventos en lote para pruebas unitarias y auditoría"""
        results = []
        suppressed_count = 0
        confirmed_count = 0

        for event in events:
            res = self.process_single_event(event, trigger_dispatch=trigger_dispatch)
            results.append(res)
            if res.get("suppressed"):
                suppressed_count += 1
            elif res.get("is_real_attack"):
                confirmed_count += 1

        total = len(events)
        rate = (suppressed_count / total) if total > 0 else 0.0

        return {
            "total_processed": total,
            "suppressed_count": suppressed_count,
            "confirmed_count": confirmed_count,
            "suppression_rate": round(rate, 4),
            "suppression_percentage": f"{rate * 100:.2f}%",
            "meets_rubric_gt_50pct": rate > 0.50,
            "results": results
        }

    def dispatch_voice_alert(self, incident: Dict[str, Any]):
        """Envía el incidente validado al webhook del despachador de voz Asterisk/Gemini"""
        logging.critical(
            f"DISPARANDO ALERTA DE EMERGENCIA AL CISO: "
            f"{incident['attack_type']} ({incident['attacker_ip']})"
        )
        for attempt in range(3):
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(incident).encode('utf-8'),
                headers={'Content-Type': 'application/json',
                         'Authorization': 'Bearer ' + os.getenv('KRONOS_DISPATCH_TOKEN', '')}
            )
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    result = json.loads(resp.read(16000))
                    if not isinstance(result, dict):
                        raise ValueError("Dispatcher response must be an object")
                    logging.info("Despachador HTTP %s: estado=%s llamada_iniciada=%s",
                                 resp.status, result.get("status"), result.get("call_initiated"))
                return True
            except urllib.error.HTTPError as error:
                logging.warning("Despacho HTTP %s (intento %s/3)", error.code, attempt + 1)
                error.close()
                if error.code < 500:
                    break
            except (urllib.error.URLError, OSError, ValueError):
                logging.exception("Despacho no confirmado (intento %s/3)", attempt + 1)
            if attempt < 2:
                time.sleep(2 ** attempt)
        logging.error("Notificacion de voz no confirmada para %s; bloqueo pfctl=%s",
                      incident['attacker_ip'], incident.get('pfctl_blocked'))
        return False

    def _follow_eve_lines(self, stop_event: Optional[Event] = None):
        """Follow complete records; drain rotated files and read replacements from byte zero."""
        stop_event = stop_event or Event()
        first_open = True
        while not stop_event.is_set():
            try:
                with open(self.eve_log_path, "rb") as stream:
                    inode = os.fstat(stream.fileno()).st_ino
                    if first_open:
                        stream.seek(0, os.SEEK_END)
                        first_open = False
                    while not stop_event.is_set():
                        position = stream.tell()
                        if os.fstat(stream.fileno()).st_size < position:
                            logging.info("EVE truncado; reiniciando lectura")
                            stream.seek(0)
                            position = 0
                        line = stream.readline()
                        if line.endswith(b"\n"):
                            yield line
                            continue
                        # Suricata can append a JSON record in several writes.
                        # Re-read its prefix once the terminating newline arrives.
                        stream.seek(position)
                        try:
                            if os.stat(self.eve_log_path).st_ino != inode:
                                logging.info("EVE rotado; leyendo reemplazo desde el inicio")
                                break
                        except FileNotFoundError:
                            # Keep draining this descriptor until its replacement exists.
                            pass
                        stop_event.wait(0.05)
            except OSError:
                logging.exception("EVE no disponible: %s", self.eve_log_path)
                stop_event.wait(2)

    def tail_eve_log(self, stop_event: Optional[Event] = None):
        """Monitorea EVE sin perder los eventos posteriores a una línea defectuosa."""
        logging.info(f"Iniciando ingesta de telemetría desde: {self.eve_log_path}")
        for line in self._follow_eve_lines(stop_event):
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError("EVE record must be an object")
                self.process_event(event)
            except Exception:
                logging.exception("Error en evento EVE; continuando con el siguiente registro")


if __name__ == "__main__":
    print("=================================================================")
    print("      KRONOS HEURISTIC CORRELATION ENGINE ACTIVE (PYTHON 3.12)   ")
    print("  FreeBSD Kernel pfctl State Management & snort2c Integration    ")
    print("=================================================================")
    correlator = PfctlLogCorrelator()
    correlator.tail_eve_log()
