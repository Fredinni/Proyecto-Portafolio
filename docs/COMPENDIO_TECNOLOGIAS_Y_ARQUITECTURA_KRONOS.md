# COMPENDIO TÉCNICO DE TECNOLOGÍAS, PROTOCOLOS Y ARQUITECTURA
## Proyecto: KRONOS SENTINEL (APT122) — Autonomous AI-IPS & Real-Time Incident Voice Response
**Autor:** Bruno Urrea Ortiz | Especialidad en Conectividad, Redes y Ciberseguridad  
**Institución:** Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín  
**Estado:** Prototipo Funcional en Desarrollo y Validación de Laboratorio (Portafolio de Título)  
**Premisa de Costo:** **100% Código Abierto y Capas Gratuitas ($0 CLP)**

---

<p align="center">
  <img src="../assets/sentinel_shield_logo.png" alt="KRONOS SENTINEL Logo" width="280px">
</p>

---

## 1. INTRODUCCIÓN Y MAPA TECNOLÓGICO GLOBAL

**KRONOS SENTINEL** es una arquitectura integral de defensa en profundidad, mitigación en kernel y respuesta autónoma ante incidentes (*Security Orchestration, Automation, and Response - SOAR*). El sistema integra 10 componentes tecnológicos estratégicos articulados en 4 capas operativas:

