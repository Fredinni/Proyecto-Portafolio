#!/usr/bin/env python3
"""
KRONOS SENTINEL - Simulador de Vector de Ataque y Trigger SOAR con Memoria Obsidian
Autor: Bruno Urrea Ortiz - Proyecto Portafolio de Título APT122
Duoc UC - Sede San Joaquín
"""

import os
import sys
import time
import json
import base64
import subprocess
import urllib.request
import urllib.error
import logging
import paramiko

# Ajustar rutas de módulos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "pfsense_pfctl_engine"))
PBX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "asterisk_pbx"))
for d in [BASE_DIR, PBX_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from log_correlator import PfctlLogCorrelator
from call_trigger import AsteriskCallTrigger
from obsidian_memory_manager import ObsidianMemoryManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [KRONOS-ATTACKER] %(message)s')

def get_gemini_key():
    for env_path in [r"C:\Users\bruno\.env", os.path.expanduser("~/.env"), os.path.join(os.path.dirname(__file__), "..", ".env")]:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip().strip("'\"")
    return os.getenv("GEMINI_API_KEY", "")

def pregenerate_live_gemini_speech(attacker_ip: str, incident_type: str, recurrence_count: int = 1,
                                   vm103_ip: str = "192.168.30.50", target_service: str = "DVWA en DMZ",
                                   tautologies: list = None):
    """
    Genera en vivo la alerta de inicio con Gemini 3.8 Live (Voz: Aoede),
    incorporando la correlación de reincidencia de Obsidian y telemetría de pfSense.
    """
    api_key = get_gemini_key()
    if not api_key:
        print(" [!] No se encontró GEMINI_API_KEY.")
        return

    print(f" -> Correlación de Memoria Obsidian: IP {attacker_ip} | Reincidencia: x{recurrence_count}")

    if recurrence_count >= 2:
        prompt_instruction = (
            f"Saluda con '¡Aló Bruno! Oye, este compadre de la {attacker_ip} ya van {recurrence_count} veces que nos tira {incident_type}, revísalo. "
            "El pfSense ya le chantó DROP en snort2c y mató los estados. ¿Lo dejamos bloqueado nomás?'"
        )
    else:
        prompt_instruction = (
            f"Saluda con '¿Aló, Bruno? Oye...' y dile que frenaste un {incident_type} desde la IP {attacker_ip} hacia {target_service}. "
            "El pfSense ya le chantó DROP en snort2c y mató los estados. Pregúntale si lo dejamos bloqueado nomás."
        )

    sys_prompt = (
        "Eres la operadora de IA del sistema de ciberseguridad KRONOS SENTINEL. "
        "Estás en una llamada telefónica en vivo con Bruno Urrea (CISO). "
        "HABLA DE TÚ A TÚ, SÚPER INFORMAL, MUY CASUAL CHILENA, COMO UNA COLEGA CAPA Y RELAJADA. "
        "Cero formalismos corporativos. Sé súper breve, directa y al grano. "
        f"{prompt_instruction} "
        "Máximo 18 palabras. Devuelve SOLO el diálogo a pronunciar en una línea sin comillas ni markdown."
    )

    LLM_MODELS = [
        "gemini-3-flash-preview",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]

    TTS_MODELS = [
        "gemini-3.8-flash-tts",
        "gemini-3.8-flash-lite-tts",
        "gemini-3.1-flash-tts-preview"
    ]

    spoken_alert = ""
    for m in LLM_MODELS:
        url_llm = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        body_llm = {
            "systemInstruction": {"parts": [{"text": sys_prompt}]},
            "contents": [{"parts": [{"text": "Genera el diálogo de alerta telefónica para Bruno."}]}]
        }
        req = urllib.request.Request(url_llm, data=json.dumps(body_llm).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                spoken_alert = data['candidates'][0]['content']['parts'][0]['text'].strip()
                if spoken_alert:
                    print(f" -> Diálogo generado con {m}: \"{spoken_alert}\"")
                    break
        except Exception as e:
            print(f" -> Aviso LLM con {m}: {e}. Intentando siguiente modelo...")
            continue

    if not spoken_alert:
        if recurrence_count >= 2:
            spoken_alert = f"¡Aló Bruno! Oye, este compadre de la {attacker_ip} ya van {recurrence_count} veces que nos tira {incident_type}, revísalo. El pfSense ya le chantó DROP en snort2c y mató los estados. ¿Lo dejamos bloqueado nomás?"
        else:
            spoken_alert = f"¿Aló, Bruno? Oye, frené un {incident_type} desde la IP {attacker_ip} hacia {target_service}. El pfSense ya le chantó DROP en snort2c y mató los estados. ¿Lo dejamos bloqueado nomás?"

    print(f" -> Sintetizando alerta con Gemini 3.8 Live TTS (Aoede)...")
    raw_pcm_alert = None
    for model in TTS_MODELS:
        url_tts = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        body = {
            "contents": [{"parts": [{"text": spoken_alert}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": "Aoede"
                        }
                    }
                }
            }
        }
        req = urllib.request.Request(url_tts, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                raw_pcm_alert = base64.b64decode(data['candidates'][0]['content']['parts'][0]['inlineData']['data'])
                print(f" -> Síntesis OK con {model} ({len(raw_pcm_alert)} bytes PCM)")
                break
        except Exception as e:
            print(f" -> Aviso TTS con {model}: {e}. Probando siguiente modelo...")
            continue

    if not raw_pcm_alert:
        print(" [!] No se pudo sintetizar audio con Gemini TTS.")
        return

    # Subir audio y contexto estructurado a Asterisk PBX VM103
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(vm103_ip, username='kronos', password='3IDQInZoYuSPns4K-YhAIkTRl0ESa0Dt', timeout=10)

        # Contexto JSON para el script EAGI
        incident_context = {
            "attacker_ip": attacker_ip,
            "attack_type": incident_type,
            "target_service": target_service,
            "recurrence_count": recurrence_count,
            "tautologies": tautologies or [],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        sftp = c.open_sftp()
        with sftp.file('/tmp/gemini_live_alert.raw', 'wb') as f:
            f.write(raw_pcm_alert)
        with sftp.file('/tmp/incident_context.json', 'w') as f:
            f.write(json.dumps(incident_context, indent=2))
        sftp.close()

        def run_sudo(cmd_str):
            stdin, stdout, _ = c.exec_command(f"sudo -S -p '' {cmd_str}")
            stdin.write("3IDQInZoYuSPns4K-YhAIkTRl0ESa0Dt\n")
            stdin.flush()
            stdin.channel.shutdown_write()
            return stdout.read().decode('utf-8', errors='replace').strip()

        # Copiar al contenedor Asterisk
        run_sudo("docker cp /tmp/gemini_live_alert.raw kronos_asterisk_pbx:/tmp/gemini_live_alert.raw")
        run_sudo("docker cp /tmp/incident_context.json kronos_asterisk_pbx:/tmp/incident_context.json")
        run_sudo("docker exec kronos_asterisk_pbx chmod 666 /tmp/incident_context.json")

        # Convertir con sox a 8kHz WAV y ULAW
        run_sudo("docker exec kronos_asterisk_pbx sox -t raw -r 24000 -c 1 -b 16 -e signed-integer /tmp/gemini_live_alert.raw -r 8000 -c 1 /tmp/gemini_alert_current.wav")
        run_sudo("docker exec kronos_asterisk_pbx sox /tmp/gemini_alert_current.wav -t ul /tmp/gemini_alert_current.ulaw")
        run_sudo("docker exec kronos_asterisk_pbx chown asterisk:asterisk /tmp/gemini_alert_current.*")

        c.close()
        print(" -> Alerta Gemini 3.8 Live y Contexto Obsidian desplegados en Asterisk PBX!")
    except Exception as e:
        print(f" [!] Error subiendo audio a Asterisk: {e}")

def launch_attack_and_trigger_pipeline(attacker_ip: str = "185.220.101.5", target_host: str = "192.168.20.50"):
    print("=" * 72)
    print("           KRONOS SENTINEL - DISPARO DE ATAQUE Y LLAMADA SOAR           ")
    print("=" * 72)

    # 1. Petición HTTP L7 hacia DVWA
    attack_url = f"http://{target_host}/vulnerabilities/sqli/?id=1%27%20OR%20%271%27%3D%271%20--&Submit=Submit"
    print(f"\n[*] PASO 1: Enviando vector HTTP SQL Injection hacia DVWA ({attack_url})...")
    try:
        req = urllib.request.Request(attack_url, headers={
            "User-Agent": "Mozilla/5.0 (KRONOS RedTeam Pentest Framework)",
            "X-Forwarded-For": attacker_ip
        })
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f" -> Respuesta DVWA: HTTP {resp.status} (Inyección recibida en servidor)")
    except Exception as e:
        print(f" -> Entrega HTTP: {e} (Continuando con correlación)")

    # 2. Correlación y análisis AST con el motor KRONOS
    print(f"\n[*] PASO 2: Ingesta en Motor de Correlación KRONOS y Análisis AST...")
    correlator = PfctlLogCorrelator()
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
    print(f" -> Estado de Detección: {diag['status']}")
    print(f" -> Tipo de Ataque: {diag['attack_type']}")
    print(f" -> Confianza: {diag['confidence']:.2f}")
    print(f" -> Verificado por AST: {diag['incident']['ast_verified']}")
    print(f" -> Tautologías extraídas: {diag['incident']['tautologies']}")
    print(f" -> Acción en Kernel pfctl: {diag['pfctl_action']}")

    # 2.1. Memoria de Incidentes y Vault Obsidian
    print(f"\n[*] PASO 2.1: Actualizando Memoria Persistente y Vault Obsidian...")
    obsidian_mgr = ObsidianMemoryManager()
    recurrence_count, mem_rec = obsidian_mgr.record_incident(
        attacker_ip=attacker_ip,
        attack_type=diag["attack_type"],
        target_service="DVWA en DMZ",
        tautologies=diag["incident"]["tautologies"],
        action_taken=diag["pfctl_action"]
    )
    print(f" -> Reincidencia registrada en Obsidian: x{recurrence_count}")

    # 2.5. Síntesis en tiempo real con Gemini Live (Voz femenina Aoede)
    print(f"\n[*] PASO 2.5: Generando síntesis en vivo con Gemini 3.8 Live (Aoede)...")
    pregenerate_live_gemini_speech(
        attacker_ip=attacker_ip,
        incident_type=diag["attack_type"],
        recurrence_count=recurrence_count,
        vm103_ip="192.168.30.50",
        target_service="DVWA en DMZ",
        tautologies=diag["incident"]["tautologies"]
    )

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
    print(f" -> Método: {call_result['method']}")
    print(f" -> CallID: {call_result['call_id']}")
    print(f" -> Destino: {call_result['target_channel']} (Bruno Urrea - CISO)")
    print(f" -> Resultado: {'EXITOSO - TIMBRANDO EN IPHONE ZOIPER' if call_result['success'] else 'FALLIDO'}")

    print("\n" + "=" * 72)
    print("  PIPELINE COMPLETADO: VERIFICA EL TIMBRADO EN ZOIPER DE TU IPHONE  ")
    print("=" * 72 + "\n")

if __name__ == "__main__":
    launch_attack_and_trigger_pipeline()