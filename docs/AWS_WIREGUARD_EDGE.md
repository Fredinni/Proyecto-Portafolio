# KRONOS SENTINEL: AWS Public Edge

Implementado y verificado el 22 de septiembre de 2026. AWS actúa como transporte
IPv4/routing; pfSense y Suricata permanecen en el cloud privado.

## Inventario real

| Campo | Valor |
|---|---|
| Región configurada | `us-east-1` |
| EC2 | `KRONOS-PUBLIC-EDGE`, `t3.micro` |
| Nombre AMI | `ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-20260904` |
| Creación / owner verificado | `2026-09-04T11:46:14.000Z` / Canonical `099720109477` |
| IPv4 privada / interfaz | privada de EC2 / `ens5` |
| Elastic IP | `100.50.147.57` |
| SourceDestCheck | `false` en instancia y ENI primaria |
| Security Group | `kronos-public-edge-sg` |
| Key Pair | `kronos-edge` (clave privada fuera de Git) |
| EBS raiz | 20 GiB gp3 cifrado, DeleteOnTermination=true |
| VPC reutilizada | default VPC publica |
| Subnet reutilizada | subnet publica existente |
| IGW / tabla reutilizados | gateway y ruta existentes |

Recursos creados: una EC2 con su ENI primaria, un EBS, una EIP, un SG y una
key pair. No se crearon VPC, subnets, gateways ni servicios adicionales.
Los recursos nuevos llevan Project=KRONOS-SENTINEL, Environment=title-lab,
ManagedBy=codex, Role=public-edge. Se buscaron recursos antes de crear.
La instancia se lanzó sin IPv4 pública automática; solo se asignó una EIP.

## Configuración activa

WireGuard `wg0`: `10.255.255.1/30`, UDP/51820, MTU 1420.
Clave pública AWS: `N4okt5x9yB635l1t03xammTPr1tWuwnfR82SgsZqUzw=`.
Peer local: `DghnLg9VBRkr34Y7Lcr1NrGHg1Fn4dYZ5jRQ1as2/WE=`;
AllowedIPs AWS: `10.255.255.2/32, 10.254.254.0/30`, sin Endpoint fijo.

El SG permite todo IPv4 de entrada/salida deliberadamente. No hay reglas IPv6
en el SG. nftables INPUT permite loopback, established/related, TCP/22 y
UDP/51820 IPv4; descarta el resto. SSH acepta claves, sin password ni root login.
La huella SSH ED25519 se comparó con la consola autenticada de EC2 antes de SSH:
`SHA256:9v9qxAmzDGCnRh/sBnABsILCu5q22EfqSuBqXwBwYvk`.

WEB MODE activo: TCP/80 y TCP/443 hacia `10.254.254.2`, conservando IP origen.
Las reglas usan `ens5` y la IPv4 privada porque AWS traduce EIP fuera del SO.
Solo conexiones originadas en `10.254.254.0/30` hacia WAN reciben MASQUERADE;
se excluyen conexiones con estado DNAT. Conntrack revierte el DNAT de respuestas.
La ruta `10.254.254.0/30` sale por wg0 y el forwarding IPv4 es persistente.

Operación en EC2:

```bash
sudo kronos-edge-status
sudo kronos-web-mode
# Solo activar deliberadamente para otro experimento:
sudo kronos-full-perimeter-mode
```

FULL está preparado, no activado. Reserva TCP/22 y UDP/51820 en AWS; el resto
dirigido a la IPv4 privada se deriva a pfSense. Cada modo persiste en
`/etc/nftables.conf`; scripts destinados exclusivamente a esta VM dedicada.
Cambiar modo no elimina conexiones existentes de conntrack.

## Instalar el Ubuntu Edge local

Bundle privado: `~/.kronos-secrets/local-edge/` en el perfil del operador.
Contiene `wg0.conf`, `README-LOCAL.txt`, `kronos-local-routing.sh` y
`kronos-local-nftables.nft`. Claves privadas y PSK permanecen fuera de Git.
En Windows se aplicaron ACL NTFS exclusivas al usuario, equivalente funcional
de permisos privados; en Ubuntu se instala wg0.conf con modo 600.

Desde PowerShell, reemplazar usuario y dirección del Ubuntu local:

```powershell
scp -r "$env:USERPROFILE\.kronos-secrets\local-edge" USUARIO@IP_UBUNTU_LOCAL:~/
ssh USUARIO@IP_UBUNTU_LOCAL
```

En Ubuntu:

```bash
chmod 700 ~/local-edge
chmod 600 ~/local-edge/wg0.conf
sudo apt-get update
sudo apt-get install -y wireguard wireguard-tools nftables iproute2
sudo install -d -m 700 /etc/wireguard
sudo install -m 600 ~/local-edge/wg0.conf /etc/wireguard/wg0.conf
cd ~/local-edge
sudo bash kronos-local-routing.sh
```

