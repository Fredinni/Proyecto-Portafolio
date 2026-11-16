#!/usr/bin/env bash
# Deploy only on the KRONOS VoIP VM, preserving the existing SIP credentials.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO=$(cd "$HERE/../../.." && pwd)
test "$(id -u)" -eq 0
test -r /etc/kronos/voice.env
test -r /etc/kronos/voice/config.json
test -r /etc/kronos/asterisk/pjsip.conf
test -r /etc/kronos/asterisk/manager.conf

BASE=(docker compose -f "$HERE/compose.voip.yml")
LIVE=(docker compose -f "$HERE/compose.voip.yml" -f "$HERE/compose.live.yml")
"${LIVE[@]}" config --quiet
docker exec kronos_asterisk_pbx asterisk -rx 'module show like app_audiosocket.so' | grep -q app_audiosocket.so
test "$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' kronos_asterisk_pbx)" = kronos-voip
"${LIVE[@]}" build voice
# Nothing has been switched yet: verify real model access and SSH first.
"${LIVE[@]}" run --rm --no-deps voice python /opt/kronos/src/asterisk_pbx/voice_preflight.py

BACKUP="/etc/kronos/voice-backup-$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 0700 "$BACKUP"
# Preserve files installed manually inside the old PBX as well as bind mounts.
ROLLBACK_IMAGE="kronos-asterisk:prelive-$(date -u +%Y%m%d%H%M%S)"
docker commit kronos_asterisk_pbx "$ROLLBACK_IMAGE" > "$BACKUP/container-image-id"
printf 'services:\n  asterisk:\n    image: %s\n' "$ROLLBACK_IMAGE" > "$BACKUP/rollback.compose.yml"
cp -p /etc/kronos/asterisk/extensions.conf "$BACKUP/extensions.conf"
cp -p /etc/kronos/voice.env "$BACKUP/voice.env"
printf '%s\n' "$BACKUP" > /etc/kronos/last-voice-backup
chmod 0600 /etc/kronos/last-voice-backup
chmod +x "$REPO/src/asterisk_pbx/gemini_audio_bridge.py"
install -m 0640 "$REPO/src/asterisk_pbx/extensions.conf" /etc/kronos/asterisk/extensions.conf
# Recreate for the new shared call-context mount and AGI bind mount.
if ! "${LIVE[@]}" up -d --no-build; then
  cp -p "$BACKUP/extensions.conf" /etc/kronos/asterisk/extensions.conf
  "${BASE[@]}" -f "$BACKUP/rollback.compose.yml" up -d --force-recreate --no-build
  echo 'Deploy failed; previous PBX dialplan restored.' >&2
  exit 1
fi
docker exec kronos_asterisk_pbx asterisk -rx 'dialplan show 1000@kronos-internal'
docker exec kronos_asterisk_pbx asterisk -rx 'pjsip show contacts'
echo 'LIVE_DEPLOYED; telephone audio and authorized unblock still require end-to-end verification.'
