"""Small local evidence store; the SSH reader exposes incident identity only."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

IDENTITY_FIELDS = ("incident_id", "timestamp", "attacker_ip", "target_ip", "target_service",
                   "signature", "signature_id", "sensor_action", "sensor_dropped", "source_identity",
                   "source_protected", "attacker_public_ip", "attacker_private_ip", "victim_private_ip",
                   "observed_source_ip", "origin_resolution", "attacker_public_ip_status")
IDENTITY_FIELDS += ("sensor_log", "flow_id")


def save_identity(directory, incident):
    material = {k: incident.get(k) for k in ("timestamp", "attacker_ip", "target_ip", "signature_id", "signature")}
    identity = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()
    incident["incident_id"] = identity
    root = Path(directory)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = root / (identity + ".json")
    data = {k: incident[k] for k in IDENTITY_FIELDS if k in incident}
    with tempfile.NamedTemporaryFile(mode='w', dir=root, suffix='.tmp', delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(data, stream)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return identity


def read_identity(directory, identity):
    if not re.fullmatch(r"[a-f0-9]{64}", identity):
        raise ValueError("Invalid incident ID")
    path = Path(directory) / (identity + ".json")
    if path.is_symlink() or path.stat().st_size > 16384:
        raise ValueError("Invalid evidence file")
    data = json.loads(path.read_text())
    if data.get("incident_id") != identity:
        raise ValueError("Incident ID mismatch")
    return {"success": True, "source": "PFSENSE_EVE",
            "incident": {k: data[k] for k in IDENTITY_FIELDS if k in data}}


def main():
    try:
        config = json.loads(Path('/usr/local/etc/kronos/voice-firewall.json').read_text())
        print(json.dumps(read_identity(config['incident_store_dir'], sys.argv[1])))
    except (OSError, ValueError, KeyError, IndexError):
        print(json.dumps({"success": False, "error": "Evidence unavailable on pfSense"}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
