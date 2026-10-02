<?php
require_once('config.inc');require_once('functions.inc');require_once('filter.inc');require_once('shaper.inc');
if(config_get_path('interfaces/wan/if')!=='vtnet0'||config_get_path('interfaces/lan/ipaddr')!=='192.168.99.1')throw new Exception('Not the KRONOS firewall');
umask(0077);$backup='/root/kronos-backups/config.before-s7-guard-20261002.xml';
if(!file_exists($backup)&&!copy('/cf/conf/config.xml',$backup))throw new Exception('Backup failed; no configuration changed');
if(!is_file($backup)||!chmod($backup,0600))throw new Exception('Cannot secure backup; no configuration changed');
$aliases=config_get_path('aliases/alias',[]);
foreach(['KRONOS_IPS_GUARD'=>'0.0.0.0/0','KRONOS_GUARD_PRIVATE'=>'10.0.0.0/8 172.16.0.0/12 192.168.0.0/16','KRONOS_PUBLIC_WEB'=>'80 443'] as $name=>$addresses){
 $idx=null;foreach($aliases as $i=>$a)if($a['name']===$name){if(strpos($a['descr']??'','KRONOS readiness guard')!==0)throw new Exception('Foreign alias collision');$idx=$i;}
 $entry=['name'=>$name,'type'=>$name==='KRONOS_PUBLIC_WEB'?'port':'network','address'=>$addresses,'descr'=>'KRONOS readiness guard - '.($name==='KRONOS_IPS_GUARD'?'closed persistent default':'control plane selector'),'detail'=>''];
 if($idx===null)$aliases[]=$entry;else$aliases[$idx]=$entry;
}
config_set_path('aliases/alias',$aliases);
$rules=config_get_path('filter/rule',[]);$rules=array_values(array_filter($rules,fn($r)=>strpos($r['descr']??'','KRONOS IPS GUARD ')!==0));
$new=[];$tracker=time();
function guardrule($descr,$type,$ifaces,$protocol,$source,$dest){global $tracker;return ['type'=>$type,'interface'=>$ifaces,'ipprotocol'=>'inet','protocol'=>$protocol,'floating'=>'yes','quick'=>'yes','direction'=>'in','source'=>$source,'destination'=>$dest,'descr'=>'KRONOS IPS GUARD '.$descr,'tracker'=>++$tracker,'created'=>['time'=>time(),'username'=>'codex'],'updated'=>['time'=>time(),'username'=>'codex']];}
$new[]=guardrule('DHCP control','pass','lan,opt1,opt2,opt3','udp',['any'=>'','port'=>'68'],['address'=>'255.255.255.255','port'=>'67']);
$new[]=guardrule('MGMT Tailscale HTTPS','pass','lan','tcp',['address'=>'192.168.99.10'],['address'=>'KRONOS_GUARD_PRIVATE','not'=>'','port'=>'443']);
$new[]=guardrule('MGMT Tailscale UDP','pass','lan','udp',['address'=>'192.168.99.10'],['address'=>'KRONOS_GUARD_PRIVATE','not'=>'','port'=>'3478:41641']);
// Keep this UDP exception narrow: a dedicated alias contains only STUN and default peer port.
$aliases=config_get_path('aliases/alias',[]);$udpidx=null;foreach($aliases as $i=>$a)if($a['name']==='KRONOS_TAILSCALE_UDP')$udpidx=$i;
$udp=['name'=>'KRONOS_TAILSCALE_UDP','type'=>'port','address'=>'3478 41641','descr'=>'KRONOS readiness guard - Tailscale ports','detail'=>''];
if($udpidx===null)$aliases[]=$udp;else{if(strpos($aliases[$udpidx]['descr']??'','KRONOS readiness guard')!==0)throw new Exception('Foreign UDP alias');$aliases[$udpidx]=$udp;}
config_set_path('aliases/alias',$aliases);$new[2]['destination']['port']='KRONOS_TAILSCALE_UDP';
$block=guardrule('transit until both IPS ready','block','wan,lan,opt1,opt2,opt3','any',['address'=>'KRONOS_IPS_GUARD'],['network'=>'(self)','not'=>'']);$block['log']='';$new[]=$block;
$web=guardrule('WAN web until both IPS ready','block','wan','tcp',['address'=>'KRONOS_IPS_GUARD'],['network'=>'(self)','port'=>'KRONOS_PUBLIC_WEB']);$web['log']='';$new[]=$web;
config_set_path('filter/rule',array_merge($new,$rules));
config_set_path('system/maximumtableentries','2000000');
$commands=config_get_path('system/shellcmd',[]);if(!is_array($commands))$commands=[$commands];
$commands=array_values(array_filter($commands,fn($c)=>$c!=='/usr/local/sbin/kronos-ips-guard start'));
$command='/usr/local/sbin/kronos-ips-guard boot-start';if(!in_array($command,$commands))$commands[]=$command;
config_set_path('system/shellcmd',$commands);
write_config('KRONOS S7 native IPS readiness guard and PF table capacity');
filter_configure_sync();echo "GUARD_RULES_CONFIGURED_CLOSED_DEFAULT\n";
?>
