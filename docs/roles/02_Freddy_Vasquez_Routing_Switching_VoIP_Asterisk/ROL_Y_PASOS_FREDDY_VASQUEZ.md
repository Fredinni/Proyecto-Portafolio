# GUÍA DE ROL Y MANUAL OPERATIVO: INGENIERÍA DE ROUTING, SWITCHING Y TELEFONÍA VOIP ASTERISK
## Integrante: Freddy Vásquez Cortés
**Carrera:** Ingeniería en Conectividad y Redes — Duoc UC Sede San Joaquín  
**Asignatura:** Portafolio de Título (APT122) — Proyecto KRONOS SENTINEL  
**Rol Oficial:** *Ingeniería de Routing, Switching perimetral y Configuración de Telefonía VoIP Asterisk*

---

## 1. MISIÓN Y RESPONSABILIDADES PRINCIPALES

Como Ingeniero de Networking y Telefonía VoIP de KRONOS SENTINEL, eres el responsable de la **topología de comunicaciones L2/L3, el túnel Zero Trust y la centralita Asterisk PBX**:

1. **Segmentación de Red L2/L3 y Troncal 802.1Q en pfSense:**
   * Configurar y validar los enlaces troncales 802.1Q en la interfaz LAN (`vtnet1`).
   * Mantener el direccionamiento IP de las 4 VLANs:
     * **VLAN 10 (Corporativa):** `192.168.10.0/24`
     * **VLAN 20 (DMZ Servidores):** `192.168.20.0/24`
     * **VLAN 30 (VoIP PBX):** `192.168.30.0/24`
     * **VLAN 99 (Gestión SecOps):** `192.168.99.0/24`
2. **Centralita Telefónica Asterisk 20 LTS en Docker:**
   * Mantener los archivos de configuración de Asterisk (`src/asterisk_pbx/`):
     * `pjsip.conf`: Configuración de extensiones para el equipo (1001 Bruno, 1002 Freddy, 1003 Cristóbal, 1004 Kevin) y anexo IA 1000.
     * `extensions.conf`: Plan de marcado (*Dialplan*) con enlace al bridge de audio y cola de emergencia.
     * `rtp.conf`: Rango de puertos UDP para streaming de audio (10000-10100).
3. **Auto-Dialer Telefónico mediante Asterisk Manager Interface (AMI):**
   * Desarrollar y verificar el script de disparo telefónico `call_trigger.py` mediante comandos `Action: Originate`.
4. **Malla VPN Zero Trust con Tailscale Subnet Router:**
   * Publicar la subred `192.168.30.0/24` en Tailscale para permitir que el CISO conecte su softphone móvil (Zoiper/Linphone) de forma remota sin requerir IP pública fija ni apertura de puertos NAT.

---

## 2. CHECKLIST PASO A PASO PARA EL DESPLIEGUE TÉCNICO

### Fase A: Despliegue del Contenedor Asterisk PBX
```bash
# 1. Acceder al directorio de Asterisk:
cd src/asterisk_pbx

# 2. Construir y levantar el contenedor Docker:
docker compose up -d --build

# 3. Comprobar que el servicio SIP esté escuchando en el puerto UDP 5060:
docker compose ps
docker exec -it asterisk_pbx rasterisk -x "pjsip show endpoints"
```

### Fase B: Validación de Extensiones SIP / PJSIP
```bash
# Comprobar registros de anexos en la centralita:
docker exec -it asterisk_pbx rasterisk -x "pjsip show aors"
docker exec -it asterisk_pbx rasterisk -x "dialplan show default"
```

### Fase C: Prueba de Auto-Dialer hacia el Softphone del CISO
```bash
# Ejecutar prueba de llamada táctica directa a la extensión 1001:
python call_trigger.py --extension 1001 --priority HIGH
```

### Fase D: Validación de la Subred Tailscale en pfSense
```bash
# Comprobar estado del demonio Tailscale en pfSense vía CLI:
tailscale status
tailscale set --advertise-routes=192.168.30.0/24
```

---

## 3. GUÍA DE DEFENSA ANTE LA COMISIÓN EVALUADORA (PREGUNTAS CLAVE)

### P1: "¿Por qué se eligió Asterisk en lugar de enviar un mensaje de WhatsApp o un bot de Telegram?"
* **Respuesta Senior:** *"Profesor, en situaciones de crisis de seguridad crítica, las notificaciones por chat o email sufren de ceguera por sobrecarga de mensajes. Una llamada telefónica SIP irrumpe de forma prioritaria, despierta al operador en turnos de madrugada y permite una interacción conversacional bidireccional inmediata para recibir instrucciones de contención en tiempo real."*

### P2: "¿Cómo aseguraron que el tráfico VoIP de Asterisk no interfiera ni sea interceptado desde la DMZ?"
* **Respuesta Senior:** *"Implementamos aislamiento estricto en Capa 2 y Capa 3. La centralita Asterisk reside en la VLAN 30 (`192.168.30.0/24`). Las reglas de pfSense bloquean cualquier tráfico originado en la VLAN 20 (DMZ) con destino a la VLAN 30, impidiendo que un atacante que comprometa el servidor web pueda alcanzar la telefonía."*
