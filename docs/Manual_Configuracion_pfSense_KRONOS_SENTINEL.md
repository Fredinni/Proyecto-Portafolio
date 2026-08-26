# MANUAL MAESTRO DE CONFIGURACIÓN Y HARDENING PERIMETRAL: pfSense CE 2.7.2
## Proyecto: KRONOS SENTINEL (APT122) — Autonomous AI-IPS & Voice SOAR
**Autor:** Bruno Urrea Ortiz | Especialidad en Conectividad, Redes y Ciberseguridad  
**Institución:** Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín  
**Documento Técnico:** Portafolio de Título APT122 // Manual de Despliegue y Configuración de Laboratorio

---

<p align="center">
  <img src="../assets/sentinel_shield_logo.png" alt="KRONOS SENTINEL Logo" width="350px">
</p>

---

# PARTE 1: GUÍA PASO A PASO POR INTERFAZ GRÁFICA (WebGUI)

---

### MÓDULO 1: SETUP BASE, ASIGNACIÓN DE INTERFACES Y SEGMENTACIÓN DE VLANs (802.1Q)

#### 1.1 Topología de Interfaces Físicas y Asignaciones
* **Interfaz WAN Física (`vtnet0` / `em0`):** Conexión hacia Uplink / Internet / Gateway ISP.
* **Interfaz LAN Troncal Trunk 802.1Q (`vtnet1` / `em1`):** Enlace troncal hacia switch de distribución Cisco L2/L3 o Proxmox Linux Bridge (`vmbr0`).

#### 1.2 Creación de VLANs en pfSense
1. Navegar a **Interfaces > Assignments > VLANs**.
2. Hacer clic en **+ Add** y configurar la siguiente matriz de segmentación:

| VLAN Tag | Parent Interface | Nombre de Interfaz | Subred IPv4 | Gateway pfSense | Propósito Táctico |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **VLAN 10** | `vtnet1` | `VLAN10_CORP` | `192.168.10.0/24` | `192.168.10.1` | Estaciones de trabajo corporativas y red interna. |
| **VLAN 20** | `vtnet1` | `VLAN20_DMZ` | `192.168.20.0/24` | `192.168.20.1` | Zona Desmilitarizada (DVWA Web App / Servidores expuestos). |
| **VLAN 30** | `vtnet1` | `VLAN30_VOIP` | `192.168.30.0/24` | `192.168.30.1` | Telefonía VoIP, Centralita Asterisk PBX y enlaces SIP. |
| **VLAN 99** | `vtnet1` | `VLAN99_MGMT` | `192.168.99.0/24` | `192.168.99.1` | Administración Out-of-Band (SSH pfSense, Proxmox, WebGUI). |

3. En **Interfaces > Assignments > Interface Assignments**, mapear los adaptadores virtuales a los nombres lógicos:
   * `OPT1` → `VLAN10_CORP` en `vtnet1.10`
   * `OPT2` → `VLAN20_DMZ` en `vtnet1.20`
   * `OPT3` → `VLAN30_VOIP` en `vtnet1.30`
   * `OPT4` → `VLAN99_MGMT` en `vtnet1.99`
4. Habilitar cada interfaz marcando **Enable Interface**, asignar **IPv4 Configuration Type: Static IPv4**, definir la IP estática y máscara `/24`. Guardar y **Apply Changes**.

#### 1.3 Configuración de Servidores DHCP
1. Dirigirse a **Services > DHCP Server**.
2. Habilitar DHCP en **VLAN10_CORP** (Rango: `192.168.10.100` - `192.168.10.200`, DNS: `192.168.10.1`).
3. En **VLAN20_DMZ**, configurar reservas estáticas (Static DHCP Mapping) para el host DVWA Docker:
   * IP Asignada: `192.168.20.50` (o `192.168.100.50` según esquema DMZ).
   * MAC Address: Dirección MAC del contenedor o VM objetivo.
4. En **VLAN30_VOIP**, asignar IP estática al contenedor Asterisk PBX: `192.168.30.50`.

---

### MÓDULO 2: DESPLIEGUE Y HARDENING DE SURICATA EN MODO INLINE IPS (NETMAP ENGINE)

#### 2.1 Instalación de Paquetes
1. Ir a **System > Package Manager > Available Packages**.
2. Buscar `suricata` e instalar la versión oficial `pfSense-pkg-suricata` (Suricata 7.x).

