# KRONOS SENTINEL - Asterisk PBX 20 LTS Dockerfile
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    asterisk \
    python3 \
    python3-pip \
    python3-websockets \
    curl \
    sox \
    libsox-fmt-all \
    && rm -rf /var/lib/apt/lists/*

# Runtime configuration is mounted from /etc/kronos/asterisk. Repository
# pjsip.conf and manager.conf are templates, never active credentials.

# 5060 SIP, 5038 AMI, 10000-10100 RTP media
EXPOSE 5038/tcp 5060/udp 5060/tcp 10000-10100/udp

CMD ["/usr/sbin/asterisk", "-f", "-vvvddd"]
