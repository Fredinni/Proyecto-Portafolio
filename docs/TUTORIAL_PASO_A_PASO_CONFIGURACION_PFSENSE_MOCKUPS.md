# MANUAL MAESTRO DE CONFIGURACIÓN PASO A PASO: pfSense CE 2.9.0
## Blueprint Visual Completo, Simulación WebGUI y Parámetros Oficiales de Laboratorio
**Autor:** Bruno Urrea Ortiz | Especialidad en Conectividad, Redes y Ciberseguridad  
**Institución:** Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín  
**Proyecto:** Portafolio de Título (APT122) — Arquitectura de Costo Cero ($0 CLP)  
**Sistema Base:** FreeBSD 14.0-CURRENT / pfSense CE 2.9.0 (amd64)  
**Clasificación:** Manual Técnico de Laboratorio y Guía Paso a Paso de Despliegue

---

<p align="center">
  <img src="../assets/sentinel_shield_logo.png" alt="KRONOS SENTINEL Logo" width="280px">
</p>

---

## 📌 ESTRUCTURA METODOLÓGICA DEL TUTORIAL

Este documento constituye la guía oficial y exhaustiva para el despliegue del firewall **pfSense CE 2.9.0** en el proyecto **KRONOS SENTINEL**. Cada módulo incluye el árbol de navegación oficial, los parámetros técnicos requeridos por las mejores prácticas de Netgate/FreeBSD y la **simulación visual de los formularios WebGUI**.

---

# FASE 1: SETUP INICIAL, HARDWARE TUNING & NETWORKING BASE

---

### PASO 1.1: CONFIGURACIÓN GENERAL DEL SISTEMA Y SERVIDORES DNS

**Ruta en WebGUI:** `System > General Setup`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: System / General Setup                                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Hostname:             [ kronos-fw                                                              ] │
│ Domain:               [ kronos.local                                                           ] │
│                                                                                                  │
│ --- DNS SERVER SETTINGS ---                                                                      │
│ DNS Server 1:         [ 1.1.1.1                    ] Gateway: [ none (WAN_DHCP)              ▼ ] │
│ DNS Server 2:         [ 8.8.8.8                    ] Gateway: [ none (WAN_DHCP)              ▼ ] │
│ DNS Server Override:  [ ] Allow DNS server list to be overridden by DHCP/PPP on WAN             │
│ DNS Resolution Behavior:[ Use local DNS (127.0.0.1), fall back to remote DNS Servers         ▼ ] │
│                                                                                                  │
│ --- TIME CONFIGURATION ---                                                                       │
│ Timezone:             [ America/Santiago (Chile Standard Time)                                 ▼ ] │
│ NTP Time Server:      [ 0.south-america.pool.ntp.org                                           ] │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 1.2: HARDWARE OFFLOADING TUNING (CRÍTICO PARA NETMAP INLINE IPS)

> [!IMPORTANT]
> Para garantizar la estabilidad del framework `netmap(4)` en modo **Inline IPS** y evitar colisiones con los ring buffers de la tarjeta de red, la documentación oficial de Netgate exige **desactivar todo el offloading de hardware** en el kernel de FreeBSD.

**Ruta en WebGUI:** `System > Advanced > Networking` ➔ Sección **Network Interfaces**

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: System / Advanced / Networking                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ --- HARDWARE CHECKSUM OFFLOADING ---                                                             │
│ Hardware Checksum Offload:      [X] Disable hardware checksum offload                            │
│                                     (Checking this option disables hardware checksum calculation) │
│                                                                                                  │
│ --- HARDWARE TCP SEGMENTATION ---                                                                │
│ Hardware TCP Segmentation:      [X] Disable hardware TCP segmentation offload (TSO)              │
│                                     (Mandatory for Suricata Netmap Inline packet interception)   │
│                                                                                                  │
│ --- HARDWARE LARGE RECEIVE ---                                                                   │
│ Hardware Large Receive Offload:  [X] Disable hardware large receive offload (LRO)                │
│                                     (Prevents driver-level packet aggregation before IPS)        │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 1.3: CREACIÓN DE TRONCAL 802.1Q Y VLANs

