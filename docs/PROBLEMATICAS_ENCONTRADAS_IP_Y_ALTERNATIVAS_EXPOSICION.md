# INFORME TÉCNICO: PROBLEMÁTICAS DE DIRECCIONAMIENTO IP, CGNAT Y ESTRATEGIAS DE EXPOSICIÓN WAN
## Proyecto de Portafolio de Título: KRONOS SENTINEL (APT122)
**Autor:** Bruno Urrea Ortiz | Especialidad en Conectividad, Redes y Ciberseguridad  
**Institución:** Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín  
**Clasificación:** Documento Técnico de Arquitectura de Red y Despliegue Perimetral

---

<p align="center">
  <img src="../assets/sentinel_shield_logo.png" alt="KRONOS SENTINEL Logo" width="300px">
</p>

---

## 1. RESUMEN EJECUTIVO Y DESAFÍO DE INFRAESTRUCTURA

El proyecto **KRONOS SENTINEL** requiere exponer servicios web seguros (HAProxy que publica la aplicación DVWA en DMZ) hacia la red pública de Internet para recibir ataques reales (inyecciones SQL, escaneos de vulnerabilidades) y activar la cadena de respuesta autónoma (Suricata Inline IPS, correlación `pfctl` y llamada telefónica de emergencia vía Asterisk PBX / Gemini Live API).

Al virtualizar **pfSense CE** y los contenedores de soporte en un entorno de laboratorio doméstico (notebook o servidor local), se presentan desafíos críticos de conectividad L3/L4 derivados de la infraestructura de los Proveedores de Servicios de Internet (ISP) residenciales en Chile (Movistar, VTR, Entel, Mundo, Claro).

---

## 2. MATRIZ DE PROBLEMÁTICAS TÉCNICAS IDENTIFICADAS

### 2.1 Carrier-Grade NAT (CGNAT / RFC 6598)
* **Descripción:** Los ISP asignan al router del hogar (ONT/HGU) una dirección IP privada dentro del rango `100.64.0.0/10` en lugar de una IPv4 pública enrutable en Internet.
* **Impacto en KRONOS SENTINEL:** Cualquier intento de reenvío de puertos (*Port Forwarding*) en el router del hogar resulta inútil, ya que el ISP realiza una segunda traslación NAT en sus routers de borde (CGNAT Gateway), haciendo imposible alcanzar la interfaz WAN de pfSense desde el exterior.
* **Comprobación Técnica (Diagnóstico):**
  ```bash
  # 1. Obtener la IP pública vista desde Internet:
  curl -s https://ifconfig.me

  # 2. Comparar con la IP asignada en la WAN del router ISP:
  # Si la IP del router empieza con 100.64.x.x, 10.x.x.x o 172.16.x.x - 172.31.x.x -> ESTÁS BAJO CGNAT.
  
  # 3. Trazado de ruta para detectar salto CGNAT intermedio:
  traceroute -n -m 5 1.1.1.1
  ```

### 2.2 Bloqueo de Puertos Canónicos por Política de Seguridad ISP
* **Descripción:** Los planes residenciales bloquean puertos de entrada canónicos como `80 (HTTP)`, `443 (HTTPS)`, `25 (SMTP)` y `5060 (SIP)` para evitar la operación de servidores en redes hogareñas.
* **Impacto:** Aunque se cuente con IP pública, los paquetes entrantes TCP 80/443 son descartados en la red del ISP antes de llegar al router del hogar.

### 2.3 Doble NAT (Double NAT) y Bloqueo de Redes RFC 1918 en pfSense
* **Descripción:** Si el router ISP entrega una IP privada a la WAN de pfSense (ej. `192.168.1.200/24`) y pfSense crea sus propias subredes internas (`192.168.10.0/24`, `192.168.20.0/24`), se genera un escenario de Doble NAT.
* **Impacto:** pfSense, por defecto, activa la regla de seguridad `Block private networks and loopback addresses` en la interfaz WAN. Si la WAN tiene una IP privada (192.168.x.x), **pfSense descartará silenciosamente todo el tráfico entrante reenviado desde el router ISP**.

---

## 3. ANÁLISIS COMPARATIVO DE ALTERNATIVAS DE EXPOSICIÓN

