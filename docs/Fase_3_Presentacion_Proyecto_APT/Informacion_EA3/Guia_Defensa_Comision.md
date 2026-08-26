# Guía de Preparación para la Defensa ante la Comisión Evaluadora
### Fase 3: Presentación Proyecto APT (Semanas 16 a 18)
**Proyecto:** KRONOS SENTINEL (Autonomous AI-IPS & Voice SOAR)

---

## 1. Estructura Recomendada de la Presentación (20 Minutos)

```
[00:00 - 03:00]  1. Introducción y Problemática: La crisis de los falsos positivos en SOC y la latencia en notificación.
[03:00 - 07:00]  2. Arquitectura de Red y Perímetro: pfSense, VLANs, pfBlockerNG GeoIP y Suricata Inline IPS (Netmap).
[07:00 - 11:00]  3. Motor de Correlación pfctl: Algoritmo de descarte de ruido y validación en kernel FreeBSD (snort2c).
[11:00 - 16:00]  4. DEMOSTRACIÓN EN VIVO (Live Attack & AI Voice Call):
                 - Inyección SQL simulada contra DVWA vía HAProxy.
                 - Bloqueo instantáneo en pfSense (Drop de paquete).
                 - Asterisk PBX llama en directo al CISO.
                 - Gemini Live API efectúa el debriefing por voz y propone mitigación.
[16:00 - 18:00]  5. Conclusiones, ROI Operacional y Escalabilidad en Infraestructuras OT/IT.
[18:00 - 20:00]  6. Ronda de Preguntas y Respuestas con la Comisión.
```

---

## 2. Checklist Técnico para la Demostración en Vivo
- [ ] Proxmox VE con recursos asignados suficientes (pfSense, DVWA, Asterisk).
- [ ] HAProxy activo y resolviendo peticiones SSL hacia DVWA.
- [ ] Suricata con interfaz WAN/LAN en modo Inline IPS (Netmap).
- [ ] Token de API de Google Gemini (Live API Flash 3.1) configurado y validado.
- [ ] Asterisk PBX registrado con el softphone/móvil del CISO listo para recibir llamada.
- [ ] Terminal con `pfctl -t snort2c -T show` y logs `eve.json` visibles en pantalla secundaria.