**Ruta en WebGUI:** `Interfaces > Assignments > VLANs` ➔ `[ + Add ]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Interfaces / VLANs / Edit                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Parent Interface:     [ vtnet1 (LAN Trunk Physical Adapter)                                   ▼ ] │
│ VLAN Tag:             [ 10                                                                      ] │
│ VLAN Priority:        [ 0 (Best Effort)                                                         ] │
│ Description:          [ VLAN_10_CORP_INTERNAL                                                   ] │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

* **Tabla de Asignación de Tags VLAN:**
  1. **VLAN 10:** Tag `10` | Parent `vtnet1` | Descripción: `VLAN_10_CORP`
  2. **VLAN 20:** Tag `20` | Parent `vtnet1` | Descripción: `VLAN_20_DMZ_SERVERS`
  3. **VLAN 30:** Tag `30` | Parent `vtnet1` | Descripción: `VLAN_30_VOIP_PBX`
  4. **VLAN 99:** Tag `99` | Parent `vtnet1` | Descripción: `VLAN_99_MGMT_SEC`

---

### PASO 1.4: ASIGNACIÓN DE INTERFACES Y DIRECCIONAMIENTO IP ESTÁTICO

**Ruta en WebGUI:** `Interfaces > Assignments` ➔ Asignar cada puerto y configurar IP fija:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Interfaces / DMZ_SERVERS (vtnet1.20)                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Enable:               [X] Enable interface                                                       │
│ Description:          [ DMZ_SERVERS                                                            ] │
│ IPv4 Configuration:   [ Static IPv4                                                            ▼ ] │
│ IPv4 Address:         [ 192.168.20.1               ] / [ 24                                    ▼ ] │
│ IPv4 Upstream Gateway:[ None                                                                   ▼ ] │
│                                                                                                  │
│ --- WAN SPECIFIC SETTINGS (Interfaces > WAN vtnet0) ---                                          │
│ Block Private Networks:[ ] Block private networks and loopback addresses (Desmarcar para Lab)    │
│ Block Bogon Networks:  [ ] Block bogon networks (Desmarcar para reenvío en Lab/Tethering)        │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

* **Matriz de Direccionamiento IP por Interfaz:**
  * **WAN (`vtnet0`):** `198.51.100.1/24` (IP Estática en Lab Dual-Host) o DHCP en red externa.
  * **LAN_CORP (`vtnet1.10`):** `192.168.10.1/24`
  * **DMZ_SERVERS (`vtnet1.20`):** `192.168.20.1/24`
  * **VOIP_PBX (`vtnet1.30`):** `192.168.30.1/24`
  * **MGMT_SEC (`vtnet1.99`):** `192.168.99.1/24`

---

# FASE 2: SERVICIOS DHCP Y RESERVAS ESTÁTICAS DE INFRAESTRUCTURA

---

### PASO 2.1: SERVIDOR DHCP Y RESERVA FIJA PARA EL SERVIDOR WEB DMZ (DVWA)

**Ruta en WebGUI:** `Services > DHCP Server > DMZ_SERVERS`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / DHCP Server / DMZ_SERVERS                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Enable:               [X] Enable DHCP server on DMZ_SERVERS interface                            │
│ Subnet:               192.168.20.0 / Subnet Mask: 255.255.255.0                                  │
│ Available Range:      192.168.20.1 - 192.168.20.254                                              │
│ Range:                From: [ 192.168.20.100       ] To: [ 192.168.20.199       ]                │
│ DNS Servers:          [ 192.168.20.1               ] [ 1.1.1.1                  ]                │
│ Gateway:              [ 192.168.20.1               ]                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DHCP Static Mappings (Reserva Fija para DVWA):                                                   │
│   • MAC Address:      [ 02:42:c0:a8:14:32          ]                                             │
│   • IP Address:       [ 192.168.20.50              ]                                             │
│   • Hostname:         [ dvwa-dmz-target            ]                                             │
│   • Description:      [ Laboratorio Web Vulnerable Controlado - DMZ ]                            │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 2.2: SERVIDOR DHCP Y RESERVA FIJA PARA CENTRALITA ASTERISK PBX

**Ruta en WebGUI:** `Services > DHCP Server > VOIP_PBX`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / DHCP Server / VOIP_PBX                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Enable:               [X] Enable DHCP server on VOIP_PBX interface                               │
│ Range:                From: [ 192.168.30.100       ] To: [ 192.168.30.199       ]                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DHCP Static Mappings (Reserva Fija para Asterisk PBX Core):                                      │
│   • MAC Address:      [ 02:42:c0:a8:1e:32          ]                                             │
│   • IP Address:       [ 192.168.30.50              ]                                             │
│   • Hostname:         [ asterisk-pbx-core          ]                                             │
│   • Description:      [ Centralita Telefonica SIP/PJSIP y Auto-Dialer SOAR ]                     │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# FASE 3: SURICATA 7.X — PREVENCIÓN EN KERNEL (NETMAP INLINE IPS)

---

### PASO 3.1: INSTALACIÓN DEL PAQUETE SURICATA

**Ruta en WebGUI:** `System > Package Manager > Available Packages` ➔ Buscar `suricata` ➔ `[ + Install ]`

---

### PASO 3.2: CONFIGURACIÓN GLOBAL DE REGLAS (ET OPEN & SNORT COMMUNITY)

**Ruta en WebGUI:** `Services > Suricata > Global Settings`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / Suricata / Global Settings                                            │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ --- RULESETS SUBSCRIPTION ($0 COST COMMUNITY EDITIONS) ---                                       │
│ Install ETOpen Rules: [X] Install Emerging Threats Open rules (Free Community Ruleset)           │
│ Install Snort Rules:  [X] Install Snort Community rules (Free Cisco Talos Community)             │
│ Snort Oinkmaster Code:[ none (Not required for Snort Community Free Tier)                      ] │
│                                                                                                  │
│ --- AUTOMATIC UPDATES & LIVE SWAP ---                                                            │
│ Update Interval:      [ 12 Hours                                                               ▼ ] │
│ Live Rule Swap:       [X] Live rule swap on update (Zero downtime inspection)                    │
│                                                                                                  │
│                       [ Save ]                                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 3.3: CONFIGURACIÓN DE LA INTERFAZ WAN EN MODO INLINE IPS (NETMAP)

**Ruta en WebGUI:** `Services > Suricata > Interfaces > Edit [WAN]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / Suricata / Interfaces / WAN Settings                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Enable:               [X] Enable Suricata inspection on this interface                           │
│ Interface:            [ WAN (vtnet0)                                                           ▼ ] │
│ Description:          [ WAN External Perimeter Inspection                                       ] │
│                                                                                                  │
│ --- INLINE IPS CONFIGURATION ---                                                                 │
│ IPS Mode:             ( ) Legacy Mode   (X) Inline Mode (netmap framework)                       │
│ Block on Alerts:      [X] Block offenders (enforces hardware ring-buffer drop)                   │
│ Kill States:          [X] Kill states for dropped connections                                    │
│                                                                                                  │
│ --- LOGS & EVE JSON TELEMETRY ---                                                                │
│ EVE JSON Log:         [X] Enable EVE JSON Log output                                             │
│ EVE Output Type:      (X) FILE   ( ) SYSLOG                                                      │
│ EVE Log Alerts:       [X] Alert events (essential for pfctl Engine)                              │
│ EVE Log HTTP:         [X] Extended HTTP metadata (URI, User-Agent, POST payload)                 │
│ EVE Log TLS:          [X] TLS/SSL handshake metadata                                             │
│ EVE Log File:         /var/log/suricata/eve.json                                                 │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 3.4: GESTIÓN DE FIRMAS ET OPEN Y POLÍTICA `dropsid.conf`

