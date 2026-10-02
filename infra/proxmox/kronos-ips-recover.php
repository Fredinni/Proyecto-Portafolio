#!/usr/local/bin/php
<?php
// Explicit operator recovery, limited to the two KRONOS Suricata sensors.
require_once('config.inc');
require_once('/usr/local/pkg/suricata/suricata.inc');
function recovery_error($message) {fwrite(STDERR,$message."\n");exit(1);}
if (function_exists('posix_geteuid') && posix_geteuid()!==0) recovery_error('Requires root');
if (config_get_path('interfaces/wan/if')!=='vtnet0' || config_get_path('interfaces/lan/ipaddr')!=='192.168.99.1') recovery_error('Not KRONOS');
$guard='/usr/local/sbin/kronos-ips-guard';
passthru($guard.' hold',$rc); if ($rc!==0) exit(1);
$wanted=['wan'=>['vtnet0','49823'],'opt2'=>['vtnet1.20','62511']];$seen=[];
foreach(config_get_path('installedpackages/suricata/rule',[]) as $r) {
    $iface=$r['interface']??'';if(!isset($wanted[$iface]))continue;
    $real=get_real_interface($iface);$uuid=(string)($r['uuid']??'');
    if([$real,$uuid]!==$wanted[$iface] || ($r['enable']??'')!=='on') recovery_error('Unexpected sensor; guard held closed');
    $seen[]=$iface;$pidfile='/var/run/suricata_'.$real.$uuid.'.pid';
    if(isvalidpid($pidfile)) {
        $pid=trim(file_get_contents($pidfile));$out=[];
        exec('/bin/ps -p '.escapeshellarg($pid).' -o command=',$out,$rc);
        if($rc!==0 || strpos(implode(' ',$out),'suricata_'.$uuid.'_'.$real.'/suricata.yaml')===false) recovery_error('PID identity mismatch; guard held closed');
        continue;
    }
    // A SIGKILL can leave a stale pidfile; never remove a live process' file.
    unlink_if_exists($pidfile);suricata_start($r,$real);echo "Start requested: $iface\n";
}
if(count($seen)!==2)recovery_error('Both expected sensors required; guard held closed');
for($n=0;$n<150;$n++) {
    exec('/bin/timeout 3 /usr/local/sbin/kronos-ips-status >/dev/null 2>&1',$out,$rc);
    if($rc===0) {passthru($guard.' resume',$rc);exit($rc);}
    sleep(1);
}
fwrite(STDERR,"Readiness timeout; guard remains held closed\n");exit(1);