#### 2.2 Configuración Global de Firmas (Global Settings)
1. Navegar a **Services > Suricata > Global Settings**.
2. **Rule Categories Setup:**
   * Habilitar **Emerging Threats (ET) Open Rules** o **ET Pro Telemetry Edition**.
   * Habilitar **Snort Community Rules** y **GPLv2 Rules**.
3. **Automatic Rule Update:**
   * Update Interval: `Every 12 Hours` (o `Daily` a las 02:00 UTC).
4. Guardar cambios y dirigirse a la pestaña **Updates** para forzar la primera descarga de reglas (**Update Rules**).

#### 2.3 Configuración de Interfaz WAN en Modo Inline IPS
1. Ir a **Services > Suricata > Interfaces** y añadir la interfaz `WAN` (`vtnet0`).
2. En **General Settings**:
   * Description: `KRONOS_WAN_INLINE_IPS`.
   * Enable: Marcar casilla.
3. En **Control / Inspection Settings**:
   * **IPS Mode:** Seleccionar **Inline IPS Mode** *(Crítico: Utiliza el subsystem `netmap(4)` de FreeBSD para interceptar y descartar paquetes en el ring buffer de la tarjeta sin pasar por la cola de red del kernel si coinciden con reglas DROP)*.
   * **Block Offenders:** Seleccionar `Both` (Bloquea tráfico entrante y saliente).
   * **Kill States:** Habilitado (Mata estados TCP/UDP existentes inmediatamente cuando se genera una alerta/drop).
4. **EVE JSON Output Log Settings (Telemetría para KRONOS Engine):**
   * **EVE JSON Log:** Habilitar.
   * **EVE Output Type:** `FILE`.
   * **EVE Log Full Filename:** `/var/log/suricata/eve.json`.
   * **EVE Logged Info:** Marcar `ALERTS`, `HTTP`, `TLS`, `DNS`, `SSH`, `DROP`, `FILES`.
5. En **WAN Rules / Categories**:
   * Activar categorías de alto impacto: `emerging-sqli.rules`, `emerging-exploit.rules`, `emerging-web_server.rules`, `emerging-attack_response.rules`, `emerging-scan.rules`.
   * En **SID Mgmt**, habilitar política de transformación de alertas a bloqueo forzado (`dropsid.conf`).
6. Iniciar el motor Suricata en la interfaz WAN y validar estado **Running (Verde)**.

---

### MÓDULO 3: pfBlockerNG-devel CON INTELIGENCIA GeoIP Y FEEDS DE REPUTACIÓN

#### 3.1 Integración de Licencia MaxMind GeoLite2
1. Ir a **System > Package Manager** e instalar `pfBlockerNG-devel`.
2. Navegar a **Firewall > pfBlockerNG > IP > MaxMind GeoIP configuration**.
3. Ingresar la clave de licencia gratuita obtenida desde la cuenta MaxMind:
   * **MaxMind License Key:** `[TU_MAXMIND_LICENSE_KEY]`
   * **Account ID:** `[TU_MAXMIND_ACCOUNT_ID]`
4. Guardar y verificar que la base de datos descargue en `/usr/local/share/GeoIP/`.

#### 3.2 Bloqueo Geográfico Inbound (Top Spammers & High-Risk Continents)
1. Ir a **Firewall > pfBlockerNG > IP > GeoIP**.
2. En la categoría **Top Spammers**:
   * Action: **Deny Inbound** (Genera reglas de bloqueo automático en WAN para países con alto índice de ataques).
3. En la categoría **Asia / Europe / Africa** (según política corporativa):
   * Seleccionar países sin operaciones comerciales legítimas y aplicar **Deny Inbound**.

#### 3.3 Configuración de Feeds de Reputación IP (IPv4 Blacklists)
1. Navegar a **Firewall > pfBlockerNG > IP > IP Feeds**.
2. Añadir los feeds de inteligencia contra botnets y C2:

| Nombre del Feed | URL de Descarga | List Action | Update Freq |
| :--- | :--- | :---: | :---: |
| **FireHOL_L1** | `https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset` | `Deny Inbound` | `Every 6 Hours` |
| **ET_Compromised** | `https://rules.emergingthreats.net/blockrules/compromised-ips.txt` | `Deny Inbound` | `Every 12 Hours` |
| **Spamhaus_DROP** | `https://www.spamhaus.org/drop/drop.txt` | `Deny Both` | `Daily` |
| **AbuseIPDB_Top** | `https://api.abuseipdb.com/api/v2/blacklist` | `Deny Inbound` | `Daily` |

