#!/usr/bin/env python3
"""Synthetic root/Linux namespace tests of installed AWS nftables, not a real WG peer.

Only temporary network namespaces are changed. No host nftables/sysctls/routes change.
Run: sudo python3 test-routing.py --rules /etc/nftables.conf
"""
import argparse
import json
import os
import selectors
import subprocess
import sys
import uuid


def run(*args, data=None):
    return subprocess.run(args, input=data, text=True, capture_output=True,
                          check=True, timeout=15).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", default="/etc/nftables.conf")
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error("Linux root is required")
    with open(args.rules, encoding="utf-8") as handle:
        rules = handle.read()
    # Discover actual WAN metadata; substitute only in our isolated copy.
    route = json.loads(run("ip", "-j", "-4", "route", "show", "default"))[0]
    wan = route["dev"]
    addresses = json.loads(run("ip", "-j", "-4", "addr", "show", "dev", wan))
    private_ip = next(a["local"] for a in addresses[0]["addr_info"]
                      if a.get("scope") == "global")
    rules = rules.replace('"' + wan + '"', '"wan"').replace(private_ip, "192.0.2.1")
    prefix = "kronos-test-" + uuid.uuid4().hex[:10]
    router, client, peer = [prefix + suffix for suffix in ("-r", "-c", "-p")]
    created, processes = [], []

    def ns(name, *command, data=None):
        return run("ip", "netns", "exec", name, *command, data=data)

    def server(name, address, port):
        code = """import json,socket,sys
s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind((sys.argv[1],int(sys.argv[2])));s.listen(1);s.settimeout(12)
print('READY',flush=True)
c,a=s.accept();c.sendall(json.dumps(list(a)).encode());c.close();s.close()
"""
        process = subprocess.Popen(["ip", "netns", "exec", name, sys.executable,
                                    "-u", "-c", code, address, str(port)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        processes.append(process)
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            if not selector.select(5) or process.stdout.readline().strip() != "READY":
                raise RuntimeError("Test listener did not become ready")
        return process

    def connect(name, address, port):
        code = """import json,socket,sys
s=socket.create_connection((sys.argv[1],int(sys.argv[2])),timeout=3)
print(json.dumps({'remote':list(s.getpeername()),'observed_source':json.loads(s.recv(4096))}))
s.close()
"""
        return json.loads(ns(name, sys.executable, "-c", code, address, str(port)))

    def check(condition, message):
        if not condition:
            raise AssertionError(message)
        print("PASS " + message, flush=True)

    try:
        for name in (router, client, peer):
            run("ip", "netns", "add", name)
            created.append(name)
            ns(name, "ip", "link", "set", "lo", "up")
        # Create links inside the namespace directly: no host interfaces are touched.
        ns(router, "ip", "link", "add", "wan", "type", "veth", "peer", "name", "client0")
        ns(router, "ip", "link", "set", "client0", "netns", client)
        ns(router, "ip", "link", "add", "wg0", "type", "veth", "peer", "name", "peer0")
        ns(router, "ip", "link", "set", "peer0", "netns", peer)
        for name, iface, address in ((router, "wan", "192.0.2.1/24"),
                                     (client, "client0", "192.0.2.2/24"),
                                     (router, "wg0", "10.254.254.1/30"),
                                     (peer, "peer0", "10.254.254.2/30")):
            ns(name, "ip", "addr", "add", address, "dev", iface)
            ns(name, "ip", "link", "set", iface, "up")
        ns(client, "ip", "route", "add", "default", "via", "192.0.2.1")
        ns(peer, "ip", "route", "add", "default", "via", "10.254.254.1")
        ns(router, "sysctl", "-qw", "net.ipv4.ip_forward=1")
        ns(router, "nft", "-c", "-f", "-", data=rules)
        ns(router, "nft", "-f", "-", data=rules)

        for port in (80, 443):
            listener = server(peer, "10.254.254.2", port)
            result = connect(client, "192.0.2.1", port)
            listener.communicate(timeout=5)
            check(result["observed_source"][0] == "192.0.2.2",
                  "DNAT TCP/%s preserves client source 192.0.2.2" % port)
            check(result["remote"] == ["192.0.2.1", port],
                  "DNAT TCP/%s reply reverses NAT to WAN 192.0.2.1" % port)

        listener = server(client, "192.0.2.2", 8080)
        result = connect(peer, "192.0.2.2", 8080)
        listener.communicate(timeout=5)
        check(result["observed_source"][0] == "192.0.2.1",
              "Transit-originated outbound TCP masquerades to WAN 192.0.2.1")

        listener = server(router, "192.0.2.1", 22)
        result = connect(client, "192.0.2.1", 22)
        listener.communicate(timeout=5)
        check(result["observed_source"][0] == "192.0.2.2", "Reserved SSH TCP/22 reaches router")

        server(router, "192.0.2.1", 18081)
        blocked = """import socket,sys
try:
 s=socket.create_connection(('192.0.2.1',18081),timeout=2)
except socket.timeout:
 print('DROP')
else:
 s.close();sys.exit('Unexpected successful connection')
"""
        check(ns(client, sys.executable, "-c", blocked).strip() == "DROP",
              "Unpublished router INPUT TCP/18081 drops despite active listener")
        print("SYNTHETIC ROUTING TESTS PASS (veth emulates wg0; no real WireGuard handshake tested)")
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=3)
        for name in reversed(created):
            run("ip", "netns", "del", name)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("FAIL synthetic routing: " + str(exc), file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError):
            print(exc.stderr, file=sys.stderr)
        sys.exit(1)
