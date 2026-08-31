# Guía 1. Definición Proyecto APT
### Asignatura: Portafolio de Título (APT122) — Asignatura Capstone (Fase 1)
**Institución:** Duoc UC — Sede San Joaquín  
**Escuela:** Escuela de Informática y Telecomunicaciones  
**Carrera:** Ingeniería en Conectividad y Redes  
**Estudiante:** Bruno Urrea Ortiz  
**RUT:** 21.543.637-3  
**Docente Guía:** Comisión Evaluadora APT122  
**Fecha:** Septiembre 2026  

---

## Índice de Contenidos
1. [Portada Institucional](#portada-institucional)
2. [A. PARTE I](#a-parte-i)
   - [1. Antecedentes Personales](#1-antecedentes-personales)
   - [2. Descripción Proyecto APT](#2-descripción-proyecto-apt)
   - [3. Fundamentación Proyecto APT](#3-fundamentación-proyecto-apt)
     - [3.1 Relevancia del proyecto APT](#31-relevancia-del-proyecto-apt)
     - [3.2 Descripción del Proyecto APT](#32-descripción-del-proyecto-apt)
     - [3.3 Pertinencia del proyecto con el perfil de egreso](#33-pertinencia-del-proyecto-con-el-perfil-de-egreso)
     - [3.4 Relación con los intereses profesionales](#34-relación-con-los-intereses-profesionales)
     - [3.5 Factibilidad de desarrollo del Proyecto APT](#35-factibilidad-de-desarrollo-del-proyecto-apt)
3. [B. PARTE II](#b-parte-ii)
   - [4. Objetivos](#4-objetivos)
     - [4.1 Objetivo General](#41-objetivo-general)
     - [4.2 Objetivos Específicos (Formulados como Acciones)](#42-objetivos-específicos-formulados-como-acciones)
   - [5. Metodología](#5-metodología)
     - [5.1 Descripción de la Metodología](#51-descripción-de-la-metodología)
     - [5.2 Funciones, Tareas y Responsabilidades del Equipo](#52-funciones-tareas-y-responsabilidades-del-equipo)
   - [6. Evidencias (Tabla Oficial)](#6-evidencias)
   - [7. Plan de Trabajo (Tabla Oficial con Recursos y Factores)](#7-plan-de-trabajo)
   - [8. Carta Gantt (18 Semanas Académicas)](#8-carta-gantt)

---

# A. PARTE I

## 1. Antecedentes Personales
A continuación, se presenta la tabla en la que se completa la información solicitada:

| Campo | Información Solicitada |
| :--- | :--- |
| **Nombre estudiante** | Bruno Urrea Ortiz |
| **Rut** | 21.543.637-3 |
| **Carrera** | Ingeniería en Conectividad y Redes |
| **Sede** | San Joaquín |
| **Integrantes del Equipo (Grupal)** | • **Bruno Urrea Ortiz:** Líder de Ciberseguridad, Motor KRONOS y Gemini Live API.<br>• **Freddy Vásquez Cortés:** Ingeniería de Routing, Switching perimetral y Telefonía Asterisk PBX.<br>• **Cristóbal Quezada:** Administración de Servicios Web, Proxy Inverso HAProxy y DMZ.<br>• **Kevin Retamales:** Hardening Perimetral, Inteligencia pfBlockerNG y Control de Calidad QA. |

---

## 2. Descripción Proyecto APT
En la descripción se señala brevemente el nombre del proyecto APT, las áreas de desempeño y las competencias del perfil de egreso que se ponen en práctica:

| Campo | Detalle |
| :--- | :--- |
| **Nombre del proyecto** | **KRONOS SENTINEL:** Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture |
| **Área(s) de desempeño** | • **Seguridad de Sistemas y Redes:** Ciberseguridad Defensiva, Hardening Perimetral y Prevención de Intrusiones (IPS).<br>• **Administración de Redes y Telecomunicaciones:** Infraestructura Corporativa L2/L3 y Segmentación en VLANs 802.1Q.<br>• **Comunicación Unificada y Corporativa:** Telefonía IP Asterisk (PJSIP), Dialplans y Streaming de Voz en Tiempo Real.<br>• **Análisis de Soluciones de Conectividad:** Automatización en Python 3.12, Orquestación SOAR e Inteligencia Artificial Multimodal. |
| **Competencias** | • **Competencia 8:** Crear planes de prevención y respuesta a riesgos informáticos en la red de acuerdo con estándares, normativas y buenas prácticas de la industria.<br>• **Competencia 6:** Automatizar procesos y gestión de plataformas de red mediante programación y scripting avanzado.<br>• **Competencia 5:** Unificar servicios de voz, datos y video en redes de clientes asegurando calidad de servicio (QoS) y convergencia tecnológica.<br>• **Competencia 4:** Controlar y operar redes corporativas de gran tamaño manteniendo la continuidad operativa y alta disponibilidad.<br>• **Competencia 3:** Adaptar tecnologías de punta y tendencias tecnológicas emergentes para resolver necesidades de innovación organizacional.<br>• **Competencia 7:** Gestionar la seguridad de la información frente a vulnerabilidades en aplicaciones y servicios de red. |

---

## 3. Fundamentación Proyecto APT

| Campo | Detalle y Justificación |
| :--- | :--- |
| **Relevancia del proyecto APT** | **¿Por qué se escogió este tema y cuál es su relevancia laboral?**<br>En los Centros de Operaciones de Seguridad (SOC) modernos existen dos fallas críticas:<br>1. *Crisis de hiper-alerta y falsos positivos (>50%):* Los motores de inspección profunda tradicionales (Suricata/Snort) saturan al analista con alertas inocuas.<br>2. *Colapso cognitivo del operador bajo ataque crítico:* Ante una intrusión grave (SQLi/RCE), el operador entra en visión de túnel al intentar aislar el firewall por CLI y redactar reportes al CISO simultáneamente, provocando demoras de horas y errores de tipeo.<br><br>**¿Dónde se ubica la situación?**<br>En datacenters corporativos, entidades financieras, plataformas web expuestas e infraestructuras empresariales de Chile y Latinoamérica.<br><br>**¿A quiénes afecta o impacta?**<br>Impacta a Analistas SOC N1/N2/N3, CISOs, Directores de TI y a la continuidad del negocio corporativo.<br><br>**¿Cuál es el aporte de valor?**<br>KRONOS SENTINEL aporta una solución SOAR de Costo Cero ($0 CLP) que desacopla la contención técnica atómica en kernel de FreeBSD (<100 ms) de la comunicación estratégica mediante llamadas telefónicas con Inteligencia Artificial conversacional (Gemini Live Flash 3.1) en tiempo real (<1.5 s). |
| **Descripción del Proyecto APT** | **Propósito Central y Enfoque Metodológico:**<br>Diseñar, implementar y validar una arquitectura de defensa en profundidad de 4 pilares tecnológicos:<br>1. *Perímetro Fortificado:* Firewall **pfSense CE 2.9.0** con **Suricata 7.x Inline IPS (Netmap)** para descarte de paquetes en hardware sin latencia, más **pfBlockerNG-devel** con inteligencia GeoIP MaxMind y listas FireHOL.<br>2. *Capa Web DMZ:* Proxy inverso **HAProxy 2.8+** con terminación SSL/TLS (puerto 443) y *Stick-Tables* anti-fuzzing L7 protegiendo el entorno vulnerable controlado (**DVWA** en Docker, VLAN 20).<br>3. *Motor de Correlación KRONOS (Python 3.12):* Daemon asíncrono que ingesta `eve.json`, suprime >50% de falsos positivos mediante analizador sintáctico AST y ejecuta la herramienta de kernel de FreeBSD **`pfctl`** para terminar estados hostiles (`pfctl -k`) y verificar la tabla `<snort2c>`.<br>4. *Respuesta Telefónica Autónoma SOAR:* Centralita **Asterisk 20 LTS** en Docker con módulo AMI (`Originate`) que timbra al softphone del CISO y conecta el flujo de audio RTP con **Google Gemini Live Flash 3.1** mediante WebSocket bidireccional (PCM 24kHz). |
| **Pertinencia del proyecto con el perfil de egreso** | El proyecto articula de forma rigurosa las 4 áreas troncales de la carrera:<br>• **Networking L2/L3:** Segmentación en 4 VLANs 802.1Q (Corp 10, DMZ 20, VoIP 30, Mgmt 99), direccionamiento CIDR y conmutación.<br>• **Seguridad Perimetral:** Hardening de kernel Unix/FreeBSD, reglas Zero Trust, inspección profunda Netmap e inteligencia de amenazas.<br>• **Telefonía VoIP:** Despliegue de centralita Asterisk PBX, protocolo SIP/PJSIP, códecs de audio y enlaces telefónicos en tiempo real.<br>• **Automatización y Programación:** Desarrollo de software en Python, manejo de sockets IPC, parsing estructurado JSON y consumo de APIs de IA Generativa. |
| **Relación con los intereses profesionales** | **¿Cuáles son tus intereses profesionales?**<br>Especialización en Ciberseguridad Defensiva (Blue Team), Arquitectura de Seguridad Perimetral, Hardening de Sistemas Unix/FreeBSD y Sistemas Autónomos de Orquestación y Respuesta ante Incidentes (SOAR).<br><br>**¿Qué aspectos se ven reflejados en el Proyecto APT?**<br>El diseño de infraestructuras Zero Trust, la mitigación atómica de ataques en kernel, el análisis heurístico de tráfico malicioso y la integración de IA generativa aplicada a operaciones de seguridad.<br><br>**¿Cómo contribuye a tu desarrollo profesional?**<br>Permite proyectar mi inserción laboral hacia cargos como Ingeniero de Ciberseguridad / Arquitecto SecOps en SOC corporativos o liderar equipos de respuesta ante amenazas APT, acreditando dominio práctico de tecnologías Enterprise de costo cero ($0 CLP) y alineación con certificaciones internacionales (Cisco CCNA, CompTIA Security+, NIST SP 800-207). |
| **Factibilidad de desarrollo del Proyecto APT** | **Acotación del Alcance a 18 Semanas con el Equipo Disponible:**<br>• *(1) Duración del semestre:* 18 semanas académicas cronogramadas en 4 fases de trabajo.<br>• *(2) Horas asignadas:* 72 horas presenciales de taller de titulación + 144 horas de laboratorio autónomo = 216 horas por integrante (864 horas de ingeniería grupal total).<br>• *(3) Materiales requeridos ($0 CLP):* 100% Open Source y capas comunitarias gratuitas (FreeBSD 14, pfSense CE 2.9.0, Suricata 7.x, HAProxy 2.8, Asterisk 20 LTS, Docker, Python 3.12, Google AI Studio Free Tier, MaxMind GeoLite2). Cero costo de licenciamiento comercial.<br>• *(4) Factores que facilitan el desarrollo:* Plataforma de virtualización Proxmox VE bare-metal / VMware, laboratorios de redes Duoc UC San Joaquín y modularidad de la arquitectura.<br>• *(5) Factores que dificultan y soluciones:*<br>   - *Dificultad:* Bloqueo de puertos o CGNAT en redes institucionales/remotas.<br>   - *Solución:* Malla VPN Zero Trust con **Tailscale Subnet Router** (túnel WireGuard) para acceder a la subred VoIP `192.168.30.0/24` sin requerir IP pública fija.<br>   - *Dificultad:* Saturación de llamadas por falsos positivos.<br>   - *Solución:* Filtro heurístico AST que exige confirmación atómica en la tabla `<snort2c>` antes de activar el auto-dialer AMI.<br>   - *Dificultad:* Latencia en respuesta de voz.<br>   - *Solución:* Conexión WebSocket directa PCM 24kHz con Gemini Live Flash 3.1 (<400 ms). |

---

# B. PARTE II

## 4. Objetivos

### 4.1 Objetivo General
Diseñar, implementar y validar una arquitectura de defensa en profundidad y respuesta autónoma ante incidentes (SOAR) de costo cero ($0 CLP) denominada **KRONOS SENTINEL**, integrando prevención de intrusiones en kernel, supresión heurística de falsos positivos e interlocución telefónica interactiva por voz en tiempo real con Inteligencia Artificial hacia los responsables de seguridad (CISO).

### 4.2 Objetivos Específicos (Formulados como Acciones)
1. **Diseñar** la topología lógica y física de red perimetral y el esquema de direccionamiento CIDR segmentado en 4 VLANs 802.1Q (Corporativa, DMZ, VoIP y Gestión) en pfSense CE 2.9.0.
2. **Implementar** la configuración del cortafuegos perimetral pfSense CE 2.9.0 con políticas Zero Trust, reglas de aislamiento entre subredes y optimización de hardware offloading para Netmap.
3. **Configurar** el motor de detección y prevención de intrusiones Suricata 7.x en modo Inline IPS sobre framework Netmap con firmas ET Open y reglas automáticas `dropsid.conf` para el descarte de paquetes maliciosos en hardware ring-buffer.
4. **Implementar** el filtrado geográfico y reputacional de amenazas con pfBlockerNG-devel utilizando bases de datos MaxMind GeoLite2 y listas de bloqueo global FireHOL L1 y Spamhaus DROP.
5. **Configurar** el proxy inverso HAProxy 2.8+ con terminación segura SSL/TLS (puerto 443) y *Stick-Tables* de control de tasa L7 en memoria RAM, protegiendo y publicando el servidor web de pruebas vulnerables DVWA en la DMZ.
6. **Desarrollar** en Python 3.12 el Motor de Correlación KRONOS con analizador estructurado de logs `eve.json` y algoritmo heurístico AST para suprimir más del 50% de falsos positivos en vectores de inyección SQL (SQLi) y ejecución remota de comandos (RCE).
7. **Integrar** el control atómico de estados y tablas en el kernel de FreeBSD mediante la herramienta de sistema `pfctl`, ejecutando la terminación inmediata de sesiones activas (`pfctl -k`) y verificando la persistencia del atacante en la tabla dinámica `<snort2c>`.
8. **Desplegar** la centralita de telefonía IP Asterisk 20 LTS en contenedor Docker con canal PJSIP, configuración de Dialplans y módulo auto-dialer AMI (`Originate`) para el timbrado prioritario al softphone del CISO.
9. **Construir** el puente de audio bidireccional por WebSocket hacia Google Gemini Live Flash 3.1 (PCM 24kHz), permitiendo la entrega de un debriefing táctico hablado en lenguaje natural y la recepción de instrucciones de respuesta por voz.
10. **Validar** el rendimiento, la latencia total de respuesta (<1.5 s) y la efectividad de la arquitectura completa mediante la ejecución de matrices de pruebas de aseguramiento de calidad (QA) y simulación de ataques en vivo.

---

## 5. Metodología

### 5.1 Descripción de la Metodología
Se aplicará una **Metodología de Ingeniería en Ciclo Iterativo e Incremental**, estructurada en 4 etapas operativas con control de calidad y pruebas de regresión continuas:
* **Etapa 1: Levantamiento, Diseño y Topología de Red (Semanas 1 a 4):** Modelamiento de direccionamiento IP, matriz de VLANs 802.1Q, hardening base del sistema operativo FreeBSD y configuración inicial de pfSense CE 2.9.0.
* **Etapa 2: Implementación de Perímetro y Capa Web DMZ (Semanas 5 a 10):** Despliegue de Suricata Inline Netmap IPS, configuración de pfBlockerNG GeoIP, parametrización de HAProxy SSL con Stick-Tables y puesta en marcha del laboratorio DVWA en Docker.
* **Etapa 3: Desarrollo de KRONOS, Telefonía PBX y Voz IA (Semanas 11 a 15):** Programación en Python 3.12 del analizador AST, creación de wrappers `pfctl`, construcción de imagen Docker Asterisk 20 LTS, desarrollo del auto-dialer AMI y bridge WebSocket de Gemini Live API.
* **Etapa 4: Pruebas de Integración QA, Documentación y Defensa (Semanas 16 a 18):** Pruebas de penetración SQLi en vivo, medición de tiempos de respuesta (<1.5 s), generación de manuales técnicos PDF y preparación de la presentación ejecutiva ante la comisión.

### 5.2 Funciones, Tareas y Responsabilidades del Equipo
* **Bruno Urrea Ortiz (Líder de Ciberseguridad, Motor KRONOS y Gemini Live):**
  - Dirección arquitectónica y diseño de la solución SOAR.
  - Desarrollo del Motor de Correlación KRONOS (`log_correlator.py`) y del filtro sintáctico AST (`false_positive_filter.py`).
  - Implementación de wrappers de kernel FreeBSD con `pfctl` (`pfctl_wrapper.py`).
  - Integración del cliente WebSocket seguro hacia Google Gemini Live Flash 3.1 (`gemini_live_client.py`).
* **Freddy Vásquez Cortés (Ingeniero de Routing, Switching y Telefonía Asterisk PBX):**
  - Configuración de la troncal 802.1Q y direccionamiento de subredes VLAN en pfSense.
  - Despliegue y hardening de la centralita Asterisk 20 LTS en Docker (`pjsip.conf`, `extensions.conf`).
  - Desarrollo del script auto-dialer AMI (`call_trigger.py`).
  - Configuración del enrutamiento VPN Zero Trust con Tailscale Subnet Router.
* **Cristóbal Quezada (Administrador de Servicios Web, Proxy HAProxy y DMZ):**
  - Configuración del frontend y backend de HAProxy 2.8+ con terminación HTTPS 443.
  - Parametrización de *Stick-Tables* de rate-limiting anti-fuzzing L7 en memoria RAM.
  - Despliegue, aislamiento y administración del contenedor vulnerable DVWA en VLAN 20 DMZ.
  - Hardening de protocolos TLS y auditoría de certificados SSL.
* **Kevin Retamales (Hardening Perimetral, Inteligencia pfBlockerNG y Control de Calidad QA):**
  - Hardening de políticas Zero Trust en pfSense y reglas de firewall flotantes.
  - Configuración de feeds de inteligencia de amenazas pfBlockerNG-devel (MaxMind GeoLite2 y listas FireHOL/Spamhaus).
  - Diseño y ejecución de matrices de pruebas funcionales de aseguramiento de calidad (QA).
  - Verificación de registros forenses EVE JSON y telemetría de red.

---

## 6. Evidencias

| Tipo de evidencia (avance o final) | Nombre de la evidencia | Descripción | Justificación |
| :--- | :--- | :--- | :--- |
| **Avance (Fase 1)** | Informe de Definición y Topología de Red | Documento técnico formal con diseño L2/L3, matriz de direccionamiento IP y fundamentación metodológica. | Valida la correcta planificación de la infraestructura de red perimetral y el marco teórico de partida. |
| **Avance (Fase 2)** | Repositorio Git de Código Fuente e IaC | Repositorio GitHub con el código del Motor KRONOS, Dockerfiles de Asterisk/DVWA y XML de pfSense. | Demuestra el avance tangible en desarrollo de software, integración de APIs y automatización de red. |
| **Avance (Fase 2)** | Manuales Técnicos y Mockups en PDF | Manual de configuración de pfSense CE 2.9.0 y Tutorial Paso a Paso con WebGUI mockups de alta calidad. | Acredita la reproducibilidad y rigor técnico de los procedimientos de hardening perimetral. |
| **Final (Fase 3)** | Demostración en Vivo de Intrusión y Respuesta SOAR | Ejecución de inyección SQL en DVWA ➔ Bloqueo en kernel FreeBSD (`snort2c`) ➔ Llamada por voz Gemini Live. | Evidencia concluyente del funcionamiento operativo y cumplimiento del objetivo general ante la comisión. |
| **Final (Fase 3)** | Matrices de Pruebas de Calidad (QA) y Logs Forenses | Registros EVE JSON de Suricata, salidas `pfctl -t snort2c -T show` y mediciones de latencia (<1.5 s). | Respaldan con datos empíricos la supresión de falsos positivos y la robustez del filtrado en kernel. |
| **Final (Fase 3)** | Informe Final Consolidado y Presentación Ejecutiva | Documento consolidado del proyecto y diapositivas de defensa ejecutiva en formato 16:9 widescreen. | Entrega formal académica exigida por la pauta de evaluación de Portafolio de Título (APT122). |

---

## 7. Plan de Trabajo

| Competencia o unidades de competencias | Nombre de Actividades/Tareas | Descripción Actividades/Tareas | Recursos | Duración de la actividad | Responsable¹ | Observaciones (Dificultades / Facilitadores) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Comp. 4 & 8** | A1. Diseño y Setup Base pfSense | Instalación de pfSense CE 2.9.0, configuración WAN/LAN y tuning de hardware offloading para Netmap. | Hipervisor Proxmox/VMware, ISO pfSense CE 2.9.0 | Semanas 1 - 2 | Bruno Urrea / Freddy Vásquez | *Facilitador:* Documentación oficial Netgate.<br>*Dificultad:* Incompatibilidad de Netmap con TSO/LRO; se resuelve desactivando hardware offloading. |
| **Comp. 4** | A2. Segmentación de VLANs 802.1Q | Creación de subredes VLAN 10 (Corp), 20 (DMZ), 30 (VoIP) y 99 (Mgmt) y servidores DHCP locales. | pfSense WebGUI, Switch L2 virtual, perfiles VLAN | Semanas 3 - 4 | Freddy Vásquez | *Facilitador:* Soporte nativo 802.1Q en pfSense.<br>*Dificultad:* Filtrado inter-VLAN; se soluciona con reglas Zero Trust por interfaz. |
| **Comp. 7 & 8** | A3. Despliegue de Suricata Inline IPS | Instalación de Suricata 7.x, activación de modo Inline Netmap, reglas ET Open y configuración `dropsid.conf`. | Paquete Suricata, feeds ET Open, consola pfSense | Semanas 5 - 6 | Bruno Urrea / Kevin Retamales | *Facilitador:* Netmap permite descarte en ring-buffer sin latencia.<br>*Dificultad:* Ajuste de falsos positivos; se mitiga con reglas SID selectivas. |
| **Comp. 7 & 8** | A4. Hardening GeoIP con pfBlockerNG | Configuración de cuenta MaxMind Free, bloqueo Top Spammers y feeds FireHOL L1 / Spamhaus DROP. | pfBlockerNG-devel, cuenta MaxMind GeoLite2 | Semanas 7 - 8 | Kevin Retamales | *Facilitador:* Listas de reputación globales actualizadas.<br>*Dificultad:* Sobrecarga de memoria RAM; se optimiza el límite de tablas en pfSense. |
| **Comp. 7** | A5. Proxy Inverso HAProxy & DVWA | Configuración de Frontend HTTPS VIP 443, SSL Offloading, Stick-Tables anti-fuzzing y contenedor DVWA. | Paquete HAProxy, Docker Engine, imagen DVWA | Semanas 9 - 10 | Cristóbal Quezada | *Facilitador:* Stick-Tables en RAM procesan peticiones a nivel microsegundo.<br>*Dificultad:* Certificados autofirmados; se emite CA interna para el laboratorio. |
| **Comp. 6 & 8** | A6. Motor de Correlación KRONOS | Programación en Python 3.12 del parser `eve.json`, filtro heurístico AST y wrapper de kernel FreeBSD `pfctl`. | Python 3.12, librería PyYAML, FreeBSD CLI | Semanas 11 - 12 | Bruno Urrea | *Facilitador:* Librería estándar AST de Python.<br>*Dificultad:* Privilegios de ejecución en pfSense; se configura sudoers restringido para pfctl. |
| **Comp. 5** | A7. Centralita VoIP Asterisk PBX | Construcción de imagen Docker Asterisk 20 LTS, configuración de `pjsip.conf`, `extensions.conf` y auto-dialer AMI. | Docker Engine, Asterisk 20 LTS, AMI, softphone | Semanas 13 - 14 | Freddy Vásquez | *Facilitador:* Canal PJSIP moderno y ligero.<br>*Dificultad:* NAT traversal en VoIP; se resuelve con directivas `local_net` y `external_media_address`. |
| **Comp. 3 & 5** | A8. Integración Gemini Live Voice | Desarrollo de cliente WebSocket seguro, diseño de System Prompts tácticos y conexión de audio PCM con Asterisk. | Google AI Studio API Key, Python websockets | Semanas 14 - 15 | Bruno Urrea | *Facilitador:* Google Gemini Live Flash 3.1 Free Tier con baja latencia.<br>*Dificultad:* Sincronización dúplex de audio; se utiliza códec PCM lineal 24kHz. |
| **Comp. 3 & 4** | A9. Enlace Zero Trust Tailscale | Publicación de subred VoIP `192.168.30.0/24` en Tailscale para softphones móviles remotos sin abrir puertos. | Paquete Tailscale, túnel WireGuard Mesh | Semana 15 | Freddy Vásquez | *Facilitador:* WireGuard supera cualquier CGNAT o firewall intermedio.<br>*Dificultad:* Enrutamiento de subredes; se aprueba la ruta en el panel admin. |
| **Comp. 7, 8 & 11** | A10. Pruebas QA, Auditoría & Defensa | Ejecución de matrices de prueba de penetración, medición de tiempos (<1.5 s), manuales PDF y preparación de defensa. | Repositorio GitHub, softphone, ReportLab | Semanas 16 - 18 | Todo el Equipo | *Facilitador:* Roles bien delimitados y automatización previa.<br>*Dificultad:* Coordinación de demostración en vivo; se preparan scripts de contingencia. |

*¹ En caso de que el Proyecto APT sea grupal, en esta columna se indica el nombre de los responsables de cada tarea o actividad para permitir diferenciar la evaluación por cada integrante.*

---

## 8. Carta Gantt

| Actividad / Hito | Fase 1 (S1-S4) | | | | Fase 2 (S5-S15) | | | | | | | | | | | Fase 3 (S16-S18) | | |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
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
