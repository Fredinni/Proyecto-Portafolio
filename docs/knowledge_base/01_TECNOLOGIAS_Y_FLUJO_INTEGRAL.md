# BASE DE CONOCIMIENTO GENERAL: TECNOLOGÍAS, JUSTIFICACIÓN Y FLUJO INTEGRAL
## Compendio Estratégico de Ingeniería y Arquitectura KRONOS SENTINEL
**Institución:** Duoc UC Sede San Joaquín — Escuela de Informática y Telecomunicaciones  
**Asignatura:** Portafolio de Título (APT122) — Ingeniería en Conectividad y Redes  
**Proyecto:** KRONOS SENTINEL — Arquitectura de Costo Cero ($0 CLP)

---

## 1. MATRIZ MAESTRA DE LAS 10 TECNOLOGÍAS SELECCIONADAS

| N° | Tecnología Implementada | Licencia / Costo | ¿Por qué se eligió? (Justificación Técnica) | Rol Táctico en KRONOS SENTINEL |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **pfSense CE 2.9.0** | Open Source ($0 CLP) | Estabilidad sobre FreeBSD 14, soporte nativo de VLANs 802.1Q y ecosistema de paquetes de seguridad. | Firewall perimetral L2/L3, puerta de enlace y segmentación de subredes corporativas. |
| **2** | **FreeBSD pf(4) & pfctl** | BSD License ($0 CLP) | Motor de filtrado en kernel de ultrabaja latencia con tablas dinámicas en memoria RAM (`snort2c`). | Bloqueo atómico de paquetes en microsegundos y persistencia en memoria sin tocar disco. |
| **3** | **Suricata 7.x (Netmap)** | GPLv2 ($0 CLP) | Inspección profunda multihilo con soporte directo de `netmap(4)` para intercepción *Inline IPS* real. | Descarte (*Drop*) de paquetes hostiles en el ring-buffer de la tarjeta de red sin reenviarlos a la DMZ. |
| **4** | **Emerging Threats (ET Open)** | Free Tier ($0 CLP) | Base de datos de más de 30,000 firmas de amenazas actuales mantenida por la comunidad global de ciberseguridad. | Firmas de detección para vectores SQLi, exploits web, shellcodes y escáneres hostiles. |
| **5** | **pfBlockerNG-devel** | Open Source ($0 CLP) | Integración nativa de listas de reputación IP y GeoIP en reglas flotantes prioritarias en pfSense. | Primera barrera perimetral para descartar tráfico de países hostiles y botnets globales conocidas. |
| **6** | **MaxMind GeoLite2** | Free Tier ($0 CLP) | Base de datos comunitaria gratuita de geolocalización IP con alta precisión para enriquecimiento forense. | Identificación del país de origen de la IP atacante para el reporte verbal al CISO. |
| **7** | **HAProxy 2.8+ Community** | GPLv2 ($0 CLP) | Proxy inverso de alto rendimiento con soporte de SSL Offloading y *Stick-Tables* dinámicas en RAM. | Protección anti-DoS L7, rate-limiting, ocultamiento de IP real y terminación HTTPS 443. |
| **8** | **Asterisk 20 LTS (Docker)** | GPLv2 ($0 CLP) | Servidor de telefonía PBX líder de la industria con canal PJSIP y control programable vía AMI (*Asterisk Manager*). | Generador autónomo de llamadas telefónicas SIP inmediatas hacia el móvil/softphone del CISO. |
| **9** | **Google Gemini Live Flash 3.1**| Free Tier ($0 CLP) | Modelo multimodal con soporte de audio bidireccional por WebSocket de ultrabaja latencia (<300ms). | Interlocutor de voz inteligente que entrega el debriefing táctico y responde dudas de mitigación. |
| **10**| **Tailscale Subnet Router** | Free Tier ($0 CLP) | Malla VPN Zero Trust basada en WireGuard que atraviesa NAT y CGNAT sin necesidad de IP pública estática. | Acceso remoto cifrado para el softphone del CISO hacia la subred de telefonía VoIP (`192.168.30.0/24`). |

---

## 2. FLUJO DE PROCESAMIENTO INTEGRAL DE EXTREMO A EXTREMO

```text
 ┌─────────────────┐       ┌────────────────────────┐       ┌────────────────────────┐
 │ 1. INGRESS WAN  │ ────> │ 2. SURICATA NETMAP IPS │ ────> │ 3. FREEBSD KERNEL PF   │
 │ Hostile SQLi    │       │ Inline Packet Drop     │       │ Tabla <snort2c> en RAM │
 └─────────────────┘       └────────────────────────┘       └────────────────────────┘
                                                                        │
                                                                        ▼
 ┌─────────────────┐       ┌────────────────────────┐       ┌────────────────────────┐
 │ 6. CISO VOICE   │ <──── │ 5. ASTERISK AUTO-DIAL  │ <──── │ 4. KRONOS PFCTL ENGINE │
 │ Gemini Live API │       │ AMI PJSIP Trunk        │       │ AST & Noise Supression │
 └─────────────────┘       └────────────────────────┘       └────────────────────────┘
```

1. **Intrusión Hostil Externa:** El atacante lanza un payload malicioso (ej. `admin' OR '1'='1 --`) dirigido al puerto HTTPS 443 expuesto en el firewall.
2. **Intercepción en Hardware Netmap (0 ms):** Suricata en modo Inline intercepta el paquete en el ring-buffer de la tarjeta de red, detecta la firma ET Open (`SID: 2008287`), ejecuta el **Drop** inmediato y escribe el evento en `/var/log/suricata/eve.json`.
3. **Persistencia en Kernel de FreeBSD:** El subsistema `pf(4)` inserta la IP atacante en la tabla en memoria RAM `<snort2c>`, cortando cualquier intento de conexión subsiguiente a nivel de socket.
4. **Validación Heurística del Motor KRONOS:** El script `log_correlator.py` procesa el evento JSON, descarta falsos positivos mediante análisis AST y verifica atómicamente con `pfctl -t snort2c -T test <IP>` que la amenaza esté neutralizada.
5. **Auto-Dialer Telefónico Asterisk:** El despachador SOAR contacta a la centralita Asterisk vía AMI (`Originate`), marcando a la extensión del CISO (`PJSIP/1001`).
6. **Debriefing Táctico con Gemini Live:** Al descolgar la llamada, el agente de voz de Google Gemini Live Flash 3.1 dialoga con el CISO, informa los datos del incidente y proporciona asesoría táctica inmediata.
