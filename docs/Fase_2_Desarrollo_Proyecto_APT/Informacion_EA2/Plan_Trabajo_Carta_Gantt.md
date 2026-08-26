# Plan de Trabajo y Carta Gantt - Fase 2: Desarrollo del Proyecto APT
### Asignatura: Portafolio de Título (APT122) | Semanas 5 a 15

---

## 1. Cronograma de Hitos y Entregables

| Semana | Actividad / Módulo | Responsable | Estado |
| :---: | :--- | :--- | :---: |
| **S5** | Instalación y configuración base de pfSense en entorno Proxmox VE. Segmentación de VLANs (WAN, LAN, DMZ, MGMT). | Bruno Urrea / Freddy Vásquez | **Completado** |
| **S6** | Despliegue de Suricata en pfSense en modo Inline IPS (Netmap) y configuración de reglas Emerging Threats Open. | Bruno Urrea | **Completado** |
| **S7** | Configuración de pfBlockerNG-devel con licencia gratuita MaxMind GeoIP y listas de reputación IP (FireHOL). | Kevin Retamales | **Completado** |
| **S8** | Implementación de HAProxy en pfSense y despliegue del contenedor Docker DVWA en DMZ. | Cristóbal Quezada | **Completado** |
| **S9** | Desarrollo del motor de correlación de logs en Python (`pfctl Engine` y parser de `eve.json`). | Bruno Urrea | **Completado** |
| **S10** | Algoritmo de supresión de falsos positivos y verificación de tabla `snort2c` de FreeBSD `pfctl`. | Bruno Urrea | **Completado** |
| **S11** | Despliegue de Asterisk PBX en contenedor Docker con soporte PJSIP y dialplan de emergencia. | Freddy Vásquez | **Completado** |
| **S12** | Integración del Agente de Voz IA con Gemini Live API (Flash 3.1) mediante WebSockets y audio bidireccional. | Bruno Urrea | **Completado** |
| **S13** | Pruebas integradas de inyección SQL con SQLmap y Burp Suite contra DVWA y validación de trigger de llamada. | Todo el equipo | **Completado** |
| **S14** | Optimización de latencia, afinamiento de prompts para el CISO y recolección de evidencias técnicas. | Todo el equipo | **Completado** |
| **S15** | Consolidación del informe de la Fase 2, preparación de evidencias de avance y sincronización en GitHub. | Todo el equipo | **Completado** |

---

## 2. Diagrama de Flujo de Trabajo (Gantt Conceptual)

```mermaid
gantt
    title Cronograma de Implementación KRONOS SENTINEL (Semanas 5 a 15)
    dateFormat  YYYY-MM-DD
    section Infraestructura & Red
    pfSense & VLANs en Proxmox        :done, s5, 2026-03-01, 7d
    Suricata Inline IPS (Netmap)      :done, s6, 2026-03-08, 7d
    pfBlockerNG & GeoIP MaxMind       :done, s7, 2026-03-15, 7d
    HAProxy & Contenedor DVWA         :done, s8, 2026-03-22, 7d
    section Desarrollo & Correlación
    Motor pfctl & Parser eve.json     :done, s9, 2026-03-29, 7d
    Supresión de Falsos Positivos     :done, s10, 2026-04-05, 7d
    section Telefonía & Agente de Voz
    Asterisk PBX Docker & PJSIP       :done, s11, 2026-04-12, 7d
    Gemini Live API Flash 3.1         :done, s12, 2026-04-19, 7d
    section Testing & Integración
    Simulación de Inyección SQL       :done, s13, 2026-04-26, 7d
    Afinamiento de Latencia y Voice   :done, s14, 2026-05-03, 7d
    Entrega Informe Fase 2            :done, s15, 2026-05-10, 7d
```
