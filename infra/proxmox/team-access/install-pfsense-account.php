<?php
/* Run only on KRONOS-PFSENSE CE 2.9. Password arrives on stdin. */
require_once('globals.inc');
require_once('functions.inc');
require_once('config.inc');
require_once('auth.inc');

if (config_get_path('interfaces/wan/if') !== 'vtnet0' ||
    config_get_path('interfaces/wan/ipaddr') !== '10.254.254.2' ||
    config_get_path('interfaces/lan/if') !== 'vtnet1.99') {
    fwrite(STDERR, "Not the expected KRONOS pfSense VM; no change made\n");
    exit(1);
}
$password = trim((string) file_get_contents('php://stdin'));
if (!preg_match('/^[A-Za-z0-9_-]{30,80}$/', $password)) {
    fwrite(STDERR, "Invalid password input; no change made\n");
    exit(1);
}
$backup = '/root/kronos-backups/config.xml.pre-team-access-20260923';
if (!file_exists($backup) && !copy('/cf/conf/config.xml', $backup)) {
    fwrite(STDERR, "Config backup failed; no change made\n");
    exit(1);
}
chmod($backup, 0600);

$users = config_get_path('system/user', []);
$index = null;
foreach ($users as $i => $existing) {
    if (($existing['name'] ?? '') === 'kronos') {
        $index = $i;
        if (($existing['descr'] ?? '') !== 'KRONOS team access') {
            fwrite(STDERR, "Existing kronos user is not managed by this installer\n");
            exit(1);
        }
        break;
    }
}
if ($index === null) {
    $uid = (int) config_get_path('system/nextuid');
    if ($uid < 1000 || $uid > 65000) {
        fwrite(STDERR, "Unexpected nextuid; no change made\n");
        exit(1);
    }
    $user = [
        'name' => 'kronos', 'uid' => $uid, 'scope' => 'system',
        'descr' => 'KRONOS team access', 'priv' => ['user-shell-access'],
        'authorizedkeys' => '',
    ];
    config_set_path('system/nextuid', $uid + 1);
} else {
    $user = $users[$index];
    $uid = (int) $user['uid'];
    $user['priv'] = array_values(array_unique(array_merge($user['priv'] ?? [], ['user-shell-access'])));
}
$passwordItem = ['idx' => null, 'item' => $user];
local_user_set_password($passwordItem, $password);
unset($password);
$user = $passwordItem['item'];
if ($index === null) {
    $users[] = $user;
} else {
    $users[$index] = $user;
}
config_set_path('system/user', $users);

$groups = config_get_path('system/group', []);
$changedGroups = [];
foreach ($groups as $i => &$group) {
    if (!in_array(($group['name'] ?? ''), ['all', 'admins'], true)) {
        continue;
    }
    $members = $group['member'] ?? [];
    if (!is_array($members)) {
        $members = [];
    }
    if (!in_array($uid, $members)) {
        $members[] = $uid;
    }
    $group['member'] = $members;
    $changedGroups[$group['name']] = $group;
}
unset($group);
if (!isset($changedGroups['all'], $changedGroups['admins'])) {
    fwrite(STDERR, "Required pfSense groups absent; no user sync performed\n");
    exit(1);
}
config_set_path('system/group', $groups);

/* The native GUI uses this absence to permit password SSH authentication. */
config_del_path('system/ssh/sshdkeyonly');
local_user_set($user);
foreach ($changedGroups as $group) {
    local_group_set($group);
}
write_config('KRONOS team account for pfSense WebGUI and SSH');
echo "PFSENSE_TEAM_ACCOUNT_CONFIGURED; reboot VM101, then test SSH and WebGUI\n";
