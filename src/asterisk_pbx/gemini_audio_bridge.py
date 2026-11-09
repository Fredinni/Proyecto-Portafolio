#!/usr/bin/env python3
"""
KRONOS SENTINEL - Puente Conversacional de Voz en Tiempo Real para Asterisk (EAGI)
Autores: Bruno Urrea Ortiz & Kevin Retamales (Portafolio de Título - Duoc UC)
Proyecto: KRONOS SENTINEL - Autonomous AI-IPS & Live Voice Incident Response
Descripción:
  Agente de respuesta telefónica a incidentes de seguridad integrado con Asterisk 20 LTS.
  - Interacción bidireccional mediante streaming de audio y telefonía SIP.
  - Supresión de tonos de grabación para interacción fluida de baja latencia.
  - Comprensión multimodal de audio con Gemini API.
  - Síntesis de voz dinámica en tiempo real (TTS Aoede).
  - Desbloqueo y gestión reactiva de tablas de firewall snort2c bajo comando del operador.
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

# SSL context (ignorar verificación en entorno de laboratorio cerrado)
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

OPERATOR_MAP = {
    "1001": ("Bruno", "CISO / SecOps Lead"),
    "1002": ("Freddy", "VoIP & Network Engineer"),
    "1003": ("Cristóbal", "DMZ & Proxy Admin"),
    "1004": ("Kevin", "Threat Intel & Hardening QA Lead")
}

def send_agi(command: str) -> str:
    """Envía un comando al canal Asterisk AGI y lee la respuesta síncrona"""
    sys.stdout.write(f"{command}\n")
    sys.stdout.flush()
    res = sys.stdin.readline().strip()
    logger.info(f"AGI -> '{command}' | Asterisk <- '{res}'")
    return res

def read_agi_env():
    """Consume las cabeceras iniciales enviadas por Asterisk por stdin"""
    env = {}
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        if ":" in line:
            k, v = line.split(":", 1)
            env[k.strip()] = v.strip()
    return env

# Modelos multimodales para comprensión de audio (ordenados por velocidad y cuota)
LLM_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3-flash-preview"
]

# Modelos TTS para síntesis vocal en vivo (Aoede)
TTS_MODELS = [
    "gemini-3.8-flash-lite-tts",
    "gemini-2.5-flash-preview-tts",
    "gemini-3.1-flash-tts-preview"
]

def unblock_ip_pfsense(ip_to_unblock: str, pfsense_ip: str = "192.168.99.1", port: int = 8443) -> bool:
    """
    Desbloquea en tiempo real una dirección IP en la tabla snort2c del kernel de pfSense
    a través del endpoint administrativo autorizado para el agente SOAR de KRONOS.
    """
    clean_ip = re.sub(r'[^0-9a-fA-F.:]', '', ip_to_unblock.strip())
    if not clean_ip:
        logger.warning("No se proporcionó una IP válida para desbloquear.")
        return False

    base_url = f"https://{pfsense_ip}:{port}"
    try:
        # 1. Obtener token CSRF
        req1 = urllib.request.Request(f"{base_url}/", headers={"User-Agent": "KRONOS-SOAR-Agent/1.0"})
        with urllib.request.urlopen(req1, timeout=4, context=SSL_CTX) as resp1:
            html1 = resp1.read().decode('utf-8', errors='replace')
            cookies = resp1.headers.get_all('Set-Cookie') or []
            cookie_header = "; ".join([c.split(';')[0] for c in cookies])

        csrf_match = re.search(r'var\s+csrfMagicToken\s*=\s*"(sid:[^"]+)";', html1)
        if not csrf_match:
            csrf_match = re.search(r'name=["\']__csrf_magic["\']\s+value=["\']([^"\']+)["\']', html1)
        if not csrf_match:
            logger.error("No se pudo obtener CSRF token de pfSense para el desbloqueo.")
            return False
        csrf_token = csrf_match.group(1)

        # 2. Login administrativo
        login_body = urllib.parse.urlencode({
            '__csrf_magic': csrf_token,
            'usernamefld': 'kronos',
            'passwordfld': 'Iw5vPx1iR0L2TlwiIriAdfFWjE_iHtF_',
            'login': 'Sign In'
        }).encode('utf-8')

        req2 = urllib.request.Request(
            f"{base_url}/",
            data=login_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": cookie_header,
                "User-Agent": "KRONOS-SOAR-Agent/1.0"
            }
        )
        with urllib.request.urlopen(req2, timeout=4, context=SSL_CTX) as resp2:
            new_cookies = resp2.headers.get_all('Set-Cookie') or []
            if new_cookies:
                cookie_header = "; ".join([c.split(';')[0] for c in new_cookies])

        # 3. Obtener CSRF de diag_command.php
        req3 = urllib.request.Request(f"{base_url}/diag_command.php", headers={"Cookie": cookie_header, "User-Agent": "KRONOS-SOAR-Agent/1.0"})
        with urllib.request.urlopen(req3, timeout=4, context=SSL_CTX) as resp3:
            html3 = resp3.read().decode('utf-8', errors='replace')

        csrf_diag = re.search(r'name=["\']__csrf_magic["\']\s+value=["\']([^"\']+)["\']', html3)
        csrf_cmd = csrf_diag.group(1) if csrf_diag else csrf_token

        # 4. Ejecutar borrado en tabla snort2c y purga de estados
        cmd_body = urllib.parse.urlencode({
            '__csrf_magic': csrf_cmd,
            'txtCommand': f'pfctl -t snort2c -T delete {clean_ip} ; pfctl -k {clean_ip}',
            'submit': 'EXEC'
        }).encode('utf-8')

        req4 = urllib.request.Request(
            f"{base_url}/diag_command.php",
            data=cmd_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": cookie_header,
                "User-Agent": "KRONOS-SOAR-Agent/1.0"
            }
        )
        with urllib.request.urlopen(req4, timeout=4, context=SSL_CTX) as resp4:
            resp4.read()

        logger.info(f"✅ ¡DESBLOQUEO EN KERNEL EXITOSO! IP {clean_ip} eliminada de snort2c.")
        return True
    except Exception as e:
        logger.error(f"❌ Error ejecutando desbloqueo en pfSense para {clean_ip}: {e}")
        return False

def synthesize_gemini_audio(text_to_speak: str, output_prefix: str, voice_name: str = "Aoede") -> bool:
    """
    Sintetiza audio al vuelo usando Gemini TTS con la voz Aoede.
    Convierte el flujo PCM de 24kHz a 8kHz mono WAV y ULAW para Asterisk.
    Optimizado para frases tácticas de < 10 palabras (latencia < 2.0s).
    """
    if not API_KEY:
        logger.error("No hay API Key configurada para síntesis Gemini TTS.")
        return False

    # Permitir frases tácticas completas de hasta 60 palabras
    words = text_to_speak.split()
    if len(words) > 60:
        text_to_speak = " ".join(words[:60]) + "."

    raw_path = f"{output_prefix}_raw.pcm"
    wav_path = f"{output_prefix}.wav"
    ulaw_path = f"{output_prefix}.ulaw"

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
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
                data = json.loads(resp.read().decode())
                p = data["candidates"][0]["content"]["parts"][0]
                raw_pcm = base64.b64decode(p["inlineData"]["data"])

            with open(raw_path, "wb") as f:
                f.write(raw_pcm)

            # Conversión rápida mono 8kHz WAV y ULAW
            subprocess.run(
                ["sox", "-t", "raw", "-r", "24000", "-c", "1", "-b", "16", "-e", "signed-integer", raw_path, "-r", "8000", "-c", "1", wav_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            subprocess.run(
                ["sox", wav_path, "-t", "ul", ulaw_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            dur = time.time() - t0
            logger.info(f"Audio sintetizado con {model} en {dur:.2f}s ({len(raw_pcm)} bytes PCM) -> {wav_path}")
            return True
        except urllib.error.HTTPError as he:
            logger.warning(f"TTS {model} error HTTP {he.code}: {he.reason}. Intentando siguiente...")
            continue
        except Exception as e:
            logger.warning(f"TTS {model} excepción: {e}. Intentando siguiente...")
            continue

    logger.error("Todos los modelos TTS de Gemini fallaron.")
    return False

def understand_and_respond_multimodal(
    wav_path: str,
    operator_name: str,
    operator_role: str,
    incident_type: str,
    attacker_ip: str,
    target_service: str,
    recurrence_count: int = 1,
    is_direct_call: bool = False
) -> str:
    """
    Procesa el audio directo del micrófono del operador usando la API Multimodal de Gemini.
    Zero transcripción externa: Gemini escucha el WAV y responde directamente.
    """
    if not os.path.exists(wav_path):
        logger.error(f"Archivo de grabación no existe: {wav_path}")
        return ""

    file_size = os.path.getsize(wav_path)
    if file_size < 3000:
        logger.info(f"Audio de micrófono descartado por tamaño insignificante ({file_size} bytes).")
        return ""

    try:
        with open(wav_path, "rb") as f:
            wav_bytes = f.read()
        b64_audio = base64.b64encode(wav_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Error leyendo WAV para envío multimodal: {e}")
        return ""

    rec_info = f"Este atacante ya reincidió {recurrence_count} veces." if recurrence_count >= 2 else "Es el primer intento registrado."

    system_instruction = (
        f"Eres la operadora de ciberseguridad de IA del sistema KRONOS SENTINEL. "
        f"Estás en una llamada telefónica en vivo con {operator_name} ({operator_role}). "
        f"HABLA DE TÚ A TÚ, SÚPER INFORMAL, MUY CASUAL CHILENA, RELAJADA, COMO UNA COLEGA CAPA DE SOC. "
        f"Cero formalismos corporativos, cero introducciones robóticas, CERO narraciones de lo que dijo el operador. "
        f"Contexto técnico: Mitigamos un ataque de {incident_type} desde la IP {attacker_ip} hacia {target_service}. "
        f"El pfSense ya le chantó un DROP en la tabla snort2c y mató todos los sockets TCP activos. {rec_info} "
        f"Escucha atentamente lo que {operator_name} acaba de decir en el audio grabado de su micrófono. "
        f"Respóndele DIRECTAMENTE en máximo 15 palabras, de forma clara, natural y chilena: "
        f"- Si pide bloquear o confirmar, responde que ya quedó sellada en el firewall ('Listo compadre, ya quedó sellada en el firewall.'). "
        f"- Si pide desbloquear la IP, levantar el bloqueo, liberarla, o dice que era él testeando: responde confirmando con buena onda (ej: '[ACTION:UNBLOCK] Listo Kevin, ya te liberé la IP en el firewall para que sigas.') e incluye SIEMPRE la etiqueta [ACTION:UNBLOCK] al inicio. "
        f"- Si pregunta qué IP fue o detalles del ataque, indícale la IP {attacker_ip} y DVWA ('Te botó la inyección SQL en DVWA desde tu IP.'). "
        f"- Si dice 'vale', 'gracias', 'chao', 'listo' o se despide, despídete en buena onda ('¡Vale compadre, avísame cualquier cosa!'). "
        f"- Si pregunta cómo está la red, dile que la DMZ está segura ('La DMZ está impeque, todo asegurado.'). "
        f"MÁXIMO 15 PALABRAS. CERO PREÁMBULOS NI EXPLICACIONES. Habla ÚNICAMENTE la frase directa a pronunciar por teléfono."
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
                            "text": f"Responde directamente a {operator_name} en máximo 15 palabras:"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 80,
                "temperature": 0.1,
                "thinkingConfig": {"thinkingBudget": 0}
            }
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
                # Limpiar posibles narrativas residuales ('Kevin preguntó... Le respondo:')
                reply = re.sub(r'^(.*?)(respondo|dile|dice|pregunta|dijo|preguntó):\s*', '', reply, flags=re.IGNORECASE)
                reply = reply.strip('"\' \n\r')
                dur = time.time() - t0
                logger.info(f"Gemini Multimodal ({m}) procesó audio en {dur:.2f}s: '{reply}'")
                return reply
        except Exception as e:
            logger.warning(f"Error procesando audio con {m}: {e}. Intentando siguiente modelo...")
            continue

    logger.error("No se pudo procesar el audio con ningún modelo Gemini.")
    return ""

def main():
    agi_env = read_agi_env()
    args = sys.argv[1:]

    # Valores por defecto del incidente
    incident_type = "Inyección SQL Crítica en DMZ"
    attacker_ip = "186.10.176.148"
    geo_origin = "Entorno de Pruebas QA"
    target_service = "DVWA en DMZ"
    recurrence_count = 1

    # Cargar argumentos pasados por Asterisk Dialplan
    if len(args) >= 2 and args[0] != "DIRECT_CALL":
        if args[0] and not args[0].startswith("${"):
            incident_type = args[0]
        if args[1] and not args[1].startswith("${"):
            attacker_ip = args[1]
        if len(args) >= 3 and args[2] and not args[2].startswith("${"):
            geo_origin = args[2]

    # Determinar si es llamada directa al anexo 1000
    is_direct_call = False
    caller_id = agi_env.get("agi_callerid", "").strip()

    if len(args) > 0 and args[0] == "DIRECT_CALL":
        is_direct_call = True
        if len(args) > 1 and args[1]:
            caller_id = args[1].strip()
    elif not caller_id and len(args) > 1:
        caller_id = args[1].strip()

    # Identificar operador
    operator_name, operator_role = OPERATOR_MAP.get(caller_id, ("Kevin", "Threat Intel QA Lead"))
    is_kevin_test = ("186.10" in attacker_ip) or (operator_name == "Kevin")

    logger.info(f"=== NUEVA SESIÓN DE VOZ GEMINI LIVE EN TIEMPO REAL ===")
    logger.info(f"Operador: {operator_name} (Anexo: {caller_id}) | Modo: {'DIRECT_CALL (1000)' if is_direct_call else 'EMERGENCY_DISPATCH'}")
    logger.info(f"Ataque: {incident_type} | IP Atacante: {attacker_ip} | Reincidencia: x{recurrence_count}")

    # =========================================================================
    # PASO 1: Reproducción Inmediata del Saludo Inicial Dinámico y Contextual
    # =========================================================================
    played_greeting = False

    # A) Si es llamada directa al 1000 y existe audio pre-calentado para este anexo
    if is_direct_call:
        prewarmed_path = f"/tmp/gemini_greeting_{caller_id}"
        if os.path.exists(f"{prewarmed_path}.wav"):
            logger.info(f"Reproduciendo saludo pre-calentado para anexo {caller_id} (0.0s de latencia)")
            send_agi(f"STREAM FILE {prewarmed_path} \"\"")
            played_greeting = True

    # B) Generación dinámica en vivo e informada
    if not played_greeting:
        if is_direct_call:
            opening_text = f"¡Aló {operator_name}! Soy la operadora de KRONOS SENTINEL. Estoy monitoreando la DMZ y el pfSense. ¿Qué necesitas revisar o desbloquear?"
        else:
            if is_kevin_test:
                opening_text = f"¡Aló Kevin! Oye, te llamo porque el IPS en la DMZ te acaba de frenar una inyección SQL hacia DVWA. Como estás probando tú, ¿quieres que te desbloquee la IP al tiro para que sigas?"
            else:
                opening_text = f"¡Aló {operator_name}! Oye, frenamos un ataque de {incident_type} desde la IP {attacker_ip} hacia {target_service}. ¿Lo dejamos bloqueado o te lo desbloqueo?"

        prefix_opening = f"/tmp/gemini_opening_{int(time.time())}"
        logger.info(f"Sintetizando saludo dinámico en vivo para {operator_name}: '{opening_text}'")
        if synthesize_gemini_audio(opening_text, prefix_opening, voice_name="Aoede"):
            send_agi(f"STREAM FILE {prefix_opening} \"\"")
        else:
            logger.error("Fallo crítico sintetizando saludo inicial.")

    # =========================================================================
    # PASO 2: Bucle Conversacional Multi-Turno en Vivo (Sin Tonos de Grabadora)
    # =========================================================================
    turn = 0
    max_turns = 8
    consecutive_silences = 0

    while turn < max_turns:
        turn += 1
        rec_prefix = f"/tmp/operator_rec_{int(time.time())}_{turn}"
        logger.info(f"--- Turno {turn}: Escuchando micrófono de {operator_name} (sin beeps)...")

        # Asterisk RECORD FILE sin beep:
        # 5000ms max con detección de silencio 's=1' (corta tras 1 segundo de silencio completo)
        rec_res = send_agi(f"RECORD FILE {rec_prefix} wav \"#\" 5000 0 s=1")
        if "result=-1" in rec_res:
            logger.info("Canal colgado por el usuario durante la grabación.")
            break

        rec_wav = f"{rec_prefix}.wav"
        rec_size = os.path.getsize(rec_wav) if os.path.exists(rec_wav) else 0

        if rec_size > 3000:
            consecutive_silences = 0
            logger.info(f"{operator_name} habló por micrófono ({rec_size} bytes). Procesando con Gemini Multimodal...")

            ai_response = understand_and_respond_multimodal(
                wav_path=rec_wav,
                operator_name=operator_name,
                operator_role=operator_role,
                incident_type=incident_type,
                attacker_ip=attacker_ip,
                target_service=target_service,
                recurrence_count=recurrence_count,
                is_direct_call=is_direct_call
            )

            if not ai_response:
                ai_response = f"Dale {operator_name}, la red quedó protegida en el firewall y el atacante está bloqueado."

            # Detección y ejecución de acción SOAR: Desbloqueo en caliente a solicitud de voz
            unblock_triggers = [
                "[action:unblock]", "liberar", "desbloquear", "liberé", "libere",
                "desbloqueé", "desbloquee", "desbloqueo", "desbloqueada", "desbloqueado",
                "liberada", "liberado", "libera", "desbloquea", "sácala", "sacala"
            ]
            lower_ai = ai_response.lower()
            if any(t in lower_ai for t in unblock_triggers):
                ai_response = re.sub(r'\[action:unblock\]', '', ai_response, flags=re.IGNORECASE).strip()
                logger.info(f"⚡ ORDEN DE VOZ DETECTADA: Desbloquear IP atacante {attacker_ip} en pfSense...")
                unblock_ok = unblock_ip_pfsense(attacker_ip)
                if unblock_ok:
                    logger.info(f"✅ IP {attacker_ip} desbloqueada exitosamente por comando de voz de {operator_name}.")
                else:
                    logger.warning(f"⚠️ No se pudo completar el desbloqueo automático de {attacker_ip}.")

            logger.info(f"Respuesta generada para {operator_name}: '{ai_response}'")
            reply_prefix = f"/tmp/gemini_reply_{int(time.time())}_{turn}"
            if synthesize_gemini_audio(ai_response, reply_prefix, voice_name="Aoede"):
                play_res = send_agi(f"STREAM FILE {reply_prefix} \"\"")
                if "result=-1" in play_res:
                    break

            # Si el usuario o el bot indicaron despedida, terminar la llamada amistosamente
            lower_resp = ai_response.lower()
            if any(w in lower_resp for w in ["chao", "hasta luego", "nos vemos", "que estés bien"]):
                logger.info("Despedida completada. Finalizando sesión telefónica.")
                break
        else:
            consecutive_silences += 1
            if consecutive_silences == 1:
                # Primer silencio: repregunta amigable
                prompt_text = f"¿Aló {operator_name}? ¿Sigues ahí? Dime si necesitas algo más."
                prompt_prefix = f"/tmp/gemini_prompt_{int(time.time())}"
                if synthesize_gemini_audio(prompt_text, prompt_prefix, voice_name="Aoede"):
                    send_agi(f"STREAM FILE {prompt_prefix} \"\"")
            else:
                # Segundo silencio consecutivo: despedida y cierre
                farewell_text = f"Vale {operator_name}, te dejo tranquilo. Cualquier cosa te timbro de nuevo. ¡Chao!"
                farewell_prefix = f"/tmp/gemini_farewell_{int(time.time())}"
                if synthesize_gemini_audio(farewell_text, farewell_prefix, voice_name="Aoede"):
                    send_agi(f"STREAM FILE {farewell_prefix} \"\"")
                break

    time.sleep(0.5)
    send_agi("HANGUP")
    logger.info("Llamada interactiva finalizada exitosamente.")

if __name__ == "__main__":
    main()
