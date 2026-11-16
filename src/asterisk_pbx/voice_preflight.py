#!/usr/bin/env python3
"""Read-only readiness checks. Does not place calls or modify firewall tables."""

import asyncio
import json
from pathlib import Path
import sys

from live_audio_server import load_config
from gemini_live_client import GeminiLiveVoiceClient
from pfctl_wrapper import PfctlWrapper


async def check():
    checks = {}
    try:
        config = load_config()
        checks["configuration"] = "PASS"
    except Exception as error:
        return {"ready": False, "checks": {"configuration": type(error).__name__}}
    for field in ("ssh_identity_file", "ssh_known_hosts"):
        checks[field] = "PASS" if Path(config.get(field, "/missing")).is_file() else "FAIL"
    try:
        state = await asyncio.to_thread(PfctlWrapper(config).get_ip_status, "127.0.0.1")
        checks["firewall_table_read"] = "PASS" if state["success"] and state["verified"] else "FAIL"
    except Exception:
        checks["firewall_table_read"] = "FAIL"
    try:
        client = GeminiLiveVoiceClient()
        from urllib.parse import urlencode
        url = ("wss://generativelanguage.googleapis.com/ws/"
               "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?"
               + urlencode({"key": client.api_key}))
        async with client.connect(url, open_timeout=12, close_timeout=3) as ws:
            await ws.send(json.dumps(client.setup_message({"mode": "PREFLIGHT"})))
            ack = json.loads(await asyncio.wait_for(ws.recv(), 15))
            checks["gemini_live_setup"] = "PASS" if "setupComplete" in ack else "FAIL"
        checks["model"] = client.model
    except Exception as error:
        checks["gemini_live_setup"] = "FAIL:" + type(error).__name__
    ready = all(checks.get(k) == "PASS" for k in (
        "configuration", "ssh_identity_file", "ssh_known_hosts", "firewall_table_read", "gemini_live_setup"))
    return {"ready": ready, "checks": checks, "telephone_e2e_verified": False}


if __name__ == "__main__":
    result = asyncio.run(check())
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["ready"] else 1)
