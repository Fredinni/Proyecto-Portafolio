# Guía 1. Definición Proyecto APT
### Asignatura: Portafolio de Título (APT122) — Fase 1
**Institución:** Duoc UC — Sede San Joaquín  
**Escuela:** Escuela de Informática y Telecomunicaciones  
**Carrera:** Ingeniería en Conectividad y Redes  
**Estudiante:** Bruno Urrea Ortiz  

---

# A. PARTE I

## 1. Antecedentes Personales

| Campo | Información Solicitada |
| :--- | :--- |
| **Nombre estudiante** | Bruno Urrea Ortiz |
| **Rut** | 21.345.678-9 |
| **Carrera** | Ingeniería en Conectividad y Redes |
| **Sede** | San Joaquín |
| **Integrantes del Equipo (Grupal)** | • Bruno Urrea Ortiz (Líder de Ciberseguridad, Motor KRONOS y Gemini Live)<br>• Freddy Vásquez Cortés (Routing, Switching y Telefonía Asterisk PBX)<br>• Cristóbal Quezada (Servicios Web, HAProxy SSL y DMZ DVWA)<br>• Kevin Retamales (Hardening Perimetral, pfBlockerNG y QA) |

---

## 2. Descripción Proyecto APT

| Campo | Detalle |
| :--- | :--- |
| **Nombre del proyecto** | **KRONOS SENTINEL:** Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture |
| **Área(s) de desempeño** | • Seguridad de la Información, Ciberseguridad Defensiva y Hardening Perimetral.<br>• Infraestructura de Redes Corporativas, Routing y Switching L2/L3 (VLANs 802.1Q).<br>• Telecomunicaciones, Telefonía VoIP SIP/PJSIP y Streaming de Audio en Tiempo Real.<br>• Automatización, Programación en Python e Integración de Inteligencia Artificial (SOAR). |
| **Competencias** | • **Competencia 3:** Adaptar tecnologías de punta y tendencias emergentes de conectividad.<br>• **Competencia 4:** Controlar y operar redes corporativas de gran tamaño.<br>• **Competencia 5:** Unificar servicios de voz, datos y video.<br>• **Competencia 6:** Automatizar procesos y gestión de plataformas de red.<br>• **Competencia 7:** Gestionar la seguridad de la información frente a vulnerabilidades.<br>• **Competencia 8:** Crear planes de prevención y respuesta a riesgos informáticos. |

---

## 3. Fundamentación Proyecto APT

### 3.1 Relevancia del proyecto APT
* **¿Por qué se escogió este tema?** En la industria de la ciberseguridad corporativa moderna, los Centros de Operaciones de Seguridad (SOC) y los firewalls perimetrales enfrentan dos fallas estructurales críticas:
  1. *La crisis de hiper-alerta y falsos positivos:* Los motores de inspección profunda como Suricata o Snort generan más de un 50% de alertas ruidosas e inocuas (escaneos automáticos de puertos, crawlers web y firmas no explotables), saturando las colas de incidentes.
  2. *El colapso cognitivo del operador humano bajo presión:* Ante una intrusión real y de alto impacto (ej. inyecciones SQL masivas o exploits RCE), el analista SOC entra en visión de túnel y pánico, viéndose obligado a investigar y mitigar en la consola del firewall y, al mismo tiempo, redactar reportes o llamar al CISO (Chief Information Security Officer). Al intentar hacer ambas tareas a la vez, se cometen errores de digitación, se bloquea la comunicación verbal y la contención se retrasa críticamente.
* **¿Dónde se ubica la situación?** Se sitúa en infraestructuras corporativas empresariales, entidades financieras, instituciones de educación superior y organizaciones con servicios web expuestos a Internet en Chile y Latinoamérica.
* **¿A quiénes impacta?** Impacta directamente a los equipos de ingeniería de seguridad (SOC Nivel 1/2/3), a los CISOs y decisores estratégicos, y a la continuidad operativa de los servicios digitales corporativos.
* **¿Cuál es el aporte de valor?** KRONOS SENTINEL aporta una solución **SOAR (Security Orchestration, Automation and Response) de Costo Cero ($0 CLP)** que desacopla la contención técnica de la comunicación estratégica: ejecuta la mitigación atómica en el kernel de FreeBSD en microsegundos (<100 ms) y, de forma simultánea, realiza una llamada telefónica interactiva con Inteligencia Artificial conversacional (Google Gemini Live Flash 3.1) para entregar un debriefing táctico hablado en tiempo real (<1.5 s).

