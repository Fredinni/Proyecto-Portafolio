# INFORME TÉCNICO: PROBLEMÁTICAS DE DIRECCIONAMIENTO IP, CGNAT Y ESTRATEGIAS DE EXPOSICIÓN WAN ($0 COSTO)
## Proyecto de Portafolio de Título: KRONOS SENTINEL (APT122)
**Autor:** Bruno Urrea Ortiz | Especialidad en Conectividad, Redes y Ciberseguridad  
**Institución:** Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín  
**Clasificación:** Documento Técnico de Arquitectura de Red y Despliegue Presencial de Titulación  
**Premisa Económica:** **Arquitectura 100% Costo Cero ($0 CLP)** mediante Capas Gratuitas (Free Tiers), Open Source y Enlaces Móviles.

---

<p align="center">
  <img src="../assets/sentinel_shield_logo.png" alt="KRONOS SENTINEL Logo" width="300px">
</p>

---

## 1. RESUMEN EJECUTIVO Y PREMISA DE COSTO CERO ($0 CLP)

El proyecto **KRONOS SENTINEL** ha sido diseñado bajo una estricta restricción de ingeniería financiera: **Costo de Infraestructura = $0 CLP**. Se aprovechan al 100% plataformas de código abierto, licencias comunitarias y capas gratuitas de computación e Inteligencia Artificial:

* **IA Generativa de Voz Multimodal:** Google Gemini Live API Flash 3.1 (*Google AI Studio Free Tier* con cuota gratuita de peticiones por minuto).
* **Firewall & Kernel Filtering:** pfSense CE 2.9.0 (FreeBSD Open Source, $0).
* **Prevención de Intrusos (IPS):** Suricata 7.x en modo Inline Netmap + *Emerging Threats Open Rulesets* ($0).
* **Geolocalización IP:** MaxMind GeoLite2 Free Edition ($0).
* **Centralita Telefónica:** Asterisk 20 LTS en Docker ($0).
* **Proxy Inverso & Balanceo:** HAProxy Community Edition ($0).
* **Red Mesh Zero Trust:** Tailscale Free Community Plan (hasta 100 nodos cifrados con WireGuard, $0).
* **Conectividad a Internet:** Hotspot 4G/5G de smartphone personal o conexión cableada RJ45 en laboratorios de Duoc UC ($0).

El objetivo de este informe es analizar las limitaciones reales de red (CGNAT, Doble NAT, aislamiento de puertos institucional) y definir la **estrategia de exposición óptima y más resiliente para la defensa presencial ante la comisión evaluadora de Duoc UC**.

---

## 2. MATRIZ DE PROBLEMÁTICAS TÉCNICAS EN REDES RESIDENCIALES Y SEDE DUOC UC

### 2.1 Carrier-Grade NAT (CGNAT / RFC 6598 - `100.64.0.0/10`)
* **Problemática:** Los ISP residenciales en Chile (Movistar, Entel, VTR, Mundo) y los operadores móviles en 4G/5G (WOM, Claro, Entel) no asignan una IPv4 pública enrutable al router/móvil, sino una IP privada en el rango `100.64.0.0/10`.
* **Impacto:** Resulta imposible realizar *Port Forwarding* tradicional desde Internet hacia la WAN de pfSense sin túneles de reversa.
* **Diagnóstico en CLI:**
  ```bash
  # Comprobación de IP pública vista desde Internet vs IP local del router:
  curl -s https://ifconfig.me
  traceroute -n -m 4 1.1.1.1
  ```

### 2.2 Doble NAT y Bloqueo de Redes Privadas (RFC 1918) en pfSense
* **Problemática:** Al conectar la WAN de pfSense al router del hogar o tethering (recibiendo `192.168.1.x` o `192.168.43.x`), pfSense activa por defecto el descarte estricto de redes privadas.
* **Solución Mandatoria en WebGUI:** En **Interfaces > WAN**, desmarcar `Block private networks and loopback addresses` y `Block bogon networks` para permitir la ingesta del tráfico entrante.

