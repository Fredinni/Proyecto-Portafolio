#!/usr/local/bin/php
<?php
// Purge only project MGMT transit states, retaining firewall administration and
// the explicitly allowed Tailscale transport. Never flush the PF state table.
function kronos_state_keep(string $header): bool {
    $self = ['10.254.254.2','192.168.10.1','192.168.20.1','192.168.30.1','192.168.99.1'];
    if (strpos($header, '->') !== false) [$src,$dst] = explode('->',$header,2);
    elseif (strpos($header, '<-') !== false) { [$dst,$src] = explode('<-',$header,2); }
    else return false;
    // Ignore the WAN NAT source address: preserve only when the opposite
    // endpoint is the firewall itself, not every masqueraded MGMT connection.
    $srcMgmt=preg_match('/(?<![\d.])192\.168\.99\.\d{1,3}(?![\d.])/',$src)===1;
    $other=$srcMgmt?$dst:$src;
    preg_match_all('/(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])/', $other, $matches);
    foreach ($matches[0] as $ip) if (in_array($ip, $self, true)) return true;
    if (!preg_match('/(?<![\d.])192\.168\.99\.10(?=[:\s)])/',$src)) return false;
    if (!preg_match('/(?<![\d.])((?:\d{1,3}\.){3}\d{1,3}):(\d+)/',$dst,$target)) return false;
    $ip = ip2long($target[1]); if ($ip === false) return false;
    foreach (['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'] as $cidr) {
        [$net,$bits]=explode('/',$cidr); $mask=(-1 << (32-(int)$bits));
        if (($ip & $mask) === (ip2long($net) & $mask)) return false;
    }
    return (strpos($header,' tcp ')!==false && $target[2]==='443') ||
        (strpos($header,' udp ')!==false && in_array($target[2],['3478','41641'],true));
}
function kronos_mgmt_states(string $text): array {
    $kill=[]; $keep=0; $header=null; $relevant=false; $identified=true;
    foreach (explode("\n",$text) as $line) {
        // Reset for every state header, including GRE/ESP/AH and numeric
        // protocols: never reuse a previous MGMT header for another state ID.
        if (preg_match('/^\S+\s+\S+\s+.*(?:->|<-)/',$line)) {
            if ($relevant && !$identified) throw new RuntimeException('MGMT state without exact ID');
            $header=$line; $relevant=preg_match('/(?<![\d.])192\.168\.99\.\d{1,3}(?![\d.])/',$line)===1;
            $identified=!$relevant;
        } elseif ($line!=='' && !ctype_space($line[0])) {
            throw new RuntimeException('Unrecognized PF state header; no states purged');
        } elseif ($relevant && preg_match('/\bid: ([a-fA-F0-9]{16}) creatorid: ([a-fA-F0-9]+)/',$line,$id)) {
            $identified=true;
            if (kronos_state_keep($header)) $keep++; else $kill[]=$id[1].'/'.$id[2];
        }
    }
    if ($relevant && !$identified) throw new RuntimeException('MGMT state without exact ID');
    return ['kill'=>$kill,'preserved'=>$keep];
}
if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') !== __FILE__) return;
if (function_exists('posix_geteuid') && posix_geteuid()!==0) {fwrite(STDERR,"Requires root\n");exit(1);}
try {
    $lines=[]; exec('/sbin/pfctl -ss -vv 2>/dev/null',$lines,$rc);
    if ($rc!==0) throw new RuntimeException('Cannot read PF states');
    $plan=kronos_mgmt_states(implode("\n",$lines)); $failed=0;
    foreach ($plan['kill'] as $id) {
        $out=[]; exec('/sbin/pfctl -k id -k '.escapeshellarg($id).' 2>&1',$out,$rc);
        if ($rc!==0) $failed++;
    }
    echo json_encode(['selected'=>count($plan['kill']),'preserved'=>$plan['preserved'],'failed'=>$failed])."\n";
    exit($failed===0?0:1);
} catch (Throwable $e) {fwrite(STDERR,$e->getMessage()."\n");exit(1);}
