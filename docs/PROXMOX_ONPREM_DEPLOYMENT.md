# KRONOS SENTINEL — despliegue on-premise

Despliegue iniciado el 22 de septiembre de 2026; actualizado el 23 después de instalar CE 2.9. No modifica los hitos académicos: A1 permanece completado/probado en su entorno previo, A2 en ejecución y A3–A9 planificados. Una VM creada no completa una actividad.

## Estado y evidencia

Este documento distingue **PROVISIONED** (recurso creado), **CONFIGURED** (configuración aplicada), **TESTED** (prueba ejecutada con resultado) y **VALIDATED** (requisitos funcionales completos comprobados). Las pruebas de red indicadas abajo se ejecutaron sobre CE instalado; los servicios de aplicación se clasifican por separado.

Estado comprobado: VMs100–105 y bridges vmbr2/vmbr3 existen; **pfSense CE2.9 está instalado**, WAN `10.254.254.2/30` y VLANs99/10/20/30 operativas. Se probaron handshake AWS, DNS y salida con EIP `100.50.147.57`, pruebas negativas inter-VLAN y preservación del origen público `un cliente externo` capturado en `vtnet0`. DVWA y MariaDB corren en DMZ; Asterisk está provisionado, mientras AMI y Gemini siguen pendientes. Las seis VMs tienen un usuario de trabajo `kronos` con contraseña propia; se probó SSH real a todas desde MGMT y login WebGUI de pfSense, incluso tras reiniciar las VMs. MGMT está **Running/Online** en la tailnet separada del equipo `tailnet KRONOS del equipo`; la ruta `10.254.254.1/32` ya está aprobada y TCP22 respondió desde esta PC de esa tailnet; falta probar autenticación desde los dispositivos de cada compañero.

El inventario previo, los identificadores del plano administrativo y los logs crudos se conservan localmente fuera del control de versiones. Este documento publica solo el inventario KRONOS necesario para el equipo.

Nodo `pve`, Proxmox VE `9.2.11`, standalone, SSH/WebGUI `[IP privada de Proxmox]`. Solo el **operador de infraestructura** administra Proxmox mediante su tailnet y el subnet router **RProxy**, `[IP Tailscale del operador]`, que anuncia `10.10.20.0/24`. La tailnet separada del equipo usa KRONOS-MGMT y no anuncia esa red ni Proxmox. El host Proxmox **no tiene Tailscale instalado**. No se modificaron las VMs ajenas 200/300/500/600.

Se seleccionó `VM-SSD` (ZFS sparse, images/rootdir): aproximadamente 131 GiB libres antes del despliegue, frente a unos 18 GiB en el pool del sistema. ISO storage `local`, `/var/lib/vz/template/iso/`. CPU: 72 hilos lógicos; RAM disponible previa aproximada 32 GiB. Los discos virtuales de las seis VMs suman 95 GiB; clones vinculados comparten base. El espacio lógico no equivale al consumido: vigilar `pvesm status` y no eliminar la plantilla de la que dependen los clones. Snapshots consumen bloques conforme cambian los discos.

## Red realmente creada

| Función | Nombre real | Configuración |
|---|---|---|
| Uplink/administración existente | vmbr0 | [IP privada de Proxmox]/24, eno4, gateway host [gateway privado del host]; conservado |
| WAN_TRANSIT | vmbr2 | aislado, sin NIC física, sin IP/gateway del host |
| Trunk protegido | vmbr3 | aislado, VLAN-aware 10/20/30/99, sin NIC física ni IP/gateway del host |

Los nombres conceptuales `vmbr-kronos-wan` y `vmbr-kronos-trunk` se implementan como `vmbr2` y `vmbr3`, compatibles con las restricciones de nombres del sistema. Proxmox no se configura como router entre VLANs.

## Inventario asignado

