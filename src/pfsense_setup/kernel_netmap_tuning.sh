#!/bin/sh
# KRONOS A1: read-only audit for the supported pfSense CE 2.9.0 / FreeBSD 16 profile.
# No loader.conf/sysctl.conf/config.xml writes, sysctl assignments, or interface changes.
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if ! command -v python3.11 >/dev/null 2>&1; then
    printf '%s\n' 'FAIL: python3.11 is required to measure the deployed pfSense.' >&2
    exit 1
fi
exec python3.11 "$SCRIPT_DIR/verify_kernel_hardening.py" --profile current "$@"
