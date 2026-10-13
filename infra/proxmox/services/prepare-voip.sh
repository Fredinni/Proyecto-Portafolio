#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO=$(cd "$HERE/../../.." && pwd)
test "$(id -u)" -eq 0
ip -4 addr show | grep -q 'inet 192.168.30.50/24'
if [ "${OFFLINE:-0}" != 1 ]; then
  bash "$HERE/install-docker.sh"
  export DEBIAN_FRONTEND=noninteractive
  apt-get install -y --no-install-recommends build-essential python3 python3-venv
fi
install -d -m 0750 /etc/kronos/asterisk
if [ ! -f /etc/kronos/asterisk/pjsip.conf ]; then
  cat > /etc/kronos/asterisk/pjsip.conf <<'EOF'
[global]
type=global
user_agent=KRONOS-SENTINEL-LAB
[transport-udp]
type=transport
protocol=udp
bind=192.168.30.50:5060
; Freddy must add authenticated endpoints with fresh secrets outside Git.
EOF
fi
if [ ! -f /etc/kronos/asterisk/manager.conf ]; then
  printf '[general]\nenabled=no\n' > /etc/kronos/asterisk/manager.conf
fi
if [ ! -f /etc/kronos/asterisk/extensions.conf ]; then
  printf '[general]\nstatic=yes\nwriteprotect=yes\n[kronos-internal]\n; Pending endpoints and validated voice integration.\n' > /etc/kronos/asterisk/extensions.conf
fi
if [ ! -f /etc/kronos/asterisk/rtp.conf ]; then
  install -m 0640 "$REPO/src/asterisk_pbx/rtp.conf" /etc/kronos/asterisk/rtp.conf
fi
chmod 0640 /etc/kronos/asterisk/*.conf
docker compose -f "$HERE/compose.voip.yml" config --quiet
if [ "${OFFLINE:-0}" = 1 ]; then
  docker compose -f "$HERE/compose.voip.yml" up -d --no-build --pull never
else
  docker compose -f "$HERE/compose.voip.yml" up -d --build
fi
for attempt in {1..30}; do
  if docker exec kronos_asterisk_pbx asterisk -rx 'core show version'; then
    echo 'ASTERISK_CONTAINER_PROVISIONED; AMI_NOT_CONFIGURED; GEMINI_TRANSPORT_NOT_IMPLEMENTED; GEMINI_E2E_NOT_TESTED'
    exit 0
  fi
  sleep 2
done
echo 'Asterisk CLI not ready' >&2
exit 1
