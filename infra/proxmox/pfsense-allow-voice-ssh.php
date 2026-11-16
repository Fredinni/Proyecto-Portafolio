<?php
/* One management connection: VM103 -> pfSense TCP22. The voice key is forced
 * to voice_ssh_command.py and cannot open a shell or forward network traffic.
 */
require_once('config.inc');
require_once('filter.inc');
if (config_get_path('interfaces/opt3/ipaddr') !== '192.168.30.1' ||
    config_get_path('interfaces/lan/ipaddr') !== '192.168.99.1') {
    fwrite(STDERR, "Not the KRONOS firewall\n"); exit(1);
}
$description = 'KRONOS Voice restricted pfctl SSH';
$rules = config_get_path('filter/rule', []);
foreach ($rules as $rule) {
    if (($rule['descr'] ?? '') === $description) { echo "VOICE_SSH_RULE_EXISTS\n"; exit(0); }
}
$rule = ['type'=>'pass', 'interface'=>'opt3', 'ipprotocol'=>'inet', 'protocol'=>'tcp',
         'source'=>['address'=>'192.168.30.50'],
         'destination'=>['address'=>'192.168.99.1', 'port'=>'22'],
         'descr'=>$description, 'tracker'=>(string)time(), 'statetype'=>'keep state'];
array_unshift($rules, $rule);
config_set_path('filter/rule', $rules);
write_config('KRONOS voice: allow VM103 forced-command SSH to pfSense only');
$result = filter_configure();
echo 'VOICE_SSH_RULE_APPLIED result=' . json_encode($result) . "\n";
