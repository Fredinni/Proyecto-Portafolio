<?php
/* Configure only the KRONOS backend sensor. Validate before activating. */
require_once('config.inc');
require_once('/usr/local/pkg/suricata/suricata.inc');
$new = file_get_contents('/tmp/kronos-web-ips.rules');
if ($new === false || strpos($new, 'sid:1000010;') === false) { exit(1); }
$rules = config_get_path('installedpackages/suricata/rule', []);
$found = false;
foreach ($rules as &$sensor) {
    if (($sensor['interface'] ?? '') !== 'opt2' || (string)$sensor['uuid'] !== '62511') { continue; }
    $directory = '/usr/local/etc/suricata/suricata_62511_vtnet1.20';
    $backup = '/root/kronos-backups/pre-web-ips-20261116';
    @mkdir($backup, 0700, true);
    if (!file_exists($backup . '/sensor.json')) {
        file_put_contents($backup . '/sensor.json', json_encode($sensor));
        copy($directory . '/suricata.yaml', $backup . '/suricata.yaml');
        copy($directory . '/rules/custom.rules', $backup . '/custom.rules');
    }
    $old = base64_decode($sensor['customrules'] ?? '', true) ?: '';
    $lines = explode("\n", $old);
    $lines = array_filter($lines, fn($line) => !preg_match('/sid:100001[0-5];/', $line));
    $custom = rtrim(implode("\n", $lines)) . "\n" . $new;
    $sensor['customrules'] = base64_encode($custom);
    $sensor['eve_log_alerts_xff'] = 'on';
    $sensor['eve_log_alerts_xff_mode'] = 'extra-data';
    $sensor['eve_log_alerts_xff_deployment'] = 'reverse';
    $sensor['eve_log_alerts_xff_header'] = 'X-Forwarded-For';
    $sensor['eve_log_alerts_metadata'] = 'on';
    suricata_generate_yaml($sensor);
    file_put_contents($directory . '/rules/custom.rules', $custom);
    exec('/usr/local/bin/suricata -T -c ' . escapeshellarg($directory . '/suricata.yaml') .
         ' > /tmp/kronos-web-full-test.log 2>&1', $output, $rc);
    if ($rc !== 0) {
        copy($backup . '/suricata.yaml', $directory . '/suricata.yaml');
        copy($backup . '/custom.rules', $directory . '/rules/custom.rules');
        fwrite(STDERR, "Validation failed; runtime files restored.\n"); exit(1);
    }
    $found = true; break;
}
unset($sensor);
if (!$found) { fwrite(STDERR, "Backend sensor not found.\n"); exit(1); }
config_set_path('installedpackages/suricata/rule', $rules);
write_config('KRONOS explicit backend SQLi/RCE drops and trusted-proxy XFF telemetry');
echo "WEB_IPS_CONFIGURED_AND_VALIDATED; sensor restart required for XFF logging\n";
