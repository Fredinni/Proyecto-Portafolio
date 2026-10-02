#!/usr/bin/env bash
# Install exactly one password-based KRONOS team account on a named project VM.
# Password is read from stdin; never pass it as an argument or log it.
set -Eeuo pipefail
umask 077

expected_host=${1:?expected KRONOS hostname required}
case "$expected_host" in
  KRONOS-EDGE|KRONOS-DMZ|KRONOS-VOIP|KRONOS-CORP-TEST|KRONOS-MGMT) ;;
  *) echo 'Refusing non-KRONOS hostname' >&2; exit 1 ;;
esac
[[ $(id -u) == 0 && $(hostname) == "$expected_host" ]] || {
  echo 'Wrong guest or not root; no account changed' >&2; exit 1;
}
IFS= read -r password || [[ -n ${password:-} ]]
[[ $password =~ ^[A-Za-z0-9_-]{30,80}$ ]] || {
  echo 'Password format invalid; no account changed' >&2; exit 1;
}

if id kronos >/dev/null 2>&1; then
  [[ $(id -u kronos) -ge 1000 ]] || { echo 'Existing kronos user has unexpected UID' >&2; exit 1; }
else
  useradd --create-home --shell /bin/bash kronos
fi
usermod --append --groups sudo kronos
printf 'kronos:%s\n' "$password" | chpasswd
unset password

config=/etc/ssh/sshd_config
marker='# KRONOS_TEAM_ACCESS_BEGIN'
if ! grep -Fq "$marker" "$config"; then
  backup="${config}.pre-kronos-$(date -u +%Y%m%dT%H%M%SZ)"
  cp -p -- "$config" "$backup"
  {
    printf '\n%s\n' "$marker"
    if [[ $expected_host == KRONOS-EDGE ]]; then
      # pfSense's WAN-side transit address is the only allowed password source.
      printf 'Match User kronos Address 10.254.254.2\n'
    else
      printf 'Match User kronos\n'
    fi
    printf '    PasswordAuthentication yes\n'
    printf '    KbdInteractiveAuthentication no\n'
    printf '# KRONOS_TEAM_ACCESS_END\n'
  } >> "$config"
  if ! sshd -t; then
    cp -p -- "$backup" "$config"
    echo 'sshd rejected configuration; restored backup' >&2
    exit 1
  fi
fi

sshd -t
effective=$(sshd -T -C user=kronos,host=localhost,addr=10.254.254.2)
grep -qx 'passwordauthentication yes' <<< "$effective"
grep -qx 'kbdinteractiveauthentication no' <<< "$effective"
operator=$(sshd -T -C user=ubuntu,host=localhost,addr=10.254.254.2)
grep -qx 'passwordauthentication no' <<< "$operator"
if [[ $expected_host == KRONOS-EDGE ]]; then
  lan=$(sshd -T -C user=kronos,host=localhost,addr=10.10.20.1)
  grep -qx 'passwordauthentication no' <<< "$lan"
fi
systemctl enable --now ssh.service >/dev/null
systemctl reload ssh.service
id kronos | sed 's/^/TEAM_USER: /'
echo 'TEAM_SSH_PASSWORD_ONLY_FOR_KRONOS_USER; OPERATOR_REMAINS_KEY_ONLY'
