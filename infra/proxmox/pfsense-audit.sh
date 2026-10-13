#!/bin/sh
# Read-only pfSense audit. No changes, no full config dump, no assumed PASS.
set -u
if [ "$(uname -s)" != FreeBSD ] || [ ! -r /conf/config.xml ]; then
    echo 'FAIL: run inside the deployed pfSense VM (FreeBSD + /conf/config.xml required).'
    exit 2
fi
echo '=== PLATFORM ==='
uname -a
cat /etc/version
echo '=== INTERFACES AND ROUTES (active options must be inspected) ==='
ifconfig -a
netstat -rn -f inet
echo '=== LIVE SYSCTL VALUES ==='
for setting in net.inet.ip.forwarding net.inet.ip.fastforwarding net.inet.ip.intr_queue_maxlen net.pf.states_hashsize net.pf.source_nodes_hashsize kern.ipc.nmbclusters hw.netmap.buf_size hw.netmap.ring_size hw.netmap.if_size hw.vtnet.csum_disable hw.vtnet.tso_disable hw.vtnet.lro_disable; do
    if value=$(sysctl -n "$setting" 2>/dev/null); then
        printf 'OBSERVED %s=%s\n' "$setting" "$value"
    else
        printf 'UNSUPPORTED_OR_UNAVAILABLE %s\n' "$setting"
    fi
done
echo '=== FILTER AND NAT ==='
pfctl -sr
pfctl -sn
echo '=== INSTALLED PACKAGES / SURICATA PROCESSES ==='
pkg info -q | grep -Ei 'suricata|haproxy|python' || true
pgrep -l suricata || true
echo '=== SELECTED CONFIG FIELDS (no credentials) ==='
if command -v php >/dev/null 2>&1; then
    php <<'PHP'
<?php
libxml_use_internal_errors(true);
$x = simplexml_load_file('/conf/config.xml', 'SimpleXMLElement', LIBXML_NONET);
if ($x === false) { fwrite(STDERR, "FAIL: XML parse failed\n"); exit(1); }
foreach ($x->interfaces->children() as $id => $entry) {
    $safe = [];
    foreach (['if', 'descr', 'ipaddr', 'subnet', 'gateway'] as $field) {
        if (isset($entry->$field)) { $safe[$field] = (string)$entry->$field; }
    }
    foreach (['enable', 'blockpriv', 'blockbogons'] as $field) {
        $safe[$field . '_present'] = isset($entry->$field);
    }
    echo $id . ' ' . json_encode($safe) . PHP_EOL;
}
foreach (['disablechecksumoffloading', 'disablesegmentationoffloading', 'disablelargereceiveoffloading'] as $field) {
    echo $field . ' ' . json_encode(['present' => isset($x->system->$field), 'value' => (string)$x->system->$field]) . PHP_EOL;
}
foreach ($x->vlans->vlan ?? [] as $entry) {
    $safe = [];
    foreach (['if', 'tag', 'pcp', 'vlanif', 'descr'] as $field) { $safe[$field] = (string)$entry->$field; }
    echo 'vlan ' . json_encode($safe) . PHP_EOL;
}
?>
PHP
else
    echo 'WAITING_FOR_MANUAL_ACTION: PHP unavailable, selected XML audit skipped.'
fi
echo 'AUDIT_COLLECTED: observations only; traffic tests and review still required.'