```
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                      MAPA TECNOLÓGICO DE KRONOS SENTINEL ($0 CLP)                      │
 ├────────────────────────────────────────────────────────────────────────────────────────┤
 │ 1. CAPA PERIMETRAL & KERNEL   │ pfSense CE 2.7.2 • FreeBSD 14 (pf) • Tabla snort2c     │
 │ 2. CAPA PREVENCIÓN IPS & GeoIP│ Suricata 7.x (Netmap) • ET Open Rules • pfBlockerNG   │
 │ 3. CAPA PROXY DMZ & LAB       │ HAProxy 2.8+ (Stick Tables) • DVWA Docker              │
 │ 4. CAPA ANÁLISIS & FILTRADO   │ Motor pfctl en Python 3.12 • Heurística Anti-FP (>50%) │
 │ 5. CAPA TELEFONÍA & VOZ IA    │ Asterisk 20 LTS PBX • Google Gemini Live Flash 3.1     │
 │ 6. CAPA ACCESO ZERO TRUST     │ Tailscale Subnet Router (Mesh WireGuard)               │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. DESGLOSE DETALLADO DE LAS 10 TECNOLOGÍAS

---

### 2.1 pfSense CE 2.7.2 & Kernel FreeBSD 14 (`pf` / Packet Filter)
* **¿Qué es?**  
  pfSense Community Edition es una distribución de seguridad de red de código abierto basada en el sistema operativo FreeBSD. Utiliza el módulo de filtrado de paquetes en kernel `pf(4)` (*Packet Filter*), originalmente desarrollado por el proyecto OpenBSD.
* **¿Cómo funciona bajo el capó?**  
  `pf` procesa paquetes a nivel de capa 3 y 4 del modelo OSI en el espacio de kernel. Mantiene una tabla de estados en memoria (*Stateful Packet Inspection - SPI*) que rastrea flujos TCP (flags SYN, ACK, FIN, RST) y pseudo-estados UDP/ICMP. Permite manipular listas dinámicas de direcciones IP en memoria RAM denominadas **Tablas `pf`** (estructuras `struct pfr_ktable` en lenguaje C), las cuales ofrecen tiempos de búsqueda atómicos de complejidad algorítmica $O(1)$ gracias a árboles binarios radix (*Radix Trees*).
* **Rol en KRONOS SENTINEL:**  
  * Actúa como el firewall perimetral y enrutador principal segmentando la red en 4 VLANs (Corp 10, DMZ 20, VoIP 30, Mgmt 99).
  * Administra la tabla en memoria `<snort2c>`, la cual ejecuta el *blackholing* instantáneo de atacantes a nivel de kernel.
* **Licenciamiento:** 100% Open Source (Licencia Apache 2.0 / FreeBSD), costo **$0 CLP**.

---

### 2.2 Suricata 7.x & Subsistema `netmap(4)` en Modo Inline IPS
* **¿Qué es?**  
  Suricata es un motor de detección y prevención de intrusiones (*IDS/IPS*) y análisis de seguridad de red multiproceso (*multi-threaded*) de alto rendimiento desarrollado por la *Open Information Security Foundation* (OISF).
* **¿Cómo funciona bajo el capó?**  
  En lugar de operar en modo pasivo (*Legacy PCAP*) donde solo se escuchan copias de paquetes, KRONOS implementa Suricata en modo **Inline IPS** utilizando el framework de kernel `netmap(4)` de FreeBSD:
  * `netmap(4)` desacopla los anillos de descriptores de la tarjeta de red (*Ring Buffers RX/TX*) del stack de red tradicional del sistema operativo.
  * Los paquetes cruzan directamente la memoria compartida (*zero-copy buffer*) hacia los hilos de inspección de Suricata.
  * Si un paquete coincide con una firma configurada como `DROP`, Suricata descarta el paquete físicamente en el anillo de hardware **antes de que ingrese al stack TCP/IP del firewall**, logrando una prevención con latencia inferior a microsegundos.
  * Todos los eventos inspeccionados se serializan en el archivo de eventos JSON estructurado `/var/log/suricata/eve.json`.
* **Rol en KRONOS SENTINEL:** Inspección profunda de paquetes (DPI) en WAN y LAN para la detección en tiempo real de payloads maliciosos (SQLi, RCE, escaneos de puertos).
* **Licenciamiento:** 100% Open Source (GPLv2), costo **$0 CLP**.

---

### 2.3 Reglas de Detección ET Open (Emerging Threats) & Snort Community
* **¿Qué son?**  
  Conjunto de firmas comunitarias estandarizadas y reglas heurísticas de detección de amenazas de capa 7 basadas en patrones de expresiones regulares (PCRE), cabeceras HTTP y firmas de tráfico malicioso conocido.
* **¿Cómo funcionan?**  
  Cada regla evalúa condiciones lógicas específicas en el payload de los paquetes:
  ```snort
  # Ejemplo de firma ET Open para SQLi:
  drop tcp $EXTERNAL_NET any -> $HTTP_SERVERS $HTTP_PORTS (msg:"ET WEB_SPECIFIC_APPS SQL Injection Attempt"; flow:established,to_server; content:"UNION"; nocase; content:"SELECT"; nocase; classtype:web-application-attack; sid:2008287; rev:3;)
  ```
  Mediante la política `dropsid.conf`, KRONOS transforma automáticamente las alertas en acciones `DROP` de bloqueo inmediato.
* **Rol en KRONOS SENTINEL:** Proveer la base de conocimiento de firmas para identificar inyecciones SQL y ataques a la DMZ.
* **Licenciamiento:** Open Community Rulesets, **100% Gratis ($0 CLP)** sin requerir suscripciones de pago.

---

### 2.4 pfBlockerNG-devel & Base de Datos MaxMind GeoLite2 Free
* **¿Qué es?**  
  Paquete avanzado de inteligencia de amenazas para pfSense que fusiona listas de reputación IP (*IP Feeds*) y geolocalización de tráfico.
* **¿Cómo funciona?**  
  Descarga periódicamente la base de datos binaria gratuita `GeoLite2-Country.mmdb` provista por MaxMind y compila listas de rangos CIDR asignados por los RIRs (ARIN, RIPE, LACNIC, APNIC, AFRINIC). pfBlockerNG crea **reglas de firewall flotantes** de alta prioridad que descartan el tráfico entrante de países catalogados como *Top Spammers* antes de que el paquete llegue a Suricata o HAProxy, reduciendo en un 40% la carga computacional del firewall.
* **Rol en KRONOS SENTINEL:** Blindaje perimetral geográfico e inmunidad contra botnets y redes de escaneo masivo (FireHOL L1, Spamhaus DROP).
* **Licenciamiento:** Software GPLv3 / Base de datos MaxMind GeoLite2 Free (con cuenta comunitaria gratuita), costo **$0 CLP**.

---

### 2.5 HAProxy 2.8+ Community Edition & Stick Tables en Memoria
* **¿Qué es?**  
  HAProxy (*High Availability Proxy*) es el balanceador de carga y proxy inverso TCP/HTTP de mayor rendimiento y confiabilidad en la industria de redes.
* **¿Cómo funciona bajo el capó?**  
  * **Terminación SSL/TLS:** Desencripta el tráfico HTTPS en el puerto 443 mediante OpenSSL y lo reenvía sin cifrar o re-encriptado hacia la DMZ, liberando de carga criptográfica a los servidores web internos.
  * **Inyección de Encabezados:** Agrega `X-Forwarded-For` y `X-Real-IP` para que las aplicaciones conozcan la IP real del cliente.
  * **Stick Tables:** Estructuras de datos en memoria RAM que registran métricas de cada cliente en ventanas de tiempo deslizantes:
    * `table type ip size 100k expire 30s store http_req_rate(10s),http_err_rate(10s)`
    * Si un cliente supera 100 peticiones en 10 segundos o genera más de 25 errores HTTP 4xx (fuzzing), HAProxy responde automáticamente con código `429 Too Many Requests` o corta la conexión.
* **Rol en KRONOS SENTINEL:** Publicación segura del laboratorio DVWA en la VLAN 20 DMZ y mitigación de DoS/Fuzzing L7.
* **Licenciamiento:** 100% Open Source (GPLv2 / LGPLv2.1), costo **$0 CLP**.

---

### 2.6 DVWA (Damn Vulnerable Web Application) en Contenedor Docker
* **¿Qué es?**  
  Una aplicación web PHP/MySQL intencionalmente vulnerable diseñada por profesionales de ciberseguridad para probar herramientas de explotación y validar sistemas de defensa.
* **¿Cómo funciona?**  
  Ejecutada en un contenedor Docker aislado dentro de la VLAN 20 DMZ (`192.168.20.50`), expone módulos vulnerables a *SQL Injection*, *Cross-Site Scripting (XSS)* y *Command Execution* con niveles de seguridad configurables (Low, Medium, High).
* **Rol en KRONOS SENTINEL:** Entorno objetivo controlado para lanzar ataques reales con `sqlmap` o scripts de explotación y demostrar la reacción del firewall.
* **Licenciamiento:** Open Source (GPLv3), costo **$0 CLP**.

---

### 2.7 Motor de Correlación y Supresión de Falsos Positivos (`pfctl Engine` en Python)
* **¿Qué es?**  
  El núcleo de software desarrollado a medida para el proyecto (ubicado en `src/pfsense_pfctl_engine/`).
* **¿Cómo funciona bajo el capó?**  
  1. **Ingesta Continua:** Monitorea en tiempo real `/var/log/suricata/eve.json` mediante un hilo `asyncio` no bloqueante.
  2. **Filtro Heurístico Anti-Ruido (>50%):** Analiza el payload del evento descartando escaneos genéricos inocuos (ej. firmas sin parámetros explotables).
  3. **Validador AST SQLi:** Evalúa la presencia de operadores lógicos relacionales (`OR 1=1`, `UNION SELECT`, comentarios `--`, `' #`) asignando un índice de confianza $\text{Confianza}_{\text{SQLi}} \in [0.0, 1.0]$.
  4. **Verificación Atómica en Kernel:** Ejecuta `pfctl -t snort2c -T test <IP>`. Si la IP fue efectivamente bloqueada por el kernel de FreeBSD, confirma el incidente y dispara el webhook local hacia el despachador de voz.
