# Resumen Ejecutivo - Fase 1: Definición Proyecto APT
### Asignatura: Portafolio de Título (APT122)
**Institución:** Duoc UC - Sede San Joaquín  
**Carrera:** Ingeniería en Conectividad y Redes  
**Proyecto:** KRONOS SENTINEL (Autonomous AI-IPS & Voice SOAR)

---

## 1. Justificación y Problemática
En la actualidad, los Centros de Operaciones de Seguridad (SOC) y los sistemas de prevención de intrusiones (IPS) convencionales se enfrentan a dos grandes problemas críticos:
1. **Sobrecarga por Falsos Positivos:** Motores tradicionales como Suricata o Snort generan entre un 40% y 60% de alertas ruidosas o firmas genéricas no explotables, saturando las colas de incidentes.
2. **Latencia en la Notificación Crítica:** Cuando ocurre una intrusión real y de alto impacto (por ejemplo, una inyección SQL dirigida a bases de datos corporativas), las alertas por correo electrónico o Slack suelen perderse entre cientos de notificaciones secundarias, retrasando la toma de decisiones por parte del CISO o líder de seguridad.

---

## 2. Propuesta de Solución Tecnológica
**KRONOS SENTINEL** propone una arquitectura de defensa activa en profundidad compuesta por:
* **Perímetro Fortificado:** Firewall **pfSense** con **Suricata en modo Inline IPS (Netmap)** para corte inmediato de flujos maliciosos, combinado con **pfBlockerNG-devel** (GeoIP MaxMind y listas de reputación IP globales).
* **Zona Desmilitarizada (DMZ):** Proxy inverso **HAProxy** con SSL/TLS termination protegiendo aplicaciones web (ej. laboratorio DVWA para validación ética).
* **Motor de Inteligencia y Correlación de Logs (`pfctl Engine`):** Scripting avanzado en Python que correlaciona `eve.json` con el estado en tiempo real de la tabla `snort2c` de FreeBSD `pfctl`, confirmando ataques legítimos bloqueados y descartando escaneos inocuos.
* **Respuesta Autónoma por Voz con IA (SOAR):** Integración con **Asterisk PBX** en contenedor Docker y la API de voz en tiempo real **Gemini Live Flash 3.1**, disparando una llamada telefónica directa al CISO para explicar el vector de ataque, la procedencia geográfica del atacante, el estado de contención y las recomendaciones de mitigación.

---

## 3. Integrantes del Equipo y Roles
* **Bruno Urrea Ortiz:** Arquitectura de Ciberseguridad, Motor de Correlación pfctl e Integración con Gemini Live API.
* **Freddy Vásquez Cortés:** Configuración de Routing, Switching y Telefonía VoIP sobre Asterisk PBX.
* **Cristóbal Quezada:** Administración de Servicios Web, Proxy HAProxy y Laboratorio DVWA.
* **Kevin Retamales:** Políticas de Hardening, Listas de Amenazas pfBlockerNG y Documentación de Calidad.
