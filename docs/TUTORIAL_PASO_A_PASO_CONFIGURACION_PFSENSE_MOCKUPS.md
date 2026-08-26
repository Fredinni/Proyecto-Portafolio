# TUTORIAL PASO A PASO: CONFIGURACIÓN MAESTRA DE pfSense CE 2.9.0
## Simulación Visual de WebGUI y Parámetros Oficiales para KRONOS SENTINEL
**Autor:** Bruno Urrea Ortiz | Especialidad en Conectividad, Redes y Ciberseguridad  
**Institución:** Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín  
**Proyecto:** Portafolio de Título (APT122) — Arquitectura de Costo Cero ($0 CLP)  
**Entorno de Validación:** FreeBSD 14.0-CURRENT / pfSense CE 2.9.0 (amd64)

---

<p align="center">
  <img src="../assets/sentinel_shield_logo.png" alt="KRONOS SENTINEL Logo" width="280px">
</p>

---

## 📌 GUÍA TÉCNICA Y BLUEPRINT VISUAL DE CONFIGURACIÓN

Este documento constituye la guía oficial y tutorial paso a paso para reproducir la configuración exacta del firewall **pfSense CE 2.9.0** en el laboratorio de titulación. Cada paso incluye el **árbol de navegación oficial**, la **representación visual de la interfaz WebGUI** y los **valores obligatorios de cada campo**.

---

### PASO 1: CONFIGURACIÓN DE TRONCAL 802.1Q Y CREACIÓN DE VLANs

**Ruta en WebGUI:** `Interfaces > Assignments > VLANs` ➔ `[ + Add ]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Interfaces / VLANs / Edit                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Parent Interface:     [ vtnet1 (LAN Trunk Physical Interface)                                 ▼ ] │
│ VLAN Tag:             [ 10                                                                      ] │
│ VLAN Priority:        [ 0                                                                       ] │
│ Description:          [ VLAN_10_CORP_INTERNAL                                                   ] │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

* **Repetir para todas las subredes del proyecto:**
  * **VLAN 10 (Corporativa):** Tag `10` | Parent `vtnet1` | Asignación: `LAN_CORP` (`192.168.10.1/24`)
  * **VLAN 20 (DMZ Web):** Tag `20` | Parent `vtnet1` | Asignación: `DMZ_SERVERS` (`192.168.20.1/24`)
  * **VLAN 30 (Telefonía VoIP):** Tag `30` | Parent `vtnet1` | Asignación: `VOIP_PBX` (`192.168.30.1/24`)
  * **VLAN 99 (Administración):** Tag `99` | Parent `vtnet1` | Asignación: `MGMT_SEC` (`192.168.99.1/24`)

---

### PASO 2: SERVIDOR DHCP Y RESERVAS ESTÁTICAS DE IP (DVWA Y ASTERISK)

**Ruta en WebGUI:** `Services > DHCP Server > [DMZ_SERVERS]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / DHCP Server / DMZ_SERVERS                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Enable:               [X] Enable DHCP server on DMZ_SERVERS interface                            │
│ Subnet:               192.168.20.0 / Subnet Mask: 255.255.255.0 / Available Range: .1 to .254    │
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

* **Reserva en VLAN 30 VoIP (`Services > DHCP Server > VOIP_PBX`):**
  * MAC Address: `02:42:c0:a8:1e:32` | IP Address: `192.168.30.50` | Hostname: `asterisk-pbx-core`

---

### PASO 3: SURICATA 7.X — MODO INLINE IPS NETMAP Y TELEMETRÍA EVE JSON

**Ruta en WebGUI:** `Services > Suricata > Interfaces > Edit [WAN]`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / Suricata / Interfaces / WAN Settings                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Enable Interface:     [X] Enable Suricata inspection on this interface                           │
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
│ EVE Log File:         /var/log/suricata/eve.json                                                 │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 4: GESTIÓN DE FIRMAS ET OPEN Y POLÍTICA ATÓMICA `dropsid.conf`

**Ruta en WebGUI:** `Services > Suricata > SID Mgmt` ➔ `Enable Automatic SID Management`

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ pfSense WebGUI: Services / Suricata / SID Mgmt                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Automatic SID Mgmt:   [X] Enable Automatic SID State Management                                  │
│                                                                                                  │
│ Drop SID List:        [ dropsid.conf                                                           ▼ ] │
│ Content of dropsid:                                                                              │
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

### PASO 5: pfBlockerNG-devel — GEOIP MAXMIND Y LISTAS DE REPUTACIÓN IP

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
│ --- IP THREAT FEEDS (FireHOL L1 & Spamhaus DROP) ---                                             │
│ Feed 1: FireHOL_L1    URL: https://iplists.firehol.org/files/firehol_level1.netset | Action: Deny│
│ Feed 2: Spamhaus_DROP URL: https://www.spamhaus.org/drop/drop.txt                   | Action: Deny│
│ Update Frequency:     [ Every 4 Hours                                                          ▼ ] │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 6: HAPROXY 2.8+ — FRONTEND SSL Y STICK-TABLES ANTI-FUZZING

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
│ --- ADVANCED STICK TABLES & RATE LIMITING ---                                                    │
│ Advanced pass thru:   stick-table type ip size 100k expire 30s store http_req_rate(10s),http_err_rate(10s)│
│                       http-request track-sc0 src                                                 │
│                       http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }        │
│                       http-request deny deny_status 403 if { sc_http_err_rate(0) gt 25 }         │
│                                                                                                  │
│ Default Backend:      [ DVWA_DMZ_POOL                                                          ▼ ] │
│                       Address: 192.168.20.50 | Port: 80 | Health Check: HTTP GET /index.php      │
│                                                                                                  │
│                       [ Save ]   [ Apply Changes ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PASO 7: MATRIZ DE REGLAS DE FIREWALL ZERO TRUST

**Ruta en WebGUI:** `Firewall > Rules > [WAN / DMZ_SERVERS / VOIP_PBX]`

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

### PASO 8: TAILSCALE SUBNET ROUTER PARA TELEFONÍA ASTERISK PBX

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

### PASO 9: VERIFICACIÓN EN CONSOLA FREEBSD (CLI DE DIAGNÓSTICO)

Acceder por SSH al firewall (`ssh admin@192.168.99.1`):

```bash
# 1. Comprobar que Suricata está capturando en modo netmap:
ps aux | grep suricata
netstat -i

# 2. Monitorear eventos EVE JSON en tiempo real:
tail -f /var/log/suricata/eve.json | jq '{timestamp, src_ip, dest_ip, alert: .alert.signature}'

# 3. Comprobar la tabla atómica de bloqueo en memoria del kernel:
pfctl -t snort2c -T show

# 4. Probar atómicamente si una IP atacante está bloqueada:
pfctl -t snort2c -T test 198.51.100.100
```
