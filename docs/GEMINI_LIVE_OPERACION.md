# Operación de voz con Gemini Live

El IPS de pfSense conserva el bloqueo inmediato. El agente telefónico consulta su
estado, explica el incidente y ejecuta cambios solamente por orden del operador.
MaxMind/GeoLite2 permanece registrado e instalado en **pfSense**. El recolector
local lee sus MMDB existentes y adjunta `geoip` a la alerta; Gemini no consulta
MaxMind ni necesita sus credenciales o una copia de la base.

Flujo implementado: alerta EVE → correlador de pfSense + GeoLite2 → dispatcher
autenticado → AMI → anexo SIP → AudioSocket bidireccional → una sesión Gemini Live.
Gemini escucha PCM16 a 16 kHz y devuelve audio nativo a 24 kHz. El puente convierte
a telefonía de 8 kHz y envía cuadros de 20 ms. Las interrupciones descartan el audio
pendiente. No se generan grabaciones WAV ni se usa un segundo modelo TTS.

## Instalación validada

La instalación del 16 de noviembre usa los servicios de host sin privilegios
`kronos-voice` y `kronos-dispatcher`, más `compose.live-host.yml` para Asterisk.
El código está en `/opt/kronos/live-current`; las dependencias se instalan en
`/opt/kronos/voice-venv`. El directorio compartido de llamadas usa grupo
`kronos-voice`, setgid y permisos 2770. Para actualizar ese entorno preparado se
incluye `deploy-live-host.sh`. `compose.live.yml` es una alternativa con servicios
en contenedores, no el runtime usado en esta validación.

Ver [resultados, recuperación de DVWA y límites](VALIDACION_OPERATIVA_2026-11-16.md).

## Configuración en VM103

Se utiliza la instalación existente en `/etc/kronos/asterisk`; no reemplazar
`pjsip.conf` ni `manager.conf` con plantillas del repositorio.

1. Copiar `infra/proxmox/services/voice-config.example.json` a
   `/etc/kronos/voice/config.json` y `voice.env.example` a `/etc/kronos/voice.env`.
   Ajustar host, tabla, operadores y anexo receptor a la instalación real.
2. Guardar la clave Gemini en `/etc/kronos/voice/gemini.key`, permisos 0600.
   Configurar `ASTERISK_AMI_SECRET` con el secreto existente y generar un token
   aleatorio para `KRONOS_DISPATCH_TOKEN`. No guardar estos valores en Git.
3. Configurar la llave SSH y `known_hosts` de pfSense en el directorio de voz.
   Verificar la huella por el acceso administrativo existente. La cuenta necesita
   permiso real para las operaciones `pfctl` de la tabla seleccionada; comprobar
   si corresponde `sudo -n` antes de establecer `ssh_sudo=true`. No habilitar una
   shell administrativa sin restricciones para resolver permisos.
4. Permitir el dispatcher únicamente desde el recolector de pfSense, en la VLAN
   de gestión y por las ACL del laboratorio. El HTTP de ese segmento lleva el
   token; usar TLS o un túnel si el tráfico cruza una red no confiable.
5. Comprobar que no haya otro dispatcher ocupando el puerto configurado. Migrar
   el servicio anterior con respaldo; no ejecutar dos lectores de EVE que llamen
   por el mismo incidente.
6. Ejecutar como root `bash infra/proxmox/services/deploy-live-voice.sh` desde el
   checkout en VM103. El script valida primero acceso al modelo y lectura real de
   la tabla, guarda el dialplan anterior y después activa los servicios.

El modelo predeterminado es `gemini-3.1-flash-live-preview`, configurable mediante
`GEMINI_LIVE_MODEL`. La disponibilidad y cuota de la clave deben pasar el preflight;
no hay sustitución silenciosa por modelos que no soporten Live.

## Recolector en pfSense

Configurar el `geoip.db_path` existente en `src/pfsense_pfctl_engine/config.yaml`
con la ubicación **real en pfSense** del archivo City o Country `.mmdb` ya instalado.
`geoip.asn_db_path` es opcional. La ruta publicada es un ejemplo, no prueba que la
base esté allí. El lector requiere `maxminddb` en el Python que ejecuta el recolector
(dependencias en `src/pfsense_pfctl_engine/requirements.txt`). No copia ni descarga
MMDB a la IA y no cambia el registro/licencia MaxMind.

