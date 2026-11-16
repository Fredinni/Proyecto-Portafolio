#!/usr/bin/env bash
set -euo pipefail
# Only the project's Docker subnet; preserve unrelated host and Docker rules.
# Established replies to HAProxy remain allowed. New sessions can reach the DB
# on the same Docker network, but cannot download binaries or contact miners.
args=(-s 172.20.20.0/24 ! -d 172.20.20.0/24 -m conntrack --ctstate NEW -j REJECT)
iptables -C DOCKER-USER "${args[@]}" 2>/dev/null || iptables -I DOCKER-USER 1 "${args[@]}"
