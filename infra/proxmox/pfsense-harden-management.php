<?php
/* Apply on KRONOS-PFSENSE only after verifying admin key and GUI access. */
require_once('globals.inc');
require_once('functions.inc');
require_once('config.inc');

if (config_get_path('interfaces/wan/if') !== 'vtnet0' ||
    config_get_path('interfaces/wan/ipaddr') !== '10.254.254.2' ||
    config_get_path('interfaces/lan/if') !== 'vtnet1.99' ||
    config_get_path('interfaces/lan/ipaddr') !== '192.168.99.1') {
    fwrite(STDERR, "Unexpected pfSense network; no change made\n");
    exit(1);
}

$backup = '/root/kronos-backups/config.xml.pre-management-hardening-20260923';
if (!file_exists($backup) && !copy('/cf/conf/config.xml', $backup)) {
    fwrite(STDERR, "Could not back up pfSense config; no change made\n");
    exit(1);
}
chmod($backup, 0600);

config_set_path('system/webgui/noantilockout', true);
config_set_path('system/ssh/sshdkeyonly', 'enabled');
write_config('KRONOS restrict management to explicit MGMT rules and SSH keys');
echo "KRONOS_MANAGEMENT_HARDENING_WRITTEN; reboot VM101 and verify access/rules\n";
