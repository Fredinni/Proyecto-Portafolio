<?php
/* Read a new random password from stdin; never place it in argv, XML exports,
 * script source or console output. Use only on the dedicated KRONOS pfSense VM.
 */
require_once('globals.inc');
require_once('functions.inc');
require_once('config.inc');
require_once('auth.inc');

$password = rtrim(stream_get_contents(STDIN), "\r\n");
if (strlen($password) < 24) {
    fwrite(STDERR, "Password too short; configuration unchanged\n");
    exit(1);
}
$users = config_get_path('system/user', []);
$updated = false;
foreach ($users as $index => $user) {
    if (($user['name'] ?? '') !== 'admin') {
        continue;
    }
    $record = ['idx' => $index, 'item' => $user];
    local_user_set_password($record, $password);
    local_user_set($record['item']);
    $updated = true;
    break;
}
unset($password);
if (!$updated) {
    fwrite(STDERR, "Admin user not found; configuration unchanged\n");
    exit(1);
}
write_config('KRONOS admin credential rotated');
echo "KRONOS_ADMIN_PASSWORD_ROTATED\n";