En el proceso del recolector establecer `KRONOS_DISPATCH_URL` a la URL privada del
dispatcher y `KRONOS_DISPATCH_TOKEN` al mismo token de VM103. El payload completo
incluye firma, tipo, fecha, destino, URL si existe y GeoIP. AMI lo transporta como
JSON en base64 sin perder esos campos. Los orígenes privados/reservados no tienen
ubicación pública. Si la base o el registro no están disponibles, se informa esa
limitación; nunca se deduce un país a partir del prefijo IP.

`trusted_proxy_ips` solo debe contener proxies realmente controlados que
sobrescriban cabeceras de origen. Si no están verificados, usar la IP observada por
el sensor. Una IP y su geolocalización no identifican a la persona atacante.

## Comportamiento esperado

- «¿Qué ataque fue y de dónde venía?» devuelve los datos del incidente mediante
  `get_incident_details`; no modifica el firewall.
- «Déjala bloqueada» o «no la desbloquees» conserva el bloqueo.
- «Desbloquea esa IP» ejecuta `unblock_ip` y consulta de nuevo la tabla.
- «Sí» solo autoriza después de una pregunta explícita de desbloqueo.
- Ser Kevin o estar haciendo QA no autoriza una acción por sí mismo.
- Un error SSH, un resultado desconocido o una verificación fallida nunca se
  anuncia como desbloqueo exitoso. Si la transcripción no llega a tiempo, se pide
  repetir la orden. La política consume cada autorización una sola vez.
- El endpoint SIP autenticado identifica al operador, no el CallerID del bot.
- El desbloqueo elimina la entrada de la tabla configurada. No desactiva el IPS:
  un ataque posterior puede volver a bloquear al actor. No es una lista blanca.
- El agente solo describe el estado de esa tabla; no certifica la seguridad de
  toda la red ni la persistencia de un bloqueo tras reinicio.

El enfriamiento de llamadas se configura con `KRONOS_CALL_COOLDOWN_SECONDS`
y `KRONOS_GLOBAL_CALL_COOLDOWN_SECONDS` (120 segundos predeterminados). El
bloqueo del IPS sigue funcionando mientras se suprimen avisos repetidos.

## Verificación y límites de esta entrega

`python -m pytest tests src/pfsense_setup/tests -q` ejecuta las pruebas locales.
Incluyen sockets TCP y WebSocket reales contra un servidor Gemini simulado,
transporte PCM, herramienta de desbloqueo, verificación, negativa, autorización,
GeoIP y contexto por llamada. No hacen llamadas a personas ni cambian pfSense.

El preflight abre una sesión real Gemini (sin voz), comprueba SSH/tabla y devuelve
JSON sin credenciales. Eso aún no prueba SIP/RTP ni la comprensión de voz real.
La validación del 16 de noviembre incluyó llamadas automatizadas al anexo 1000
por SIP/RTP y Tailscale, herramientas contra pfSense real y una alerta SQLi pública.
Para la grabación corresponde usar los softphones del equipo; no participaron
personas en las pruebas automatizadas. No presentar pruebas
simuladas como una certificación de funcionamiento en producción.

Para volver al estado anterior, restaurar el `extensions.conf` del directorio
indicado en `/etc/kronos/last-voice-backup`, detener `dispatcher` y `voice` con el
overlay, y recrear Asterisk con `compose.voip.yml` más el `rollback.compose.yml`
guardado en ese respaldo. Ese archivo usa la imagen del contenedor anterior,
incluyendo scripts instalados manualmente. Conservar los logs de
la operación; no eliminar las evidencias históricas del proyecto.

Referencias: [Gemini Live](https://ai.google.dev/gemini-api/docs/live),
[herramientas Live](https://ai.google.dev/gemini-api/docs/live-tools),
[AudioSocket Asterisk](https://docs.asterisk.org/Configuration/Channel-Drivers/AudioSocket/).
