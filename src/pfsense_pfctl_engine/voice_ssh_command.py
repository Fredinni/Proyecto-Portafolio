#!/usr/local/bin/python3.11
"""Forced SSH command for the voice key: one table, individual IPs, no shell."""

import ipaddress
import json
import os
import re
from pathlib import Path
import shlex
import subprocess
import sys


def validate_command(command, table, protected_ips=()):
    args = shlex.split(command)
    if len(args) == 2 and args[0] == "kronos-incident-identity" and re.fullmatch(r"[a-f0-9]{64}", args[1]):
        return ["/usr/local/bin/python3.11", str(Path(__file__).with_name("incident_store.py")), args[1]]
    if args == ["pfctl", "-t", table, "-T", "show"]:
        return ["/sbin/pfctl", *args[1:]]
    mutating_ip = None
    if len(args) == 6 and args[:4] == ["pfctl", "-t", table, "-T"] and args[4] in {"add", "delete"}:
        mutating_ip = args[5]
    elif len(args) == 3 and args[:2] == ["pfctl", "-k"]:
        mutating_ip = args[2]
    elif len(args) == 5 and args[:4] == ["pfctl", "-k", "0.0.0.0/0", "-k"]:
        mutating_ip = args[4]
    if mutating_ip is None:
        raise ValueError("Command not allowed")
    ip = ipaddress.ip_address(mutating_ip)
    if ip.is_unspecified or ip.is_multicast or ip.is_loopback or ip.is_link_local or str(ip) in protected_ips:
        raise ValueError("Protected address")
    return ["/sbin/pfctl", *args[1:]]


def main():
    try:
        config = json.loads(Path("/usr/local/etc/kronos/voice-firewall.json").read_text())
        command = validate_command(os.getenv("SSH_ORIGINAL_COMMAND", ""),
                                   config["pfctl_table"], config.get("protected_ips", []))
    except (ValueError, KeyError, OSError):
        print("KRONOS: command denied", file=sys.stderr)
        return 126
    result = subprocess.run(command, timeout=5, capture_output=True)
    sys.stdout.buffer.write(result.stdout)
    sys.stderr.buffer.write(result.stderr)
    if "show" not in command:
        import syslog
        syslog.syslog(syslog.LOG_NOTICE, "KRONOS voice action " + shlex.join(command[1:]) +
                      " rc=" + str(result.returncode))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
