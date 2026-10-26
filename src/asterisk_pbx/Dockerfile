# KRONOS SENTINEL - Asterisk PBX 20 LTS Dockerfile
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    asterisk \
    asterisk-modules \
    asterisk-pjsip \
    python3 \
    python3-pip \
    python3-websockets \
    curl \
    sox \
    libsox-fmt-all \
    && rm -rf /var/lib/apt/lists/*

COPY extensions.conf /etc/asterisk/extensions.conf
COPY pjsip.conf /etc/asterisk/pjsip.conf
COPY manager.conf /etc/asterisk/manager.conf
COPY rtp.conf /etc/asterisk/rtp.conf

# 5060 SIP, 5038 AMI, 10000-10100 RTP media
EXPOSE 5038/tcp 5060/udp 5060/tcp 10000-10100/udp

CMD ["/usr/sbin/asterisk", "-f", "-vvvddd"]