* **Rol en KRONOS SENTINEL:** Erradicar la sobrecarga de alertas innecesarias y garantizar que solo se llame al CISO ante amenazas reales neutralizadas.
* **Licenciamiento:** Código propietario del proyecto de título (Licencia MIT), costo **$0 CLP**.

---

### 2.8 Asterisk 20 LTS PBX en Contenedor Docker
* **¿Qué es?**  
  Asterisk es el motor de comunicaciones y centralita telefónica (*Private Branch Exchange - PBX*) de código abierto líder a nivel mundial.
* **¿Cómo funciona bajo el capó?**  
  * **Stack SIP/PJSIP:** Implementa el protocolo SIP sobre el canal `PJSIP`, gestionando registros de usuarios (`1001` Bruno Urrea, `1002` Freddy Vásquez, `1003` Cristóbal Quezada, `1004` Kevin Retamales) y el anexo del agente IA (`1000`).
  * **Asterisk Manager Interface (AMI):** Expone un socket TCP administrativo en el puerto `5038`. Cuando el despachador recibe una alerta confirmada, envía el comando `Action: Originate` para marcar de inmediato al softphone del CISO (`PJSIP/1001`) y conectarlo al canal de audio del agente.
  * **RTP Streaming:** Transporta los flujos de voz bidireccionales en códecs PCM/G.711u a través de puertos UDP `10000:10100`.
* **Rol en KRONOS SENTINEL:** Plataforma de conmutación telefónica y llamada de emergencia automática.
* **Licenciamiento:** 100% Open Source (GPLv2), costo **$0 CLP**.

---

### 2.9 Google Gemini Live API Flash 3.1 (Audio Multimodal en Tiempo Real)
* **¿Qué es?**  
  El modelo de Inteligencia Artificial generativa multimodal de última generación de Google DeepMind optimizado para procesamiento de texto, audio y visión con latencia de respuesta ultra-baja.
