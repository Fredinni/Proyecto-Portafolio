<?php
// Local fixtures only: requiring the helper does not execute PF commands.
require_once($argv[1] ?? dirname(__DIR__).'/kronos-guard-mgmt-states.php');
function state_fixture(string $header,string $id='0000000000000001'): string {
    return $header."\n   age 00:00:04, expires in 00:01:00, 2:2 pkts, 100:100 bytes\n   id: $id creatorid: 00000000\n";
}
$cases=[
 ['nat_https','vtnet0 tcp 10.254.254.2:52001 (192.168.99.10:52001) -> 198.51.100.20:443 ESTABLISHED:ESTABLISHED',[],1],
 ['nat_http','vtnet0 tcp 10.254.254.2:52001 (192.168.99.10:52001) -> 198.51.100.20:80 ESTABLISHED:ESTABLISHED',['0000000000000001/00000000'],0],
 ['nat_8443','vtnet0 tcp 10.254.254.2:52001 (192.168.99.10:52001) -> 198.51.100.20:8443 ESTABLISHED:ESTABLISHED',['0000000000000001/00000000'],0],
 ['other_mgmt_https','vtnet1.99 tcp 192.168.99.11:52001 -> 198.51.100.20:443 ESTABLISHED:ESTABLISHED',['0000000000000001/00000000'],0],
 ['stun','vtnet0 udp 10.254.254.2:52001 (192.168.99.10:52001) -> 198.51.100.20:3478 MULTIPLE:MULTIPLE',[],1],
 ['peer_port','vtnet1.99 udp 192.168.99.10:52001 -> 198.51.100.20:41641 MULTIPLE:MULTIPLE',[],1],
 ['udp_not_stun','vtnet1.99 udp 192.168.99.10:52001 -> 198.51.100.20:3480 MULTIPLE:MULTIPLE',['0000000000000001/00000000'],0],
 ['udp_mid_range','vtnet1.99 udp 192.168.99.10:52001 -> 198.51.100.20:40000 MULTIPLE:MULTIPLE',['0000000000000001/00000000'],0],
 ['pf_self_admin','vtnet1.99 tcp 192.168.99.10:52001 -> 192.168.99.1:8443 ESTABLISHED:ESTABLISHED',[],1],
 ['private_https_not_ts','vtnet1.99 tcp 192.168.99.10:52001 -> 192.168.20.50:443 ESTABLISHED:ESTABLISHED',['0000000000000001/00000000'],0],
 ['reverse_https','vtnet0 tcp 198.51.100.20:443 <- 10.254.254.2:52001 (192.168.99.10:52001) ESTABLISHED:ESTABLISHED',[],1],
 ['reverse_http','vtnet0 tcp 198.51.100.20:80 <- 10.254.254.2:52001 (192.168.99.10:52001) ESTABLISHED:ESTABLISHED',['0000000000000001/00000000'],0],
 ['inbound_to_mgmt','vtnet1.99 tcp 192.168.99.10:22 <- 198.51.100.20:52001 ESTABLISHED:ESTABLISHED',['0000000000000001/00000000'],0],
 ['unrelated_ipv4','vtnet0 tcp 198.51.100.10:52001 -> 203.0.113.20:443 ESTABLISHED:ESTABLISHED',[],0],
 ['unrelated_ipv6','vtnet0 tcp 2001:db8::1[52001] -> 2001:db8::2[443] ESTABLISHED:ESTABLISHED',[],0],
];
$results=[];
foreach($cases as [$name,$header,$kill,$kept]) {
 try {$got=kronos_mgmt_states(state_fixture($header));$pass=$got['kill']===$kill&&$got['preserved']===$kept;$results[]=['test'=>$name,'status'=>$pass?'PASS':'FAIL','obtained'=>$got];}
 catch(Throwable $e){$results[]=['test'=>$name,'status'=>'FAIL','error'=>$e->getMessage()];}
}
foreach(['esp','gre','ah','47'] as $proto) {
 $text=state_fixture('vtnet1.99 tcp 192.168.99.10:52001 -> 198.51.100.20:80 ESTABLISHED:ESTABLISHED');
 $text.=state_fixture("vtnet0 $proto 198.51.100.10 -> 203.0.113.20 SINGLE:SINGLE",'0000000000000002');
 try {$got=kronos_mgmt_states($text);$pass=$got['kill']===['0000000000000001/00000000']&&$got['preserved']===0;$results[]=['test'=>$proto.'_after_mgmt','status'=>$pass?'PASS':'FAIL','obtained'=>$got];}
 catch(Throwable $e){$results[]=['test'=>$proto.'_after_mgmt','status'=>'FAIL','error'=>$e->getMessage()];}
}
$exceptions=[
 'missing_id_at_eof'=>"vtnet1.99 tcp 192.168.99.10:52001 -> 198.51.100.20:80 ESTABLISHED:ESTABLISHED\n   age 00:00:01\n",
 'missing_id_before_next_header'=>"vtnet1.99 tcp 192.168.99.10:52001 -> 198.51.100.20:80 ESTABLISHED:ESTABLISHED\n".state_fixture('vtnet0 esp 198.51.100.10 -> 203.0.113.20 SINGLE:SINGLE','0000000000000002'),
 'unknown_header_without_arrow'=>state_fixture('vtnet1.99 tcp 192.168.99.10:52001 -> 198.51.100.20:80 ESTABLISHED:ESTABLISHED').state_fixture('vtnet0 unknown 198.51.100.10 / 203.0.113.20 SINGLE:SINGLE','0000000000000002'),
];
foreach($exceptions as $name=>$text){
 try {$got=kronos_mgmt_states($text);$results[]=['test'=>$name,'status'=>'FAIL','obtained'=>$got,'expected'=>'RuntimeException'];}
 catch(RuntimeException $e){$results[]=['test'=>$name,'status'=>'PASS','obtained'=>'RuntimeException'];}
 catch(Throwable $e){$results[]=['test'=>$name,'status'=>'FAIL','error'=>$e->getMessage()];}
}
$fail=count(array_filter($results,fn($r)=>$r['status']!=='PASS'));
echo json_encode(['scope'=>'synthetic parser fixtures; no PF mutation','pass'=>count($results)-$fail,'fail'=>$fail,'tests'=>$results],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n";
exit($fail?1:0);
