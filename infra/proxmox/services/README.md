# Guest service provisioning

Execute only inside the corresponding Ubuntu 24.04 guest after copying the repository to `/opt/kronos/Proyecto-Portafolio` and configuring its single VLAN access NIC and pfSense gateway:

```bash
sudo bash /opt/kronos/Proyecto-Portafolio/infra/proxmox/services/deploy-dmz.sh
sudo bash /opt/kronos/Proyecto-Portafolio/infra/proxmox/services/prepare-voip.sh
```

The first command belongs to DMZ; the second belongs to VOIP. Neither provisions VM networking. Both validate the expected guest address before changes. Docker Engine is installed using its [official Ubuntu repository](https://docs.docker.com/engine/install/ubuntu/).

For offline protected VLANs, first prepare a dedicated template with `install-docker.sh`, install `build-essential python3-venv`, pull `ghcr.io/digininja/dvwa:latest` and `mariadb:10.11`, then run `docker compose -f infra/proxmox/services/compose.voip.yml build` without starting any containers. Run guest deployment with `sudo OFFLINE=1 bash .../deploy-dmz.sh` or `sudo OFFLINE=1 bash .../prepare-voip.sh`; both reuse local images without attempting package downloads. No temporary uplink is added to protected guests.

DVWA follows the [maintainer compose structure](https://github.com/digininja/DVWA/blob/master/compose.yml), with MariaDB, external random database credentials in `/etc/kronos/dvwa.env` (0600), a private Docker subnet 172.20.20.0/24, bounded logs and HTTP bound solely to 192.168.20.50:80. The DB has no published port. The initial HTTP response alone is not a database/login validation. The database was initialized once with `sudo python3 /opt/kronos/Proyecto-Portafolio/infra/proxmox/services/init-dvwa-db.py`; this script refuses to reset existing tables. `/login.php` returned HTTP200, while interactive login remains for Cristóbal to test privately before publication. No Tailscale runs in DVWA. pfSense controls inter-VLAN access. Images should be recorded by digest in deployment evidence.

VOIP builds a minimal Ubuntu Asterisk image. Configuration in `/etc/kronos/asterisk` is preserved across reruns. SIP binds only 192.168.30.50:5060; no SIP identities/passwords are invented. AMI is disabled pending Freddy's access policy and credentials. Existing source `pjsip.conf` passwords are not copied. Existing dialplan is retained in the repository for Freddy, but the deployed dialplan starts empty to avoid invoking the unimplemented Gemini transport.

Bruno owns Gemini/pfctl integration. `gemini_live_client.py` currently simulates success without a WebSocket; `gemini_audio_bridge.py` does not transport bidirectional audio. `dispatcher.py` exposes an unauthenticated incident HTTP endpoint and `call_trigger.py` uses call files, not AMI. None is auto-started. No Gemini credentials are generated. Asterisk container availability, AMI configuration, Gemini transport implementation and voice end-to-end validation are distinct statuses.

HAProxy remains a future pfSense task for Cristobal: backend 192.168.20.50:80, external TLS termination then internal HTTP. The prepared source HAProxy configuration now targets 192.168.20.50 and uses three named stick-table backends; it still requires `haproxy -c -f` with a real TLS PEM and functional rate-limit tests before deployment. This preparation does not mark A5 completed. Suricata WAN sees encrypted TLS metadata, not plaintext SQLi inside HTTPS. Internal HTTP inspection is a separate required test. No roadmap completion states are modified.
