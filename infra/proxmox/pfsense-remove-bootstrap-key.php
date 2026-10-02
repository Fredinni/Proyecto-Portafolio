<?php
/* Remove only the temporary automation SSH public key from pfSense admin. */
require_once('globals.inc');
require_once('functions.inc');
require_once('config.inc');
require_once('auth.inc');

if (config_get_path('interfaces/wan/if') !== 'vtnet0' ||
    config_get_path('interfaces/wan/ipaddr') !== '10.254.254.2') {
    fwrite(STDERR, "Unexpected pfSense WAN; no change made\n");
    exit(1);
}
$remove = trim((string) @file_get_contents('/tmp/kronos-bootstrap.pub'));
$operator = trim((string) @file_get_contents('/tmp/kronos-operator.pub'));
if (!preg_match('/^ssh-ed25519 [A-Za-z0-9+\/=]+(?: .*)?$/', $remove)) {
    fwrite(STDERR, "Missing/invalid temporary public key; no change made\n");
    exit(1);
}
if (!preg_match('/^ssh-ed25519 [A-Za-z0-9+\/=]+(?: .*)?$/', $operator)) {
    fwrite(STDERR, "Missing/invalid operator public key; no change made\n");
    exit(1);
}
$users = config_get_path('system/user', []);
$changed = false;
foreach ($users as &$user) {
    if (($user['name'] ?? '') !== 'admin') {
        continue;
    }
    $current = base64_decode($user['authorizedkeys'] ?? '', true);
    if ($current === false) {
        fwrite(STDERR, "Admin keys invalid; no change made\n");
        exit(1);
    }
    $keys = array_values(array_filter(array_map('trim', explode("\n", $current))));
    $remaining = array_values(array_filter($keys, fn($key) => $key !== $remove));
    if (count($remaining) === count($keys)) {
        echo "BOOTSTRAP_KEY_ALREADY_ABSENT\n";
        exit(0);
    }
    if (count($remaining) < 1) {
        fwrite(STDERR, "Refusing to remove the last admin public key\n");
        exit(1);
    }
    if (!in_array($operator, $remaining, true)) {
        fwrite(STDERR, "Operator public key is not among remaining admin keys; no change made\n");
        exit(1);
    }
    $backup = '/root/kronos-backups/config.xml.pre-bootstrap-key-removal-20260923';
    if (!file_exists($backup) && !copy('/cf/conf/config.xml', $backup)) {
        fwrite(STDERR, "Could not back up config; no change made\n");
        exit(1);
    }
    chmod($backup, 0600);
    $user['authorizedkeys'] = base64_encode(implode("\n", $remaining) . "\n");
    local_user_set($user);
    $changed = true;
    break;
}
unset($user);
if (!$changed) {
    fwrite(STDERR, "Admin user not found; no change made\n");
    exit(1);
}
config_set_path('system/user', $users);
write_config('KRONOS temporary automation SSH key removed');
echo "BOOTSTRAP_KEY_REMOVED; remaining admin public key(s) preserved\n";
