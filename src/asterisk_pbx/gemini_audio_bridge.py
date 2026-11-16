#!/usr/bin/env python3
"""AGI metadata handoff. All audio is transported by AudioSocket, never RECORD FILE."""

import base64
import json
import os
from pathlib import Path
import re
import sys
import time
import uuid


def command(value):
    print(value, flush=True)
    response = sys.stdin.readline().strip()
    if not response or "result=-1" in response:
        raise RuntimeError("AGI channel closed")
    return response


def variable(name):
    response = command("GET VARIABLE " + name)
    match = re.match(r"200 result=1 \((.*)\)$", response)
    return match.group(1) if match else ""


def register_context(env, mode, get_variable=variable, directory=None):
    # PJSIP/<endpoint>-<call-id> identifies the authenticated endpoint. CallerID
    # on outbound alerts is the bot's 1000, not the person who answered.
    endpoint = re.fullmatch(r"PJSIP/([A-Za-z0-9_]+)-[0-9a-fA-F]+", env.get("agi_channel", ""))
    extension = endpoint.group(1) if endpoint else ""
    encoded = ""
    if mode != "DIRECT_CALL":
        parts = get_variable("INCIDENT_PARTS")
        if parts:
            count = int(parts)
            if not 1 <= count <= 54:
                raise ValueError("Invalid incident part count")
            encoded = "".join(get_variable(f"INCIDENT_JSON_{i:03d}") for i in range(count))
        else:
            encoded = get_variable("INCIDENT_JSON")
    context = {}
    if encoded:
        if len(encoded) > 24000:
            raise ValueError("Incident context too large")
        context = json.loads(base64.b64decode(encoded, validate=True))
        if not isinstance(context, dict):
            raise ValueError("Incident context must be an object")
    elif mode != "DIRECT_CALL":
        # Compatibility with existing AMI and call-file dispatchers.
        context = {"attack_type": get_variable("INCIDENT_TYPE"),
                   "attacker_ip": get_variable("ATTACKER_IP"),
                   "geo_country": get_variable("GEO_ORIGIN")}
    context.update({"mode": mode, "operator_extension": extension, "created_at": time.time()})
    session_id = str(uuid.uuid4())
    root = Path(directory or os.getenv("KRONOS_CALL_DIR", "/run/kronos/calls"))
    root.mkdir(parents=True, exist_ok=True, mode=0o750)
    path = root / (session_id + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(context, handle, ensure_ascii=False)
    return session_id


def main():
    env = {}
    for line in sys.stdin:
        if not line.strip():
            break
        key, _, value = line.partition(":")
        env[key.strip()] = value.strip()
    try:
        mode = "DIRECT_CALL" if sys.argv[1:2] == ["DIRECT_CALL"] else "INCIDENT"
        session_id = register_context(env, mode)
        command(f'SET VARIABLE KRONOS_SESSION_ID "{session_id}"')
    except Exception:
        command('SET VARIABLE KRONOS_SESSION_ID ""')
        # Never print secrets or Python traceback on the AGI command channel.
        command('VERBOSE "KRONOS: fallo registrando contexto de llamada" 1')


if __name__ == "__main__":
    main()