**Ruta en WebGUI:** `Services > Suricata > SID Mgmt` ➔ `Enable Automatic SID Management`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / Suricata / SID Mgmt                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Automatic SID Mgmt:   [X] Enable Automatic SID State Management                                  │
│                                                                                                  │
│ Drop SID List:        [ dropsid.conf                                                           ▼ ] │
│ Edit dropsid.conf:                                                                               │
│   pcre:emerging-sql                                                                              │
│   pcre:emerging-exploit                                                                          │
│   pcre:emerging-current_events                                                                   │
│   pcre:community-web-attacks                                                                     │
│   2008287, 2008288, 2013028, 2013029                                                            │
│                                                                                                  │
│ State Order:          Drop > Enable > Disable                                                    │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# FASE 4: INTELIGENCIA DE AMENAZAS CON pfBlockerNG-devel Y MAXMIND GEOIP

---

### PASO 4.1: CONFIGURACIÓN DE MAXMIND GEOIP FREE TIER

**Ruta en WebGUI:** `Firewall > pfBlockerNG > IP > GeoIP`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Firewall / pfBlockerNG / IP / GeoIP                                              │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MaxMind Account ID:   [ 1024982                    ] (Cuenta Comunitaria Free $0 CLP)            │
│ License Key:          [ ************************** ]                                             │
│                                                                                                  │
│ --- TOP SPAMMERS & THREAT CONTINENTS ---                                                         │
│ Top Spammers:         [ CN, RU, IR, KP, VN, NG                                                 ▼ ] │
│ Action:               ( ) Disabled   ( ) Permit   (X) Deny Inbound   ( ) Deny Both               │
│ Logging:              [X] Enable pfBlockerNG log (/var/log/pfblockerng/ip_block.log)             │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 4.2: FEEDS DE REPUTACIÓN IP GLOBALES (FireHOL & Spamhaus)

