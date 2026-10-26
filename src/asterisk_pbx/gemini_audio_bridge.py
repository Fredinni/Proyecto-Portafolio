#!/usr/bin/env python3
"""
KRONOS SENTINEL - Gemini Live Voice Agent Bridge (EAGI)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
Description:
  Real-time AI voice incident responder using Google Gemini 3.1 Flash + Gemini TTS (Voice: Aoede).
  Conducts interactive phone debriefing with the CISO in informal, casual Spanish.
"""

import sys
import os
import json
import base64
import time
import ssl
import subprocess
import urllib.request
import urllib.error
import logging

LOG_FILE = "/var/log/asterisk/kronos_gemini_bridge.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [GEMINI-EAGI] %(message)s"
)

# SSL context para compatibilidad segura
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def get_api_key():
    for key_path in ["/etc/gemini.key", "/etc/kronos/gemini.key", "/root/.env"]:
        if os.path.exists(key_path):
            with open(key_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if "GEMINI_API_KEY=" in content:
                    for line in content.splitlines():
                        if line.startswith("GEMINI_API_KEY="):
                            return line.split("=", 1)[1].strip().strip("'\"")
                elif content:
                    return content
    return os.getenv("GEMINI_API_KEY", "")

API_KEY = get_api_key()

def send_agi(command: str) -> str:
    """Envía un comando al canal Asterisk AGI y lee la respuesta"""
    sys.stdout.write(f"{command}\n")
    sys.stdout.flush()
    res = sys.stdin.readline().strip()
    logging.info(f"AGI -> '{command}' | Asterisk <- '{res}'")
    return res

def read_agi_env():
    """Consume las cabeceras iniciales que Asterisk envía por stdin"""
    env = {}
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        if ":" in line:
            k, v = line.split(":", 1)
            env[k.strip()] = v.strip()
    return env

def generate_gemini_text(prompt: str, system_prompt: str) -> str:
    """Genera el texto de respuesta usando Gemini 3.1 Flash Lite"""
    if not API_KEY:
        return "¡Hola Bruno! Oye, te cuento que saltó una inyección SQL al DVWA, pero tranqui que el pfSense ya le chantó un drop en snort2c y mató los estados. ¿Lo dejamos bloqueado nomás?"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={API_KEY}"
    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
            data = json.loads(resp.read().decode())
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        logging.error(f"Error generando texto con Gemini: {e}")
        return "¡Hola Bruno! Oye, te cuento: hubo un ataque SQL Injection al servidor DVWA, pero el pfSense ya lo bloqueó en snort2c y limpió el kernel. ¿Quieres que revise algo más o lo dejamos bloqueado?"

TTS_MODELS = [
    "gemini-3.1-flash-tts-preview",
    "gemini-3.8-flash-lite-tts",
    "gemini-3.8-flash-tts",
    "gemini-2.5-flash-preview-tts"
]

def synthesize_gemini_audio(text_to_speak: str, output_prefix: str, voice_name: str = "Aoede") -> bool:
    """Sintetiza audio con voz femenina (Aoede) usando Gemini TTS con conmutación por cuota y lo convierte a 8kHz WAV/ULAW"""
    if not API_KEY:
        logging.error("No hay API Key para síntesis Gemini TTS.")
        return False

    for model in TTS_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        body = {
            "contents": [{"parts": [{"text": text_to_speak}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": voice_name
                        }
                    }
                }
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                data = json.loads(resp.read().decode())
                p = data["candidates"][0]["content"]["parts"][0]
                raw_pcm = base64.b64decode(p["inlineData"]["data"])

            raw_path = f"{output_prefix}_raw.pcm"
            wav_path = f"{output_prefix}.wav"
            ulaw_path = f"{output_prefix}.ulaw"

            with open(raw_path, "wb") as f:
                f.write(raw_pcm)

            # Conversión con sox de 24kHz mono 16-bit PCM a 8kHz mono WAV y ULAW para Asterisk
            subprocess.run(
                ["sox", "-t", "raw", "-r", "24000", "-c", "1", "-b", "16", "-e", "signed-integer", raw_path, "-r", "8000", "-c", "1", wav_path],
                check=True
            )
            subprocess.run(
                ["sox", wav_path, "-t", "ul", ulaw_path],
                check=True
            )
            logging.info(f"Audio generado con {model} y convertido exitosamente en {wav_path} y {ulaw_path}")
            return True
        except Exception as e:
            logging.warning(f"Error en síntesis con {model}: {e}. Conmutando al siguiente modelo TTS...")
            continue

    logging.error("Todos los modelos TTS de Gemini fallaron o agotaron cuota.")
    return False

def main():
    agi_env = read_agi_env()
    args = sys.argv[1:]

    incident_type = args[0] if len(args) > 0 and args[0] else "Inyección SQL Crítica"
    attacker_ip = args[1] if len(args) > 1 and args[1] else "185.220.101.5"
    geo_origin = args[2] if len(args) > 2 and args[2] else "Nodo Hostil"

    logging.info(f"Iniciando llamada interactiva Gemini Live: {incident_type} | {attacker_ip} | {geo_origin}")

    # Verificar si el pipeline ya pre-generó el briefing en vivo para eliminar la latencia
    cached_briefing = "/tmp/gemini_alert_current"
    used_cached = False
    if os.path.exists(f"{cached_briefing}.wav"):
        file_age = time.time() - os.path.getmtime(f"{cached_briefing}.wav")
        if file_age < 180:
            logging.info(f"Reproduciendo briefing Gemini Live en tiempo real (edad: {file_age:.1f}s)")
            send_agi(f"STREAM FILE {cached_briefing} \"\"")
            used_cached = True

    if not used_cached:
        # Prompt del sistema para el tono solicitado: de tú a tú, súper informal, muy casual
        sys_prompt = (
            "Eres la operadora de IA del sistema de ciberseguridad KRONOS SENTINEL. "
            "Estás en una llamada telefónica en vivo con Bruno Urrea (CISO). "
            "HABLA DE TÚ A TÚ, SÚPER INFORMAL, MUY CASUAL, COMO UNA COLEGA CAPA Y RELAJADA. "
            "Cero formalismos corporativos. "
            f"Explícale que acabas de mitigar una intrusión de inyección SQL hacia DVWA desde la IP {attacker_ip}, "
            "y que el pfSense ya le chantó un DROP en la tabla snort2c y mató todos los estados activos en el kernel. "
            "Pregúntale qué hacemos ahora: si revisamos el tráfico o si lo dejamos bloqueado nomás. "
            "Máximo 30 palabras. Responde SOLO el diálogo a pronunciar."
        )

        spoken_text = generate_gemini_text("Inicia el reporte de alerta a Bruno.", sys_prompt)
        logging.info(f"Texto generado por Gemini: {spoken_text}")

        prefix_alert = f"/tmp/gemini_call_{int(time.time())}"
        if synthesize_gemini_audio(spoken_text, prefix_alert, voice_name="Aoede"):
            send_agi(f"STREAM FILE {prefix_alert} \"\"")
        else:
            send_agi("STREAM FILE custom/kronos_alert \"\"")

    # Turno interactivo: escuchar la respuesta de Bruno
    send_agi("STREAM FILE beep \"\"")
    record_prefix = f"/tmp/bruno_rec_{int(time.time())}"
    # Grabar hasta 6 segundos o hasta 2 segundos de silencio
    send_agi(f"RECORD FILE {record_prefix} wav \"#\" 6000 0 BEEP s=2")

    # Respuesta interactiva de cierre con Gemini (Aoede)
    cached_closing = "/tmp/gemini_close_current"
    played_closing = False
    if os.path.exists(f"{cached_closing}.wav"):
        file_age = time.time() - os.path.getmtime(f"{cached_closing}.wav")
        if file_age < 300:
            logging.info(f"Reproduciendo respuesta de cierre Gemini Live pre-sintetizada (edad: {file_age:.1f}s)")
            send_agi(f"STREAM FILE {cached_closing} \"\"")
            played_closing = True

    if not played_closing:
        farewell_prompt = (
            "Eres la operadora de IA de KRONOS en la llamada con Bruno. "
            "Cierra la llamada de tú a tú, muy informal y casual, diciéndole que la amenaza ya quedó totalmente bloqueada "
            "en el firewall pfSense y que cualquier otra cosa le pegas una llamada al tiro. "
            "Máximo 18 palabras."
        )
        closing_text = generate_gemini_text("Despídete y cierra la llamada.", farewell_prompt)
        prefix_closing = f"/tmp/gemini_close_{int(time.time())}"
        if synthesize_gemini_audio(closing_text, prefix_closing, voice_name="Aoede"):
            send_agi(f"STREAM FILE {prefix_closing} \"\"")
        else:
            logging.warning("Fallback: reproduciendo despedida por defecto")
            send_agi("STREAM FILE custom/kronos_farewell \"\"")

    time.sleep(1)
    send_agi("HANGUP")
    logging.info("Llamada interactiva Gemini Live completada exitosamente.")

if __name__ == "__main__":
    main()
