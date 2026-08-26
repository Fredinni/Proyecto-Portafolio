# Perfil Técnico y Contexto del Desarrollador: Bruno Urrea Ortiz

Este archivo define el contexto técnico, entorno de trabajo, stack tecnológico y directrices de desarrollo para las interacciones en este proyecto.

---

## 1. Identidad y Perfil Profesional
* **Nombre:** Bruno Urrea Ortiz
* **Especialidad:** Futuro Ingeniero en Conectividad y Redes (Duoc UC, Sede San Joaquín).
* **Áreas de Enfoque:** Ciberseguridad ofensiva/defensiva, infraestructura de hacking ético, despliegue de entornos OT/IT, arquitectura de redes complejas y securización perimetral.

---

## 2. Entorno de Trabajo y Stack Tecnológico (Daily Workflow)
* **Sistema Operativo Base:** Arch Linux (instalación/configuración personalizada desde cero) con gestor de ventanas **Hyprland** y entorno **Caelestia**.
* **Laboratorio & Virtualización (Home Lab):**
  * Virtualización bare-metal con **Proxmox VE**.
  * Emulación de redes avanzadas mediante **GNS3** integrado con hardware/imágenes de enrutamiento **Cisco**.
  * Despliegue y orquestación de aplicaciones con **Dokploy** sobre VMs/contenedores Ubuntu en Proxmox.
* **Seguridad Perimetral & Monitoreo:**
  * Administración avanzada de firewalls **pfSense**.
  * Detección y Prevención de Intrusos (**IDS/IPS**) con **Suricata** (reglas a medida para detección de malware, escaneos de puertos y hardening continuo de infraestructura).

---

## 3. Ciberseguridad, CTF y Entornos OT (Operational Technology)
* **Diseño de Topologías:** Creación de arquitecturas de red complejas para entornos IT y OT (Tecnología Operativa).
* **Desarrollo de Desafíos & Exploits:** Creación de retos técnicos para competiciones CTF orientados a protocolos industriales (ej. explotación y análisis de **MQTT** para CTF *Llaitún 2025 - Water Shield Edition*).
* **Despliegues en Vivo:** Infraestructuras CTF en tiempo real para demostraciones de alta concurrencia y visibilidad internacional (ej. *FIDAE 2026* con el equipo *Ciberlab*).
* **Trayectoria Competitiva:** Operador activo en el equipo **DevSec** (junto a Rodrigo Lagos, Sebastián Porma y Vicente Arriagada), con logros destacados como Top 4 en *Hackingta CTF*.

---

## 4. Proyecto de Portafolio de Título: KRONOS SENTINEL (APT122)
* **Título del Proyecto:** *KRONOS SENTINEL: Sistema Autónomo de Detección IPS, Filtrado Inteligente de Falsos Positivos y Respuesta Telefónica de Incidentes en Tiempo Real mediante Agente de IA y Asterisk PBX*.
* **Pilares de Arquitectura:**
  1. **Perímetro pfSense:** Suricata en modo Inline IPS (Netmap), pfBlockerNG-devel con GeoIP MaxMind gratuito y listas de reputación IP (FireHOL, Spamhaus, AbuseIPDB).
  2. **DMZ & Reverse Proxy:** HAProxy con terminación SSL publicando la web vulnerable DVWA para pruebas éticas.
  3. **Motor pfctl de Correlación & Supresión de Falsos Positivos:** Scripting en Python que analiza `eve.json` de Suricata y las tablas en kernel de FreeBSD `pfctl` (tabla `snort2c` y estados de conexión), eliminando el >50% de falsos positivos y aislando ataques SQLi reales.
  4. **Agente de Voz IA (Gemini Live Flash 3.1) & Asterisk PBX:** Ante un ataque real validado y bloqueado en `pfctl`, se dispara un webhook a una centralita Asterisk PBX en Docker que efectúa una llamada telefónica inmediata al CISO. El agente de voz interactúa en directo entregando debriefing del incidente (IP, país, vector, estado de bloqueo) y proponiendo medidas de mitigación.

---

## 5. Automatización, Cloud & Proyectos de Innovación
* **Automatización y Gestión de Eventos:** Arquitectura técnica para *Cyb4Students Week* (Google Apps Script, integración de flujos de registro y streaming vía Microsoft Teams).
* **Smart Cities & IoT:** Desarrollo de proyectos tecnológicos de eficiencia hídrica y ciudades inteligentes (Ganador 1° Lugar en el *4° SummIT 5G Innovation Challenge*, Viña del Mar).

---

## 6. Certificaciones y Networking
* **Certificación Objetivo:** Cisco **CCNA 200-301** (dominio de módulos Cisco Networking Academy, routing, switching, subnetting, VLANs, protocolos de enrutamiento OSPF, ACLs, NAT y automatización de redes).

---

## 7. Directrices para el Asistente de IA (Coding & Architecture Assistant)
* **Nivel Técnico:** Asumir un nivel técnico senior/avanzado en redes, administración Linux, ciberseguridad, protocolos industriales y virtualización.
* **Enfoque de Soluciones:** Priorizar soluciones robustas, modulares, seguras por diseño (*Security by Design*), con scripts eficientes (Bash, Python, Automatización) y buenas prácticas de hardening y segmentación de red.
* **Compatibilidad de Entorno:** Adaptar configuraciones, comandos y herramientas a entornos Linux (especialmente Arch/Ubuntu/Debian), Proxmox, Docker y topologías Cisco/pfSense cuando aplique.