| VMID | Nombre | CPU | RAM MiB | Disk GiB | NIC/bridge y VLAN | IPv4 / gateway objetivo | Estado |
|---|---|---:|---:|---:|---|---|---|
| 100 | KRONOS-EDGE | 1 | 1024 | 10 | net0 vmbr0 DHCP; net1 vmbr2 | [gateway privado del host]18 DHCP / uplink DHCP; 10.254.254.1/30 sin GW; wg0 10.255.255.2/30 | PROVISIONED; túnel CONFIGURED y handshake TESTED |
| 101 | KRONOS-PFSENSE | 2 | 4096 | 20 | net0 vmbr2; net1 vmbr3 trunk | WAN 10.254.254.2/30 / 10.254.254.1 | PROVISIONED / CONFIGURED; red y gestión TESTED tras reboot |
| 102 | KRONOS-DMZ | 2 | 2048 | 20 | net0 vmbr3 tag20 | 192.168.20.50/24 / 192.168.20.1 | PROVISIONED / CONFIGURED; DVWA HTTP y base TESTED; HAProxy pendiente |
| 103 | KRONOS-VOIP | 2 | 4096 | 25 | net0 vmbr3 tag30 | 192.168.30.50/24 / 192.168.30.1 | PROVISIONED / CONFIGURED; Asterisk container y CLI TESTED; AMI/Gemini pendientes |
| 104 | KRONOS-CORP-TEST | 1 | 1024 | 10 | net0 vmbr3 tag10 | 192.168.10.50/24 / 192.168.10.1 | PROVISIONED / CONFIGURED; VLAN operativa |
| 105 | KRONOS-MGMT | 1 | 1024 | 10 | net0 vmbr3 tag99 | 192.168.99.10/24 / 192.168.99.1 | PROVISIONED / CONFIGURED; Tailscale Running/Online en tailnet separada; prueba desde compañero pendiente |
| 106 | ubuntu-2404-kronos-template | — | — | base compartida | plantilla cloud-init Ubuntu 24.04 amd64 | sin función de router | Pendiente evidencia final |

Tags de proyecto: `kronos`, `title-lab`, `managed-by-codex`. MACs, estados de arranque y snapshots se deben contrastar con `qm config <VMID>` y la evidencia final. Orden objetivo: EDGE 1, pfSense 2, MGMT 3, DMZ 4, VOIP 5, CORP 6; primero debe estar disponible el uplink y luego el firewall.

MACs obtenidas mediante `qm config`: Edge uplink/net0 `BC:24:11:91:C4:4C`, transit/net1 `BC:24:11:32:29:4D`; pfSense WAN/net0 `BC:24:11:E0:13:8F`, trunk/net1 `BC:24:11:8D:97:48`; DMZ `BC:24:11:7B:A3:8D`; VOIP `BC:24:11:1A:5C:95`; CORP `BC:24:11:BE:29:82`; MGMT `BC:24:11:4B:98:D3`. Todos tienen `onboot=1` y orden 1/2/4/5/6/3 respectivamente. Los snapshots base se conservan. Para restaurar el estado con cuentas del equipo usar `team-access-edge`, `team-access-pfsense`, `team-access-dmz`, `team-access-voip`, `team-access-corp` y `team-access-mgmt`.

Topología de recursos existentes, con routing CE y salida AWS probados:

```text
Operador solamente -> RProxy [IP Tailscale del operador] -> Proxmox pve [IP privada de Proxmox]
                                                    |
                                     vmbr0 (uplink existente intacto)
                                                    |
AWS 100.50.147.57 <-- WireGuard probado --> VM100 EDGE [gateway privado del host]18
 AWS wg .255.255.1                          local wg 10.255.255.2
                                                    |
                                          transit 10.254.254.1
                                                    |
                                                 vmbr2
                                                    |
                                     VM101 pfSense CE2.9 instalado
                                        net0 WAN / net1 trunk
                                                    |
                                           vmbr3 VLAN-aware
                                 +----------+-------+--------+
                               tag20      tag30   tag10    tag99
                               VM102      VM103   VM104    VM105 <- tailnet equipo
                                DMZ        VOIP    CORP     MGMT
                           .20.50      .30.50    .10.50    .99.10  100.73.101.28
                     (todas 192.168.x.x; gateways CE .1 operativos)
```

