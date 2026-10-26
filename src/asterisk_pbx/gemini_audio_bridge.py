#!/usr/bin/env python3
"""
KRONOS SENTINEL - Gemini Live Multimodal Voice Agent Bridge (EAGI)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
Description:
  Real-time AI voice incident responder using Google Gemini 3 Flash / 3.1 Flash (Multimodal Audio Understanding)
  and Gemini 3.8 Live TTS (Voice: Aoede).
  Processes actual microphone audio from CISO (zero canned recordings) and conducts an interactive debriefing.
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
import signal

LOG_FILE = "/var/log/asterisk/kronos_gemini_bridge.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

logger = logging.getLogger("GEMINI-EAGI")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [GEMINI-EAGI] %(message)s")
handler = FlushFileHandler(LOG_FILE, encoding="utf-8")
handler.setFormatter(formatter)
logger.addHandler(handler)

# SSL context
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def handle_sighup(signum, frame):
    logger.info("Canal telefónico cerrado por el usuario o Asterisk (SIGHUP recibido).")
    sys.exit(0)

signal.signal(signal.SIGHUP, handle_sighup)

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
    logger.info(f"AGI -> '{command}' | Asterisk <- '{res}'")
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

LLM_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.5-flash"
]

TTS_MODELS = [
    "gemini-3.8-flash-lite-tts",
    "gemini-3.8-flash-tts",
    "gemini-3.1-flash-tts-preview"
]

def synthesize_gemini_audio(text_to_speak: str, output_prefix: str, voice_name: str = "Aoede") -> bool:
    """Sintetiza audio con voz femenina (Aoede) usando Gemini 3.8 Live y lo convierte a 8kHz WAV/ULAW"""
    if not API_KEY:
        logger.error("No hay API Key para síntesis Gemini TTS.")
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
            with urllib.request.urlopen(req, timeout=12, context=SSL_CTX) as resp:
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
            logger.info(f"Audio sintetizado con {model} ({len(raw_pcm)} bytes PCM) -> {wav_path}")
            return True
        except Exception as e:
            logger.warning(f"Error en síntesis con {model}: {e}. Probando siguiente modelo...")
            continue

    logger.error("Todos los modelos TTS de Gemini fallaron.")
    return False

def understand_and_respond_multimodal(wav_path: str, incident_type: str, attacker_ip: str, target_service: str, recurrence_count: int = 1) -> str:
    """
    Procesa directamente el audio capturado del micrófono de Bruno usando la API Multimodal de Gemini.
    Zero transcripción externa - Gemini 'escucha' el WAV y responde directamente al contenido.
    """
    if not os.path.exists(wav_path):
        logger.error(f"Archivo de grabación no existe: {wav_path}")
        return ""

    file_size = os.path.getsize(wav_path)
    logger.info(f"Procesando audio de micrófono de Bruno: {wav_path} ({file_size} bytes)")

    if file_size < 3500:
        logger.info("Audio de micrófono demasiado corto (silencio detectado).")
        return ""

    try:
        with open(wav_path, "rb") as f:
            wav_bytes = f.read()
        b64_audio = base64.b64encode(wav_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Error leyendo WAV: {e}")
        return ""

    rec_info = f"Este atacante ya reincidió {recurrence_count} veces." if recurrence_count >= 2 else "Es el primer intento detectado."

    system_instruction = (
        "Eres la operadora de ciberseguridad de IA del sistema KRONOS SENTINEL. "
        "Estás en una llamada telefónica en vivo con Bruno Urrea (CISO). "
        "HABLA DE TÚ A TÚ, SÚPER INFORMAL, MUY CASUAL CHILENA, RELAJADA, COMO UNA COLEGA CAPA DE SOC. "
        "Cero formalismos corporativos ni discursos largos. "
        f"Contexto del incidente: Mitigamos un ataque de {incident_type} desde la IP {attacker_ip} hacia {target_service}. "
        f"El pfSense ya le chantó un DROP en snort2c y mató todos los estados. {rec_info} "
        "Escucha atentamente lo que Bruno acaba de decir en el audio grabado de su micrófono. "
        "Respóndele DIRECTAMENTE a lo que dijo o preguntó: "
        "- Si te dice que lo bloquees o confirmes, dile que ya quedó sellado en snort2c y que no entra más. "
        "- Si te pregunta qué IP fue o qué pasó, dale los datos técnicos exactos. "
        "- Si te dice 'vale', 'chao' o agradece, despídete rápido en buena onda. "
        "Máximo 14 palabras. Responde ÚNICAMENTE el diálogo que vas a pronunciar por teléfono."
    )

    for m in LLM_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={API_KEY}"
        body = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [
                {
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": "audio/wav",
                                "data": b64_audio
                            }
                        },
                        {
                            "text": "¿Qué me respondió Bruno en el teléfono y cuál es tu respuesta inmediata para él?"
                        }
                    ]
                }
            ]
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}
            )
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=8, context=SSL_CTX) as resp:
                data = json.loads(resp.read().decode())
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                logger.info(f"Gemini Multimodal ({m}) procesó micrófono en {time.time()-t0:.2f}s: '{reply}'")
                return reply
        except Exception as e:
            logger.warning(f"Error procesando audio con {m}: {e}. Probando siguiente modelo...")
            continue

    logger.error("No se pudo procesar el audio con ningún modelo Gemini.")
    return ""

def main():
    agi_env = read_agi_env()
    args = sys.argv[1:]

    # Cargar contexto enriquecido si existe en /tmp/incident_context.json
    incident_type = "Inyección SQL Crítica"
    attacker_ip = "185.220.101.5"
    geo_origin = "Nodo Hostil"
    target_service = "DVWA en DMZ"
    recurrence_count = 1

    ctx_file = "/tmp/incident_context.json"
    if os.path.exists(ctx_file):
        try:
            with open(ctx_file, "r", encoding="utf-8") as f:
                ctx = json.load(f)
                incident_type = ctx.get("attack_type", incident_type)
                attacker_ip = ctx.get("attacker_ip", attacker_ip)
                geo_origin = ctx.get("geo_country", geo_origin)
                target_service = ctx.get("target_service", target_service)
                recurrence_count = ctx.get("recurrence_count", recurrence_count)
                logger.info(f"Contexto cargado de {ctx_file}: {attacker_ip} (Reincidencia: x{recurrence_count})")
        except Exception as e:
            logger.warning(f"Error leyendo {ctx_file}: {e}")
    else:
        if len(args) > 0 and args[0]: incident_type = args[0]
        if len(args) > 1 and args[1]: attacker_ip = args[1]
        if len(args) > 2 and args[2]: geo_origin = args[2]

    logger.info(f"=== NUEVA LLAMADA INTERACTIVA GEMINI LIVE ===")
    logger.info(f"Ataque: {incident_type} | IP: {attacker_ip} | Reincidencia: x{recurrence_count}")

    # PASO 1: Reproducir el Briefing Inicial (0.0s de latencia con audio pre-generado)
    cached_briefing = "/tmp/gemini_alert_current"
    used_cached = False
    if os.path.exists(f"{cached_briefing}.wav"):
        file_age = time.time() - os.path.getmtime(f"{cached_briefing}.wav")
        if file_age < 300:
            logger.info(f"Reproduciendo briefing inicial Gemini Live (edad: {file_age:.1f}s)")
            send_agi(f"STREAM FILE {cached_briefing} \"\"")
            used_cached = True

    if not used_cached:
        rec_str = f"este compadre de la {attacker_ip} ya van {recurrence_count} veces que nos tira {incident_type}, revísalo." if recurrence_count >= 2 else f"frené un ataque de {incident_type} desde la IP {attacker_ip} hacia {target_service}."
        prompt_fallback = (
            f"¿Aló, Bruno? Oye, {rec_str} El pfSense ya le chantó DROP en snort2c y mató los estados. ¿Lo dejamos bloqueado nomás?"
        )
        prefix_alert = f"/tmp/gemini_alert_{int(time.time())}"
        if synthesize_gemini_audio(prompt_fallback, prefix_alert, voice_name="Aoede"):
            send_agi(f"STREAM FILE {prefix_alert} \"\"")
        else:
            send_agi("STREAM FILE custom/kronos_alert \"\"")

    # PASO 2: Turno Interactivo - Escuchar el Micrófono de Bruno
    send_agi("STREAM FILE beep \"\"")
    record_prefix = f"/tmp/bruno_rec_{int(time.time())}"
    logger.info(f"Iniciando grabación de micrófono de Bruno en {record_prefix}.wav...")
    # Graba hasta 6 segundos, corta tras 2 segundos de silencio o presionar '#'
    send_agi(f"RECORD FILE {record_prefix} wav \"#\" 6000 0 BEEP s=2")

    rec_wav = f"{record_prefix}.wav"
    rec_size = os.path.getsize(rec_wav) if os.path.exists(rec_wav) else 0

    if rec_size > 3500:
        # Bruno habló por el micrófono -> Dar feedback inmediato con audio natural
        logger.info(f"Bruno habló ({rec_size} bytes). Reproduciendo audio de transición inmediata...")
        send_agi("STREAM FILE custom/kronos_thinking \"\"")

        # PASO 3: Comprensión Multimodal con Gemini (Directo del WAV grabado)
        ai_response = understand_and_respond_multimodal(
            wav_path=rec_wav,
            incident_type=incident_type,
            attacker_ip=attacker_ip,
            target_service=target_service,
            recurrence_count=recurrence_count
        )

        if ai_response:
            logger.info(f"Respuesta generada para Bruno: '{ai_response}'")
            prefix_reply = f"/tmp/gemini_reply_{int(time.time())}"
            if synthesize_gemini_audio(ai_response, prefix_reply, voice_name="Aoede"):
                send_agi(f"STREAM FILE {prefix_reply} \"\"")
            else:
                logger.warning("Fallback TTS en respuesta a Bruno")
                send_agi("STREAM FILE custom/kronos_farewell \"\"")

            # Turno de cierre breve
            send_agi("STREAM FILE beep \"\"")
            rec_prefix_2 = f"/tmp/bruno_close_{int(time.time())}"
            send_agi(f"RECORD FILE {rec_prefix_2} wav \"#\" 3000 0 BEEP s=1")
        else:
            send_agi("STREAM FILE custom/kronos_farewell \"\"")
    else:
        # Si no hubo audio o hubo silencio absoluto
        logger.info("Sin respuesta audible de Bruno, reproduciendo despedida de guardia.")
        silence_farewell = "Oye Bruno, cualquier cosa rara con el pfSense te timbro de nuevo. Chao!"
        prefix_silence = f"/tmp/gemini_silence_{int(time.time())}"
        if synthesize_gemini_audio(silence_farewell, prefix_silence, voice_name="Aoede"):
            send_agi(f"STREAM FILE {prefix_silence} \"\"")
        else:
            send_agi("STREAM FILE custom/kronos_farewell \"\"")

    time.sleep(1)
    send_agi("HANGUP")
    logger.info("Llamada interactiva completada exitosamente.")

if __name__ == "__main__":
    main()