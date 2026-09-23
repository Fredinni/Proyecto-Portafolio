<?php
/* Run on the dedicated KRONOS pfSense CE VM after placing authorized_keys.
 * This preserves SSH keys through pfSense user synchronization and reboots.
 * No key material is embedded in this file or repository.
 */
require_once('globals.inc');
require_once('functions.inc');
require_once('config.inc');
require_once('auth.inc');

$keyFile = '/root/.ssh/authorized_keys';
$keys = @file_get_contents($keyFile);
if ($keys === false || trim($keys) === '') {
    fwrite(STDERR, "No bootstrap public keys found\n");
    exit(1);
}
$lines = array_values(array_unique(array_filter(array_map('trim', explode("\n", $keys)))));
foreach ($lines as $line) {
    if (!preg_match('/^ssh-ed25519 [A-Za-z0-9+\/=]+(?: .*)?$/', $line)) {
        fwrite(STDERR, "Unexpected public-key format\n");
        exit(1);
    }
}
$users = config_get_path('system/user', []);
$found = false;
foreach ($users as &$user) {
    if (($user['name'] ?? '') !== 'admin') {
        continue;
    }
    $current = base64_decode($user['authorizedkeys'] ?? '', true);
    if ($current !== false) {
        foreach (explode("\n", $current) as $line) {
            $line = trim($line);
            if ($line !== '' && !in_array($line, $lines, true)) {
                $lines[] = $line;
            }
        }
    }
    $user['authorizedkeys'] = base64_encode(implode("\n", $lines) . "\n");
    local_user_set($user);
    $found = true;
    break;
}
unset($user);
if (!$found) {
    fwrite(STDERR, "Admin user not found; configuration unchanged\n");
    exit(1);
}
config_set_path('system/user', $users);
write_config('KRONOS admin SSH public keys persisted');
echo "KRONOS_ADMIN_SSH_KEYS_PERSISTED\n";
