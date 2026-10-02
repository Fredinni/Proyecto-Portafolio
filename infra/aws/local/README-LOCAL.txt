KRONOS SENTINEL - Ubuntu Edge local 24.04

Este bundle se instala en el Ubuntu local, no en pfSense. wg0.conf contiene
una clave privada y PSK: no publicarlo ni introducirlo en Git.

1. Copiar el directorio local-edge completo al Ubuntu usando SSH/SCP.
   Ejemplo PowerShell desde el equipo que genero el bundle:
   scp -r "$HOME/.kronos-secrets/local-edge" usuario@IP_UBUNTU_LOCAL:~/

2. En Ubuntu:
   chmod 700 ~/local-edge
   chmod 600 ~/local-edge/wg0.conf
   sudo apt-get update
   sudo apt-get install -y wireguard wireguard-tools nftables iproute2
   sudo install -d -m 700 /etc/wireguard
   sudo install -m 600 ~/local-edge/wg0.conf /etc/wireguard/wg0.conf
   ip -br link
   ip -4 route show default
   cd ~/local-edge
   sudo bash kronos-local-routing.sh UPLINK_IF TRANSIT_IF

   Reemplazar UPLINK_IF y TRANSIT_IF por nombres reales, por ejemplo ens18 ens19.
   Sin argumentos el script detecta uplink/default y una unica segunda NIC;
   si existen varias NIC candidatas solicita TRANSIT_IF en terminal interactiva.
   UPLINK_IF conserva DHCP, DNS y default gateway del router/ISP local.
   TRANSIT_IF debe ser una NIC exclusiva sin DHCP, conectada al WAN-BRIDGE de
   pfSense. No debe estar conectada a Internet ni a las VLAN protegidas.
   Deshabilitar DHCP en TRANSIT_IF en el gestor de red existente antes de instalar.

3. El script instala y habilita kronos-local-routing.service, dependiente de
   wg-quick@wg0 y network-online. Persiste 10.254.254.1/30 en TRANSIT_IF,
   ip_forward=1, rp_filter=2, regla origen 10.254.254.0/30 prioridad 100 y tabla
   51820 con default dev wg0 y ruta conectada al transit para respuestas del
   gateway local hacia pfSense. No sustituye el default de main ni cambia DNS.
   wg0.conf debe mantener Table = off y no definir DNS; AllowedIPs = 0.0.0.0/0
   permite fuentes publicas reales por el tunel. Keepalive de 25 s mantiene NAT.

   La tabla nft inet kronos_local_edge solamente permite forwarding IPv4
   wg0 <-> TRANSIT_IF para 10.254.254.0/30. No instala SNAT/MASQUERADE ni altera
   INPUT/OUTPUT. Es un router dedicado: otro forwarding queda bloqueado.
   No borra tablas ajenas. Si UFW u otra tabla bloquea FORWARD, hay que integrar
   las dos autorizaciones en esa politica antes de probar el flujo completo.
   No habilita nftables.service ni sobrescribe /etc/nftables.conf: la unidad
   KRONOS carga su propia tabla despues del servicio nftables al arrancar.
   Si otra herramienta recarga/borra nftables despues, ejecutar:
   sudo systemctl restart kronos-local-routing

4. Configurar posteriormente pfSense: WAN vtnet0 = 10.254.254.2/30,
   gateway 10.254.254.1. Deshabilitar block private y block bogon en WAN.
   Para salida desde LAN/VLAN, pfSense debe hacer outbound NAT hacia su WAN
   10.254.254.2; las redes internas no forman parte de AllowedIPs del AWS peer.
   WireGuard termina en Ubuntu, y pfSense recibe Ethernet normal para Netmap.

5. Verificacion real despues de conectar (no ejecutada por generar el bundle):
   sudo systemctl is-active wg-quick@wg0 kronos-local-routing
   sudo wg show
   ip -br addr show wg0
   ip -4 route show default
   ip rule show
   ip route show table 51820
   ip route get 1.1.1.1 from 10.254.254.2 iif TRANSIT_IF
   sysctl net.ipv4.ip_forward
   sudo nft list table inet kronos_local_edge

   El AWS INPUT inicial permite SSH y WireGuard; no permite ICMP al propio AWS.
   Por eso ping puede no responder aunque el handshake funcione. Usar latest
   handshake y contadores wg show como primera prueba del tunel.
   Probar HTTP/HTTPS a la EIP desde una red externa solo cuando pfSense tenga
   reglas WAN, DNAT o listener y backend listos. Comprobar que pfSense ve la IP
   publica original del cliente. Reiniciar Ubuntu y repetir los comandos.

6. Reversion manual: guardar primero evidencia/configuracion. Deshabilitar
   kronos-local-routing y wg-quick@wg0, retirar solo la regla exacta KRONOS,
   rutas KRONOS de tabla 51820, direccion 10.254.254.1/30 y tabla kronos_local_edge.
   Retirar su archivo sysctl y restaurar los valores previos de forwarding y
   rp_filter segun la politica local. No ejecutar flush ruleset ni borrar otras
   rutas, reglas o archivos de red.