### 3.2 Descripción del Proyecto APT
El proyecto consiste en el diseño, implementación y validación de una arquitectura de defensa en profundidad compuesta por:
1. **Perímetro Fortificado:** Firewall **pfSense CE 2.9.0** con **Suricata 7.x en modo Inline IPS (Netmap)** para descarte de paquetes en hardware sin latencia, y **pfBlockerNG-devel** con inteligencia GeoIP MaxMind y listas de reputación global (FireHOL, Spamhaus).
2. **Capa Web DMZ:** Proxy inverso **HAProxy 2.8+** con SSL Offloading (puerto 443) y *Stick-Tables* dinámicas en RAM para mitigación de DoS/Fuzzing L7, protegiendo un laboratorio vulnerable controlado (**DVWA** en Docker, VLAN 20).
3. **Motor de Correlación KRONOS (Python 3.12):** Daemon asíncrono que ingesta `eve.json`, suprime más del 50% de falsos positivos mediante análisis sintáctico AST de payloads SQLi/RCE y utiliza **`pfctl`** (la herramienta de kernel de FreeBSD) para terminar estados activos (`pfctl -k`) y verificar la tabla dinámica `<snort2c>`.
4. **Respuesta Telefónica Autónoma SOAR:** Centralita **Asterisk 20 LTS** en Docker que ejecuta un auto-dialer AMI hacia el softphone del CISO, conectando el flujo de audio RTP con **Google Gemini Live Flash 3.1** mediante WebSocket para interactuar por voz en lenguaje natural.

### 3.3 Pertinencia del proyecto con el perfil de egreso
El proyecto integra de forma armónica las 4 áreas troncales de la carrera de Ingeniería en Conectividad y Redes:
* **Networking & Switching:** Segmentación L2/L3 en 4 VLANs (Corp 10, DMZ 20, VoIP 30, Mgmt 99) sobre troncal 802.1Q.
* **Seguridad Perimetral:** Hardening de kernel FreeBSD, configuración de reglas Zero Trust, listas de amenazas y prevención IPS Inline.
* **Telefonía VoIP:** Despliegue de centralita Asterisk PBX, protocolo SIP/PJSIP, Dialplans y códecs de audio en tiempo real.
* **Automatización y Programación:** Desarrollo de software en Python, manejo de sockets IPC, parsing estructurado JSON y consumo de APIs de IA generativa multimodal.

### 3.4 Relación con los intereses profesionales
KRONOS SENTINEL se alinea directamente con mi meta profesional de desempeñarme como **Ingeniero de Ciberseguridad / Arquitecto de Infraestructura y SecOps**, especializándome en arquitecturas Zero Trust, mitigación perimetral y automatización de respuesta ante incidentes. Asimismo, consolida la experiencia técnica adquirida liderando el equipo de competiciones CTF **DevSec** y en despliegues tecnológicos de alta concurrencia.

### 3.5 Factibilidad de desarrollo del Proyecto APT
* **(1) Duración del semestre:** 18 semanas académicas planificadas cronológicamente.
* **(2) Horas asignadas:** 72 horas presenciales de taller de titulación más 144 horas de trabajo autónomo en laboratorio.
* **(3) Materiales requeridos:** Arquitectura 100% de Costo Cero ($0 CLP), basada en software libre y código abierto (FreeBSD, pfSense CE, Suricata, Asterisk, Docker, Python) y capas gratuitas comunitarias (Google AI Studio Free Tier para Gemini Live, MaxMind Free Tier).
* **(4) Factores externos que facilitan el desarrollo:** Disponibilidad de laboratorios en Duoc UC San Joaquín, soporte multiplataforma de virtualización (Proxmox VE / VMware) y documentación oficial de Netgate.
* **(5) Factores externos que dificultan y solución:**
  * *Dificultad:* Presencia de CGNAT o bloqueo de puertos entrantes en redes residenciales o institucionales.
  * *Solución Técnica:* Implementación de malla VPN Zero Trust con **Tailscale Subnet Router**, permitiendo que el softphone del CISO acceda a la subred de telefonía (`192.168.30.0/24`) mediante túnel WireGuard saliente sin requerir IP pública fija ni apertura de puertos NAT.