**Ruta en WebGUI:** `Firewall > pfBlockerNG > IP > IP Feeds` ➔ `[ + Add ]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Firewall / pfBlockerNG / IP / IP Feeds / Edit                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Group Name:           [ FireHOL_Level1                                                         ] │
│ Description:          [ Listas de Maxima Amenaza C2, Botnets y Scanners Activos                ] │
│ State:                [ ON                                                                     ▼ ] │
│                                                                                                  │
│ Source URL:           [ https://iplists.firehol.org/files/firehol_level1.netset                ] │
│ List Action:          [ Deny Inbound                                                           ▼ ] │
│ Update Frequency:     [ Every 4 Hours                                                          ▼ ] │
│ Automatic Rule Order: [ | pfB_Block (Floating Rules Top Priority)                              ▼ ] │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# FASE 5: PROXY INVERSO HAPROXY 2.8+ Y PROTECCIÓN ANTI-DOS / FUZZING

---

### PASO 5.1: CONFIGURACIÓN DEL BACKEND (DVWA EN DMZ)

**Ruta en WebGUI:** `Services > HAProxy > Backend` ➔ `[ + Add ]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / HAProxy / Backend / Edit: DVWA_DMZ_POOL                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Name:                 [ DVWA_DMZ_POOL                                                          ] │
│ Server list:                                                                                     │
│   • Mode:             [ active                                                                 ▼ ] │
│   • Name:             [ dvwa-target                                                            ] │
│   • Forward to:       [ Address+Port                                                           ▼ ] │
│   • Address:          [ 192.168.20.50                                                          ] │
│   • Port:             [ 80                                                                     ] │
│   • SSL:              [ ] Encrypt connection to backend (HTTP Plano en DMZ interna)              │
│                                                                                                  │
│ --- HEALTH CHECKING ---                                                                          │
│ Health check method:  [ HTTP                                                                   ▼ ] │
│ HTTP check URI:       [ /index.php                                                             ] │
│ Check frequency:      [ 2000 ms                                                                ] │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 5.2: CONFIGURACIÓN DEL FRONTEND SSL Y STICK-TABLES DE RATE LIMITING

**Ruta en WebGUI:** `Services > HAProxy > Frontend` ➔ `[ + Add ]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / HAProxy / Frontend / Edit: KRONOS_HTTPS_VIP                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Name:                 [ KRONOS_HTTPS_FRONTEND                                                  ] │
│ External Address:     [ WAN address (198.51.100.1)                                             ▼ ] │
│ Port:                 [ 443                                                                    ] │
│ Type:                 ( ) HTTP / HTTPS (offloading)   (X) SSL / HTTPS offloading                 │
│ SSL Offloading Cert:  [ KRONOS_LAB_SELF_SIGNED_CERT (RSA 2048 / SHA256)                         ▼ ] │
│                                                                                                  │
│ --- ADVANCED STICK TABLES & RATE LIMITING (Pass thru) ---                                        │
│ Advanced pass thru:   stick-table type ip size 100k expire 30s store http_req_rate(10s),http_err_rate(10s)│
│                       http-request track-sc0 src                                                 │
│                       http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }        │
│                       http-request deny deny_status 403 if { sc_http_err_rate(0) gt 25 }         │
│                                                                                                  │
│ Default Backend:      [ DVWA_DMZ_POOL                                                          ▼ ] │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# FASE 6: MATRIZ DE REGLAS DE FIREWALL ZERO TRUST

---

### PASO 6.1: REGLAS EN INTERFAZ WAN (ACCESO A HAPROXY)

**Ruta en WebGUI:** `Firewall > Rules > WAN`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Firewall / Rules / WAN                                                           │
├──────┬─────────┬──────────────┬───────────────┬────────────────┬───────────────┬─────────────────┤
│ Act  │ Proto   │ Source       │ Port          │ Destination    │ Port          │ Description     │
├──────┼─────────┼──────────────┼───────────────┼────────────────┼───────────────┼─────────────────┤
│ PASS │ IPv4    │ *            │ *             │ WAN address    │ 443 (HTTPS)   │ HAProxy VIP     │
│ PASS │ IPv4    │ *            │ *             │ WAN address    │ 80 (HTTP)     │ Redirect HTTP   │
│ DROP │ IPv4    │ *            │ *             │ *              │ *             │ Default Block   │
└──────┴─────────┴──────────────┴───────────────┴────────────────┴───────────────┴─────────────────┘
```