### 2.3 Políticas de Seguridad y Aislamiento de Clientes en Sede Duoc UC (RJ45 / Wi-Fi)
* **Problemática:** La infraestructura de red cableada e inalámbrica de Duoc UC cuenta con políticas de *Client Isolation*, filtrado de escaneos (IPS institucional) y bloqueo de puertos entrantes (80, 443, 5060) para proteger los laboratorios.
* **Impacto en Vivo:** Una máquina atacante externa o conectada al Wi-Fi de alumnos **no puede alcanzar directamente** la IP de otra máquina en la misma sala sin ser bloqueada por los switches de la sede.

---

## 3. ANÁLISIS COMPARATIVO DE OPCIONES PARA LA DEFENSA PRESENCIAL EN DUOC UC

---

```
                       ┌─────────────────────────────────────────────────────────────┐
                       │   ESCENARIOS DE DEFENSA PRESENCIAL (TITULACIÓN DUOC UC)     │
                       └─────────────────────────────────────────────────────────────┘
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         │                                            │                                            │
         ▼                                            ▼                                            ▼
 ┌──────────────────────────────┐            ┌──────────────────────────────┐             ┌──────────────────────────────┐
 │ OPCIÓN 1 (ESTÁNDAR DE ORO)   │            │ OPCIÓN 2 (CLOUDFLARE TUNNEL) │             │ OPCIÓN 3 (RED FÍSICA RJ45)   │
 │ Lab Virtual Autónomo         │            │ Túnel Zero Trust Free        │             │ Cableada a Switch Duoc UC    │
 │ + Hotspot 4G/5G para Gemini  │            │ + Hotspot 4G/5G              │             │ + NAT Estudiante             │
 ├──────────────────────────────┤            ├──────────────────────────────┤             ├──────────────────────────────┤
 │ • Ataque: Local (0ms lag)    │            │ • Ataque: Vía Internet       │             │ • Ataque: Inter-Host LAN     │
 │ • Voz IA: Salida 443 HTTPS   │            │ • Túnel: cloudflared a DMZ   │             │ • Riesgo: Client Isolation   │
 │ • Costo: $0 CLP              │            │ • Costo: $0 CLP              │             │ • Costo: $0 CLP              │
 │ • Fiabilidad: 100% INMUNE    │            │ • Fiabilidad: 85% (Depende)  │             │ • Fiabilidad: 40% (Alto)     │
 └──────────────────────────────┘            └──────────────────────────────┘             └──────────────────────────────┘
```

---

### OPCIÓN 1: LABORATORIO VIRTUAL AUTÓNOMO DUAL-HOST + HOTSPOT 4G/5G PARA GEMINI (RECOMENDACIÓN TÁCTICA DUOC UC)

Esta es la arquitectura **más profesional, robusta y 100% inmune a fallas externas**:

```
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ NOTEBOOK PRINCIPAL (Proxmox VE / VMware Workstation / Arch Linux Host)                          │
 │                                                                                                  │
 │   [ VM Atacante Kali Linux ] ──── (vSwitch WAN Aislado: 198.51.100.0/24) ────▶ [ pfSense WAN ]   │
 │   IP: 198.51.100.100                                                           IP: 198.51.100.1  │
 │                                                                                       │          │
 │                                                               (VLANs 10, 20, 30) ─────┤          │
 │                                                                                       ▼          │
 │   [ Asterisk PBX 192.168.30.50 ] ◀── [ Motor pfctl ] ◀── [ Suricata Netmap ] ◀── [ HAProxy ]     │
 │                 │                                                                                │
 │                 ▼ (Llamada Saliente WebSocket PCM 24kHz vía HTTPS 443)                           │
 └─────────────────┼────────────────────────────────────────────────────────────────────────────────┘
                   │
                   ▼ (Conexión Hotspot 4G/5G del Celular o RJ45 Duoc UC)
      [ Google Gemini Live API Flash 3.1 Free Tier ]
                   │
                   ▼ (Llamada de Voz Bidireccional)
      [ Softphone CISO en Celular / Laptop ]
```

