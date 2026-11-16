#!/usr/bin/env python3
"""Replay a saved lab incident through the real dispatcher; no pregenerated speech."""

import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("incident_json", type=Path, help="Saved incident JSON; may ring the configured operator")
    parser.add_argument("--url", default=os.getenv("KRONOS_DISPATCH_URL"))
    args = parser.parse_args()
    token = os.getenv("KRONOS_DISPATCH_TOKEN", "")
    if not args.url or not token:
        parser.error("Configure KRONOS_DISPATCH_URL and KRONOS_DISPATCH_TOKEN")
    incident = json.loads(args.incident_json.read_text(encoding="utf-8"))
    if not isinstance(incident, dict) or not incident.get("attacker_ip") or not incident.get("attack_type"):
        parser.error("Incident must include attacker_ip and attack_type")
    incident["lab_replay"] = True
    request = urllib.request.Request(args.url, data=json.dumps(incident).encode(), headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            print(response.read().decode())
    except urllib.error.HTTPError as error:
        print(json.dumps({"success": False, "http_status": error.code}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