| Alternativa | Mecanismo Técnico | Viabilidad Técnica | Grado de Complejidad | Dependencia de Terceros |
| :--- | :--- | :---: | :---: | :---: |
| **Opción A: Modo Puente ISP (Bridge Mode)** | ONT en modo puente + PPPoE/DHCP en pfSense WAN | Media | Media | Alta (Requiere ISP sin CGNAT o soporte telefónico) |
| **Opción B: DMZ Host en Router ISP** | DMZ `192.168.1.200` + Desactivar bloqueo RFC 1918 en pfSense | Alta | Baja | Media (Requiere acceso admin a ONT) |
| **Opción C: Túnel WireGuard / Cloud Relay VPS** | VPS con IP Pública fija + Túnel WireGuard hacia pfSense | **Máxima (Recomendada)** | Media | Mínima (Cero dependencia de ISP) |
| **Opción D: Tailscale Subnet Router** | Red Mesh WireGuard para VoIP Asterisk y Softphone CISO | **Máxima (Recomendada)** | Baja | Mínima (Encriptación E2E nativa) |
| **Opción E: Laboratorio Virtual Autónomo (Dual-Host)** | Simulación WAN pública aislada en Proxmox/VMware | **Máxima (Demo Duoc UC)** | Baja | Nula (100% Offline para Defensa) |

---

## 4. GUÍA DE IMPLEMENTACIÓN DETALLADA POR OPCIÓN

---

### OPCIÓN A: MODO PUENTE (BRIDGE MODE) EN ROUTER ISP (EJ. MOVISTAR / ENTEL)

#### Requisitos y Pasos:
1. Acceder a la interfaz de administración del router HGU/ONT (ej. `http://192.168.1.1` con credenciales de instalador).
2. En la configuración de WAN, cambiar el modo de operación de **PPPoE Routing** a **Bridge (Monopuesto / Puente)** en el puerto Ethernet LAN 1 o 4.
3. Conectar el cable de red desde el puerto en puente del router ISP hacia la tarjeta física dedicada a la WAN de pfSense (`vtnet0` / `em0`).
4. En pfSense (**Interfaces > WAN**):
   * Si el ISP requiere credenciales: Configurar **IPv4 Configuration Type: PPPoE** (ingresar usuario y contraseña entregados por el ISP).
   * Si el ISP asigna por DHCP: Configurar **IPv4 Configuration Type: DHCP**.
5. Validar que la interfaz WAN en el Dashboard de pfSense reciba una IPv4 pública real (no perteneciente a `100.64.0.0/10`).

---

### OPCIÓN B: DMZ HOST Y PORT FORWARDING EN ROUTER HOGAR (ESCENARIO DOBLE NAT)

Si no se puede configurar modo puente o se desea mantener el WiFi residencial del hogar funcionando:

```
 [ INTERNET ] ──▶ [ Router ISP (192.168.1.1) ] ── (DMZ a 192.168.1.200) ──▶ [ pfSense WAN (192.168.1.200) ]
                                                                                       │
                                                                                       ▼
                                                                             [ HAProxy / Suricata ]
```

#### Paso 1: Configurar IP Estática en la WAN de pfSense
* **Interfaces > WAN**:
  * IPv4 Configuration Type: `Static IPv4`
  * IPv4 Address: `192.168.1.200 / 24`
  * IPv4 Upstream Gateway: `192.168.1.1` (IP del router ISP).

#### Paso 2: Desactivar Bloqueo RFC 1918 en pfSense (CRÍTICO)
* Ir a **Interfaces > WAN**.
* Al final de la página, **DESMARCAR** la casilla:
  * ❌ `Block private networks and loopback addresses`
  * ❌ `Block bogon networks`
* Hacer clic en **Save** y **Apply Changes**. *(Sin este paso, pfSense descarta el 100% de los paquetes del router ISP)*.

#### Paso 3: Configurar DMZ Host en el Router ISP
* En el menú del router ISP (HGU), ir a **Seguridad > DMZ (Zona Desmilitarizada)**.
* Habilitar DMZ y apuntar a la IP: `192.168.1.200`.
* Esto reenviará automáticamente todos los puertos TCP/UDP entrantes hacia pfSense.

---

### OPCIÓN C: RELAY EN LA NUBE CON TÚNEL WIREGUARD (BYPASS TOTAL DE CGNAT)

Esta es la solución más robusta y profesional en ciberseguridad cuando el ISP tiene CGNAT estricto:

```
 [ ATACANTE WAN ] ──▶ [ Cloud VPS (IP Pública Fija: 203.0.113.10) ]
                                    │ (Túnel WireGuard Cifrado)
                                    ▼
                         [ pfSense WAN / HAProxy ] ──▶ [ DVWA DMZ ]
```

1. Se despliega un VPS en Oracle Cloud (Free Tier) o DigitalOcean (\$4 USD) con una IPv4 pública fija (`203.0.113.10`).
2. Se levanta un túnel WireGuard punto a punto entre el VPS (`10.50.0.1`) y pfSense (`10.50.0.2`).
3. En el VPS, se configuran reglas `iptables` de reenvío de puertos para redirigir el tráfico 80 y 443 a través del túnel:
   ```bash
   # En el VPS en la nube:
   sysctl -w net.ipv4.ip_forward=1
   iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.50.0.2:80
   iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 10.50.0.2:443
   iptables -t nat -A POSTROUTING -o wg0 -j MASQUERADE
   ```
