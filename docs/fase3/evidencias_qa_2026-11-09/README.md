# Evidencias de QA · Fase 3 (9 de noviembre de 2026)

**Actividad:** A10 — Aseguramiento de Calidad · **Fase 3** (QA, Validación y Defensa).

Pruebas de QA ejecutadas desde el equipo del analista (macOS), conectado al laboratorio por el túnel Tailscale (WireGuard), hacia los servicios publicados en el borde público AWS (`100.50.147.57`). Las capturas de pfSense se tomaron en modo de solo lectura.

## Prueba 1 · Calidad de la voz (QoS) — `voz/`

Llamada de la extensión 1004 (QA) al asistente de voz con IA (extensión 1000).

| Archivo | Qué demuestra |
|---|---|
| [01-llamada-ia-conectada.png](voz/01-llamada-ia-conectada.png) | Registro SIP y llamada activa con el asistente IA. |
| [02-qos-calidad-perdida-0pct.png](voz/02-qos-calidad-perdida-0pct.png) | Códec G.711 µ-law, jitter 0 ms, pérdida 0 % durante la locución del asistente. |
| [03-qos-calidad-perdida-4_5pct.png](voz/03-qos-calidad-perdida-4_5pct.png) | Pérdida de 4,5 % en conversación en vivo (sin cortes audibles). |
| [04-qos-bitrate-g711.png](voz/04-qos-bitrate-g711.png) | Bitrate ~85 kb/s, coherente con G.711. |
| [05-historial-llamadas-contestadas.png](voz/05-historial-llamadas-contestadas.png) | Cuatro llamadas contestadas por el asistente. |

| Métrica | Medición | Estándar | Resultado |
|---|---|---|---|
| Códec | G.711 µ-law (~85 kb/s) | — | OK |
| Jitter | 0 ms | < 30 ms | PASS |
| Pérdida (locución IA) | 0 % | < 1 % | PASS |
| Pérdida (conversación en vivo) | 4,5 % | < 1 % ideal | Observación |

**Análisis.** La voz se escuchó sin cortes en ambos sentidos. La pérdida de 4,5 % se atribuye a la ruta de acceso remoto (relay de Tailscale, ~270 ms ida y vuelta), no a la red interna; G.711 enmascara pérdidas pequeñas. La **configuración** de priorización QoS en la VLAN 30 de voz corresponde a A9; estas mediciones son la línea base para contrastarla.

## Prueba 2 · Inyección SQL desde Internet — `pentest/`

Ataque de SQL Injection contra DVWA a través del flujo real (Internet → borde AWS → HAProxy → DMZ).

| Archivo | Qué demuestra |
|---|---|
| [01-sqli-exfiltracion-credenciales.png](pentest/01-sqli-exfiltracion-credenciales.png) | SQLi `UNION SELECT` exitoso en nivel *Low*: volcado de usuarios y hashes de contraseña. |
| [02-dvwa-security-level-impossible.png](pentest/02-dvwa-security-level-impossible.png) | En nivel *Impossible* (consultas parametrizadas) la aplicación resiste el mismo ataque. |

**Resultados.**
- Se confirma que DVWA es vulnerable a SQLi en nivel *Low* y que se defiende en nivel *Impossible* (defensa en profundidad a nivel de aplicación).
- Con el último ajuste de infraestructura, **Suricata en modo Inline IPS frenó el ataque real**: la IP pública del analista recibió error 504 y perdió acceso al borde, mientras una IP distinta mantenía el acceso normal (bloqueo dirigido).

## Pendiente (en corrección con el responsable de A6)

- **Doble NAT en el borde:** la IP pública real del atacante no llega a pfSense, por lo que la capa de notificación por voz reporta una IP representativa. Solución identificada: propagar la IP real vía `X-Forwarded-For` de HAProxy hacia el motor KRONOS.
- **Registro en el firewall:** que el motor escriba la IP real del atacante en su tabla de bloqueo (`KRONOS_IPS_GUARD`).
- **Medición de la cadena completa:** tiempo total detección → bloqueo (meta < 1,5 s), una vez integrada la propagación de IP.

## Video de la demostración

Grabación de la interacción con el asistente de voz con IA:

https://drive.google.com/file/d/1SPBRV5KstX7bYjfDqx7phRIwOp-AwVt3/view?usp=sharing
