#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO=$(cd "$HERE/../../.." && pwd)
test "$(id -u)" -eq 0
ip -4 addr show | grep -q 'inet 192.168.20.50/24'
if [ "${OFFLINE:-0}" != 1 ]; then
  bash "$HERE/install-docker.sh"
fi
install -d -m 0700 /etc/kronos
if [ ! -f /etc/kronos/dvwa.env ]; then
  umask 077
  python3 - <<'PY'
import secrets
from pathlib import Path
with Path('/etc/kronos/dvwa.env').open('x') as f:
    f.write('DVWA_DB_PASSWORD=' + secrets.token_hex(32) + '\n')
    f.write('DVWA_DB_ROOT_PASSWORD=' + secrets.token_hex(32) + '\n')
PY
fi
chmod 0600 /etc/kronos/dvwa.env
COMPOSE=(docker compose --env-file /etc/kronos/dvwa.env -f "$REPO/src/haproxy_dvwa/docker-compose.dvwa.yml")
"${COMPOSE[@]}" config --quiet
if [ "${OFFLINE:-0}" != 1 ]; then
  "${COMPOSE[@]}" pull
fi
"${COMPOSE[@]}" up -d --pull never --wait --wait-timeout 180
curl --retry 12 --retry-connrefused --retry-delay 2 --fail --silent --show-error --max-time 15 -o /dev/null http://192.168.20.50/login.php
"${COMPOSE[@]}" ps
echo 'DVWA HTTP responded. Database initialization/login and A5 validation remain separate tests.'