---

### PASO 6.2: REGLAS EN INTERFAZ DMZ_SERVERS (AISLAMIENTO RIGUROSO)

**Ruta en WebGUI:** `Firewall > Rules > DMZ_SERVERS`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Firewall / Rules / DMZ_SERVERS (VLAN 20)                                         │
├──────┬─────────┬──────────────┬───────────────┬────────────────┬───────────────┬─────────────────┤
│ Act  │ Proto   │ Source       │ Port          │ Destination    │ Port          │ Description     │
├──────┼─────────┼──────────────┼───────────────┼────────────────┼───────────────┼─────────────────┤
│ PASS │ IPv4    │ DMZ_SERVERS  │ *             │ * (DNS/NTP)    │ 53, 123 UDP   │ Salida básica   │
│ DROP │ IPv4    │ DMZ_SERVERS  │ *             │ LAN_CORP (V10) │ *             │ Bloqueo a Corp  │
│ DROP │ IPv4    │ DMZ_SERVERS  │ *             │ MGMT_SEC (V99) │ *             │ Bloqueo a Mgmt  │
│ PASS │ IPv4    │ DMZ_SERVERS  │ *             │ WAN Gateway    │ 80, 443 TCP   │ Salida updates  │
└──────┴─────────┴──────────────┴───────────────┴────────────────┴───────────────┴─────────────────┘
```

---

# FASE 7: ENLACE ZERO TRUST CON TAILSCALE SUBNET ROUTER (VOIP PBX)

---

### PASO 7.1: CONFIGURACIÓN DEL SERVICIO TAILSCALE EN pfSense

**Ruta en WebGUI:** `VPN > Tailscale`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: VPN / Tailscale Settings                                                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Enable Tailscale:     [X] Enable Tailscale service daemon                                        │
│ Auth Key:             [ tskey-auth-k98a-*********************************                      ] │
│ Pre-Auth Key Expire:  [ Never (Academic Portafolio Free Tier)                                   ] │
│ Advertised Routes:    [ 192.168.30.0/24                                                        ] │
│ Accept Subnet Routes: [X] Enable route passing for connected Softphones                          │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# FASE 8: VERIFICACIÓN Y DIAGNÓSTICO EN CONSOLA FREEBSD

Acceder mediante sesión SSH administrativa (`ssh admin@192.168.99.1`):

```bash
# 1. Comprobar que Suricata está ejecutando en hilos Netmap:
ps aux | grep suricata
netstat -i

# 2. Monitorear eventos EVE JSON en tiempo real con jq:
tail -f /var/log/suricata/eve.json | jq '{timestamp, src_ip, dest_ip, alert: .alert.signature}'

# 3. Comprobar la tabla de persistencia en kernel de FreeBSD (snort2c):
pfctl -t snort2c -T show

# 4. Probar atómicamente si una IP atacante está bloqueada en memoria:
pfctl -t snort2c -T test 198.51.100.100

# 5. Forzar la inserción manual de una IP en la tabla de kernel:
pfctl -t snort2c -T add 198.51.100.100

# 6. Eliminar los estados TCP/UDP activos asociados a la IP hostil:
pfctl -k 198.51.100.100
```
