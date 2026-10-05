# pfSense CE: configuración y auditoría pendiente

Este documento es un plan aplicable al pfSense **nuevo o clonado**, no evidencia de despliegue. Al redactarlo, la instalación mediante Netgate Installer v1.2 está pendiente. No se ha generado ni importado un `config.xml`. Los estados académicos permanecen A1 completado, A2 en curso y A3+ roadmap. El estado efectivo se registra en `docs/PROXMOX_ONPREM_DEPLOYMENT.md`.

## Red y acceso inicial

Conservar solo dos NIC VirtIO: `vtnet0` WAN en bridge KRONOS WAN; `vtnet1` trunk sin tag individual en bridge KRONOS TRUNK. Usar los nombres reales del inventario Proxmox: `vmbr-kronos-trunk` excede el límite Linux de 15 caracteres. No conectar estas NIC a vmbr0 ni añadir una NIC de administración.

Desde consola Proxmox: asignar WAN=vtnet0 y LAN inicialmente a la VLAN99 creada sobre vtnet1; verificar primero los nombres/MAC reales. No dejar LAN untagged con una regla automática allow-all. MGMT estará en VLAN99 y se administrará pfSense por `192.168.99.1`.

| Ruta WebGUI | Campo | Valor |
|---|---|---|
| Interfaces > WAN | Enable / IPv4 Configuration Type | Enabled / Static IPv4 |
| Interfaces > WAN | IPv4 Address | 10.254.254.2 / 30 |
| Interfaces > WAN | IPv4 Upstream gateway | KRONOS_EDGE |
| Interfaces > WAN | Block private networks and loopback addresses | Desmarcado |
| Interfaces > WAN | Block bogon networks | Desmarcado |
| System > Routing > Gateways > Add | Interface / Address Family / Name | WAN / IPv4 / KRONOS_EDGE |
| System > Routing > Gateways > Add | Gateway | 10.254.254.1 |
| System > Routing > Gateways | Default gateway IPv4 | KRONOS_EDGE |
| Interfaces > Assignments > VLANs > Add | Parent / Priority | vtnet1 / 0 |
| Interfaces > Assignments > VLANs > Add | VLAN Tag | Crear 10, 20, 30 y 99 individualmente |

Asignar cada VLAN en `Interfaces > Assignments`; en cada interfaz marcar Enable y Static IPv4. No configurar upstream gateway en las VLAN:

| VLAN | Descripción | Dirección |
|---|---|---|
| 10 | CORP | 192.168.10.1/24 |
| 20 | DMZ | 192.168.20.1/24 |
| 30 | VOIP | 192.168.30.1/24 |
| 99 | MGMT | 192.168.99.1/24 |

`Firewall > NAT > Outbound`: Automatic outbound NAT inicialmente; comprobar con `pfctl -sn` que las cuatro redes salen por WAN traducidas a `10.254.254.2`. AWS conoce transit, no las VLAN. No introducir SNAT entre Ubuntu Edge transit y WireGuard. El default route del Edge permanece en su uplink y su policy routing envía origen transit a wg0.

## Matriz Zero Trust mínima

Crear aliases `KRONOS_PROTECTED_NETS` (las cuatro /24), `KRONOS_ADMIN_HOST` (192.168.99.10), `KRONOS_SERVER_HOSTS` (.10.50, .20.50, .30.50), `KRONOS_NONPUBLIC_NETS` (RFC1918, 100.64.0.0/10 y 10.255.255.0/30). Reglas IPv4 en la interfaz de entrada, en orden; registrar blocks. Denegación implícita al final. Ninguna regla IPv6 de salida hasta configurar IPv6 explícitamente.