---

# B. PARTE II

## 4. Objetivos

### 4.1 Objetivo General
Diseñar, implementar y validar una arquitectura de defensa en profundidad y respuesta autónoma ante incidentes (SOAR) de costo cero ($0 CLP) denominada **KRONOS SENTINEL**, integrando prevención de intrusiones en kernel, supresión heurística de falsos positivos y notificación interactiva por voz en tiempo real con Inteligencia Artificial hacia los responsables de seguridad (CISO).

### 4.2 Objetivos Específicos
1. **Diseñar e implementar la infraestructura perimetral de red** en pfSense CE 2.9.0 mediante troncal 802.1Q y segmentación en 4 VLANs (Corporativa, DMZ, VoIP y Gestión SecOps).
2. **Configurar el motor de prevención de intrusiones Suricata 7.x en modo Inline IPS** sobre framework Netmap con firmas ET Open y reglas automáticas `dropsid.conf` para el descarte de tráfico malicioso en hardware sin latencia.
3. **Implementar el proxy inverso HAProxy 2.8+ con terminación SSL/TLS** y *Stick-Tables* de control de tasa L7, protegiendo y publicando el servidor web de pruebas vulnerables DVWA en la DMZ.
4. **Desarrollar en Python 3.12 el Motor de Correlación KRONOS** con parser de `eve.json` y algoritmo heurístico AST para suprimir más del 50% de falsos positivos en vectores SQLi y RCE.
5. **Integrar el control atómico de estados y tablas en kernel de FreeBSD** mediante la herramienta `pfctl`, ejecutando la terminación inmediata de conexiones hostiles (`pfctl -k`) y verificación de la tabla `<snort2c>`.
6. **Desplegar la centralita de telefonía Asterisk 20 LTS en Docker** con canal PJSIP y módulo auto-dialer AMI (`Originate`) para el timbrado prioritario al softphone móvil del CISO.
7. **Desarrollar el bridge de audio por WebSocket hacia Google Gemini Live Flash 3.1**, permitiendo la entrega de un debriefing hablado en lenguaje natural y la interlocución táctica en vivo.
8. **Validar la efectividad y rendimiento de la arquitectura completa** mediante matrices de pruebas funcionales de aseguramiento de calidad (QA) y auditoría de tiempos de respuesta (<1.5 s).

---

## 5. Metodología

### 5.1 Descripción de la Metodología
Se utilizará una **Metodología de Ingeniería en Ciclo Iterativo e Incremental**, estructurada en 4 etapas operativas con control de calidad continuo:
1. **Etapa 1 (Diseño y Topología de Red):** Modelamiento de direccionamiento IP, troncales VLAN 802.1Q y hardening base de pfSense CE 2.9.0.
2. **Etapa 2 (Seguridad Perimetral y DMZ):** Despliegue de Suricata Netmap Inline IPS, pfBlockerNG GeoIP, HAProxy SSL y contenedor DVWA.
3. **Etapa 3 (Desarrollo del Motor KRONOS y Telefonía IA):** Programación en Python 3.12 del analizador AST, wrappers `pfctl`, contenedor Asterisk PBX y WebSocket de Gemini Live API.
4. **Etapa 4 (Integración SOAR, QA y Validación de Campo):** Pruebas de inyección SQL en vivo, auditoría de tiempos de latencia, ajuste de umbrales heurísticos y compilación de documentación técnica.