4. El atacante ataca `https://203.0.113.10`, el tráfico entra por la interfaz WireGuard de pfSense, Suricata lo inspecciona en modo Inline IPS, HAProxy lo procesa y se dispara la alerta sin importar si tu casa tiene CGNAT.

---

### OPCIÓN D: INTEGRACIÓN DE TAILSCALE SUBNET ROUTER EN pfSense PARA ASTERISK PBX

Para evitar exponer los puertos de telefonía SIP (`5060 UDP`) y RTP (`10000-10100 UDP`) a escáneres maliciosos de Internet, se implementa una **Red Mesh Zero Trust con Tailscale**:

```
 [ Softphone CISO (Laptop/Celular) ] ── (Tailscale Tunnel 100.x.y.z) ──▶ [ pfSense Tailscale Subnet Router ]
                                                                                       │
                                                                                       ▼ (Ruta 192.168.30.0/24)
                                                                           [ Asterisk PBX 192.168.30.50 ]
```

#### Paso 1: Instalación de Tailscale en pfSense
1. Ir a **System > Package Manager > Available Packages**.
2. Buscar `tailscale` e instalar el paquete oficial `pfSense-pkg-tailscale`.

#### Paso 2: Autenticación y Publicación de Subredes (Subnet Router)
1. Navegar a **VPN > Tailscale**.
2. En **Authentication**, ingresar la clave de autenticación generada en la consola de Tailscale (*Auth Key*).
3. En **Advertised Routes**, ingresar la subred de telefonía VoIP:
   * `192.168.30.0/24`
4. Marcar **Accept Routes** y **Save**.

#### Paso 3: Aprobación de la Subred en la Consola Tailscale Admin
1. Ingresar a `https://login.tailscale.com/admin/machines`.
2. Ubicar el nodo `pfSense`.
3. En **Edit route settings**, aprobar la ruta `192.168.30.0/24`.

#### Paso 4: Conexión del Softphone del CISO
1. El CISO inicia sesión en la aplicación **Tailscale** en su notebook o smartphone.
2. Abre su softphone SIP (Zoiper, Linphone, MicroSIP o Grandstream Wave).
3. Configura el anexo SIP:
   * **Domain / SIP Server:** `192.168.30.50` (IP directa de Asterisk en la VLAN 30).
   * **User:** `1001` (Bruno Urrea) o anexo correspondiente.
   * **Secret:** `Bruno1001SecureKey#2026`
4. El softphone se registra de manera instantánea y segura a través del túnel cifrado WireGuard de Tailscale, listo para recibir las llamadas de emergencia generadas por el **Agente Gemini Live**.

---

### OPCIÓN E: ENTORNO DE LABORATORIO VIRTUAL AUTÓNOMO (PARA DEFENSA PRESENCIAL EN DUOC UC)

Para garantizar que la demostración en la comisión examinadora de Duoc UC funcione de forma autónoma sin depender de la conexión WiFi o firewall de la sede:

```
 [ VM Atacante (Kali Linux) ] ── (Red WAN Virtual: 198.51.100.100) ──▶ [ pfSense WAN (198.51.100.1) ]
                                                                                │
                                                                                ▼ (VLANs 10, 20, 30)
                                                                    [ DMZ / HAProxy / Asterisk ]
```

1. **Hipervisor (Proxmox VE / VMware Workstation):**
   * **Virtual Switch WAN (`vmbr1` o `VMnet2`):** Red aislada `198.51.100.0/24`.
   * **pfSense WAN:** IP `198.51.100.1/24`.
   * **Kali Linux (Atacante):** IP `198.51.100.100/24` con Gateway `198.51.100.1`.
2. **Ejecución del Ataque en Vivo:**
   * Desde Kali Linux se ejecuta: `sqlmap -u "https://198.51.100.1/vulnerabilities/sqli/?id=1&Submit=Submit" --cookie="..." --batch`.
   * Suricata en pfSense intercepta el ataque en tiempo real, `pfctl` bloquea la IP `198.51.100.100`, Asterisk dispara la llamada hacia el softphone en la máquina anfitriona y Gemini Live realiza el debriefing de voz en vivo frente a la comisión.

---

## 5. CONCLUSIÓN Y RECOMENDACIÓN TÁCTICA PARA EL PROYECTO

1. **Para Pruebas Remotas desde Internet:** Implementar la **Opción C (Túnel WireGuard en Cloud VPS)** para el tráfico web WAN hacia HAProxy y la **Opción D (Tailscale Subnet Router)** para el registro seguro del Softphone del CISO con Asterisk PBX.
2. **Para la Defensa Final en Sede Duoc UC:** Utilizar la **Opción E (Laboratorio Virtual Autónomo)**, garantizando un rendimiento determinista con latencia cero y total independencia de redes externas.
