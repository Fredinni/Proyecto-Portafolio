# Diario de Reflexión - Fase 1
### Experiencia de Aprendizaje 1 (EA1) | Definición Proyecto APT
**Estudiante:** Bruno Urrea Ortiz  
**Carrera:** Ingeniería en Conectividad y Redes  
**Institución:** Duoc UC - Sede San Joaquín  
**Asignatura:** Portafolio de Título (APT122)

---

### 1. Asignaturas y Certificados de Mayor Motivación
> **¿Cuáles son las asignaturas o certificados que más motivaron tu aprendizaje y se relacionan con tus intereses profesionales? ¿Por qué?**

Las asignaturas que mayor impacto y motivación han generado en mi formación son aquellas orientadas a la **Ciberseguridad Defensiva y Ofensiva, Seguridad Perimetral, Routing & Switching avanzado (CCNA / Cisco Networking Academy), Sistemas Operativos tipo Unix/Linux y Arquitectura de Redes**.

Bajo la exigente mentoría académica del profesor Mauricio Carrera, profundicé en la concepción de que una red no solo debe ser funcional y de alta disponibilidad, sino **inherentemente segura por diseño (*Security by Design*)**. Esto despertó mi pasión por la construcción de laboratorios complejos (Home Lab bare-metal con Proxmox VE y emulación con GNS3), la administración avanzada de firewalls **pfSense** y la detección/prevención de intrusiones con **Suricata IPS**, orientando mi perfil hacia la ingeniería de seguridad perimetral, la respuesta autónoma ante incidentes (SOAR) y la fortificación de infraestructuras críticas.

---

### 2. Análisis de Competencias (Fortalezas y Oportunidades de Mejora)
> **¿Cuáles consideras que tienes más desarrolladas y te sientes más seguro aplicando? ¿En cuáles te sientes más débil y requieren ser fortalecidas?**  
> **Sumado a lo anterior, ¿Hay alguna competencia que hayas desarrollado de forma autodidacta en alguna actividad extracurricular que quieras destacar?**

* **Competencias con mayor fortaleza y seguridad:**
  * Administración avanzada de sistemas Linux (Arch Linux configurado desde cero con gestor de ventanas Hyprland y entorno Caelestia).
  * Virtualización e infraestructura sobre Proxmox VE y orquestación con Dokploy.
  * Diseño de topologías de red segmentadas mediante VLANs, ACLs y enrutamiento dinámico.
  * Securización perimetral mediante firewalls pfSense, configuración de Suricata en modo **Inline IPS** (Netmap) y proxy inverso con HAProxy.
* **Competencias a fortalecer:**
  * Estandarización y modelamiento formal de costos operacionales/financieros a nivel corporativo bajo marcos formales (ITIL/TOGAF) y pulir metodologías de comunicación ejecutiva ante comités directivos de negocio.
* **Competencias desarrolladas de forma autodidacta / extracurricular:**
  * Investigación y explotación de vulnerabilidades en protocolos industriales y de IoT (ej. desarrollo y análisis de exploits sobre protocolo **MQTT** implementados para la competición CTF *Llaitún 2025 - Water Shield Edition*).
  * Despliegue de infraestructuras CTF en tiempo real para demostraciones de alta concurrencia y visibilidad internacional (ej. *FIDAE 2026* junto al equipo Ciberlab).
  * Desarrollo de automatizaciones y programación en Python para la integración de Inteligencia Artificial en tiempo real (APIs de voz de baja latencia).

---

### 3. Proyección Profesional y Perfil de Egreso
> **¿En qué área deseas trabajar cuando egreses de tu carrera? ¿Cómo te gustaría que fuera tu escenario laboral en 5 años más según tus intereses profesionales? ¿Cuál es tu plan o proyecto para lograrlo? ¿Cuáles son las principales competencias que requieres fortalecer?**

* **Área de desempeño al egresar:** Ingeniero de Ciberseguridad / Arquitecto de Infraestructura y SecOps, integrando ingeniería de redes perimetrales, automatización de respuesta a incidentes (SOAR) y detección de amenazas en entornos IT y OT.
* **Escenario laboral a 5 años:** Liderar un equipo de ingeniería en ciberseguridad / SOC de respuesta a incidentes o desempeñarme como consultor senior en arquitecturas Zero Trust y sistemas autónomos de defensa.
* **Plan para lograrlo:** Obtención de la certificación oficial Cisco **CCNA 200-301**, certificaciones especializadas de seguridad ofensiva/defensiva (ej. eJPT/OSCP/CompTIA Security+), y la continua participación en CTFs de élite con el equipo **DevSec** (junto a Rodrigo Lagos, Sebastián Porma y Vicente Arriagada).
* **Competencias a fortalecer:** Gestión integral de proyectos corporativos a gran escala y oratoria ejecutiva para traducir métricas técnicas de riesgo a impacto financiero y estratégico de negocio.

---

### 4. Definición del Proyecto APT (Portafolio de Título)
> **Los Proyectos APT que ya habías diseñado como plan de trabajo, ¿se relacionan con tus proyecciones profesionales actuales? ¿En qué contexto se sitúa este Proyecto APT?**

El proyecto de título seleccionado representa la convergencia directa de mis competencias en redes, ciberseguridad perimetral, automatización y tecnologías emergentes:

#### **Título del Proyecto:**
> **KRONOS SENTINEL: Sistema Autónomo de Detección IPS, Filtrado Inteligente de Falsos Positivos y Respuesta Telefónica de Incidentes en Tiempo Real mediante Agente de IA y Asterisk PBX.**

#### **Componentes y Alcance Técnico:**
1. **Infraestructura de Red y Perímetro:** Despliegue de un firewall **pfSense** configurado con **Suricata en modo Inline IPS (Netmap)**, **pfBlockerNG-devel** alimentado con bases de datos GeoIP de MaxMind y listas de reputación de IPs maliciosas (FireHOL, AbuseIPDB, Emerging Threats).
2. **Publicación Segura de Servicios:** Configuración de un proxy inverso **HAProxy** que publica hacia Internet un entorno web vulnerable controlado (**DVWA - Damn Vulnerable Web Application**) en DMZ para pruebas éticas.
3. **Motor de Correlación y Supresión de Falsos Positivos (pfctl Engine):** Desarrollo de un motor en Python que inspecciona los registros EVE de Suricata y las tablas dinámicas de FreeBSD pfctl (tabla `snort2c` y estados de conexión), eliminando el ruido y falsos positivos habituales (más del 50% del tráfico ruidoso) para aislar ataques críticos reales (ej. SQL Injection autenticado o Command Injection).
4. **Agente de IA Conversacional en Tiempo Real y Telefonía PBX:** Ante un ataque real mitigado y bloqueado por pfctl, el motor dispara un webhook/trigger hacia una centralita **Asterisk PBX** alojada en la nube/contenedor, la cual efectúa una llamada telefónica automática inmediata al CISO/SOC Lead. Un agente de IA (**Gemini Live API Flash 3.1**) interactúa por voz con el operador, entregando un debriefing preciso del ataque (IP origen, geolocalización, vector, bloqueo confirmado) y proponiendo mitigaciones estratégicas en tiempo real.
