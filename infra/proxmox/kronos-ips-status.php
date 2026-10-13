#!/usr/local/bin/php -f
<?php
/* Read-only health check for the two KRONOS pfSense Netmap instances.
 * A live process alone is insufficient: require live IPS/Netmap capture and VLAN tag/filter offload disabled.
 * Does not expose config.xml, credentials, packet payloads or unrelated interface configuration.
 */
require_once('config.inc');
require_once('/usr/local/pkg/suricata/suricata.inc');
$result=['checked_at'=>date(DATE_ATOM),'sensors'=>[],'startup'=>'IPS readiness only; forwarding protection is independently reported by kronos-ips-guard status.'];
$ok=true;$expected=['wan'=>'vtnet0','opt2'=>'vtnet1.20'];
function kronos_socket_query($uuid,$command){
 $lines=[];exec('/usr/local/bin/suricatasc -c '.escapeshellarg($command).' '.escapeshellarg('/var/run/suricata-ctrl-socket-'.$uuid).' 2>/dev/null',$lines,$rc);
 $reply=json_decode(implode("\n",$lines),true);
 return $rc===0&&($reply['return']??'')==='OK'?($reply['message']??null):null;
}
foreach(config_get_path('installedpackages/suricata/rule',[]) as $rule){
 $iface=$rule['interface']??'';if(!isset($expected[$iface]))continue;
 $real=get_real_interface($iface);$uuid=$rule['uuid']??'';
 if($real!==$expected[$iface]||!ctype_digit((string)$uuid)){ $ok=false;continue; }
 $log=SURICATALOGDIR.'suricata_'.$real.$uuid.'/suricata.log';
 $text=is_readable($log)?file_get_contents($log):'';
 $last_start=strrpos($text,'This is Suricata version');if($last_start!==false)$text=substr($text,$last_start);
 $running=suricata_is_running($uuid,$real);
 $capture=kronos_socket_query($uuid,'capture-mode');
 $copy_mode=kronos_socket_query($uuid,'conf-get netmap.1.copy-mode');
 $stats=kronos_socket_query($uuid,'ruleset-stats');
 $ifaces=kronos_socket_query($uuid,'iface-list');
 $parent=$iface==='opt2'?'vtnet1':'vtnet0';
 $counts=is_array($stats)?($stats[0]??[]):[];
 $netmap_live=$capture==='NETMAP'&&$copy_mode==='ips'&&in_array($parent,$ifaces['ifaces']??[],true)&&in_array($parent.'^',$ifaces['ifaces']??[],true);
 $ready=$running&&$netmap_live&&($counts['rules_loaded']??0)>0;
 $row=['assigned_interface'=>$iface,'netmap_parent'=>$iface==='opt2'?'vtnet1':'vtnet0','uuid'=>$uuid,
  'enabled'=>($rule['enable']??'')==='on','running'=>$running,'engine_ready'=>$ready,
  'capture_mode'=>$capture,'copy_mode'=>$copy_mode,'netmap_interfaces_live'=>$netmap_live,
  'ips_configured'=>($rule['ips_mode']??'')==='ips_mode_inline'&&($rule['blockoffenders']??'')==='on',
  'loaded_rules'=>$counts['rules_loaded']??null,'failed_rules'=>$counts['rules_failed']??null,
  'missing_flowbit_warning'=>strpos($text,"flowbit 'et.http.PK' is checked but not set")!==false];
 $result['sensors'][$iface]=$row;
 if(!$row['enabled']||!$ready||!$row['ips_configured']||$row['failed_rules']!==0||$row['missing_flowbit_warning'])$ok=false;
}
$options=[];exec('/sbin/ifconfig vtnet1',$options,$rc);$options=implode("\n",$options);
$result['trunk_vlan_tag_filter_offload_disabled']=$rc===0&&strpos($options,'VLAN_HWTAGGING')===false&&strpos($options,'VLAN_HWFILTER')===false;
$ok=$ok&&count($result['sensors'])===2&&$result['trunk_vlan_tag_filter_offload_disabled'];
$result['status']=$ok?'PASS':'FAIL_OR_NOT_READY';
echo json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
exit($ok?0:1);
