#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# Installer and boot-time apply helper for the dedicated Ubuntu local edge.
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ $EUID == 0 ]] || die 'Run with sudo.'
for command in ip nft sysctl systemctl install awk sed; do
    command -v "$command" >/dev/null || die "Missing command: $command"
done

mode=${1:-}
if [[ $mode == --apply ]]; then
    [[ -f /etc/default/kronos-local-edge ]] || die 'Install the bundle first.'
    source /etc/default/kronos-local-edge
else
    [[ $# -le 2 ]] || die 'Usage: sudo bash kronos-local-routing.sh [UPLINK_IF TRANSIT_IF]'
    UPLINK_IF=${1:-$(ip -4 route show default | awk '{for(i=1;i<=NF;i++) if($i=="dev") {print $(i+1); exit}}')}
    TRANSIT_IF=${2:-}
    if [[ -z $TRANSIT_IF ]]; then
        candidates=()
        for device in /sys/class/net/*; do
            candidate=${device##*/}
            [[ $candidate != "$UPLINK_IF" && -e $device/device ]] && candidates+=("$candidate")
        done
        if [[ ${#candidates[@]} == 1 ]]; then
            TRANSIT_IF=${candidates[0]}
        elif [[ -t 0 ]]; then
            ip -br link
            read -r -p 'Dedicated pfSense WAN transit interface: ' TRANSIT_IF
        else
            die 'Cannot uniquely detect TRANSIT_IF. Supply UPLINK_IF TRANSIT_IF explicitly.'
        fi
    fi
fi

for iface in "${UPLINK_IF:-}" "${TRANSIT_IF:-}"; do
    [[ $iface =~ ^[a-zA-Z0-9_-]{1,15}$ ]] || die "Unsupported interface name: $iface"
    ip link show dev "$iface" >/dev/null || die "Interface does not exist: $iface"
    [[ $iface != lo && $iface != wg0 ]] || die 'Physical interfaces cannot be lo or wg0.'
done
[[ $UPLINK_IF != "$TRANSIT_IF" ]] || die 'UPLINK_IF and TRANSIT_IF must differ.'
ip -4 route show default | awk -v expected="$UPLINK_IF" '
  {for(i=1;i<=NF;i++) if($i=="dev" && $(i+1)==expected) found=1} END {exit !found}' \
  || die 'UPLINK_IF must have an existing IPv4 default route. It will not be replaced.'
# Refuse to take over policy routing already owned by another application.
existing=$(ip -N -o -4 rule show priority 100)
if [[ -n $existing ]]; then
    [[ $(printf '%s\n' "$existing" | wc -l) == 1 && $existing =~ ^100:[[:space:]]+from[[:space:]]+10\.254\.254\.0/30[[:space:]]+lookup[[:space:]]+51820[[:space:]]*$ ]] \
        || die "Policy priority 100 is already occupied: $existing"
fi
table_routes=$(ip -4 route show table 51820 2>/dev/null || true)
while IFS= read -r route; do
    [[ -z $route || $route =~ ^default[[:space:]]+dev[[:space:]]+wg0([[:space:]]+scope[[:space:]]+link)?[[:space:]]*$ ||
       $route == "10.254.254.0/30 dev $TRANSIT_IF scope link" ]] \
        || die 'Table 51820 contains unrelated routes; refusing to replace them.'
done <<< "$table_routes"
transit_addresses=$(ip -o -4 address show dev "$TRANSIT_IF" | awk '{print $4}')
[[ -z $transit_addresses || $transit_addresses == 10.254.254.1/30 ]] \
    || die 'TRANSIT_IF already has a different IPv4 address; use a dedicated unconfigured NIC.'

if [[ $mode != --apply ]]; then
    bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
    [[ -f /etc/wireguard/wg0.conf ]] || die 'Install the supplied wg0.conf in /etc/wireguard first.'
    [[ -f $bundle/kronos-local-nftables.nft ]] || die 'Missing nftables template beside this script.'
    install -d -m 755 /etc/kronos
    install -m 644 "$bundle/kronos-local-nftables.nft" /etc/kronos/local-nftables.template
    if [[ $(readlink -f -- "${BASH_SOURCE[0]}") != /usr/local/sbin/kronos-local-routing ]]; then
        install -m 755 -- "${BASH_SOURCE[0]}" /usr/local/sbin/kronos-local-routing
    fi
    printf 'UPLINK_IF=%s\nTRANSIT_IF=%s\n' "$UPLINK_IF" "$TRANSIT_IF" > /etc/default/kronos-local-edge
    cat > /etc/sysctl.d/90-kronos-local-router.conf <<'SYSCTL'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=2
net.ipv4.conf.default.rp_filter=2
SYSCTL
    cat > /etc/systemd/system/kronos-local-routing.service <<'UNIT'
[Unit]
Description=KRONOS local WireGuard transit routing
Wants=network-online.target
Requires=wg-quick@wg0.service
After=network-online.target wg-quick@wg0.service nftables.service
PartOf=wg-quick@wg0.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/kronos-local-routing --apply
ExecReload=/usr/local/sbin/kronos-local-routing --apply
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target wg-quick@wg0.service
UNIT
    systemctl daemon-reload
    systemctl enable --now wg-quick@wg0.service
    systemctl enable kronos-local-routing.service
    systemctl restart kronos-local-routing.service
    printf 'Installed. Check: systemctl status kronos-local-routing; wg show; ip rule; ip route show table 51820\n'
    exit 0
fi

ip link show dev wg0 >/dev/null || die 'wg0 is not available.'
before_default=$(ip -4 route show default)
# Replace only our own nft table, in one atomic checked transaction.
transaction=$(mktemp)
trap 'rm -f -- "$transaction"' EXIT
if nft list table inet kronos_local_edge >/dev/null 2>&1; then
    printf 'delete table inet kronos_local_edge\n' >> "$transaction"
fi
sed "s/__TRANSIT_IF__/$TRANSIT_IF/g" /etc/kronos/local-nftables.template >> "$transaction"
nft --check --file "$transaction"
nft --file "$transaction"
ip link set dev "$TRANSIT_IF" up
ip address replace 10.254.254.1/30 dev "$TRANSIT_IF"
ip route replace 10.254.254.0/30 dev "$TRANSIT_IF" scope link table 51820
ip route replace default dev wg0 table 51820
[[ -n $existing ]] || ip rule add from 10.254.254.0/30 table 51820 priority 100
sysctl -p /etc/sysctl.d/90-kronos-local-router.conf
for iface in "$UPLINK_IF" "$TRANSIT_IF" wg0; do
    sysctl -w "net.ipv4.conf.$iface.rp_filter=2"
done
[[ $(ip -4 route show default) == "$before_default" ]] || die 'Default route changed concurrently; inspect local networking.'
ip route get 1.1.1.1 from 10.254.254.2 iif "$TRANSIT_IF"
printf 'Applied without modifying the main default route or DNS. No NAT rules installed.\n'
