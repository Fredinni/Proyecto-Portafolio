<?php
/* KRONOS pfSense CE 2.9 base network and explicit IPv4 policy.
 * Execute only on VM101 after backing up /conf/config.xml. Reboot VM101 to apply.
 * This file contains no credentials and refuses an unexpected firewall/VM.
 */
require_once('globals.inc');
require_once('functions.inc');
require_once('config.inc');
require_once('interfaces.inc');

function failKronos(string $reason): never {
    fwrite(STDERR, "KRONOS_ABORT: {$reason}\n");
    exit(1);
}
if (trim(file_get_contents('/etc/version')) !== '2.9.0-RELEASE') {
    failKronos('Expected pfSense CE 2.9.0');
}
foreach (['vtnet0' => 'bc:24:11:e0:13:8f',
          'vtnet1' => 'bc:24:11:8d:97:48'] as $nic => $mac) {
    $output = [];
    exec('/sbin/ifconfig ' . escapeshellarg($nic), $output, $status);
    if ($status !== 0 || !preg_match('/\bether ' . preg_quote($mac, '/') . '\b/i', implode("\n", $output))) {
        failKronos("Unexpected {$nic} MAC; refusing to change another firewall");
    }
}
$wan = config_get_path('interfaces/wan', []);
$lan = config_get_path('interfaces/lan', []);
$gateway = config_get_path('gateways/gateway_item/0', []);
if (($wan['if'] ?? '') !== 'vtnet0' || ($wan['ipaddr'] ?? '') !== '10.254.254.2' ||
    (string)($wan['subnet'] ?? '') !== '30' || ($lan['if'] ?? '') !== 'vtnet1.99' ||
    ($lan['ipaddr'] ?? '') !== '192.168.99.1' ||
    (string)($lan['subnet'] ?? '') !== '24' ||
    ($wan['gateway'] ?? '') !== 'WANGW' ||
    ($gateway['name'] ?? '') !== 'WANGW' ||
    ($gateway['gateway'] ?? '') !== '10.254.254.1') {
    failKronos('WAN/LAN/gateway differ from the installed KRONOS layout');
}
if (config_get_path('nat/outbound/mode', '') !== 'automatic') {
    failKronos('Expected automatic outbound NAT');
}
$backup = '/root/kronos-backups/config.xml.pre-kronos-20260923';
if (!is_file($backup) || filesize($backup) < 1000 ||
    @simplexml_load_file($backup, 'SimpleXMLElement', LIBXML_NONET) === false) {
    failKronos('A local configuration backup is required');
}

$vlanSpecs = [10 => ['CORP', '192.168.10.1', 'opt1'],
              20 => ['DMZ',  '192.168.20.1', 'opt2'],
              30 => ['VOIP', '192.168.30.1', 'opt3'],
              99 => ['MGMT', '192.168.99.1', 'lan']];
$vlans = config_get_path('vlans/vlan', []);
$interfaces = config_get_path('interfaces', []);
foreach ($vlanSpecs as $tag => [$name, $address, $friendly]) {
    $found = null;
    foreach ($vlans as $index => $vlan) {
        if ((string)($vlan['tag'] ?? '') === (string)$tag) {
            if (($vlan['if'] ?? '') !== 'vtnet1') {
                failKronos("VLAN {$tag} exists on an unexpected parent");
            }
            $found = $index;
            break;
        }
    }
    $vlan = ['if' => 'vtnet1', 'tag' => (string)$tag, 'pcp' => '0', 'descr' => $name];
    $vlan['vlanif'] = vlan_interface($vlan);
    if (!$vlan['vlanif']) {
        failKronos("Cannot resolve VLAN {$tag} interface");
    }
    if ($found === null) {
        $vlans[] = $vlan;
    } else {
        $vlans[$found] = array_replace($vlans[$found], $vlan);
    }
    if (isset($interfaces[$friendly]) &&
        (($interfaces[$friendly]['if'] ?? '') !== $vlan['vlanif'] ||
         ($interfaces[$friendly]['ipaddr'] ?? '') !== $address)) {
        failKronos("{$friendly} is occupied by another interface");
    }
    $interfaces[$friendly] = array_replace($interfaces[$friendly] ?? [], [
        'if' => $vlan['vlanif'], 'descr' => $name, 'enable' => '',
        'ipaddr' => $address, 'subnet' => '24',
    ]);
    unset($interfaces[$friendly]['gateway']);
}
unset($interfaces['wan']['blockpriv'], $interfaces['wan']['blockbogons']);
config_set_path('vlans/vlan', $vlans);
config_set_path('interfaces', $interfaces);
config_set_path('system/hostname', 'kronos-pfsense');
config_set_path('system/webgui/port', '8443');
foreach (['disablechecksumoffloading', 'disablesegmentationoffloading',
          'disablelargereceiveoffloading'] as $flag) {
    config_set_path("system/{$flag}", '');
}
config_del_path('system/ipv6allow');

