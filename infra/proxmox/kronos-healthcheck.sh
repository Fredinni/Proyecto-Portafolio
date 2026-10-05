#!/usr/bin/env bash
# Read-only inventory and guest probes. Run from Bash with SSH access via Tailscale.
set -u
HOST=${KRONOS_PVE_HOST:?Set KRONOS_PVE_HOST to the operator-only Proxmox hostname or IP}
KEY=${KRONOS_SSH_KEY:-$HOME/.ssh/kronos-lab-ed25519}
ssh -T -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 "root@$HOST" 'python3 -' <<'PY'
import json, pathlib, re, subprocess, sys
failed = False
pending = False
def report(state, label):
    global failed, pending
    print(f'{state}: {label}', flush=True)
    failed |= state == 'FAIL'
    pending |= state == 'WAITING_FOR_MANUAL_ACTION'
def run(args):
    try:
        p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
        return p.returncode, p.stdout.strip()
    except subprocess.TimeoutExpired:
        return 124, 'timeout'
def host(label, args):
    rc, out = run(args)
    report('PASS' if rc == 0 else 'FAIL', label)
    print(out)
def guest(vmid, label, script, waiting_code=None):
    rc, out = run(['qm','guest','exec',str(vmid),'--timeout','25','--','/bin/sh','-c',script])
    if rc:
        report('FAIL', f'{label}: guest agent unavailable or command rejected')
        print(out)
        return 'FAIL'
    try:
        data=json.loads(out)
    except ValueError:
        report('FAIL', f'{label}: unparseable guest result')
        return 'FAIL'
    state = 'FAIL'
    if data.get('exited'):
        if data.get('exitcode') == 0:
            state = 'PASS'
        elif waiting_code is not None and data.get('exitcode') == waiting_code:
            state = 'WAITING_FOR_MANUAL_ACTION'
    report(state, label)
    print(data.get('out-data','').strip())
    print(data.get('err-data','').strip())
    return state
host('Proxmox version', ['pveversion'])
host('VM inventory (existence only)', ['qm','list'])
host('Storage availability', ['pvesm','status'])
host('Host addresses', ['ip','-br','addr'])
host('Host default route', ['ip','route','show','default'])
host('VLAN membership inventory (not isolation validation)', ['bridge','vlan','show'])
for br in ('vmbr2','vmbr3'):
    rc,out=run(['ip','-j','addr','show',br])
    try:
        links=json.loads(out)
        clean=bool(links) and not any(a.get('family') in ('inet','inet6') for l in links for a in l.get('addr_info',[]))
    except ValueError:
        clean=False
    report('PASS' if rc == 0 and clean else 'FAIL', f'{br} exists without host IP')
    ports = pathlib.Path('/sys/class/net',br,'brif')
    if ports.is_dir():
        members = [p.name for p in ports.iterdir()]
        allowed = {'vmbr2': {'tap100i1','tap101i0','fwpr100p1','fwpr101p0'},
                   'vmbr3': {'tap101i1','fwpr101p1'} | {f'tap{i}i0' for i in range(102,106)} | {f'fwpr{i}p0' for i in range(102,106)}}
        isolated = all(p in allowed[br] and not pathlib.Path('/sys/class/net',p,'device').exists() for p in members)
        report('PASS' if isolated else 'FAIL', f'{br} only expected virtual VM ports: {members}')
    else:
        report('FAIL',f'{br} bridge port directory missing')
host('Trunk VLAN filtering enabled', ['sh','-c','test "$(cat /sys/class/net/vmbr3/bridge/vlan_filtering)" = 1'])
expected_nics = {100: {'net0':('vmbr0',None),'net1':('vmbr2',None)},
                 101: {'net0':('vmbr2',None),'net1':('vmbr3',None)},
                 **{i:{'net0':('vmbr3',tag)} for i,tag in ((102,'20'),(103,'30'),(104,'10'),(105,'99'))}}
for vmid, expected in expected_nics.items():
    rc,out=run(['qm','config',str(vmid)])
    actual={}
    for line in out.splitlines():
        if re.match(r'^net\d+:',line):
            key,value=line.split(':',1)
            actual[key]=dict(part.strip().split('=',1) for part in value.strip().split(',') if '=' in part)
    correct = rc == 0 and set(actual) == set(expected)
    for nic,(bridge,tag) in expected.items():
        item=actual.get(nic,{})
        correct &= item.get('bridge') == bridge and item.get('tag') == tag and 'virtio' in item
        correct &= item.get('link_down','0') == '0'
        if vmid != 101 or nic != 'net1':
            correct &= not item.get('trunks')
        elif item.get('trunks'):
            correct &= set(item['trunks'].split(';')) == {'10','20','30','99'}
    report('PASS' if correct else 'FAIL',f'VM {vmid} exact NIC/bridge/VLAN configuration; no extra NIC')
