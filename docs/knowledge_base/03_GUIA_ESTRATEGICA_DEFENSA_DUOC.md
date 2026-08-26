# BASE DE CONOCIMIENTO GENERAL: GUÍA ESTRATÉGICA DE DEFENSA PRESENCIAL DUOC UC
## Guion Táctico, Distribución de Vocería y Protocolo de Demostración en Vivo
**Institución:** Duoc UC Sede San Joaquín — Escuela de Informática y Telecomunicaciones  
**Asignatura:** Portafolio de Título (APT122) — Proyecto KRONOS SENTINEL

---

## 1. ESTRUCTURA DE TIEMPOS Y VOCERÍA EN LA DEFENSA (15-20 MINUTOS)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CRONOGRAMA DE LA DEFENSA PRESENCIAL                                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [MIN 00-04] ➔ INTRODUCCIÓN & PROBLEMÁTICA (Bruno Urrea): El colapso del factor humano y falsos +│
│ [MIN 04-07] ➔ TOPOLOGÍA DE RED Y TELEFONÍA (Freddy Vásquez): VLANs 802.1Q, Asterisk y Tailscale │
│ [MIN 07-10] ➔ CAPA WEB & HARDENING (Cristóbal Quezada & Kevin Retamales): HAProxy, DVWA, GeoIP  │
│ [MIN 10-14] ➔ DEMOSTRACIÓN EN VIVO (Todo el Equipo): Inyección SQL real ➔ Llamada de Voz IA     │
│ [MIN 14-20] ➔ RONDA DE PREGUNTAS DE LA COMISIÓN EVALUADORA                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. GUION DE LA DEMOSTRACIÓN EN VIVO (PASO A PASO)

1. **Paso 1 (Pantalla del Atacante - Cristóbal / Kevin):**
   * Se proyecta la consola del atacante y el navegador con DVWA (`https://198.51.100.1/dvwa/`).
   * Se introduce el payload malicioso de inyección SQL:
     ```sql
     admin' OR '1'='1 --
     ```
2. **Paso 2 (Pantalla del Firewall y Kernel - Bruno):**
   * Se muestra la terminal SSH de pfSense ejecutando:
     ```bash
     tail -f /var/log/suricata/eve.json | jq .
     pfctl -t snort2c -T show
     ```
   * La comisión observa cómo la IP atacante entra instantáneamente a la tabla `<snort2c>` y la conexión es bloqueada en 0 milisegundos.
3. **Paso 3 (Teléfono del CISO en Altavoz - Freddy):**
   * El teléfono móvil del CISO colocado en la mesa de la comisión comienza a timbrar (`Llamada entrante: KRONOS SENTINEL AI`).
   * Freddy descuelga y pone el altavoz.
   * La voz de **Gemini Live Flash 3.1** se escucha con total claridad:
     > *"Alerta de Seguridad Nivel Crítico. Se ha detectado y neutralizado un intento de SQL Injection dirigido al servidor web DMZ. Dirección IP atacante 185.220.101.5 proveniente de Rusia, bloqueada en el kernel de FreeBSD. Se sugiere mantener el monitoreo en la tabla snort2c."*
4. **Paso 4 (Interacción por Voz en Vivo - Bruno):**
   * Bruno le habla directamente al teléfono: *"Gemini, ¿la tabla snort2c tiene conexiones residuales?"*
   * Gemini responde en tiempo real: *"El motor pfctl ha purgado todos los estados TCP activos. El perímetro se encuentra asegurado."*
5. **Cierre de la Demostración:**
   * La comisión comprueba que todo el ciclo se ejecutó de forma 100% autónoma, sin fallos y a costo \$0 CLP.

---

## 3. REGLAS DE ORO PARA EL EQUIPO

1. **Nunca contradecirse:** Si un profesor le pregunta a uno, los otros complementan con datos técnicos de su área.
2. **Defender la filosofía de Costo Cero ($0 CLP):** Enfatizar siempre que no se utilizaron licencias comerciales pagadas, sino ingeniería pura con software libre y capas comunitarias.
3. **Destacar la innovación del Factor Humano:** Remarcar que el proyecto no es solo un firewall, sino una **plataforma SOAR con IA de voz** que protege al analista del colapso cognitivo en momentos de crisis.
