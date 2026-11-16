#!/usr/local/bin/python3.11
"""Persistent local pfSense collector for the configured EVE sensor logs."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys

from log_correlator import PfctlLogCorrelator


def main():
    service = json.loads(Path(sys.argv[1]).read_text())
    token = Path(service["dispatch_token_file"]).read_text().strip()
    if len(token) < 24:
        raise ValueError("Missing dispatcher token")
    os.environ["KRONOS_DISPATCH_TOKEN"] = token
    os.environ["KRONOS_DISPATCH_URL"] = service["dispatch_url"]
    paths = service["eve_paths"]
    if not paths or len(paths) > 8:
        raise ValueError("Configure one to eight EVE logs")
    collectors = []
    for path in paths:
        collector = PfctlLogCorrelator(service["engine_config"])
        collector.eve_log_path = path
        collectors.append(collector)
    with ThreadPoolExecutor(max_workers=len(collectors)) as pool:
        futures = [pool.submit(collector.tail_eve_log) for collector in collectors]
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
