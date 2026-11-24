# Registro de Incidencia QA · Desbloqueo de IP por Voz IA (24 de noviembre de 2026)

**Incidencia:** INC-20261124-VOZ-01  
**Severidad:** Grave (Bloqueante para flujo interactivo de QA)  
**Módulo afectado:** Agente de Voz IA (`src/ai_voice_agent/`) / Integración SOAR pfSense (`src/pfsense_pfctl_engine/`)  
**Responsables:** Bruno Urrea Ortiz (CISO / SecOps Lead) & Kevin Retamales (QA Lead)  
**Estado:** **PENDIENTE GRAVE A RESOLVER**

---

## 1. Descripción del Problema

Durante las sesiones de validación operativa en vivo de la Fase 3, tras simular un vector de ataque SQL Injection hacia DVWA desde el equipo del analista de QA (Kevin Retamales, IP `181.42.184.12` / Anexo `1004`), el sistema ejecuta la detección en Suricata y activa la llamada telefónica de alerta en Asterisk.

No obstante, cuando el analista atiende la llamada e interactúa con el agente de voz para solicitar la rehabilitación de su acceso perimetral, la acción de desbloqueo no se refleja efectivamente en el firewall pfSense o el agente no concreta la remoción de la IP en la tabla `snort2c`, requiriendo un vaciado administrativo forzado (`pfctl -t snort2c -T flush`) para restablecer el tráfico de pruebas.

---

## 2. Impacto Técnico

- **Flujo SOAR Interrumpido:** La capacidad de remediación interactiva mediante lenguaje natural (desbloqueo de falsos positivos o pruebas controladas de QA por llamada) presenta fallos de efectividad en caliente.
- **Bloqueo Persistente de QA:** El analista queda imposibilitado de continuar la batería de pruebas en DVWA de forma autónoma sin asistencia directa del administrador del firewall.

---

## 3. Puntos de Falla e Hipótesis a Investigar

1. **Sensibilidad y Sintaxis en `voice_policy.py`:**
   - La política de autorización en memoria exige coincidencias estrictas de términos (`desbloquea`, `libera`, `quítale el bloqueo`) o respuestas afirmativas directas (`sí`, `dale`, `adelante`). Si el operador emplea expresiones coloquiales no mapeadas o interrumpe la locución del bot, el token de autorización no se genera y la herramienta `unblock_ip` es rechazada.
2. **Latencia y Timeout en Ejecución Remota SSH:**
   - El wrapper `soar_tools_executor.py` invoca la clave restringida `ed25519` contra pfSense (`192.168.99.1`). Cualquier fluctuación de latencia o pérdida de paquetes en el enlace inter-VLAN durante la llamada puede provocar un timeout en la verificación atómica de estado.
3. **Re-bloqueo Inmediato por Tráfico Residual:**
   - Si el navegador o herramienta de pentest del analista mantiene sockets abiertos con payloads maliciosos en retransmisión, Suricata puede volver a insertar la IP en `snort2c` fracciones de segundo después de que la IA haya ejecutado el borrado.
4. **Validación de Parámetros en `voice_ssh_command.py`:**
   - Verificar si la IP parseada en tiempo de ejecución coincide exactamente con el formato esperado por el script enjaulado de pfSense sin caracteres de escape o espacios adicionales.

---

## 4. Plan de Acción y Tareas Pendientes

- [ ] Realizar sesión de depuración detallada con captura de tráfico pcap y trazas de `journalctl -u kronos-voice` una vez restablecida la conexión a la red Tailscale del laboratorio.
- [ ] Incorporar tolerancia léxica adicional en `voice_policy.py` para cubrir variantes coloquiales comunes de solicitud de desbloqueo en español chileno.
- [ ] Añadir reintento automático y verificación de doble estado en `PfctlWrapper.unblock_ip`.
- [ ] Implementar un periodo de gracia (grace period) de 15 segundos en el recolector EVE tras un desbloqueo manual/voz para evitar bloqueos cíclicos inmediatos por retransmisiones TCP.