## WireGuard y dependencia AWS

Endpoint AWS `100.50.147.57:51820`; AWS `10.255.255.1/30`, local `10.255.255.2/30`. Bundle privado fuera del repositorio: `~/.kronos-secrets/local-edge/`. No copiar claves privadas al equipo ni a Git.

`Table=off` conserva el default DHCP del Edge. Tabla 51820 dirige origen `10.254.254.0/30` a wg0; la ruta conectada de transit devuelve respuestas a pfSense. No hay SNAT/MASQUERADE local. El NAT de salida de las VLANs corresponde a pfSense, que traduce a su WAN `10.254.254.2`; AWS hace el NAT final. AWS AllowedIPs no anuncia las cuatro redes protegidas.

Comprobar en Edge `sudo kronos-edge-status`, `sudo wg show`, `ip rule`, `ip route show table 51820`. Un handshake no valida pfSense, las VLANs ni el tráfico extremo a extremo. Tailscale administra; WireGuard transporta el tráfico público.

El handshake local↔AWS ya fue observado durante este despliegue; repetir `wg show` para edad/RX/TX actuales. AWS habilitó persistentemente ICMP echo-request únicamente recibido por wg0 desde `10.255.255.2`, para probar `ping 10.255.255.1`; esto no abre ICMP público en EC2.

## pfSense CE instalado

La búsqueda inicial no encontró VM A1 reutilizable. El usuario aportó Netgate Installer1.2, utilizado para instalar **pfSense CE2.9**, no Plus, en VM101. SHA256 del archivo comprimido: `184514fe7df0d339362c1e33fa051c464577a450528759b343ade894c7c57955` (integridad local, no validación contra firma oficial). El sistema instalado ya tiene red probada. No hace falta subir otra imagen ni reinstalar.

Se utilizó el instalador de Netgate para CE amd64. El medio se conserva en storage local; no se utilizaron mirrors de terceros.

Consola administrativa: **VM101 > Console**. Conservar el arranque del disco instalado; no iniciar una segunda instalación ni tocar VMs existentes.

WAN usa `vtnet0`; `vtnet1` es trunk VLAN10/20/30/99. Gateways operativos: `192.168.10.1`, `192.168.20.1`, `192.168.30.1` y `192.168.99.1`, todos /24, sin upstream gateway en VLAN. MGMT administra por VLAN99 sin NIC adicional.

Durante bootstrap se usa consola Proxmox/QGA para administrar invitados Ubuntu. El túnel SSH a WebGUI descrito en TEAM_LAB_ACCESS requiere que MGMT ya sea alcanzable; no es una ruta disponible antes de autenticarlo o completar otra ruta administrativa autorizada. No habilitar administración WAN pública ni añadir NIC de bypass.

## pfSense: referencia de campos y administración comprobada

La red ya está aplicada; esta tabla sirve para mantenimiento, no para recrear VLANs. Administración: **System > Advanced > Admin Access > Protocol = HTTPS; TCP port = 8443**. Desde MGMT, el usuario `kronos` inició sesión realmente en la WebGUI y por SSH con su contraseña propia; las pruebas sobrevivieron al reinicio. pfSense tiene `passwordauthentication yes` para este acceso, pero las reglas del firewall solo permiten SSH y GUI administrativos desde MGMT `192.168.99.10`. El operador mantiene su clave pública propia. La regla automática anti-lockout no aparece en `pfctl -sr`; los accesos dependen de reglas explícitas. La auditoría real de offloads y Netmap se conserva como evidencia privada del operador; los resultados relevantes se resumen aquí.