3. Ir a **Firewall > pfBlockerNG > Update** y ejecutar **Force > Reload > All**. Validar que se creen los alias automáticos `pfB_FireHOL_L1_v4`, `pfB_Top_Spammers_v4`, etc.

---

### MÓDULO 4: REVERSE PROXY HAProxy CON TERMINACIÓN SSL/TLS Y PUBLICACIÓN DMZ

#### 4.1 Configuración de Backend DMZ (`bk_dvwa_dmz`)
1. Ir a **Services > HAProxy > Backend**.
2. Clic en **Add**:
   * **Name:** `bk_dvwa_dmz`
   * **Mode:** `HTTP`
   * **Balance:** `Round Robin`
   * **Server list:**
     * Name: `dvwa_node1`
     * Address: `192.168.20.50` (o `192.168.100.50`)
     * Port: `80`
     * Encrypt (SSL): `No` (Terminación SSL en el Proxy)
   * **Health checking:**
     * Check type: `HTTP`
     * HTTP check method: `OPTIONS` o `GET`
     * HTTP check URI: `/login.php`
     * Interval: `3000ms`, Fall: `3`, Rise: `2`
   * **Advanced settings:**
     * `option forwardfor` (Inyecta encabezado `X-Forwarded-For`).
     * `http-request set-header X-Forwarded-Proto https if { ssl_fc }`.

