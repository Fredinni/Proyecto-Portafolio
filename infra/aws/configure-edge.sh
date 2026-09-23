#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y wireguard wireguard-tools nftables tcpdump curl jq conntrack iproute2
install -m 600 /home/ubuntu/wg0.conf /etc/wireguard/wg0.conf
rm /home/ubuntu/wg0.conf
cat >/etc/sysctl.d/90-kronos-router.conf <<'EOF'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=2
net.ipv4.conf.default.rp_filter=2
EOF
sysctl --system
cat >/etc/ssh/sshd_config.d/00-kronos.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
sshd -t
systemctl reload ssh
install -d -m 755 /etc/kronos
cat >/usr/local/sbin/kronos-set-mode <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run as root'; exit 1; }
mode=${1:-web}
[[ $mode == web || $mode == full ]] || exit 2
wan=$(ip -j -4 route show default | jq -r '.[0].dev')
addr=$(ip -j -4 addr show dev "$wan" | jq -r '.[0].addr_info[] | select(.scope=="global") | .local' | head -1)
[[ $wan =~ ^[a-zA-Z0-9_.:-]+$ && $addr =~ ^[0-9.]+$ ]] || exit 3
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
cat >"$tmp" <<EOF
flush ruleset
table inet kronos_filter {
 chain input {
  type filter hook input priority filter; policy drop;
  iifname "lo" accept
  ct state invalid drop
  ct state established,related accept
  iifname "wg0" ip saddr 10.255.255.2 icmp type echo-request accept
  meta nfproto ipv4 udp dport 51820 accept
  meta nfproto ipv4 tcp dport 22 accept
 }
 chain forward {
  type filter hook forward priority filter; policy drop;
  ct state invalid drop
  ct state established,related accept
  iifname "$wan" oifname "wg0" ip daddr 10.254.254.2 ct status dnat accept
  iifname "wg0" oifname "$wan" ip saddr 10.254.254.0/30 accept
 }
 chain output { type filter hook output priority filter; policy accept; }
}
table ip kronos_nat {
 chain prerouting {
  type nat hook prerouting priority dstnat; policy accept;
EOF
if [[ $mode == web ]]; then
 echo "  iifname \"$wan\" ip daddr $addr tcp dport { 80, 443 } counter dnat to 10.254.254.2" >>"$tmp"
else
 cat >>"$tmp" <<EOF
  iifname "$wan" ip daddr $addr tcp dport 22 return
  iifname "$wan" ip daddr $addr udp dport 51820 return
  iifname "$wan" ip daddr $addr counter dnat to 10.254.254.2
EOF
fi
cat >>"$tmp" <<EOF
 }
 chain postrouting {
  type nat hook postrouting priority srcnat; policy accept;
  oifname "$wan" ip saddr 10.254.254.0/30 ct status != dnat counter masquerade
 }
}
EOF
nft -c -f "$tmp"
nft -f "$tmp"
install -m 600 "$tmp" /etc/nftables.conf
echo "$mode" >/etc/kronos/publication-mode
echo "Active mode: $mode; WAN: $wan ($addr)"
SCRIPT
chmod 755 /usr/local/sbin/kronos-set-mode
printf '#!/bin/sh\nexec /usr/local/sbin/kronos-set-mode web\n' >/usr/local/sbin/kronos-web-mode
printf '#!/bin/sh\nexec /usr/local/sbin/kronos-set-mode full\n' >/usr/local/sbin/kronos-full-perimeter-mode
cat >/usr/local/sbin/kronos-edge-status <<'EOF'
#!/bin/bash
set -eu
uname -a
ip addr
ip route
sysctl net.ipv4.ip_forward
systemctl is-active wg-quick@wg0
wg show
systemctl is-active nftables
nft list ruleset
ss -lunp | grep 51820
ip route get 10.254.254.2
cat /etc/kronos/publication-mode
EOF
chmod 755 /usr/local/sbin/kronos-{web-mode,full-perimeter-mode,edge-status}
/usr/local/sbin/kronos-web-mode
systemctl enable nftables wg-quick@wg0
systemctl restart nftables wg-quick@wg0
/usr/local/sbin/kronos-edge-status