Después de las pruebas se retiró de la configuración de pfSense la clave pública temporal de automatización, verificando que la clave pública operadora `~/.ssh/kronos-lab-ed25519.pub` siguiera autorizada. Se eliminó la credencial temporal de `/run` en MGMT. La clave temporal revocada permanece fuera de Git en el almacén local de secretos para auditoría; no proporciona acceso a pfSense.
El snapshot `team-access-pfsense` es el punto de restauración preferido. `baseline-pfsense` es anterior a la retirada de la clave pública temporal; si se revierte a ese snapshot, retirar de nuevo esa clave antes de habilitar acceso administrativo. `hardened-pfsense` es anterior a la cuenta de trabajo.

Antes de cambios, **Diagnostics > Backup & Restore > Backup**, área `All`, descargar configuración fuera de Git. No importar el fragmento XML del repo como un config.xml completo.

| Menú | Campo | Valor |
|---|---|---|
| Interfaces > WAN | Enable interface | marcado |
| Interfaces > WAN | IPv4 Configuration Type | Static IPv4 |
| Interfaces > WAN | IPv4 Address | 10.254.254.2 / 30 |
| Interfaces > WAN | IPv4 Upstream Gateway > Add | Name KRONOS_EDGE; Gateway 10.254.254.1 |
| Interfaces > WAN | Block private networks and loopback addresses | desmarcado |
| Interfaces > WAN | Block bogon networks | desmarcado para este lab |
| Interfaces > Assignments > VLANs > Add | Parent Interface | vtnet1 |
| Interfaces > Assignments > VLANs > Add | VLAN Tag | repetir 10, 20, 30, 99 |
| Interfaces > Assignments | Available network ports | asignar cada VLAN; VLAN99 ya puede estar asignada como LAN |
| Interfaces > CORP | Enable / Description / Static IPv4 | sí / CORP / 192.168.10.1/24 |
| Interfaces > DMZ | Enable / Description / Static IPv4 | sí / DMZ / 192.168.20.1/24 |
| Interfaces > VOIP | Enable / Description / Static IPv4 | sí / VOIP / 192.168.30.1/24 |
| Interfaces > MGMT (LAN) | Enable / Description / Static IPv4 | sí / MGMT / 192.168.99.1/24 |
| Todas las VLAN | IPv4 Upstream Gateway | None |
| System > Routing > Gateways | Default gateway IPv4 | KRONOS_EDGE |
| System > Advanced > Networking | Disable hardware checksum offload | marcado |
| System > Advanced > Networking | Disable hardware TCP segmentation offload | marcado |
| System > Advanced > Networking | Disable hardware large receive offload | marcado |
| Firewall > NAT > Outbound | Mode | Automatic outbound NAT; verificar reglas de las cuatro VLAN hacia WAN address |

Guardar y **Apply Changes** en cada sección. El padre vtnet1 no debe tener IPv4 de una red plana; todas las redes protegidas usan VLAN. No utilizar 192.168.100.0/24. No activar DHCP sobre WAN_TRANSIT.