* **¿Cómo funciona bajo el capó?**  
  * Se conecta mediante un canal bidireccional **WebSocket seguro (WSS) sobre HTTPS (puerto 443)** con el endpoint `generativelanguage.googleapis.com`.
  * Recibe el stream de audio en tiempo real desde Asterisk (PCM lineal a 16kHz o 24kHz) y transmite de vuelta audio sintetizado nativo sin pasar por etapas lentas de transcripción separada (Audio-to-Audio nativo).
  * El modelo recibe un System Prompt de Ciberseguridad SecOps que le instruye actuar como un analista de incidentes de guardia: entrega la IP atacante, país GeoIP, payload SQLi, confirma el bloqueo en pfSense y responde las preguntas de mitigación del CISO.
* **Rol en KRONOS SENTINEL:** Interlocutor inteligente que realiza el debriefing táctico interactivo por voz con el decisor de seguridad.
* **Licenciamiento:** *Google AI Studio Free Tier* (cuota gratuita para desarrollo e investigación académica), costo **$0 CLP**.

---

### 2.10 Tailscale Zero Trust WireGuard Mesh
* **¿Qué es?**  
  Una solución de red privada virtual (*VPN Mesh*) basada en el protocolo criptográfico moderno **WireGuard**.
* **¿Cómo funciona bajo el capó?**  
  * Conecta nodos directamente mediante cifrado asimétrico con curvas elípticas Curve25519, ChaCha20 y Poly1305.
  * Utiliza servidores de coordinación DERP y técnicas de *NAT Traversal* (STUN/ICE) para atravesar cualquier red CGNAT automáticamente.
  * **Subnet Routing:** pfSense actúa como router de subred anunciando la ruta privada `192.168.30.0/24` (VLAN VoIP). El smartphone del CISO se registra de forma transparente en Asterisk sin requerir abrir puertos SIP en el firewall público.
* **Rol en KRONOS SENTINEL:** Canal de comunicación seguro y cifrado entre el Softphone del CISO y la centralita Asterisk PBX.
* **Licenciamiento:** Tailscale Free Community Plan (gratuito hasta 100 dispositivos), costo **$0 CLP**.

---

## 3. RESUMEN DE COMPATIBILIDAD Y MATRIZ DE COSTOS

| Módulo / Tecnología | Licencia / Modelo | Costo Monetario | Impacto en KRONOS SENTINEL |
| :--- | :--- | :---: | :--- |
| **pfSense CE 2.7.2** | FreeBSD Open Source | **$0 CLP** | Firewall L2-L4, VLANs y tabla kernel `snort2c`. |
| **Suricata 7.x Inline Netmap** | GPLv2 Open Source | **$0 CLP** | Inspección profunda y Drop en ring buffer de red. |
| **Reglas ET Open & Snort** | Community Free Rules | **$0 CLP** | Base de firmas para detección de SQLi y exploits. |
| **pfBlockerNG + MaxMind** | GPLv3 / GeoLite2 Free | **$0 CLP** | Bloqueo perimetral por GeoIP y feeds de amenazas. |
| **HAProxy 2.8+ Community** | GPLv2 Open Source | **$0 CLP** | Terminación SSL, balanceo y stick-tables anti-DoS. |
| **DVWA en Docker** | GPLv3 Open Source | **$0 CLP** | Laboratorio web vulnerable controlado en DMZ. |
| **Motor pfctl (Python)** | MIT (Código Propio) | **$0 CLP** | Supresión de falsos positivos (>50%) y verificación. |
| **Asterisk 20 LTS PBX** | GPLv2 Open Source | **$0 CLP** | Telefonía VoIP, señalización PJSIP y dialer AMI. |
| **Gemini Live Flash 3.1** | Google AI Studio Free Tier | **$0 CLP** | Streaming de voz bidireccional para debriefing CISO. |
| **Tailscale Subnet Router** | WireGuard Free Tier | **$0 CLP** | Enlace seguro Zero Trust para softphone móvil. |

---

## 4. CONCLUSIÓN TÉCNICA

El compendio tecnológico de **KRONOS SENTINEL** demuestra que es técnica y económicamente viable construir una solución de **Defensa Perimetral e Incident Response Autónomo de Nivel Corporativo** utilizando exclusivamente tecnologías abiertas de alto rendimiento y capas gratuitas de computación en la nube e Inteligencia Artificial, cumpliendo con los estándares de titulación de Duoc UC.
