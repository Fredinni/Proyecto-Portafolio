#!/usr/bin/env python3
"""Read-only audit of actual pfSense/FreeBSD prerequisites for A1.

This does not prove Suricata Inline works. No observations are simulated and
historical evidence is never overwritten by default.
"""

import argparse
import datetime
import json
import os
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

CRITICAL_SYSCTLS = {
    "net.inet.ip.fastforwarding": {"expected": 0, "optional": True},
    "net.inet.ip.intr_queue_maxlen": {"minimum": 4096},
    "net.pf.states_hashsize": {"minimum": 131072},
    "kern.ipc.nmbclusters": {"minimum": 1000000},
    "hw.netmap.buf_size": {"expected": 2048, "optional": True},
    "hw.netmap.ring_size": {"expected": 4096, "optional": True},
}
CURRENT_SYSCTLS = {
    "net.inet.ip.forwarding": {"expected": 1},
    "net.inet.ip.intr_queue_maxlen": {"minimum": 4096},
    "net.pf.states_hashsize": {"minimum": 131072},
    "kern.ipc.nmbclusters": {"minimum": 1000000},
    "dev.netmap.buf_size": {"expected": 2048},
    "dev.netmap.buf_curr_size": {"expected": 2048},
    "dev.netmap.ring_curr_size": {"minimum": 1},
}
LEGACY_OIDS = ("net.inet.ip.fastforwarding", "hw.netmap.buf_size",
               "hw.netmap.ring_size")
OFFLOAD_SETTINGS = {
    "checksum": "disablechecksumoffloading",
    "tso": "disablesegmentationoffloading",
    "lro": "disablelargereceiveoffloading",
}
OFFLOAD_OPTION = re.compile(r"^(?:[RT]XCSUM(?:_IPV6)?|TSO(?:4|6)?|LRO)$")


def run_cmd(argv):
    """Retain exit status/stderr; never treat unsuccessful commands as data."""
    try:
        result = subprocess.run(
            argv, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=15,
        )
        return {"returncode": result.returncode, "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": None, "stdout": "", "stderr": str(exc)}


def observation(name, value, expected, status, **details):
    return {"parametro": name, "valor_obtenido": value,
            "valor_esperado": expected, "status": status,
            "cumplimiento": True if status == "PASS" else
            False if status == "FAIL" else None, **details}


def sysctl_check(key, spec, require_legacy=False):
    result = run_cmd(["sysctl", "-n", key])
    expected = (f">= {spec['minimum']}" if "minimum" in spec
                else str(spec["expected"]))
    if result["returncode"] != 0:
        missing_oid = bool(re.search(r"unknown oid|unknown object|no such oid",
                                     result["stderr"], re.IGNORECASE))
        status = ("UNSUPPORTED" if missing_oid and spec.get("optional")
                  and not require_legacy else "FAIL")
        return observation(key, None, expected, status, command=result)
    try:
        value = int(result["stdout"])
    except ValueError:
        return observation(key, result["stdout"], expected, "FAIL",
                           error="sysctl did not return an integer", command=result)
    passed = (value >= spec["minimum"] if "minimum" in spec
              else value == spec["expected"])
    return observation(key, value, expected, "PASS" if passed else "FAIL",
                       command=result)


def configured_offloads(config_path):
    """Return only nonsecret flags and WAN name; never serialize config.xml."""
    root = ET.parse(config_path).getroot()
    system = root.find("system")
    values = {}
    for label, key in OFFLOAD_SETTINGS.items():
        element = system.find(key) if system is not None else None
        values[label] = (element is not None and
                         (element.text or "").strip().lower() in
                         ("", "yes", "true", "1", "on"))
    return values, root.findtext("interfaces/wan/if")