* **Cómo Funciona:**
  1. La VM Kali Linux y la interfaz WAN de pfSense se conectan a un switch virtual aislado (`198.51.100.0/24`). El ataque SQLi (vía `sqlmap` o script de exploit) viaja localmente en microsegundos, demostrando el *Inline Netmap Drop* de Suricata y el bloqueo atómico de `pfctl`.
  2. Cuando el motor valida el ataque real, el contenedor de Asterisk / Python despachador utiliza la conexión a Internet del notebook (compartida por Hotspot 4G/5G del celular o cable RJ45) para abrir un **WebSocket seguro saliente (puerto TCP 443)** hacia `generativelanguage.googleapis.com` (Gemini Live API Free Tier).
  3. Asterisk genera la llamada hacia el Softphone del CISO (en el celular del alumno o en el laptop anfitrión).
* **PROS:**
  * **Costo $0:** No requiere comprar dominios, pagar VPS ni contratar IP fija.
  * **Inmune a CGNAT:** El tráfico de ataque es local, y la llamada de Gemini Live es una conexión **saliente HTTPS/WSS**, la cual **nunca es bloqueada por CGNAT ni por los firewalls de Duoc UC**.
  * **Latencia Cero en Demostración:** El bloqueo ocurre en < 150ms frente a los ojos de los profesores, sin buffering ni lag de red externa.
* **CONTRAS:**
  * Requiere un notebook con al menos 16 GB de RAM para correr pfSense, Kali Linux, Asterisk y DVWA en paralelo (escenario estándar en la carrera).

---

### OPCIÓN 2: CLOUDFLARE ZERO TRUST TUNNELS (FREE TIER) + HOTSPOT 4G/5G

Para permitir que los profesores escaneen o ataquen el entorno desde sus propios teléfonos o computadores durante la presentación:

```
 [ Profesor / Atacante en Internet ] ──▶ https://kronos-sentinel.tudominio.com (Cloudflare Edge)
                                                           │ (Túnel Cifrado Saliente cloudflared)
                                                           ▼
                                                [ pfSense / HAProxy DMZ ]
```

* **Cómo Funciona:**
  1. Se instala el conector ligero `cloudflared` (Open Source y 100% gratuito en la capa Zero Trust de Cloudflare) dentro de pfSense o en una VM auxiliar.
  2. `cloudflared` establece 4 conexiones salientes QUIC/HTTPS hacia los servidores de Cloudflare.
  3. No requiere abrir ningún puerto en el router ni en el hotspot móvil (Bypass total de CGNAT).
* **PROS:**
  * Costo $0 (Capa gratuita de Cloudflare Zero Trust).
  * Permite que cualquier persona en la sala ingrese a una URL pública segura `https://...` desde su propio dispositivo.
* **CONTRAS:**
  * Si el Wi-Fi de la sede o la señal 4G se satura durante la presentación, el tráfico web del ataque puede presentar retrasos.

---

### OPCIÓN 3: TAILSCALE SUBNET ROUTER (ENLACE ZERO TRUST VOIP ASTERISK)

La solución ideal para que el softphone en tu celular se conecte con la centralita Asterisk sin importar en qué red esté conectado:

```
 [ Celular CISO (Zoiper Softphone) ] ── (Red Mesh WireGuard 100.x.y.z) ──▶ [ pfSense Tailscale Router ]
                                                                                         │
                                                                                         ▼ (Ruta 192.168.30.0/24)
                                                                             [ Asterisk PBX 192.168.30.50 ]
```

