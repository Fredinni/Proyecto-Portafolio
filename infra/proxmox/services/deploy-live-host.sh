#!/usr/bin/env bash
# Update a prepared KRONOS VM103 using the unprivileged host runtime.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd -P)
REPO=$(cd "$HERE/../../.." && pwd -P)
test "$(id -u)" -eq 0
ip -4 address show | grep -q 'inet 192.168.30.50/24'
test -r /etc/kronos/voice.env
test -r /etc/kronos/voice/config.json
test -x /opt/kronos/voice-venv/bin/python
getent passwd kronos-voice >/dev/null
set -a
. /etc/kronos/voice.env
set +a
sudo -E -u kronos-voice /opt/kronos/voice-venv/bin/python "$REPO/src/asterisk_pbx/voice_preflight.py"
docker exec kronos_asterisk_pbx asterisk -rx 'core show channels count' | grep -q '^0 active calls'

BACKUP="/etc/kronos/backups/live-update-$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 0700 "$BACKUP"
cp -p /etc/kronos/asterisk/extensions.conf "$BACKUP/extensions.conf"
readlink -f /opt/kronos/live-current > "$BACKUP/previous-release"
ln -sfn "$REPO" /opt/kronos/live-current
install -m 0644 "$HERE/kronos-live-tmpfiles.conf" /etc/tmpfiles.d/kronos-live.conf
systemd-tmpfiles --create /etc/tmpfiles.d/kronos-live.conf
for service in kronos-voice kronos-dispatcher; do
    install -m 0644 "$HERE/$service.service" "/etc/systemd/system/$service.service"
done
systemd-analyze verify /etc/systemd/system/kronos-voice.service /etc/systemd/system/kronos-dispatcher.service
chmod 0755 "$REPO/src/asterisk_pbx/gemini_audio_bridge.py"
install -m 0640 "$REPO/src/asterisk_pbx/extensions.conf" /etc/kronos/asterisk/extensions.conf
systemctl daemon-reload
systemctl enable --now kronos-voice.service kronos-dispatcher.service
systemctl restart kronos-voice.service kronos-dispatcher.service
docker compose -f "$HERE/compose.voip.yml" -f "$HERE/compose.live-host.yml" up -d --no-build --force-recreate asterisk
systemctl is-active kronos-voice.service kronos-dispatcher.service
printf 'Updated; previous dialplan and release recorded in %s\n' "$BACKUP"
