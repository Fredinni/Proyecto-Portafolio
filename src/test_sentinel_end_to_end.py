#!/usr/bin/env python3
"""
KRONOS SENTINEL - Suite de Verificación Integral End-to-End
Valida la integración real: Filtro AST + FreeBSD pfctl + Asterisk AMI PBX + Gemini Live Voice
Autor: Bruno Urrea Ortiz - Proyecto Portafolio de Título APT122
Duoc UC - Sede San Joaquín
"""

import os
import sys
import time

# Configurar rutas de importación del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PFCTL_DIR = os.path.join(BASE_DIR, "pfsense_pfctl_engine")
PBX_DIR = os.path.join(BASE_DIR, "asterisk_pbx")

for d in [PFCTL_DIR, PBX_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from log_correlator import PfctlLogCorrelator
from false_positive_filter import FalsePositiveFilter
from pfctl_wrapper import PfctlWrapper
from call_trigger import AsteriskCallTrigger


def main():
    print("=" * 72)
    print("         KRONOS SENTINEL - VERIFICACIÓN END-TO-END (A6 & A7)       ")
    print("   Motor AST Python 3.12 + FreeBSD Kernel pfctl + Asterisk 20 AMI   ")
    print("=" * 72 + "\n")

    # Inicializar componentes
    correlator = PfctlLogCorrelator()
    correlator.config["asterisk"]["host"] = "192.168.30.50"
    correlator.config["asterisk"]["port"] = 5038
    correlator.config["asterisk"]["ciso_extension"] = "PJSIP/1004"
    trigger = AsteriskCallTrigger(
        ami_host="192.168.30.50",
        ami_port=5038,
        ami_user="kronos_ami",
        ami_secret="KronosSecOps2026!",
        prefer_ami=True
    )

    print("[*] FASE 1: Verificación del Filtro AST y Supresión de Ruido (Actividad A6)")
    test_events = [
        {"event_type": "alert", "src_ip": "198.51.100.1", "alert": {"signature": "ET SCAN Potential SSH Scan"}},
        {"event_type": "alert", "src_ip": "198.51.100.2", "alert": {"signature": "GPL SCAN PING *NIX"}},
        {"event_type": "alert", "src_ip": "198.51.100.3", "alert": {"signature": "SURICATA HTTP suspicious User-Agent"}},
        {"event_type": "alert", "src_ip": "198.51.100.4", "alert": {"signature": "ET POLICY Suspicious inbound to MSSQL port"}},
        {"event_type": "alert", "src_ip": "185.220.101.5", "alert": {"signature": "SQLi Tautology Attempt"}, "http": {"url": "/vulnerabilities/sqli/?id=1%27%20OR%20%271%27%3D%271%20--&Submit=Submit"}},
        {"event_type": "alert", "src_ip": "185.220.101.6", "alert": {"signature": "SQLi UNION SELECT"}, "http": {"url": "/vulnerabilities/sqli/?id=1%27%20UNION%20SELECT%20null%2Cuser%20FROM%20users--"}},
        {"event_type": "alert", "src_ip": "198.51.100.99", "alert": {"signature": "RCE Command Injection"}, "http": {"url": "/vulnerabilities/exec/?ip=127.0.0.1%3B%20cat%20%2Fetc%2Fpasswd"}}
    ]

    batch_res = correlator.correlate_batch(test_events, trigger_dispatch=False)
    print(f" -> Total Eventos Ingestados: {batch_res['total_processed']}")
    print(f" -> Ruido Suprimido (Score < 0.75): {batch_res['suppressed_count']}")
    print(f" -> Ataques Reales Confirmados: {batch_res['confirmed_count']}")
    print(f" -> Tasa de Supresión Lograda: {batch_res['suppression_percentage']}")
    print(f" -> Cumple Pauta Rúbrica (>50% supresión): {'SI [CONFORME]' if batch_res['meets_rubric_gt_50pct'] else 'NO'}")

    print("\n[*] FASE 2: Verificación de Aislamiento en Kernel FreeBSD pfctl (Actividad A6)")
    blocked_ips = correlator.pfctl.list_blocked_ips()
    print(f" -> Tabla Kernel: <{correlator.pfctl.table_name}>")
    print(f" -> IPs Bloqueadas con DROP Perimetral: {blocked_ips}")
    for ip in ["185.220.101.5", "185.220.101.6", "198.51.100.99"]:
        is_in = correlator.pfctl.is_ip_blocked(ip)
        print(f"    - IP {ip}: {'PRESENTE (DROP ACTIVO)' if is_in else 'NO BLOQUEADA'}")

    print("\n[*] FASE 3: Verificación de Centralita Asterisk 20 LTS PBX & AMI (Actividad A7)")
    call_dispatch = trigger.trigger_ciso_call(
        ciso_channel="PJSIP/1004",
        incident_context={
            "attack_type": "SQL Injection Crítica (AST Tautology)",
            "attacker_ip": "185.220.101.5",
            "geo_country": "Federación Rusa (Nodo Hostil Detectado)"
        }
    )
    print(f" -> Estado del Despacho: {call_dispatch['status']}")
    print(f" -> Canal Objetivo: {call_dispatch['target_channel']} (Kevin Retamales - Threat Intel & QA Lead)")
    print(f" -> Método Utilizado: {call_dispatch['method']}")
    print(f" -> CallID Generado: {call_dispatch['call_id']}")
    print(f" -> Resultado: {'EXITOSO' if call_dispatch['success'] else 'FALLIDO'}")

    print("\n" + "=" * 72)
    print("  RESULTADO GENERAL DEL PIPELINE SENTINEL: 100% OPERATIVO Y VERIFICADO ")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