rc,out=run(['bridge','-j','vlan','show'])
try:
    membership={row['ifname']:row.get('vlans',[]) for row in json.loads(out)} if rc == 0 else {}
except (ValueError,KeyError,TypeError):
    membership={}
def port_vlans(port):
    result={}
    for row in membership.get(port,[]):
        first=int(row['vlan'])
        for vlan in range(first,int(row.get('vlanEnd',first))+1):
            result[vlan]=set(row.get('flags',[]))
    return result
for vmid,tag in ((101,None),(102,20),(103,30),(104,10),(105,99)):
    index=1 if vmid==101 else 0
    candidates=[f'tap{vmid}i{index}',f'fwpr{vmid}p{index}']
    ports=[p for p in candidates if pathlib.Path('/sys/class/net/vmbr3/brif',p).exists()]
    vlans=port_vlans(ports[0]) if len(ports)==1 else {}
    if tag is None:
        good={10,20,30,99}.issubset(vlans) and all(not vlans[v] & {'PVID','Egress Untagged'} for v in (10,20,30,99))
    else:
        good=set(vlans)=={tag} and {'PVID','Egress Untagged'}.issubset(vlans[tag])
    report('PASS' if good else 'FAIL',f'VM {vmid} live trunk/access VLAN membership {ports}')
for vmid in range(100,106):
    rc,out=run(['qm','status',str(vmid)])
    if vmid==101 and 'running' not in out:
        report('WAITING_FOR_MANUAL_ACTION','pfSense 101: install official CE image and configure VLAN gateways')
    else:
        report('PASS' if rc==0 and 'running' in out else 'FAIL',f'VM {vmid}: {out}')
guest(100,'Edge exact transit / policy / uplink routes', '''python3 - <<'EDGE'
import json, subprocess
def ip(*args):
    return json.loads(subprocess.check_output(['ip','-j','-4',*args],text=True))
addresses=ip('addr','show')
transit=[a['ifname'] for a in addresses if any(x.get('local')=='10.254.254.1' and x.get('prefixlen')==30 for x in a.get('addr_info',[]))]
assert len(transit)==1, 'transit address missing/ambiguous'
assert subprocess.check_output(['sysctl','-n','net.ipv4.ip_forward'],text=True).strip()=='1', 'forwarding disabled'
main=ip('route','show','table','main','default')
assert len(main)==1 and main[0].get('dev') not in ('wg0',transit[0]) and main[0].get('gateway'), 'default must remain on uplink'
rules=ip('rule','show')
assert any((r.get('src')=='10.254.254.0/30' or (r.get('src')=='10.254.254.0' and str(r.get('srclen'))=='30')) and str(r.get('table'))=='51820' for r in rules), 'source policy rule missing'
table=ip('route','show','table','51820')
assert any(r.get('dst')=='default' and r.get('dev')=='wg0' for r in table), 'policy default missing'
route=ip('route','get','10.254.254.2','from','10.255.255.1','iif','wg0')
assert route and route[0].get('dev')==transit[0], 'incoming packets do not route to transit'
route=ip('route','get','1.1.1.1','from','10.254.254.2','iif',transit[0])
assert route and route[0].get('dev')=='wg0', 'pfSense traffic does not route to WireGuard'
print(json.dumps({'transit':transit[0],'uplink_default':main,'policy_rules':rules,'table51820':table}))
EDGE''')
guest(100,'Edge persistent routing unit and loaded nftables table','systemctl is-active kronos-local-routing.service && systemctl is-enabled kronos-local-routing.service && nft list table inet kronos_local_edge')
guest(100,'WireGuard exact address / UP / recent handshake', '''systemctl is-active wg-quick@wg0 && python3 - <<'WG'
import json, subprocess, time
links=json.loads(subprocess.check_output(['ip','-j','-4','addr','show','wg0'],text=True))
assert len(links)==1 and 'UP' in links[0].get('flags',[]), 'wg0 not administratively UP'
assert any(a.get('local')=='10.255.255.2' and a.get('prefixlen')==30 for a in links[0].get('addr_info',[])), 'wrong WireGuard address'
rows=subprocess.check_output(['wg','show','wg0','latest-handshakes'],text=True).splitlines()
ages=[time.time()-int(row.split()[1]) for row in rows if len(row.split())==2 and int(row.split()[1])>0]
assert len(rows)==1 and len(ages)==1 and 0<=ages[0]<180, 'AWS peer handshake absent, stale or future-dated'
subprocess.run(['wg','show','wg0'],check=True)
WG''')
guest(100,'AWS tunnel ICMP','ping -c 2 -W 3 10.255.255.1')
guest(100,'Edge uplink Internet','curl -4 --connect-timeout 5 --max-time 10 -fsS -o /dev/null https://cloud-images.ubuntu.com/')
guest(100,'pfSense WAN ICMP (requires diagnostic WAN allow from Edge)',
      'if ping -c 2 -W 3 10.254.254.2; then exit 0; else echo "No ICMP reply: verify pfSense installation, route and explicit diagnostic ICMP rule; reachability NOT validated"; exit 2; fi',waiting_code=2)
