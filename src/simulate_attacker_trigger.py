#!/usr/bin/env python3
"""
KRONOS SENTINEL - Simulador de Vector de Ataque y Trigger SOAR
Autor: Bruno Urrea Ortiz - Proyecto Portafolio de Título APT122
Duoc UC - Sede San Joaquín
"""

import json
import logging
import os
import sys
import time
import urllib.request

# Ajustar rutas de módulos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "pfsense_pfctl_engine"))
PBX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "asterisk_pbx"))
for d in [BASE_DIR, PBX_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from log_correlator import PfctlLogCorrelator
from call_trigger import AsteriskCallTrigger

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [KRONOS-ATTACKER] %(message)s')


def launch_attack_and_trigger_pipeline(attacker_ip: str = "185.220.101.5", target_host: str = "192.168.20.50"):
    print("=" * 72)
    print("           KRONOS SENTINEL - DISPARO DE ATAQUE Y LLAMADA SOAR           ")
    print("=" * 72)

    # 1. Petición HTTP L7 real hacia DVWA
    attack_url = f"http://{target_host}/vulnerabilities/sqli/?id=1%27%20OR%20%271%27%3D%271%20--&Submit=Submit"
    print(f"\n[*] PASO 1: Enviando inyeccion SQL maliciosa hacia DVWA ({attack_url})...")
    try:
        req = urllib.request.Request(attack_url, headers={
            "User-Agent": "Mozilla/5.0 (KRONOS RedTeam Pentest Framework)",
            "X-Forwarded-For": attacker_ip
        })
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f" -> Respuesta DVWA: HTTP {resp.status} (Payload entregado)")
    except Exception as e:
        print(f" -> Aviso entrega HTTP: {e} (Simulacion continuara con telemetria)")

    # 2. Correlación y análisis AST con el motor KRONOS
    print(f"\n[*] PASO 2: Ingesta en Motor de Correlacion KRONOS y Analisis AST...")
    correlator = PfctlLogCorrelator()
    # Conectar al Asterisk PBX en VM103
    correlator.config["asterisk"]["host"] = "192.168.30.50"
    correlator.config["asterisk"]["port"] = 5038

    event = {
        "event_type": "alert",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
        "src_ip": attacker_ip,
        "dest_ip": target_host,
        "alert": {
            "signature": "SURICATA HTTP SQL Injection Attempt (AST Validated)",
            "severity": 1
        },
        "http": {
            "url": "/vulnerabilities/sqli/?id=1%27%20OR%20%271%27%3D%271%20--&Submit=Submit",
            "http_method": "GET"
        }
    }

    diag = correlator.process_single_event(event, trigger_dispatch=False)
    print(f" -> Estado de Deteccion: {diag['status']}")
    print(f" -> Tipo de Ataque: {diag['attack_type']}")
    print(f" -> Confianza: {diag['confidence']:.2f}")
    print(f" -> Verificado por AST: {diag['incident']['ast_verified']}")
    print(f" -> Tautologias extraidas: {diag['incident']['tautologies']}")
    print(f" -> Accion en Kernel pfctl: {diag['pfctl_action']}")

    # 3. Disparar llamada prioritaria AMI a Asterisk VM103 hacia PJSIP/1001
    print(f"\n[*] PASO 3: Disparando llamada de emergencia AMI hacia Zoiper (PJSIP/1001)...")
    trigger = AsteriskCallTrigger(
        ami_host="192.168.30.50",
        ami_port=5038,
        ami_user="kronos_ami",
        ami_secret="KronosSecOps2026!",
        prefer_ami=True
    )

    call_result = trigger.trigger_ciso_call(
        ciso_channel="PJSIP/1001",
        incident_context=diag["incident"]
    )

    print(f" -> Estado de llamada: {call_result['status']}")
    print(f" -> Metodo: {call_result['method']}")
    print(f" -> CallID: {call_result['call_id']}")
    print(f" -> Destino: {call_result['target_channel']} (Bruno Urrea - CISO)")
    print(f" -> Resultado: {'EXITOSO - LLAMADA GENERADA' if call_result['success'] else 'FALLIDO'}")

    print("\n" + "=" * 72)
    print("  PIPELINE COMPLETADO: VERIFICA EL TIMBRADO EN ZOIPER DE TU IPHONE  ")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    launch_attack_and_trigger_pipeline()
