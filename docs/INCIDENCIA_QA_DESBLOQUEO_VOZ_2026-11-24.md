# Registro de Incidencia QA · Desbloqueo de IP por Voz IA (24 de noviembre de 2026)

**Incidencia:** INC-20261124-VOZ-01  
**Severidad:** Grave (Bloqueante para flujo interactivo de QA — ya mitigado)  
**Módulo afectado:** Agente de Voz IA (`src/ai_voice_agent/`, `src/asterisk_pbx/live_audio_server.py`) / Integración SOAR pfSense (`src/pfsense_pfctl_engine/`)  
**Responsables:** Bruno Urrea Ortiz (CISO / SecOps Lead) & Kevin Retamales (QA Lead)  
**Estado:** **RESUELTO Y VALIDADO EN PRODUCCIÓN (`20261124-live-03` en VM103)**

---

## 1. Descripción del Problema

Durante las sesiones de validación operativa en vivo de la Fase 3, tras simular un vector de ataque SQL Injection hacia DVWA desde el equipo del analista de QA (Kevin Retamales, IP `181.42.184.12` / Anexo `1004`), el sistema ejecuta la detección en Suricata y activa la llamada telefónica de alerta en Asterisk.

No obstante, cuando el analista atendía la llamada e interactuaba con el agente de voz para solicitar la rehabilitación de su acceso perimetral, la sesión sufría reconexiones tempranas, el filtro léxico rechazaba variantes coloquiales chilenas o, tras un desbloqueo efectivo, el navegador del cliente reenviaba el `POST` con payload SQLi causando un re-bloqueo inmediato en `snort2c`.

---

## 2. Impacto Técnico

- **Flujo SOAR Interrumpido:** La remediación interactiva por voz fallaba ante locuciones coloquiales, respuestas tardías tras saludos largos o llamadas entrantes directas (`DIRECT_CALL` / anexo `1000`).
- **Re-bloqueo Cíclico en QA:** Al recargar o retransmitir formularios con payloads de prueba tras un desbloqueo exitoso, Suricata volvía a insertar la IP del analista en `snort2c` dentro de la ventana de `cooldown` del despachador.

---

## 3. Causa Raíz Verificada en Auditoría Forense (2026-11-24)

Al revisar `journalctl -u kronos-voice`, `kronos-correlator.log`, `eve.json` y `/var/log/system.log` en pfSense, además de capturar eventos crudos del WebSocket de Gemini Live (`gemini-3.1-flash-live-preview`), se confirmaron cuatro causas reales:

1. **Disparos espurios de VAD y reconexión prematura en `gemini_live_client.py` / `audio_activity.py`:**
   - `AudioActivityGate` operaba con umbral bajo (`threshold=64`, `silence_ms=600`), fragmentando el audio entrante y enviando `audioStreamEnd` antes de concluir el saludo inicial.
   - El temporizador de corte `Model audio stalled mid-response` (`12 s` desde `last_audio`) disparaba `live_safe_reconnect` en plena escucha o justo después de `live_speech_end` cuando el modelo enviaba el audio del saludo en ráfaga más rápido que la reproducción en tiempo real a 8 kHz sin emitir `generationComplete` previo.
2. **Reglas estrictas y pérdida de turno en `voice_policy.py`:**
   - Las expresiones `UNBLOCK_EXPLICIT` y `AFFIRMATIVE_REPLY` no reconocían variantes enclíticas y coloquiales frecuentes en español chileno (`desbloquéamela`, `quítame el bloqueo`, `sácame del bloqueo`, `sí, claro, porfa`, `ya, dale`), y `QUESTION_GUARD` rechazaba `"como"` en frases declarativas (`"como estaba probando, desbloquéala"`).
   - `finish_turn()` limpiaba `input_text` al cerrarse una locución breve de transición antes de ejecutarse `toolCall`, y un rechazo local de política marcaba `mutation_attempted = True` bloqueando la recuperación de sesión.
3. **Falta de inspección de tabla en `DIRECT_CALL` (anexo `1000`):**
   - El flujo `DIRECT_CALL` no exponía una herramienta de solo lectura para consultar qué IPs figuraban activas en `snort2c` antes de confirmar el desbloqueo.
4. **Re-bloqueo posterior por tráfico residual del cliente:**
   - En las pruebas reales de las `15:15:42` y `15:42:28` (hora local), `voice_ssh_command.py` sí ejecutó `pfctl -t snort2c -T delete 181.42.184.12 rc=0` (`verified=True`). Sin embargo, a las `15:16:14` y `15:42:59` (~31–32 s después), el cliente envió nuevamente `POST /vulnerabilities/sqli/session-input.php` con `UNION SELECT`, disparando la regla SID `1000013` de Suricata y reinsertando la IP en `snort2c` mientras `dispatcher.py` suprimía una nueva llamada bajo su `cooldown` de 120 s.

---

## 4. Solución Aplicada y Evidencia de Verificación

### Cambios implementados

