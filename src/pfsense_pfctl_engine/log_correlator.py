#!/usr/bin/env python3
"""
KRONOS SENTINEL - FreeBSD pfctl & Suricata EVE Log Correlation Engine (Hardened)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import os
import json
import time
import yaml
import logging
import urllib.request
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional

from false_positive_filter import FalsePositiveFilter
from pfctl_wrapper import PfctlWrapper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [KRONOS-CORRELATOR] %(message)s'
)

class PfctlLogCorrelator:
    def __init__(self, config_path: str = "config.yaml"):
        # Buscar config en directorio actual o en ruta del script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resolved_config = os.path.join(base_dir, config_path)
        if os.path.exists(resolved_config):
            with open(resolved_config, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
            
        self.eve_log_path = self.config.get("suricata_eve_path", "/var/log/suricata/eve.json")
        self.filter = FalsePositiveFilter(self.config)
        self.pfctl = PfctlWrapper(self.config)
        
        # Cache LRU para deduplicación sin fugas de memoria (máximo 1000 eventos)
        self.processed_alerts = OrderedDict()
        self.max_cache_size = 1000
        
        # Pool de hilos para despachar alertas de voz sin bloquear la lectura de logs
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def _is_duplicate(self, event_id: str) -> bool:
        """Verifica y gestiona la deduplicación con política FIFO/LRU"""
        if event_id in self.processed_alerts:
            return True
        self.processed_alerts[event_id] = time.time()
        if len(self.processed_alerts) > self.max_cache_size:
            self.processed_alerts.popitem(last=False)
        return False

    def tail_eve_log(self):
        """Monitorea eve.json con soporte para rotación de archivos (newsyslog / logrotate)"""
        logging.info(f"Iniciando ingesta de telemetría desde: {self.eve_log_path}")
        
        while True:
            try:
                if not os.path.exists(self.eve_log_path):
                    logging.warning(f"Esperando creación de {self.eve_log_path}...")
                    time.sleep(2)
                    continue

                with open(self.eve_log_path, "r", encoding="utf-8") as f:
                    current_inode = os.stat(self.eve_log_path).st_ino
                    # Mover puntero al final del archivo existente
                    f.seek(0, 2)
                    logging.info(f"Descriptor de archivo abierto (Inodo: {current_inode}). Monitoreando...")

                    while True:
                        line = f.readline()
                        if line:
                            try:
                                event = json.loads(line.strip())
                                self.process_event(event)
                            except json.JSONDecodeError:
                                continue
                        else:
                            time.sleep(0.05)
                            # Comprobar si newsyslog rotó el archivo
                            try:
                                new_stat = os.stat(self.eve_log_path)
                                if new_stat.st_ino != current_inode:
                                    logging.info("Rotación de log detectada (newsyslog). Reabriendo archivo...")
                                    break
                            except FileNotFoundError:
                                break

            except Exception as e:
                logging.error(f"Error en bucle de lectura de logs: {e}")
                time.sleep(2)

    def process_event(self, event: Dict[str, Any]):
        """Procesa y correlaciona eventos de Suricata con el estado en kernel de pfctl"""
        if event.get("event_type") != "alert":
            return
            
        src_ip = event.get("src_ip", "")
        dest_ip = event.get("dest_ip", "")
        alert = event.get("alert", {})
        signature = alert.get("signature", "")
        severity = alert.get("severity", 3)
        http_data = event.get("http", {})
        
        # Manejo de proxy / X-Forwarded-For para evitar auto-bloqueo de pfSense o HAProxy
        if src_ip.startswith("192.168.100.1") or src_ip.startswith("127.0.0.1"):
            real_ip = http_data.get("xff", "") or http_data.get("request_headers", {}).get("X-Real-IP", "")
            if real_ip:
                src_ip = real_ip.split(",")[0].strip()

        event_id = f"{src_ip}_{signature}_{event.get('timestamp')}"
        if self._is_duplicate(event_id):
            return
        
        logging.info(f"Alerta detectada: [{signature}] de {src_ip} -> {dest_ip}")
        
        # 1. Filtro heurístico de falsos positivos
        analysis = self.filter.analyze(event)
        is_real_attack = analysis.get("is_real_attack", False)
        attack_type = analysis.get("attack_type", "UNKNOWN")
        confidence = analysis.get("confidence_score", 0.0)
        
        if not is_real_attack or confidence < self.config.get("confidence_threshold", 0.75):
            logging.info(f"-> [RUIDO SUPRIMIDO] Score: {confidence:.2f} | Tipo: {attack_type} - Sin escalamiento.")
            return
            
        logging.warning(f"-> [ATAQUE REAL CONFIRMADO] Tipo: {attack_type} | Confianza: {confidence:.2f}")
        
        # 2. Correlación atómica con kernel FreeBSD pfctl (tabla snort2c y kill states)
        is_blocked_in_pfctl = self.pfctl.is_ip_blocked(src_ip)
        
        if not is_blocked_in_pfctl:
            logging.warning(f"-> IP {src_ip} no aislada en snort2c. Ejecutando DROP perimetral y purga de estados...")
            self.pfctl.block_ip(src_ip)
            is_blocked_in_pfctl = True
            
        # 3. Construir payload del incidente para el Agente de Voz IA
        incident_payload = {
            "timestamp": event.get("timestamp"),
            "attacker_ip": src_ip,
            "target_ip": dest_ip,
            "attack_type": attack_type,
            "signature": signature,
            "severity": severity,
            "confidence_score": confidence,
            "http_endpoint": http_data.get("url", "/vulnerabilities/sqli/"),
            "http_method": http_data.get("http_method", "GET"),
            "pfctl_table": "snort2c",
            "pfctl_blocked": is_blocked_in_pfctl,
            "action_taken": "DROP & BLOCK en Firewall pfSense (Kernel pfctl State Kill)",
            "geo_country": self.filter.get_geoip(src_ip)
        }
        
        # 4. Despachar llamada asíncronamente en hilo secundario
        self.executor.submit(self.dispatch_voice_alert, incident_payload)
        
    def dispatch_voice_alert(self, incident: Dict[str, Any]):
        """Envía el incidente validado al webhook del despachador de voz Asterisk/Gemini"""
        logging.critical(f"DISPARANDO ALERTA DE EMERGENCIA AL CISO: {incident['attack_type']} ({incident['attacker_ip']})")
        webhook_url = self.config.get("dispatcher_webhook_url", "http://localhost:8080/incident")
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(incident).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                logging.info(f"Despachador de voz respondió HTTP {resp.status}")
        except Exception as e:
            logging.error(f"Error conectando con despachador de voz: {e}")

if __name__ == "__main__":
    correlator = PfctlLogCorrelator()
    print("=================================================================")
    print("      KRONOS HEURISTIC CORRELATION ENGINE ACTIVE (PYTHON 3.12)   ")
    print("  FreeBSD Kernel pfctl State Management & snort2c Integration    ")
    print("=================================================================")
    correlator.tail_eve_log()