### 5.2 Funciones, Tareas y Responsabilidades del Equipo
* **Bruno Urrea Ortiz (Líder de Ciberseguridad & Motor KRONOS):** Arquitectura global, desarrollo del Motor de Correlación KRONOS (`log_correlator.py`), algoritmo AST de supresión de falsos positivos (`false_positive_filter.py`), control de kernel FreeBSD `pfctl` e integración WebSocket con Gemini Live Flash 3.1.
* **Freddy Vásquez Cortés (Ingeniero de Routing, Switching & VoIP):** Configuración de troncal 802.1Q, direccionamiento de VLANs en pfSense, despliegue de centralita Asterisk 20 LTS en Docker (`pjsip.conf`, `extensions.conf`), auto-dialer AMI (`call_trigger.py`) y enrutamiento Tailscale.
* **Cristóbal Quezada (Administrador de Servicios Web & DMZ):** Configuración de HAProxy 2.8+ con terminación HTTPS 443, diseño de *Stick-Tables* anti-fuzzing L7 y administración del contenedor vulnerable de pruebas DVWA en VLAN 20.
* **Kevin Retamales (Especialista en Hardening, Threat Intelligence & QA):** Hardening de políticas de firewall Zero Trust en pfSense, configuración de pfBlockerNG-devel (MaxMind GeoLite2 y listas FireHOL/Spamhaus) y diseño/ejecución de matrices de prueba QA de extremo a extremo.

---

## 6. Evidencias

| Tipo de Evidencia | Nombre de la Evidencia | Descripción | Justificación |
| :--- | :--- | :--- | :--- |
| **Avance (Fase 1)** | Informe de Definición y Topología de Red | Documento técnico formal con diseño de direccionamiento IP, matriz de VLANs y arquitectura perimetral. | Valida la correcta planificación de la infraestructura L2/L3 y el marco metodológico inicial. |
| **Avance (Fase 2)** | Repositorio Git de Código Fuente e IaC | Repositorio GitHub con código del Motor KRONOS, Dockerfiles de Asterisk/DVWA y configs de pfSense. | Demuestra el avance tangible en desarrollo de software, integración de APIs y automatización de red. |
| **Avance (Fase 2)** | Manuales Técnicos y Mockups en PDF | Manual de configuración de pfSense CE 2.9.0 y Tutorial Paso a Paso de 8 páginas con WebGUI cards. | Acredita la reproducibilidad y rigurosidad técnica de los procedimientos de hardening perimetral. |
| **Final (Fase 3)** | Demostración en Vivo de Intrusión y Respuesta SOAR | Ejecución de inyección SQL en DVWA ➔ Bloqueo en kernel FreeBSD (`snort2c`) ➔ Llamada telefónica de voz con Gemini Live en altavoz. | Evidencia concluyente de la efectividad de la solución y cumplimiento del objetivo general ante la comisión. |
| **Final (Fase 3)** | Matrices de Pruebas de Calidad (QA) y Logs Forenses | Registros EVE JSON de Suricata, salidas de consola `pfctl -t snort2c -T show` y métricas de latencia (<1.5 s). | Respaldan con datos empíricos la supresión de falsos positivos y la robustez del filtrado en kernel. |
| **Final (Fase 3)** | Informe Final Consolidado y Presentación Ejecutiva | Documento consolidado del proyecto y diapositivas de defensa para examen de título. | Entrega formal académica exigida por la pauta de evaluación de Portafolio de Título (APT122). |

---

## 7. Plan de Trabajo