- [audio_activity.py](../src/ai_voice_agent/audio_activity.py): ajuste por defecto a `threshold=140` y `silence_ms=800`.
- [voice_policy.py](../src/ai_voice_agent/voice_policy.py): soporte de variantes coloquiales y enclíticas en `UNBLOCK_EXPLICIT`/`AFFIRMATIVE_REPLY`, acotamiento de `QUESTION_GUARD` a preguntas reales, preservación acotada de orden ante turnos breves (`last_turn_input`) y registro de IPs ofrecidas en `DIRECT_CALL`.
- [soar_tools_executor.py](../src/ai_voice_agent/soar_tools_executor.py) y [prompts.py](../src/ai_voice_agent/prompts.py): incorporación de la herramienta `list_blocked_ips`, bandera `firewall_touched` para distinguir rechazos locales de ejecuciones SSH reales e instrucción operativa de probar rutas limpias tras desbloquear.
- [gemini_live_client.py](../src/ai_voice_agent/gemini_live_client.py) y [live_audio_server.py](../src/asterisk_pbx/live_audio_server.py): compuerta de fin de saludo para `audioStreamEnd`, elevación de `MODEL_AUDIO_STALL_SECONDS` a `25 s` inhibido cuando existe habla o `speech_end` activo, limpieza de `response_active` obsoleto al iniciar nuevo turno de habla, 3 intentos seguros pre-mutación y trazas `reason` en `live_safe_reconnect`.
- [pfctl_wrapper.py](../src/pfsense_pfctl_engine/pfctl_wrapper.py): timeouts SSH ajustados (`ConnectTimeout=4`, ejecución `8 s`) y método `list_blocked_ips_status()`.
- [test_voice_reliability.py](../tests/test_voice_reliability.py): cobertura de regresión para fraseo chileno, `DIRECT_CALL` con `list_blocked_ips`, turnos intermedios, supresión de `audioStreamEnd` pre-saludo y ausencia de falso stall tras saludo sin `turnComplete`.

### Resultados observados

1. **Despliegue quirúrgico en VM103:**
   - Release inmutable `/opt/kronos/releases/20261124-live-03` verificada por SHA-256, `44/44` pruebas unitarias de voz (`OK`) y `voice_preflight.py` (`ready: true`, `gemini-3.1-flash-live-preview`) previos al cambio atómico de `/opt/kronos/live-current`.
   - Verificadas `0 active calls` en Asterisk antes del reinicio selectivo de `kronos-voice.service`, manteniendo `kronos-dispatcher.service` y `docker` activos sin interrupción.
2. **Pruebas automatizadas locales:**
   - `python -m pytest tests src/pfsense_setup/tests -v --tb=short`: **`85 passed, 1 warning, 37 subtests passed`** (`0` fallos).
   - `python tests/test_sentinel_pipeline.py`: **`Ran 10 tests - OK`**.
3. **Prueba E2E real AudioSocket + Gemini Live + pfSense (`198.18.0.254` aislada):**
   - **Flujo `INCIDENT` (`"Sí, desbloquéamela por favor."`, sesión `fcd76ba0-bf5a-43e5-a77d-2445920bc841`):**
     - `22:28:37,456 UTC`: `live_tool_requested name=unblock_ip ip=198.18.0.254`
     - `22:28:38,404 UTC`: `firewall_action operator=1004 action=unblock_ip ip=198.18.0.254 verified=True` (`elapsed=0.864 s`)
     - pfSense `/var/log/system.log`: `Nov 24 19:28:43 kronos-pfsense voice_ssh_command.py[73179]: KRONOS voice action -t snort2c -T delete 198.18.0.254 rc=0`
     - Verificación posterior: `is_blocked: false`, `0` reconexiones.
   - **Flujo `DIRECT_CALL` (`"Revisa qué IP está bloqueada..."` → `"Sí, claro, desbloquéamela por favor."`, sesión `72a0499d-2fb5-4229-a947-f3a63eef1fcf`):**
     - `22:29:15,598 UTC`: `live_tool name=list_blocked_ips elapsed=0.464 s`
     - `22:29:31,214 UTC`: `firewall_action operator=1004 action=unblock_ip ip=198.18.0.254 verified=True` (`elapsed=0.889 s`)
     - pfSense `/var/log/system.log`: `Nov 24 19:29:36 kronos-pfsense voice_ssh_command.py[25632]: KRONOS voice action -t snort2c -T delete 198.18.0.254 rc=0`
     - Verificación posterior: `is_blocked: false`, `0` reconexiones.
4. **Estado final de plataforma:**
   - Tabla `snort2c` en pfSense limpia (incluyendo remoción previa de `181.42.184.12`), instancias Suricata `--netmap` (`vtnet0` y `vtnet1.20`), `collector_service.py` y `haproxy` activas, y DVWA `/login.php` respondiendo `HTTP_CODE=200`.

### Pauta operativa recomendada para pruebas en vivo

Tras recibir confirmación verbal de desbloqueo, validar conectividad abriendo una ruta limpia (`/login.php`) en una pestaña nueva en vez de presionar F5 sobre un `POST` SQLi bloqueado anteriormente, ya que el reenvío de esa petición dispara nuevamente Suricata e inserta otra vez la IP en `snort2c`.