| Interfaz | Origen | Destino | Acción/puertos |
|---|---|---|---|
| Todas las VLAN | Su red | Su gateway .1 | Permitir DNS TCP/UDP 53; NTP UDP123 si pfSense sirve NTP |
| MGMT | KRONOS_ADMIN_HOST | 192.168.99.1 | Permitir HTTPS 8443, SSH 22 y ICMP diagnóstico |
| MGMT | KRONOS_ADMIN_HOST | KRONOS_SERVER_HOSTS | Permitir SSH22 e ICMP; HTTP80 a DMZ para health |
| MGMT | MGMT net | KRONOS_NONPUBLIC_NETS | Bloquear después de excepciones |
| MGMT | KRONOS_ADMIN_HOST | Internet | Permitir TCP80/443, UDP41641 y UDP3478 para actualizaciones/Tailscale |
| CORP | CORP net | KRONOS_NONPUBLIC_NETS | Bloquear |
| CORP | CORP net | Internet | Permitir IPv4 tras el bloqueo anterior |
| DMZ | DMZ net | This Firewall | Bloquear después de DNS/NTP |
| DMZ | DMZ net | KRONOS_NONPUBLIC_NETS | Bloquear, incluyendo CORP/MGMT |
| DMZ | DMZ net | Internet | Permitir TCP80/443 para actualizaciones |
| VOIP | VOIP net | KRONOS_NONPUBLIC_NETS | Bloquear salvo excepciones SIP/RTP acordadas |
| VOIP | 192.168.30.50 | Internet | Permitir TCP80/443 para instalación y HTTPS APIs; SIP/RTP solo destinos de proveedor acordados |
| WAN | any | WAN address | Permitir TCP80/443 únicamente cuando HAProxy esté configurado |

Los clientes SIP en la misma VLAN30 alcanzan Asterisk sin pasar por pfSense. Para clientes en MGMT/Tailscale agregar regla específica MGMT→192.168.30.50 UDP/TCP5060 y RTP UDP10000:10100 solo al habilitar ese servicio. No abrir AMI5038 entre VLAN por defecto. No publicar DVWA a Internet como sustituto de configurar HAProxy.

`System > Advanced > Admin Access`: WebGUI HTTPS TCP8443; acceso únicamente MGMT, SSH solo claves. Sustituir las reglas LAN automáticas por las MGMT explícitas. Si LAN corresponde a MGMT, revisar la regla anti-lockout y deshabilitarla **solo después** de comprobar la regla administrativa y consola de recuperación. Conservar DNS Rebind/CSRF y validación de host.

MGMT utiliza únicamente VLAN99. Tailscale puede anunciar las redes protegidas, pero el gateway para las otras VLAN debe ser pfSense; no crear bridges directos. Las rutas requieren aprobación Tailscale Admin. Con SNAT predeterminado de subnet routing pfSense verá origen MGMT .10; sin SNAT se necesitan rutas de retorno 100.64.0.0/10 y reglas específicas. No copiar reglas de autorización inter-VLAN indiscriminadas.

## Offloading, Netmap y servicios

`System > Advanced > Networking`: marcar Disable hardware checksum offload, Disable hardware TCP segmentation offload y Disable hardware large receive offload. Guardar/aplicar y comprobar `ifconfig vtnet0` / `vtnet1`: revisar **options activas**, no solo capabilities disponibles.

El repo propone `net.inet.ip.fastforwarding=0`, `net.inet.ip.intr_queue_maxlen=4096`, `net.pf.states_hashsize=131072`, `net.pf.source_nodes_hashsize=32768`; comprobar existencia y mutabilidad en FreeBSD real. Usar `System > Advanced > System Tunables` únicamente cuando compatibles. No añadir sysctl inexistentes ni atribuirles PASS.

No ejecutar íntegro `src/pfsense_setup/kernel_netmap_tuning.sh`: no es idempotente, hace append y puede fallar a mitad. Los límites mbuf muy grandes necesitan evaluación con 4GiB. Los nombres `hw.netmap.*` del script y `dev.netmap.*` del manual difieren: validar en el sistema instalado. No se presupone equivalencia.

`src/pfsense_setup/verify_kernel_hardening.py` se ejecutará dentro de pfSense desde una copia en /tmp si hay Python. Su salida no basta: simula resultados fuera de FreeBSD, no comprueba offloading, y no propaga fallos al estado global. Adjuntar auditoría real `pfsense-audit.sh` y pruebas de tráfico. No sobreescribir evidencia histórica A1.

