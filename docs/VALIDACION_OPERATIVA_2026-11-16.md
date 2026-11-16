# Validación del laboratorio — 16 de noviembre de 2026

Se comprobó el laboratorio por el tailnet del proyecto. Las pruebas de voz se
automatizaron con audio generado para QA: no participó una persona y no se llamó
a los teléfonos del equipo. Esto no equivale a una certificación absoluta de
seguridad ni a una medición de todos los dispositivos del usuario.

La suite de regresión local terminó con **51 pruebas aprobadas** y 20 subcasos.

| Componente | Resultado observado |
|---|---|
| Gemini | Sesión real `gemini-3.1-flash-live-preview`, audio nativo, transcripciones y herramientas |
| Decisión negativa | «No la desbloquees» conservó el bloqueo de la IP reservada de QA |
| Información adicional | La conversación consultó `get_incident_details` y explicó tipo, firma y limitación del origen reservado |
| Acción autorizada | La orden por voz ejecutó `unblock_ip`; lectura real de `snort2c` confirmó la eliminación |
| Telefonía local | Autenticación SIP, respuesta 200, saludo y respuesta por RTP PCMU/8000 |
| Telefonía por Tailscale | Desde el PC, pasada final: 567 paquetes RTP recibidos, voz en el saludo y después de la pregunta; prueba aprobada |
| IPS WAN / interno | Netmap IPS activo; 26.920 / 26.927 reglas cargadas y ninguna fallida |
| Prueba SQLi pública | Petición de prueba descartada; EVE registró `action=blocked`, `verdict=drop`, SID 1000011 |
| Identificación del actor | Se conservó la IP del transporte y se extrajo el cliente de XFF del HAProxy verificado |
| GeoIP | Base `GeoLite2-Country.mmdb` en pfSense; el origen de la prueba pública fue clasificado como Chile |
| Despacho | El evento real llegó por webhook autenticado y AMI aceptó Originate hacia un destino de QA sin teléfonos |
| Edge | Corregida validación de espacios finales en `ip route`; servicio activo y ruta principal conservada |

La IP pública de la prueba se retiró de `snort2c` al terminar. La IP reservada de
la prueba de voz también quedó sin bloqueo. No se publicó la IP pública del
usuario ni ninguna credencial en esta evidencia.

## Servicios y acceso

En VM103 la voz y el dispatcher corren como `kronos-voice`, sin shell de acceso,
mediante `kronos-voice.service` y `kronos-dispatcher.service`. Asterisk utiliza el
overlay `compose.live-host.yml`. El código activo se referencia mediante
`/opt/kronos/live-current`; configuración y llaves permanecen en `/etc/kronos`.

La llave hacia pfSense está restringida a VM103, una tabla y operaciones de IP
individual. Se comprobó que rechaza una shell. AMI se limitó a loopback y su
secreto se rotó. El recolector se ejecuta localmente en pfSense y su inicio está
registrado en `system/shellcmd`; procesa los dos EVE logs y consulta la base
GeoLite2 que ya estaba instalada. No se instaló MaxMind en la IA.

El destino normal de alertas es el anexo 1004. El anexo 1000 permite llamar al
agente. Para recibir una alerta, el softphone debe estar registrado en el tailnet
del proyecto. Las llamadas repetidas tienen un enfriamiento de 120 segundos,
configurable en `voice.env`; el IPS sigue bloqueando durante ese intervalo.

## Recuperación de DVWA

Se encontraron archivos añadidos (`filemanager.php`, `watchdog.sh`, `xmrig`, entre
otros) y la eliminación de los módulos originales de SQLi y otras vulnerabilidades.
Se detuvo el contenedor afectado y se conservaron su imagen, diferencias, procesos,
logs y una copia de la base de datos en VM102, bajo
`/etc/kronos/quarantine-20261116`. No se atribuye el incidente a una persona.

Se recreó únicamente la aplicación desde la imagen oficial instalada, fijada por
digest. Se conservó el volumen de MariaDB. Se rotaron la contraseña de conexión de
la aplicación y las cuentas de acceso de DVWA. Las nuevas credenciales del
administrador están en el handoff privado, fuera de Git.

La raíz del contenedor quedó en solo lectura; los directorios temporales usan
`noexec`, y la salida de nuevas conexiones desde la red Docker se limita a su
propia red de base de datos. El nivel predeterminado de DVWA es `impossible`.
El administrador puede cambiarlo para ejercicios controlados; no dejar niveles
vulnerables expuestos a Internet después de la demostración.

Se añadieron reglas de descarte para SQLi y comandos en el backend HTTP, después
de terminar TLS en HAProxy. Antes había miles de reglas `alert` y solo dos reglas
de prueba `drop`; que el motor estuviera en modo IPS no probaba el bloqueo de SQLi.
Las nuevas reglas pasaron validación de Suricata antes de activarse.

Las claves SIP de los softphones se conservaron para evitar invalidar las cuentas
del equipo antes de grabar. Las que hayan sido compartidas o publicadas requieren
rotación coordinada y actualización de los teléfonos.