El instalador detecta uplink y segunda NIC o solicita transit si es ambiguo.
Se pueden proporcionar nombres reales: `sudo bash kronos-local-routing.sh ens18 ens19`.
La NIC transit debe estar dedicada al WAN-BRIDGE, sin DHCP ni otra dirección.
UPLINK_IF conserva DHCP/default/DNS del ISP. El túnel usa Table=off,
AllowedIPs=0.0.0.0/0, Endpoint=100.50.147.57:51820 y PersistentKeepalive=25.

El instalador persiste forwarding, rp_filter loose, transit `10.254.254.1/30`,
regla origen `10.254.254.0/30` prioridad 100, tabla 51820 con default por wg0
y ruta conectada transit. No instala NAT. Solo permite forwarding wg0↔transit.
Ver instrucciones y comprobaciones completas en README-LOCAL.txt.

## Configuración posterior de pfSense CE

WAN `vtnet0`: **Static IPv4**, `10.254.254.2/30`, gateway `10.254.254.1`.
Deshabilitar en WAN **Block private networks and loopback addresses** y
**Block bogon networks**.

LAN `vtnet1`: trunk 802.1Q. Crear interfaces VLAN:

| VLAN | Nombre | Red |
|---|---|---|
| 10 | CORP | 192.168.10.0/24 |
| 20 | DMZ | 192.168.20.0/24 |
| 30 | VOIP | 192.168.30.0/24 |
| 99 | MGMT | 192.168.99.0/24 |

WireGuard **termina en Ubuntu Edge, no en pfSense**. pfSense recibe Ethernet/vNIC
normal en WAN para implementar posteriormente Suricata Inline/Netmap.
Configurar reglas WAN y publicación del backend HTTP/HTTPS en pfSense.
Para salida de VLAN/LAN, pfSense debe hacer outbound NAT hacia `10.254.254.2`;
AWS no tiene AllowedIPs para las redes privadas protegidas.
Las respuestas de tráfico publicado deben volver por gateway `10.254.254.1`.
No añadir SNAT en el Ubuntu local: pfSense debe observar la IP pública original.

## Verificación y límites

Los logs crudos de comandos AWS y SSH se conservan localmente fuera de Git; este documento resume las validaciones realizadas.
Se reiniciaron nftables y wg-quick, se reinició EC2 una vez y se verificó un nuevo
boot ID. Checks de sistema/instancia OK; EIP asociada; SourceDestCheck=false;
wg0 UP, UDP/51820 escuchando, nftables activo, forwarding=1 y ruta por wg0.
Los servicios están habilitados y wg0.conf tiene permiso 600.

Pruebas sintéticas ejecutadas en namespaces aislados dentro de EC2:
TCP80/443 conserva origen, respuesta revierte DNAT, salida transit hace
MASQUERADE, SSH llega al router y puerto INPUT no permitido se bloquea aun
con listener activo. Se utilizó veth para representar wg0; no valida túnel real.
La plantilla nft local pasó `nft -c` en Linux; el script local pasó `bash -n`.

Pendiente: instalar peer local, obtener handshake y probar Internet→pfSense→backend,
IP real de cliente, salida Internet y reinicio del Ubuntu local. Handshake vacío
antes de instalar el peer es esperado, no FAIL. FULL no se activó en producción.

Incidencias: IAM denegó tag:GetResources y pricing:GetProducts; se utilizaron
consultas EC2 directas y precios públicos. ssh-keyscan Windows falló por KEX;
se obtuvo la clave pública con Paramiko y se validó contra la consola EC2.

## Costos y ciclo de vida

Estimación para 730 horas/mes, sin créditos promocionales ni impuestos:
EC2 t3.micro ~$7.59 ($0.0104/h), EBS gp3 20 GiB ~$1.60, EIP ~$3.65
($0.005/h): **~USD 12.84/mes**. Transferencia saliente y CPU Unlimited sostenida
pueden añadir cargos. Fuentes: [EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/),
[EBS gp3](https://aws.amazon.com/ebs/volume-types/),
[IPv4](https://aws.amazon.com/vpc/pricing/).
Detener EC2 conserva EBS y EIP y sus cargos (~USD 5.25/mes base).
No se terminaron instancias, no se liberaron EIP y no se creó destroy automático.

## Cambio solicitado a Free Tier

La instancia existente se cambio de t3.small a t3.micro (2 vCPU, 1 GiB RAM),
marcada FreeTierEligible=true por EC2. Se conservan ID, EBS y Elastic IP.
La elegibilidad del tipo no garantiza costo cero: depende del plan, vigencia y
creditos de la cuenta. IAM denego freetier:GetAccountPlanState, por lo que no
se pudo verificar el beneficio efectivo. Referencia:
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html