for vmid,addr,gateway in ((102,'192.168.20.50','192.168.20.1'),(103,'192.168.30.50','192.168.30.1'),(104,'192.168.10.50','192.168.10.1'),(105,'192.168.99.10','192.168.99.1')):
    guest(vmid,f'VM {vmid} address {addr}',f'ip -br addr; ip route; ip -4 -o addr | grep -F " {addr}/24 "')
    guest(vmid,f'VM {vmid} VLAN gateway {gateway}',f'ping -c 2 -W 3 {gateway}')
guest(102,'DVWA HTTP (not login/DB validation)','curl -sS --connect-timeout 3 --max-time 8 -o /dev/null -w "HTTP %{http_code}\\n" -f http://192.168.20.50/')
guest(103,'Asterisk container running (not AMI/Gemini validation)','systemctl is-active docker && docker ps --format "{{.Names}} {{.Status}}" && test "$(docker inspect -f \'{{.State.Running}}\' kronos_asterisk_pbx)" = true && docker exec kronos_asterisk_pbx asterisk -rx "core show version"')
guest(105,'MGMT SSH','systemctl is-active ssh')
guest(105,'MGMT Tailscale authentication','''python3 - <<'TS'
import json, subprocess, sys
p=subprocess.run(['tailscale','status','--json'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
    data=json.loads(p.stdout)
except ValueError:
    print('Tailscale returned no valid status; daemon/installation must be checked')
    sys.exit(1)
state=data.get('BackendState')
print('BackendState:',state)
if state=='NeedsLogin':
    print('TAILSCALE_WAITING_FOR_AUTH')
    sys.exit(2)
if state=='NeedsMachineAuth':
    print('TAILSCALE_WAITING_FOR_ADMIN_APPROVAL')
    sys.exit(2)
assert p.returncode==0 and state=='Running' and data.get('Self',{}).get('Online') is True, 'Tailscale not online'
print('Tailscale online; advertised-route approval and ACL access require separate probes')
TS''',waiting_code=2)
def ssh_probe(address, blocked=False):
    return "python3 - <<'PROBE'\n" + f'''
import errno, socket, sys
address={address!r}
blocked={blocked!r}
try:
    with socket.create_connection((address,22),timeout=5) as conn:
        if blocked:
            print('Unexpected TCP22 connection: isolation failed')
            sys.exit(1)
        conn.settimeout(5)
        banner=conn.recv(128)
    assert banner.startswith(b'SSH-'), 'TCP22 listener is not SSH'
    print('Known SSH listener reachable:',address)
except (TimeoutError, ConnectionRefusedError) as error:
    if not blocked:
        raise
    print('TCP22 blocked/refused with live positive control:',address,type(error).__name__)
except OSError as error:
    print('Network error is inconclusive, not an isolation PASS:',error.errno)
    sys.exit(1)
''' + '\nPROBE'
controls={}
for vmid,address in ((102,'192.168.20.50'),(104,'192.168.10.50'),(105,'192.168.99.10')):
    controls[address]=guest(105,f'Segmentation positive control MGMT -> SSH {address}',ssh_probe(address))=='PASS'
for source,gateway,target in ((104,'192.168.10.1','192.168.99.10'),(102,'192.168.20.1','192.168.99.10'),(102,'192.168.20.1','192.168.10.50')):
    route_script=f'''ping -c 1 -W 3 {gateway} >/dev/null && python3 - <<'ROUTE'
import json,subprocess
route=json.loads(subprocess.check_output(['ip','-j','-4','route','get',{target!r}],text=True))
assert len(route)==1 and route[0].get('gateway')=={gateway!r}, 'probe does not route via pfSense VLAN gateway'
print('Probe routes through pfSense:',route[0].get('gateway'))
ROUTE'''
    route_ok=guest(source,f'Segmentation VM{source} pfSense gateway/route prerequisite',route_script)=='PASS'
    if controls[target] and route_ok:
        guest(source,f'Segmentation VM{source} -> {target}:22 denied (known SSH listener)',ssh_probe(target,blocked=True))
    else:
        report('WAITING_FOR_MANUAL_ACTION',f'Segmentation VM{source} -> {target} not assessed: positive listener or gateway prerequisite failed')
print('EVIDENCE_RECORDED: deployment capture on pfSense vtnet0 preserved public source 186.67.242.29. This historical test is NOT executed by this healthcheck; repeat with a controlled external request and capture for current validation.')
report('WAITING_FOR_MANUAL_ACTION','pfSense offloads/Netmap require the separate live on-box audit; Suricata Inline, DVWA login and HAProxy/HTTPS remain untested here; historical capture is separate from live probes')
sys.exit(1 if failed else 2 if pending else 0)
PY