| Competencia | Nombre de Actividad | Descripción de Tarea | Recursos | Duración | Responsable | Observaciones |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Comp. 4 & 8** | A1. Diseño y Setup Base pfSense | Instalación de pfSense CE 2.9.0, configuración WAN/LAN y tuning de hardware offloading para Netmap. | Hipervisor, ISO pfSense CE 2.9.0 | Semanas 1 - 2 | Bruno Urrea / Freddy Vásquez | Crucial desactivar TSO/LRO para estabilidad de Netmap. |
| **Comp. 4** | A2. Segmentación de VLANs 802.1Q | Creación de subredes VLAN 10 (Corp), 20 (DMZ), 30 (VoIP) y 99 (Mgmt) y servidores DHCP locales. | pfSense WebGUI, Switch L2 virtual | Semanas 3 - 4 | Freddy Vásquez | Se aplican reservas MAC estáticas para servidores. |
| **Comp. 7 & 8** | A3. Despliegue de Suricata Inline IPS | Instalación de Suricata 7.x, activación de modo Inline Netmap, reglas ET Open y configuración `dropsid.conf`. | Paquete pfSense Suricata, feeds ET Open | Semanas 5 - 6 | Bruno Urrea / Kevin Retamales | Bloqueo en hardware ring-buffer sin latencia. |
| **Comp. 7 & 8** | A4. Hardening GeoIP con pfBlockerNG | Configuración de cuenta MaxMind Free, bloqueo Top Spammers y feeds FireHOL L1 / Spamhaus DROP. | pfBlockerNG-devel, MaxMind GeoLite2 | Semanas 7 - 8 | Kevin Retamales | Reglas flotantes prioritarias en WAN. |
| **Comp. 7** | A5. Proxy Inverso HAProxy & DVWA | Configuración de Frontend HTTPS VIP 443, SSL Offloading, Stick-Tables anti-fuzzing y contenedor DVWA. | HAProxy package, Docker, DVWA image | Semanas 9 - 10 | Cristóbal Quezada | Aislamiento estricto de DVWA en VLAN 20 DMZ. |
| **Comp. 6 & 8** | A6. Motor de Correlación KRONOS | Programación en Python 3.12 del parser `eve.json`, filtro heurístico AST y wrapper de kernel FreeBSD `pfctl`. | Python 3.12, PyYAML, FreeBSD CLI | Semanas 11 - 12 | Bruno Urrea | Suprime >50% de ruido y ejecuta `pfctl -k`. |
| **Comp. 5** | A7. Centralita VoIP Asterisk PBX | Construcción de imagen Docker Asterisk 20 LTS, configuración de `pjsip.conf`, `extensions.conf` y auto-dialer AMI. | Docker Engine, Asterisk 20 LTS, AMI | Semanas 13 - 14 | Freddy Vásquez | Timbrado prioritario a softphone PJSIP/1001. |
| **Comp. 3 & 5** | A8. Integración Gemini Live Voice | Desarrollo de cliente WebSocket seguro, diseño de System Prompts tácticos y conexión de audio PCM con Asterisk. | Google AI Studio API Key, Python websockets | Semanas 14 - 15 | Bruno Urrea | Diálogo interactivo bidireccional de voz. |
| **Comp. 3 & 4** | A9. Enlace Zero Trust Tailscale | Publicación de subred VoIP `192.168.30.0/24` en Tailscale para softphones móviles remotos sin abrir puertos. | Tailscale package, WireGuard mesh | Semana 15 | Freddy Vásquez | Evade restricciones de CGNAT en sedes. |
| **Comp. 7, 8 & 11** | A10. Pruebas QA, Auditoría & Defensa | Ejecución de matrices de prueba de penetración, medición de tiempos (<1.5 s), manuales PDF y preparación de defensa. | Repositorio GitHub, softphone, ReportLab | Semanas 16 - 18 | Todo el Equipo | Validación final y presentación ante comisión. |

---

## 8. Carta Gantt

| Actividad / Hito | Fase 1 (S1-S4) | | | | Fase 2 (S5-S15) | | | | | | | | | | | Fase 3 (S16-S18) | | |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| | **S1** | **S2** | **S3** | **S4** | **S5** | **S6** | **S7** | **S8** | **S9** | **S10** | **S11** | **S12** | **S13** | **S14** | **S15** | **S16** | **S17** | **S18** |
| **A1. Setup Base pfSense & Tuning** | **X** | **X** | | | | | | | | | | | | | | | | |
| **A2. Segmentación VLANs 802.1Q** | | | **X** | **X** | | | | | | | | | | | | | | |
| **A3. Suricata Inline Netmap IPS** | | | | | **X** | **X** | | | | | | | | | | | | |
| **A4. Hardening GeoIP pfBlockerNG** | | | | | | | **X** | **X** | | | | | | | | | | |
| **A5. HAProxy SSL & Laboratorio DVWA**| | | | | | | | | **X** | **X** | | | | | | | | |
| **A6. Motor de Correlación KRONOS**| | | | | | | | | | | **X** | **X** | | | | | | |
| **A7. Telefonía Asterisk PBX & AMI** | | | | | | | | | | | | | **X** | **X** | | | | |
| **A8. Integración Gemini Live Voice** | | | | | | | | | | | | | | **X** | **X** | | | |
| **A9. Malla Zero Trust Tailscale** | | | | | | | | | | | | | | | **X** | | | |
| **A10. Pruebas QA, Auditoría & Defensa**| | | | | | | | | | | | | | | | **X** | **X** | **X** |
