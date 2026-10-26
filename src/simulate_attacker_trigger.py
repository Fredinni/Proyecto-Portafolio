#!/usr/bin/env python3
"""
KRONOS SENTINEL - Simulador de Vector de Ataque y Trigger SOAR
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [KRONOS-ATTACKER] %(message)s')

def get_gemini_key():
    for env_path in [r"C:\Users\bruno\.env", os.path.expanduser("~/.env"), os.path.join(os.path.dirname(__file__), "..", ".env")]:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip().strip("'\"")
    return os.getenv("GEMINI_API_KEY", "")

def pregenerate_live_gemini_speech(attacker_ip: str, incident_type: str, vm103_ip: str = "192.168.30.50", target_service: str = "DVWA en DMZ", geo_origin: str = "Nodo Hostil"):
    """Genera en vivo el debriefing y cierre con Gemini 3.5 Flash y voz femenina Aoede, subiéndolo a Asterisk"""
    api_key = get_gemini_key()
    if not api_key:
        print(" [!] No se encontro GEMINI_API_KEY. Se utilizara sintesis de respaldo.")
        return

    print(" -> Consultando Gemini 3.5 Flash (Generacion de dialogo informal en vivo con variables reales)...")
    sys_prompt = (
        "Eres la operadora de IA del sistema de ciberseguridad KRONOS SENTINEL. "
        "Estás en una llamada telefónica en vivo con Bruno Urrea (CISO). "
        "HABLA DE TÚ A TÚ, SÚPER INFORMAL, MUY CASUAL, COMO UNA COLEGA CAPA Y RELAJADA. "
        "Cero formalismos corporativos. "
        "FLUJO DE TELEFONÍA CHILENA: Empieza siempre saludando como se hace en Chile: '¿Aló, Bruno? Oye...'. "
        "Genera dos respuestas en formato JSON con las claves 'alert' y 'closing': "
        f"1. 'alert': Saluda con '¿Aló, Bruno? Oye...' y explícale que acabas de mitigar una intrusión de {incident_type} hacia {target_service} desde la IP {attacker_ip} ({geo_origin}), "
        "y que el pfSense ya le chantó un DROP en la tabla snort2c y mató todos los estados activos en el kernel. "
        "Pregúntale qué hacemos: si revisamos el tráfico o si lo dejamos bloqueado nomás. (Máximo 28 palabras). "
        f"2. 'closing': Despídete de Bruno con buena onda diciéndole que la IP {attacker_ip} ya quedó blindada en el pfSense y que ante cualquier cosa rara le timbras al tiro. (Máximo 16 palabras). "
        "Devuelve SOLO el JSON válido."
    )

    LLM_MODELS = [
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash"
    ]

    TTS_MODELS = [
        "gemini-3.1-flash-tts-preview",
        "gemini-3.8-flash-lite-tts",
        "gemini-3.8-flash-tts",
        "gemini-2.5-flash-preview-tts"
    ]

    def ask_gemini_json(prompt, sys_inst):
        for m in LLM_MODELS:
            url_llm = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            body_llm = {
                "systemInstruction": {"parts": [{"text": sys_inst}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            req = urllib.request.Request(url_llm, data=json.dumps(body_llm).encode(), headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode())
                    raw_json = data['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(raw_json)
            except Exception as e:
                print(f" -> Aviso LLM con {m}: {e}. Probando siguiente modelo...")
                continue
        return None

    def ask_gemini_tts(text_to_speak):
        for model in TTS_MODELS:
            url_tts = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            body = {
                "contents": [{"parts": [{"text": text_to_speak}]}],
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
                    pcm = base64.b64decode(data['candidates'][0]['content']['parts'][0]['inlineData']['data'])
                    print(f" -> Sintesis OK con {model} ({len(pcm)} bytes)")
                    return pcm
            except Exception as e:
                print(f" -> Aviso TTS con {model}: {e}. Intentando modelo alternativo...")
                continue
        raise RuntimeError("Todos los modelos TTS de Gemini fallaron.")

    try:
        parsed_dialogue = ask_gemini_json("Genera el diálogo de alerta y despedida para Bruno en JSON.", sys_prompt) or {}
        spoken_alert = parsed_dialogue.get("alert", f"¡Bruno! Oye, te cuento que mitigamos una inyección SQL hacia DVWA desde la IP {attacker_ip}. El pfSense ya le chantó un DROP en snort2c y mató los estados. ¿Qué hacemos, revisamos el tráfico o lo dejamos bloqueado?")
        spoken_closing = parsed_dialogue.get("closing", "¡Listo Bruno! Ya quedó todo blindado en el pfSense. Cualquier cosa rara te timbro al tiro, nos vemos.")

        print(f" -> Alerta IA Generada: \"{spoken_alert}\"")
        print(f" -> Cierre IA Generado: \"{spoken_closing}\"")

        print(" -> Sintetizando audio en vivo con Gemini TTS (Voz femenina Aoede)...")
        raw_pcm_alert = ask_gemini_tts(spoken_alert)
        time.sleep(1)
        raw_pcm_closing = ask_gemini_tts(spoken_closing)

        # Subir los PCM crudos a VM103 y convertir con sox en el contenedor a 8kHz
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(vm103_ip, username='kronos', password='3IDQInZoYuSPns4K-YhAIkTRl0ESa0Dt', timeout=10)

        sftp = c.open_sftp()
        with sftp.file('/tmp/gemini_live_alert.raw', 'wb') as f:
            f.write(raw_pcm_alert)
        with sftp.file('/tmp/gemini_live_closing.raw', 'wb') as f:
            f.write(raw_pcm_closing)
        sftp.close()

        def run_sudo(cmd_str):
            stdin, stdout, _ = c.exec_command(f"sudo -S -p '' {cmd_str}")
            stdin.write("3IDQInZoYuSPns4K-YhAIkTRl0ESa0Dt\n")
            stdin.flush()
            stdin.channel.shutdown_write()
            return stdout.read().decode('utf-8', errors='replace').strip()

        # Copiar y convertir en contenedor
        run_sudo("docker cp /tmp/gemini_live_alert.raw kronos_asterisk_pbx:/tmp/gemini_live_alert.raw")
        run_sudo("docker cp /tmp/gemini_live_closing.raw kronos_asterisk_pbx:/tmp/gemini_live_closing.raw")

        run_sudo("docker exec kronos_asterisk_pbx sox -t raw -r 24000 -c 1 -b 16 -e signed-integer /tmp/gemini_live_alert.raw -r 8000 -c 1 /tmp/gemini_alert_current.wav")
        run_sudo("docker exec kronos_asterisk_pbx sox /tmp/gemini_alert_current.wav -t ul /tmp/gemini_alert_current.ulaw")

        run_sudo("docker exec kronos_asterisk_pbx sox -t raw -r 24000 -c 1 -b 16 -e signed-integer /tmp/gemini_live_closing.raw -r 8000 -c 1 /tmp/gemini_close_current.wav")
        run_sudo("docker exec kronos_asterisk_pbx sox /tmp/gemini_close_current.wav -t ul /tmp/gemini_close_current.ulaw")

        # Asegurar permisos y crear copia en sonidos permanentes
        run_sudo("docker exec kronos_asterisk_pbx chown asterisk:asterisk /tmp/gemini_*")
        run_sudo("docker exec kronos_asterisk_pbx cp /tmp/gemini_close_current.wav /usr/share/asterisk/sounds/custom/kronos_farewell.wav")
        run_sudo("docker exec kronos_asterisk_pbx cp /tmp/gemini_close_current.ulaw /usr/share/asterisk/sounds/custom/kronos_farewell.ulaw")
        run_sudo("docker exec kronos_asterisk_pbx chown asterisk:asterisk /usr/share/asterisk/sounds/custom/kronos_farewell.*")

        c.close()
        print(" -> Audios Gemini Live desplegados en Asterisk PBX (/tmp/gemini_alert_current & /tmp/gemini_close_current)!")
    except Exception as e:
        print(f" [!] Aviso en generacion Gemini: {e}. Se utilizara sintesis local.")

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

    # 2.5. Síntesis en tiempo real con Gemini Live (Voz femenina Aoede)
    print(f"\n[*] PASO 2.5: Generando síntesis interactiva de voz con Gemini Live (Voz: Aoede)...")
    pregenerate_live_gemini_speech(
        attacker_ip=attacker_ip,
        incident_type=diag["attack_type"],
        vm103_ip="192.168.30.50",
        target_service="DVWA en DMZ",
        geo_origin="Nodo Hostil Externo"
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
    print(f" -> Metodo: {call_result['method']}")
    print(f" -> CallID: {call_result['call_id']}")
    print(f" -> Destino: {call_result['target_channel']} (Bruno Urrea - CISO)")
    print(f" -> Resultado: {'EXITOSO - LLAMADA GENERADA' if call_result['success'] else 'FALLIDO'}")

    print("\n" + "=" * 72)
    print("  PIPELINE COMPLETADO: VERIFICA EL TIMBRADO EN ZOIPER DE TU IPHONE  ")
    print("=" * 72 + "\n")

if __name__ == "__main__":
    launch_attack_and_trigger_pipeline()