#### 4.2 Configuración de Frontend WAN (`http_in`)
1. Ir a **Services > HAProxy > Frontend**.
2. Clic en **Add**:
   * **Name:** `fe_wan_https`
   * **Status:** `Active`
   * **External address:**
     * Listen address: `WAN address`, Port: `80`
     * Listen address: `WAN address`, Port: `443`, SSL Offloading marcado
   * **SSL Offloading:** Seleccionar el certificado digital emitido para KRONOS (ej. `kronos_wildcard.pem` o Let's Encrypt ACME).
   * **Redirect HTTP to HTTPS:** Añadir acción en `Actions`: `http-request redirect scheme https unless { ssl_fc }`.
   * **Rate Limiting (Mitigación DoS L7 en memoria):**
     * Configurar Stick-table: `table type ip size 100k expire 30s store http_req_rate(10s)`.
     * Acción: `http-request track-sc0 src`
     * Acción: `http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }`
   * **Default Backend:** Seleccionar `bk_dvwa_dmz`.
3. Guardar y **Apply Changes**.

---

### MÓDULO 5: MATRIZ DE REGLAS DE FIREWALL Y POLÍTICA ZERO TRUST

| Interfaz | Acción | Origen | Destino | Puerto / Protocolo | Descripción |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **WAN** | `PASS` | `*` | `WAN Address` | `80, 443 (TCP)` | Tráfico web público hacia el Frontend de HAProxy. |
| **DMZ** | `BLOCK` | `DMZ net` | `LAN net / MGMT net` | `*` | Aislamiento total: Bloquea cualquier pivotaje hacia LAN o MGMT. |
| **DMZ** | `BLOCK` | `DMZ net` | `pfSense IP` | `80, 443, 22 (TCP)` | Hardening: Impide acceso a WebGUI o SSH de pfSense desde DMZ. |
| **VoIP** | `PASS` | `VoIP net` | `192.168.30.50` | `5060 (UDP/TCP)` | Señalización SIP PJSIP para Asterisk PBX. |
| **VoIP** | `PASS` | `VoIP net` | `192.168.30.50` | `10000:10100 (UDP)` | Canales de audio RTP de voz bidireccional. |

---

### MÓDULO 6: RECOLECCIÓN Y CENTRALIZACIÓN DE LOGS (TELEMETRÍA LAN, WAN, DMZ Y SYSLOG REMOTO)

Para que el motor **KRONOS SENTINEL** y los analistas del SOC obtengan visibilidad completa de amenazas perimetrales (Norte-Sur) y movimiento lateral interno (Este-Oeste), se implementa una arquitectura de telemetría multi-capa:

#### 6.1 Inspección Suricata en Interfaces Internas (LAN y DMZ)
1. Navegar a **Services > Suricata > Interfaces** y hacer clic en **+ Add**.
2. Crear instancia para **LAN (`vtnet1.10`)** y **DMZ (`vtnet1.20`)**:
   * **Propósito:** Captura la IP de origen real del atacante o host comprometido **antes de cualquier traslación NAT o proxying**.
   * **Detección Interna:** Movimiento lateral, escaneo de puertos interno, balizas de Command & Control (C2) y exfiltración de datos.
3. En **EVE JSON Log Settings**:
   * EVE Log: `Enabled` | Output: `FILE` (`/var/log/suricata/eve.json`).
   * Información registrada: `ALERTS`, `HTTP`, `TLS`, `DNS`, `SSH`, `DROP`.

#### 6.2 Configuración de Syslog Remoto Centralizado (SIEM / SIEM Forwarder)
1. Ir a **Status > System Logs > Settings**.
2. En la sección **Remote Logging Options**:
   * **Enable Remote Logging:** Marcar casilla.
   * **Remote Log Servers:** Ingresar IP y puerto del servidor de ingesta / colector KRONOS (ej. `192.168.99.100:514` o `127.0.0.1:5140`).
   * **Remote Syslog Contents:**
     * Marcar `Firewall Events` (Eventos de filtrado `filterlog`).
     * Marcar `DHCP Service Events` (Mapeo dinámico de IPs a MACs).
     * Marcar `HAProxy` (Peticiones HTTP L7 y códigos de estado).
     * Marcar `DNS Resolver Events` (Consultas Unbound DNS para detección de dominios DGA).
3. Guardar y **Apply Changes**.

---

# PARTE 2: GUÍA AVANZADA MEDIANTE CLI / SHELL DE FREEBSD

---

### 2.1 Manipulación Directa de Tablas de Kernel con `pfctl`

El comando `pfctl` interactúa directamente con el módulo de filtrado de paquetes del kernel de FreeBSD. KRONOS SENTINEL utiliza estas primitivas para inspección y aislamiento quirúrgico:

```bash
# 1. Listar todas las IPs bloqueadas en la tabla snort2c:
pfctl -t snort2c -T show

# 2. Test atómico en kernel (Retorna 0 si existe, 1 si no existe):
pfctl -t snort2c -T test 185.220.101.5

# 3. Insertar dinámicamente una IP hostil en la tabla de bloqueo inmediato:
pfctl -t snort2c -T add 185.220.101.5

# 4. Eliminar una IP de la tabla de bloqueo (Resolución de Falsos Positivos):
pfctl -t snort2c -T delete 192.168.10.45

# 5. Purgar y terminar estados de conexión TCP/UDP activos de una IP atacante:
pfctl -k 185.220.101.5
pfctl -k 0.0.0.0/0 -k 185.220.101.5

# 6. Consultar estadísticas de memoria de tablas en kernel:
pfctl -vvsTables | grep -A 8 snort2c
```

---

### 2.2 Sintonización de Alto Rendimiento para Netmap y Tablas pf

```bash
# Aumentar límite máximo de entradas en tablas pf a 4 Millones:
sysctl net.pf.request_maxcount=4000000

# Optimizar ring buffers del subsystem netmap(4) para evitar sobrecargas:
sysctl dev.netmap.ring_size=4096
sysctl dev.netmap.buf_size=2048
```

---

### 2.3 Servicio Init Autónomo en FreeBSD (`/usr/local/etc/rc.d/kronos_sentinel.sh`)

```bash
#!/bin/sh
# PROVIDE: kronos_sentinel
# REQUIRE: NETWORKING suricata
# KEYWORD: shutdown

. /etc/rc.subr

name="kronos_sentinel"
rcvar="kronos_sentinel_enable"
command="/usr/local/bin/python3"
command_args="/usr/local/share/kronos_sentinel/log_correlator.py > /var/log/kronos_engine.log 2>&1 &"

load_rc_config $name
: ${kronos_sentinel_enable:="YES"}

run_rc_command "$1"
```

---

### 2.4 Diagnóstico y Captura de Logs en Kernel (`pflog` & `eve.json`)

```bash
# 1. Monitoreo en vivo de paquetes bloqueados en la interfaz LAN (vtnet1.10):
tcpdump -nei pflog0 -vv 'action block and inbound and in_iface vtnet1.10'

# 2. Volcado en tiempo real de eventos EVE JSON de Suricata (LAN & WAN):
tail -F /var/log/suricata/eve.json | jq 'select(.event_type=="alert") | {timestamp, in_iface, src_ip, dest_ip, alert: .alert.signature}'

# 3. Inspección del archivo de logs estructurado del firewall (filterlog):
tail -F /var/log/filter.log | awk -F',' '{print "Regla: "$1" | Interfaz: "$5" | Acción: "$7" | Origen: "$10" -> Destino: "$11}'

# 4. Verificación de conectividad Syslog remota UDP hacia el colector KRONOS:
nc -u -z -v -w 2 192.168.99.100 514
```