* **Cómo Funciona:**
  1. Se instala `pfSense-pkg-tailscale` ($0 en Package Manager).
  2. Se publica la subred VoIP: `tailscale up --advertise-routes=192.168.30.0/24`.
  3. El celular del CISO (conectado a 4G/5G o Wi-Fi) tiene la app Tailscale activa. Zoiper se registra directamente a `192.168.30.50` con el Anexo 1001.
* **PROS:**
  * **Costo $0:** Tailscale es gratuito de por vida para uso personal y académico (hasta 100 nodos).
  * **Cifrado E2E:** Toda la voz SIP/RTP viaja cifrada con curvas elípticas Curve25519 (WireGuard).
  * **Bypass de NAT:** Utiliza STUN/DERP de Tailscale para atravesar cualquier CGNAT automáticamente.

---

### OPCIÓN 4: CONEXIÓN CABLEADA DIRECTA EN SEDE DUOC UC (RJ45)

* **Cómo Funciona:** Conectar un cable RJ45 desde el switch de la sala hacia la tarjeta de red del notebook.
* **PROS:**
  * Ancho de banda estable para la descarga del audio de Gemini Live.
* **CONTRAS:**
  * La red institucional de Duoc UC restringe la comunicación directa entre puestos de trabajo (*Private VLANs / Port Isolation*), impidiendo que dos notebooks se ataquen entre sí sin usar el laboratorio virtual local (Opción 1).

---

## 4. MATRIZ DE DECISIÓN Y EVALUACIÓN DE RIESGOS

| Criterio de Evaluación | Opción 1: Lab Virtual + Hotspot (Recomendada) | Opción 2: Cloudflare Tunnel | Opción 3: Tailscale Subnet Router | Opción 4: RJ45 Sede Duoc Directo |
| :--- | :---: | :---: | :---: | :---: |
| **Costo Total** | **$0 CLP** | **$0 CLP** | **$0 CLP** | **$0 CLP** |
| **Inmunidad a CGNAT** | **100% Inmune** | **100% Inmune** | **100% Inmune** | 50% (NAT Institucional) |
| **Independencia de Red Sede** | **100% Autónomo** | 50% (Requiere Internet) | 80% (Requiere STUN) | 0% (Depende de Duoc) |
| **Riesgo de Falla en Vivo** | **Casi Nulo (< 1%)** | Medio (15%) | Bajo (5%) | Muy Alto (> 50%) |
| **Velocidad de Demostración** | Instantánea (< 150ms) | Depende de enlace (1-2s) | Instantánea (< 200ms) | Bloqueado por Firewall Duoc |

---

## 5. CONCLUSIÓN Y BLUEPRINT FINAL PARA EL DÍA DE LA DEFENSA

Para asegurar una calificación sobresaliente y garantizar que la comisión presencie una demostración impecable, el equipo adoptará la siguiente **Estrategia Híbrida de $0 Costo**:

1. **Plano de Ataque y Mitigación (100% Local y Determinista):**
   * Correr Kali Linux y pfSense en el entorno virtualizado del notebook con la red aislada `198.51.100.0/24`. Esto garantiza que Suricata Inline, la tabla `snort2c` y `pfctl` reaccionen en microsegundos sin fallar jamás.
2. **Plano de Telefonía e Inteligencia Artificial (Cero Costo Saliente):**
   * Conectar el notebook anfitrión a Internet mediante el **Hotspot 4G/5G del celular** (o cable RJ45).
   * El despachador KRONOS utiliza la cuota gratuita de **Google Gemini Live API Flash 3.1** mediante conexión saliente WebSocket HTTPS (inmune a CGNAT).
3. **Plano de Audio CISO:**
   * Utilizar **Tailscale Subnet Router** en pfSense para que el Softphone (Zoiper en el smartphone del CISO) reciba la llamada telefónica en vivo y los profesores puedan escuchar el briefing táctico de la IA en tiempo real.