Suricata se preparará desde `System > Package Manager > Available Packages` (paquete oficial). Clasificar PACKAGE INSTALLED / READY FOR A3 hasta probar Inline/Netmap WAN vtnet0, nunca wg0. HTTPS en WAN permite inspección TLS/metadatos; SQLi HTTP se inspecciona después de terminación TLS en HAProxy, hacia DMZ. HAProxy/DVWA no equivale a A5 validado sin prueba real.

## Automatización futura por shell PHP oficial

Netgate documenta `pfSsh.php` (consola opción 12), ejecución con `exec;` y guardado mediante `write_config()`. La configuración puede manipularse con `config_get_path`, `config_set_path` y `config_del_path`; eliminar un flag de presencia no equivale a escribir `false`. [PHP shell](https://docs.netgate.com/pfsense/en/latest/development/php-shell.html), [acceso a configuración](https://docs.netgate.com/pfsense/en/latest/development/php-config-arrays.html).

Antes de automatizar: leer `/etc/version`, estructura real y fuentes PHP instaladas; guardar copia 0600 de `/conf/config.xml` **dentro del firewall**; validar XML sin volcar secretos; verificar identidad y MAC de VM nueva/clon. No ejecutar scripts de actualización `gitsync`, allow-all WAN ni disablefilter.

Campos de referencia verificados en código oficial actual; deben contrastarse con la versión instalada:

| Ruta de configuración | Contenido esperado |
|---|---|
| interfaces/wan | if=vtnet0, enable presente, ipaddr=10.254.254.2, subnet=30, gateway=KRONOS_EDGE; eliminar blockpriv y blockbogons |
| gateways/gateway_item | Lista; registro por name=KRONOS_EDGE, interface=wan, ipprotocol=inet, gateway=10.254.254.1, descr apropiada |
| vlans/vlan | Lista; cada registro if=vtnet1, tag=10/20/30/99, pcp=0, descr, vlanif generado por función nativa; tag_type si lo usa versión real |
| interfaces/{lan,optN} | if=vlanif real, enable presente, descr, ipaddr=.1, subnet=24; sin upstream gateway |
| system | flags disablechecksumoffloading, disablesegmentationoffloading, disablelargereceiveoffloading según valores manejados en fuente instalada |

La WebGUI crea el nombre mediante `vlan_interface(...)` y verifica `interface_vlan_configure(...)`, guarda con `write_config(...)` y reconfigura interfaces asignadas. No asumir que el nombre es siempre `vtnet1.10`. [Fuente VLAN](https://github.com/pfsense/pfsense/blob/master/src/usr/local/www/interfaces_vlan_edit.php).

Referencias para validar campos restantes: [interfaces.php](https://github.com/pfsense/pfsense/blob/master/src/usr/local/www/interfaces.php), [gateways](https://github.com/pfsense/pfsense/blob/master/src/usr/local/www/system_gateways_edit.php), [offloading](https://github.com/pfsense/pfsense/blob/master/src/usr/local/www/system_advanced_network.php). Las ramas master son referencia, no contrato de CE instalada. Generar reglas/NAT solo tras leer ejemplos nativos de esa instalación. Guardar XML no aplica necesariamente runtime: usar funciones nativas comprobadas o reboot **de la VM** y auditar después.

## Evidencia pendiente y criterios

- WAN ping 10.254.254.1 y salida Internet; gateways VLAN accesibles desde sus VMs.
- `pfctl -sr/-sn`, rutas y opciones de NIC efectivos; offloading fuera y sysctl compatibles leídos.
- TCP22 DMZ→CORP/MGMT y CORP→MGMT deben fallar **con prueba positiva previa de que el servicio destino escucha**; correlacionar logs de bloqueo.
- MGMT→servidores TCP22 debe funcionar; ningún host Proxmox hace routing inter-VLAN.
- Captura en Edge transit y WAN pfSense debe conservar el origen del cliente externo.
- GUI WAN:443 no debe quedar expuesta; HAProxy validado antes de habilitar reglas WAN80/443.
- Snapshot baseline-pfsense únicamente al terminar instalación y comprobar estado base.

Hasta ejecutar estas pruebas: WAITING_FOR_MANUAL_ACTION / NOT_TESTED según componente; no imprimir READY a partir de este plan.