$oldRules = config_get_path('filter/rule', []);
foreach ($oldRules as $old) {
    $description = $old['descr'] ?? '';
    if (!str_starts_with($description, 'KRONOS BASE ') &&
        !in_array($description, ['Default allow LAN to any rule',
                                 'Default allow LAN IPv6 to any rule'], true)) {
        failKronos('Unexpected pre-existing firewall rule: ' . $description);
    }
}
$rules = [];
$tracker = 1790001000;
function endpointKronos(string $value): array {
    if ($value === 'any') {
        return ['any' => ''];
    }
    if (str_starts_with($value, 'network:')) {
        return ['network' => substr($value, 8)];
    }
    return ['address' => $value];
}
function addKronosRule(string $iface, string $type, string $source,
                       string $destination, ?string $proto,
                       ?string $port, string $description): void {
    global $rules, $tracker;
    $rule = [
        'type' => $type, 'ipprotocol' => 'inet', 'interface' => $iface,
        'tracker' => (string)++$tracker, 'descr' => 'KRONOS BASE ' . $description,
        'source' => endpointKronos($source),
        'destination' => endpointKronos($destination),
    ];
    if ($proto !== null) {
        $rule['protocol'] = $proto;
    }
    if ($port !== null) {
        $rule['destination']['port'] = $port;
    }
    if ($type === 'block') {
        $rule['log'] = '';
    }
    $rules[] = $rule;
}
function allowKronos(string $iface, string $src, string $dst,
                     ?string $proto, ?string $port, string $description): void {
    addKronosRule($iface, 'pass', $src, $dst, $proto, $port, $description);
}
function blockPrivateKronos(string $iface): void {
    foreach (['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16',
              '100.64.0.0/10'] as $network) {
        addKronosRule($iface, 'block', "network:{$iface}", $network,
                      null, null, "block private {$network} on {$iface}");
    }
}
function allowDnsAndNtpKronos(string $iface, string $gateway): void {
    foreach (['tcp', 'udp'] as $proto) {
        allowKronos($iface, "network:{$iface}", $gateway, $proto, '53',
                    "{$iface} DNS {$proto}");
    }
    allowKronos($iface, "network:{$iface}", $gateway, 'udp', '123',
                "{$iface} NTP");
    allowKronos($iface, "network:{$iface}", $gateway, 'icmp', null,
                "{$iface} gateway diagnostic ICMP");
}

// Only a diagnostic ping from the private Edge may reach the pfSense WAN.
allowKronos('wan', '10.254.254.1', '10.254.254.2', 'icmp', null,
            'Edge WAN diagnostic ICMP');

allowDnsAndNtpKronos('lan', '192.168.99.1');
foreach (['22', '8443'] as $port) {
    allowKronos('lan', '192.168.99.10', '192.168.99.1', 'tcp', $port,
                "MGMT administer pfSense TCP {$port}");
}
allowKronos('lan', '192.168.99.10', '192.168.99.1', 'icmp', null,
            'MGMT gateway diagnostic');
foreach (['192.168.10.50', '192.168.20.50', '192.168.30.50'] as $host) {
    allowKronos('lan', '192.168.99.10', $host, 'tcp', '22',
                "MGMT SSH {$host}");
    allowKronos('lan', '192.168.99.10', $host, 'icmp', null,
                "MGMT ping {$host}");
}
allowKronos('lan', '192.168.99.10', '192.168.20.50', 'tcp', '80',
            'MGMT DVWA HTTP health');
blockPrivateKronos('lan');
foreach (['80', '443'] as $port) {
    allowKronos('lan', '192.168.99.10', 'any', 'tcp', $port,
                "MGMT public TCP {$port}");
}
foreach (['41641', '3478'] as $port) {
    allowKronos('lan', '192.168.99.10', 'any', 'udp', $port,
                "MGMT Tailscale UDP {$port}");
}

allowDnsAndNtpKronos('opt1', '192.168.10.1');
blockPrivateKronos('opt1');
allowKronos('opt1', 'network:opt1', 'any', null, null, 'CORP public Internet');

foreach ([['opt2', '192.168.20.1', 'DMZ'],
          ['opt3', '192.168.30.1', 'VOIP']] as [$iface, $gateway, $name]) {
    allowDnsAndNtpKronos($iface, $gateway);
    blockPrivateKronos($iface);
    foreach (['80', '443'] as $port) {
        allowKronos($iface, "network:{$iface}", 'any', 'tcp', $port,
                    "{$name} public TCP {$port}");
    }
}
config_set_path('filter/rule', $rules);
write_config('KRONOS VLANs and base Zero Trust IPv4 policy');
echo 'KRONOS_BASE_CONFIG_WRITTEN; reboot VM101, then verify live interfaces/rules/NAT', "\n";
