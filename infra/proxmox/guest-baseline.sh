#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
role=${1:?edge,dmz,voip,corp,mgmt}
case "$role" in edge|dmz|voip|corp|mgmt) ;; *) exit 2;; esac
cat >/etc/ssh/sshd_config.d/00-kronos.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
install -d -m 755 /run/sshd
ssh-keygen -A
sshd -t
systemctl restart ssh.service
systemctl start qemu-guest-agent
if [[ $role != mgmt ]]; then
 systemctl disable --now tailscaled 2>/dev/null || true
 if dpkg-query -W -f='${Status}' tailscale 2>/dev/null | grep -q 'install ok installed'; then
  DEBIAN_FRONTEND=noninteractive apt-get purge -y tailscale
 fi
fi
if [[ $role != dmz && $role != voip ]]; then
 systemctl disable --now docker.service docker.socket containerd.service
fi
if [[ $role == edge ]]; then
 install -d -m 700 /etc/wireguard
 install -m 600 /root/local-edge/wg0.conf /etc/wireguard/wg0.conf
 uplink=$(ip -j -4 route show default | jq -r '.[0].dev')
 transit=$(ip -j -4 addr | jq -r '.[] | select(any(.addr_info[]; .local == "10.254.254.1")) | .ifname')
 test -n "$transit"
 bash /root/local-edge/kronos-local-routing.sh "$uplink" "$transit"
 cat >/usr/local/sbin/kronos-edge-status <<'EOF'
#!/bin/bash
ip -br addr
ip route
ip rule
ip route show table 51820
sysctl net.ipv4.ip_forward
wg show
systemctl is-active wg-quick@wg0 kronos-local-routing
nft list table inet kronos_local_edge
ping -c 2 -W 2 10.255.255.1
ping -c 2 -W 2 10.254.254.2
EOF
 chmod 755 /usr/local/sbin/kronos-edge-status
elif [[ $role == mgmt ]]; then
 cat >/etc/sysctl.d/90-kronos-mgmt.conf <<'EOF'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=2
EOF
 sysctl -p /etc/sysctl.d/90-kronos-mgmt.conf
 systemctl enable --now tailscaled
 printf '%s\n' 'TAILSCALE_WAITING_FOR_AUTH' > /etc/kronos-mgmt-status
elif [[ $role == dmz || $role == voip ]]; then
 systemctl enable --now containerd docker
 if [[ ${PREPARE_ONLY:-0} == 1 ]]; then
  echo 'PACKAGES_CONFIGURED; APPLICATION_WAITING_FOR_FIREWALL_CONNECTIVITY'
  exit 0
 fi
 services=/opt/kronos/Proyecto-Portafolio/infra/proxmox/services
 if [[ $role == dmz ]]; then
  OFFLINE=1 bash "$services/deploy-dmz.sh"
 else
  OFFLINE=1 bash "$services/prepare-voip.sh"
 fi
fi