def audit_kernel(config_path="/cf/conf/config.xml", interfaces=None,
                 require_legacy=False, profile="legacy"):
    if profile not in ("legacy", "current"):
        raise ValueError("Unknown audit profile")
    if profile == "current" and require_legacy:
        raise ValueError("--require-legacy-oids applies only to --profile legacy")
    report = {
        "responsable": "Bruno Urrea Ortiz",
        "colaborador": "Freddy Vasquez Cortes",
        "actividad": "A1 - Setup Base pfSense & Netmap Tuning",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "system": platform.system(), "release": platform.release(),
        "profile": profile,
        "items": [],
        "scope": "Kernel, offloading and Netmap device only; no Inline IPS test",
    }
    items = report["items"]
    if report["system"] != "FreeBSD":
        items.append(observation("platform", report["system"], "FreeBSD",
                                 "FAIL" if profile == "current" else "UNSUPPORTED"))
        summarize(report)
        return report

    if profile == "current":
        version = run_cmd(["/bin/cat", "/etc/version"])
        report["pfsense_version"] = version["stdout"]
        supported = (version["returncode"] == 0 and
                     re.fullmatch(r"2\.9\.0(?:-[A-Za-z0-9._-]+)?", version["stdout"])
                     is not None and
                     re.match(r"^16\.", report["release"]) is not None)
        items.append(observation("current profile platform",
                                 {"pfsense": version["stdout"],
                                  "FreeBSD": report["release"]},
                                 "pfSense CE 2.9.0 on FreeBSD 16.x",
                                 "PASS" if supported else "FAIL", command=version))
        if not supported:
            summarize(report)
            return report
        # These historical names do not define acceptance on this kernel.
        # Keep their real command results, outside PASS/FAIL prerequisites.
        report["legacy_diagnostics"] = [
            {"oid": key, "command": run_cmd(["sysctl", "-n", key]),
             "acceptance_requirement": False} for key in LEGACY_OIDS]
        report["netmap_diagnostics"] = [{
            "oid": "dev.netmap.ring_size", "unit": "bytes",
            "command": run_cmd(["sysctl", "-n", "dev.netmap.ring_size"]),
            "acceptance_requirement": False,
            "note": "Allocator ring object size; not a NIC descriptor count or throughput guarantee",
        }]
    required_sysctls = CURRENT_SYSCTLS if profile == "current" else CRITICAL_SYSCTLS
    for key, spec in required_sysctls.items():
        items.append(sysctl_check(key, spec, require_legacy))

    wan = None
    try:
        flags, wan = configured_offloads(config_path)
        for label, key in OFFLOAD_SETTINGS.items():
            items.append(observation(f"config.system.{key}", flags[label],
                                     True, "PASS" if flags[label] else "FAIL"))
    except (OSError, ET.ParseError) as exc:
        items.append(observation("config.xml", None, "Readable valid XML",
                                 "FAIL", error=str(exc)))

    selected_interfaces = interfaces or ([wan] if wan else [])
    if not selected_interfaces:
        items.append(observation("interface selection", None,
                                 "WAN in config.xml or --interface", "FAIL"))
    for interface in dict.fromkeys(selected_interfaces):
        # Interface names are separate argv elements, never shell-interpolated.
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:-]*", interface):
            items.append(observation(f"ifconfig.{interface}", None,
                                     "Valid interface name", "FAIL"))
            continue
        result = run_cmd(["ifconfig", interface])
        if result["returncode"] != 0:
            items.append(observation(f"ifconfig.{interface}", None,
                                     "Readable active options", "FAIL", command=result))
            continue
        # capabilities= lists available features, NOT enabled offload options.
        options = re.findall(r"\boptions[0-9]*=[0-9a-fA-Fx]+<([^>]*)>",
                             result["stdout"])
        if not options:
            items.append(observation(f"ifconfig.{interface}.offloads", None,
                                     "Enabled options visible", "FAIL",
                                     error="No enabled options field in ifconfig output"))
            continue
        enabled = [option.strip() for group in options for option in group.split(",")]
        active_offloads = [option for option in enabled if OFFLOAD_OPTION.fullmatch(option)]
        items.append(observation(f"ifconfig.{interface}.offloads", active_offloads,
                                 [], "FAIL" if active_offloads else "PASS",
                                 enabled_options=enabled))

    netmap = run_cmd(["/bin/test", "-c", "/dev/netmap"])
    items.append(observation("/dev/netmap", netmap["returncode"] == 0,
                             "Character device present",
                             "PASS" if netmap["returncode"] == 0 else "FAIL",
                             command=netmap))
    summarize(report)
    return report


def summarize(report):
    counts = {status: sum(item["status"] == status for item in report["items"])
              for status in ("PASS", "FAIL", "UNSUPPORTED")}
    report["summary"] = counts
    report["estado_general"] = ("FAIL" if counts["FAIL"] else
                                "PARTIAL" if counts["UNSUPPORTED"] and counts["PASS"] else
                                "UNSUPPORTED" if counts["UNSUPPORTED"] else "PASS")
    report["exit_code"] = (1 if counts["FAIL"] else 2 if counts["UNSUPPORTED"] else 0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="/cf/conf/config.xml")
    parser.add_argument("--profile", choices=("legacy", "current"), default="legacy",
                        help="legacy preserves historical reporting; current requires pfSense CE 2.9.0/FreeBSD 16")
    parser.add_argument("--interface", action="append", dest="interfaces",
                        help="Audit active NIC options (repeatable; default: WAN from XML)")
    parser.add_argument("--require-legacy-oids", action="store_true",
                        help="Fail instead of UNSUPPORTED when legacy optional OIDs are absent")
    parser.add_argument("--json", action="store_true", help="Print actual observations as JSON")
    parser.add_argument("--output", help="Explicit evidence output path; existing files refused")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing --output file")
    args = parser.parse_args(argv)
    if args.profile == "current" and args.require_legacy_oids:
        parser.error("--require-legacy-oids applies only to --profile legacy")
    report = audit_kernel(args.config, args.interfaces, args.require_legacy_oids,
                          args.profile)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"KRONOS A1 audit | {report['system']} {report['release']}")
        print(f"Profile: {report['profile']}")
        for item in report["items"]:
            print(f"[{item['status']}] {item['parametro']}: "
                  f"{item['valor_obtenido']!r}; expected {item['valor_esperado']!r}")
            error = item.get("error") or item.get("command", {}).get("stderr")
            if error:
                print(f"  {error}")
        print(f"RESULT: {report['estado_general']} | {report['summary']}")
        print(report["scope"])
        for diagnostic in report.get("legacy_diagnostics", []) + report.get("netmap_diagnostics", []):
            print(f"[INFO] {diagnostic['oid']}: {diagnostic['command']!r}; not an acceptance requirement")
    if args.output:
        flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if args.overwrite else os.O_EXCL)
        try:
            with os.fdopen(os.open(args.output, flags, 0o600), "w", encoding="utf-8") as stream:
                json.dump(report, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
        except OSError as exc:
            print(f"Evidence output failed: {exc}", file=sys.stderr)
            return 1
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
