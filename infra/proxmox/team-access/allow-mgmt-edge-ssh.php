<?php
/* Permit only KRONOS-MGMT to administer the Edge transit address via pfSense. */
require_once('globals.inc');
require_once('functions.inc');
require_once('config.inc');

if (config_get_path('interfaces/wan/ipaddr') !== '10.254.254.2' ||
    config_get_path('interfaces/lan/ipaddr') !== '192.168.99.1') {
    fwrite(STDERR, "Unexpected KRONOS interface layout; no change made\n");
    exit(1);
}
$rules = config_get_path('filter/rule', []);
$description = 'KRONOS TEAM MGMT SSH Edge transit';
foreach ($rules as $rule) {
    if (($rule['descr'] ?? '') === $description) {
        echo "EDGE_SSH_RULE_ALREADY_PRESENT\n";
        exit(0);
    }
    if (($rule['tracker'] ?? '') === '1790001999') {
        fwrite(STDERR, "Rule tracker occupied; no change made\n");
        exit(1);
    }
}
$position = null;
foreach ($rules as $i => $rule) {
    if (($rule['interface'] ?? '') === 'lan' &&
        ($rule['descr'] ?? '') === 'KRONOS BASE block private 10.0.0.0/8 on lan') {
        $position = $i;
        break;
    }
}
if ($position === null) {
    fwrite(STDERR, "Expected MGMT private-net deny rule absent; no change made\n");
    exit(1);
}
$backup = '/root/kronos-backups/config.xml.pre-team-edge-rule-20260923';
if (!file_exists($backup) && !copy('/cf/conf/config.xml', $backup)) {
    fwrite(STDERR, "Config backup failed; no change made\n");
    exit(1);
}
chmod($backup, 0600);
$new = [
    'type' => 'pass', 'ipprotocol' => 'inet', 'interface' => 'lan',
    'tracker' => '1790001999', 'descr' => $description,
    'protocol' => 'tcp',
    'source' => ['address' => '192.168.99.10'],
    'destination' => ['address' => '10.254.254.1', 'port' => '22'],
];
array_splice($rules, $position, 0, [$new]);
config_set_path('filter/rule', $rules);
write_config('KRONOS MGMT SSH to Edge transit via pfSense');
echo "EDGE_SSH_RULE_WRITTEN; apply firewall/reboot VM101 then test\n";