Referencias de campos consultadas: [asignación/configuración de interfaces](https://docs.netgate.com/pfsense/en/latest/interfaces/configure.html) y [opciones de networking](https://docs.netgate.com/pfsense/en/latest/config/advanced-networking.html).

El tuning de `src/pfsense_setup/` requiere revisión sobre la versión CE real. Consultar `sysctl net.inet.ip.fastforwarding` antes de añadir **System > Advanced > System Tunables > Add**, `Tunable=net.inet.ip.fastforwarding`, `Value=0`. Si no existe, registrar incompatibilidad; no declarar PASS. Valores del repo: `kern.ipc.nmbclusters=1000000`, `hw.netmap.buf_size=2048`, `hw.netmap.ring_size=4096`, `net.inet.ip.intr_queue_maxlen=4096`, `net.pf.states_hashsize=131072`. No aplicar ciegamente reservas de memoria sobre 4 GiB ni variables inexistentes.

Se ejecutó `src/pfsense_setup/verify_kernel_hardening.py` en CE con `python3.11`: reportó FAIL para `net.inet.ip.fastforwarding` (OID ausente), `net.inet.ip.intr_queue_maxlen=1000` frente a 4096 y `net.pf.states_hashsize=262144` frente a 131072. Su texto de offloads y conclusión de disponibilidad son fijos en el código y **no se aceptan como PASS**. La auditoría live comprobó flags de offload en config y ausencia de TXCSUM/RXCSUM/TSO/LRO activos en vtnet0; `/dev/netmap` existe y el driver vtnet reporta Netmap attach. Suricata aún no está instalado ni se probó Inline IPS. A3 sigue pendiente; su interfaz futura debe ser **WAN/vtnet0**, nunca wg0.

## Política de referencia y segmentación

Las pruebas negativas inter-VLAN pasaron. La matriz siguiente expresa la política de referencia; no certifica cada alias/puerto exacto como probado ni sustituye la evidencia de reglas activas.

En **Firewall > Aliases > IP**, crear `KRONOS_NETS` con las cuatro redes VLAN y `KRONOS_HOSTS` con `.50` de CORP/DMZ/VOIP. En **Firewall > Rules > interfaz**, procesar de arriba hacia abajo. No conservar reglas allow LAN any del instalador como política final. Establecer primero administración MGMT y verificar acceso antes de retirar reglas iniciales.

| Interfaz | Orden y regla |
|---|---|
| WAN | Permitir TCP hacia WAN address puertos 80/443 solamente cuando HAProxy esté configurado; denegar resto por default |
| MGMT | Permitir únicamente origen 192.168.99.10 a pfSense TCP22/8443, KRONOS_HOSTS TCP22, Edge transit 10.254.254.1 TCP22 y DMZ TCP80; DNS TCP/UDP53 y NTP UDP123 a gateway; bloquear resto a redes privadas; permitir DNS/HTTPS necesarios para Tailscale/actualizaciones externos |
| CORP | DNS TCP/UDP53 a 192.168.10.1; bloquear a KRONOS_NETS (incluye MGMT) y redes privadas administrativas; permitir salida Internet IPv4 después del bloqueo |
| DMZ | DNS TCP/UDP53 a 192.168.20.1; bloquear a KRONOS_NETS y redes privadas administrativas; permitir TCP80/443 hacia Internet solo durante actualizaciones |
| VOIP | DNS TCP/UDP53 a 192.168.30.1; excepciones SIP/RTP solo entre endpoints autorizados (definir puertos del PBX real); bloquear a KRONOS_NETS y redes privadas administrativas; permitir HTTPS APIs y NTP externos necesarios |

Aplicar bloqueos hacia RFC1918, 100.64.0.0/10 y redes administrativas tras excepciones explícitas y antes del permiso Internet; así un permiso genérico no permite acceso a la infraestructura privada. Reglas DNS requieren resolver pfSense habilitado y escuchando en las VLANs (**Services > DNS Resolver**). No publicar SIP/RTP en AWS por defecto.

## Servicios y responsables

DMZ: DVWA `http://192.168.20.50/`, red Docker `172.20.20.0/24`, sin Tailscale ni IP pública. MariaDB está healthy; `/setup.php` inicializó las tablas y `/login.php` respondió HTTP200 desde MGMT. Tras reiniciar VM102, Docker restauró ambos contenedores, la base volvió a healthy y `/login.php` respondió HTTP200 sin reinicializarla. El login interactivo de usuarios aún no se probó. HAProxy en pfSense terminará TLS hacia este HTTP; Suricata WAN ve TLS/metadatos, no SQLi dentro de HTTPS. Inspección HTTP interna requiere otra instancia/prueba.

El repositorio copiado en los invitados se encuentra en `/opt/kronos/Proyecto-Portafolio`. Usar esa ruta al consultar `src/` e `infra/proxmox/services/`; no asumir `/opt/Proyecto-Portafolio`.

VOIP: IP `192.168.30.50`; el contenedor `kronos_asterisk_pbx` corre y `asterisk -rx 'core show version'` devolvió 20.6.0, incluso después de reiniciar VM103. UDP5060 escucha en la IP VOIP. Esto no configura AMI ni implementa transporte Gemini o una llamada validada. No iniciar el dispatcher ni usar credenciales SIP de ejemplo. Ver [servicios](../infra/proxmox/services/README.md).

| Responsable según README | Componentes |
|---|---|
| Bruno Urrea | arquitectura, pfSense/Netmap, motor pfctl, integración Gemini |
| Freddy Vásquez | VLANs, routing, PBX/AMI y Tailscale |
| Cristóbal Quezada | HAProxy, TLS y DVWA |
| Kevin Retamales | Suricata junto a Bruno; pfBlockerNG |

## MGMT / Tailscale

No conectar MGMT a vmbr0. Su única NIC es VLAN99; salida pfSense → Edge → WireGuard → AWS probada. Tailscale reportó **Running**, `Online=True`, IP `100.73.101.28` en la tailnet separada `tailnet KRONOS del equipo`. `AllowedIPs` y `PrimaryRoutes` mostraron VLAN10/20/30/99, sin `10.10.20.0/24`. La ruta `10.254.254.1/32` figura en `PrimaryRoutes` y `AllowedIPs` de esta PC de la tailnet del equipo; su TCP22 respondió. La configuración actual anunciada es:

```bash
sudo tailscale set --advertise-routes=192.168.99.0/24,192.168.10.0/24,192.168.20.0/24,192.168.30.0/24,10.254.254.1/32
```

El login se completó con la cuenta separada del equipo. IPv4 forwarding vale 1; el default gateway de MGMT sigue en `192.168.99.1`. Tailscale usa SNAT de subnet router predeterminado, por lo que pfSense ve `192.168.99.10` y aplica las reglas de MGMT. Desde MGMT, pfSense HTTPS8443, SSH22 de DMZ/VOIP/CORP y SSH22 de Edge transit respondieron; las seis conexiones SSH `kronos` con contraseña pasaron. TCP8006 y TCP22 de Proxmox `[IP privada de Proxmox]` dieron timeout desde MGMT. Aplicar ACL/grants por usuario y validar autenticación desde los dispositivos de los compañeros antes de declarar su acceso TESTED. No anunciar `0.0.0.0/0`, `10.10.20.0/24` ni usar Tailscale para tráfico público o acceso al hipervisor.

## Pruebas y límites

Ejecutar desde Bash como operador `KRONOS_PVE_HOST=<host-privado> bash infra/proxmox/kronos-healthcheck.sh`. El script usa SSH por clave y QGA, no cambia configuración. Código 1 indica FAIL, código 2 pendientes manuales. Un ping WAN sin respuesta requiere comprobar también la regla ICMP de diagnóstico; no demuestra por sí solo fallo de routing.

Resultados ejecutados: **PASS** VLANs operativas, DNS, salida por pfSense/WireGuard/AWS con EIP `100.50.147.57`, pruebas negativas inter-VLAN, captura ingress `vtnet0` conservando origen `un cliente externo`, gestión pfSense, persistencia tras reinicio, HTTP de DVWA con base inicializada, CLI de Asterisk, Tailscale Running/Online en la tailnet separada, las seis autenticaciones SSH `kronos` con contraseña y WebGUI de pfSense. La captura prueba conservación del origen hasta WAN, no HAProxy ni respuesta HTTP externa del backend. Pendientes: autenticación desde los dispositivos de cada compañero, ACLs Tailscale, HAProxy/HTTPS extremo a extremo, Suricata Inline, AMI/Gemini y login interactivo DVWA. No se marcan A2/A3 completadas ni se declara READY por estas pruebas parciales.
