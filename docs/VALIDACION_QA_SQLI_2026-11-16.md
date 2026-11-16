# Corrección del flujo SQLi y llamadas — 16 de noviembre de 2026

## Causa observada

Los eventos EVE de las pruebas de las 18:21–18:26 (hora de Chile) contenían
`action: blocked`, `verdict.action: drop` y firmas SQLi de KRONOS. Su origen era
`192.168.99.10` (MGMT), incluido en `protected_ips`. El recolector descartaba esos
eventos antes del despacho: Suricata detenía el payload, pero no se solicitaba la
llamada. No era necesario desactivar el IPS para permitir el intento.

## Cambios aplicados

- Los descartes del IPS desde infraestructura protegida ahora se notifican con
  `source_protected: true`, sin insertar ni eliminar esa IP en la tabla global.
  La herramienta de voz también rechaza cambios sobre esos orígenes. El agente
  distingue el descarte del payload del bloqueo de una IP en `snort2c`.
- Si falta la identidad real detrás de un proxy protegido, el incidente informa
  `UNRESOLVED_PROXY`; no atribuye el ataque al proxy ni lo bloquea automáticamente.
- El lector EVE drena el archivo rotado y lee el reemplazo desde el inicio;
  maneja truncado, escrituras parciales y errores por evento sin saltarse los
  registros siguientes. Al arrancar mantiene la lectura desde el final.
- Una consulta fallida a pfctl permite notificar el incidente con estado de
  bloqueo desconocido. El webhook reintenta errores de conexión y HTTP 5xx
  hasta tres veces. Los logs muestran si hubo despacho o enfriamiento.
- DVWA quedó en `low` mediante `/etc/kronos/dvwa.env` y la variable
  `DVWA_SECURITY_LEVEL`; se recreó solamente el contenedor de aplicación.
  Se conservaron MariaDB, las credenciales, la raíz de solo lectura y las
  restricciones de salida. El compose conserva `impossible` como valor seguro
  cuando la variable no está definida.

## Verificación ejecutada

1. Pruebas locales: **60 pruebas y 22 subpruebas aprobadas**. Incluyen rotación,
   truncado, JSON parcial, fallo pfctl, reintentos y protección de MGMT.
2. DVWA: inicio de sesión autenticado, módulo SQLi HTTP 200, nivel Low seleccionado
   y ausencia de errores PHP. Se verificaron la imagen fijada, raíz de solo lectura
   y servicio de restricción de salida activo.
3. Ruta pública real: una petición SQLi fue descartada por Suricata. EVE incluyó
   la IP del proxy y el XFF real; el recolector aisló la IP pública de origen y
   recibió `HTTP 200 / DISPATCHED` del despachador.
4. Asterisk mostró el anexo autenticado 1004 en `Ringing`, después `Up` y
   `AudioSocket`. Gemini Live se conectó. En esa llamada la herramienta ejecutó
   `unblock_ip` sobre la IP del incidente con `verified=True` en pfSense.
5. Una prueba aislada con audio generado y Gemini Live real conservó el bloqueo
   ante una negativa, consultó los detalles y verificó el desbloqueo tras una orden
   expresa. Su resultado actualizado fue `passed: true`; se retiró la IP reservada
   usada para QA. Esta prueba es distinta de la llamada real al anexo 1004.
6. Se repitió la petición desde MGMT: una petición normal recibió HTTP 302 de
   acceso/login y el SQLi fue descartado. El recolector registró el origen protegido
   y envió la notificación. El dispatcher respondió `202 / CALL_COOLDOWN` porque
   estaba dentro de los 120 segundos de la llamada anterior. MGMT siguió fuera
   de `snort2c` y accesible.
7. El guard terminó con `IPS readiness: PASS`, `Hold: inactive`, tabla `OPEN` y
   estado `READY`. La IP reservada de QA quedó fuera de la tabla.

## Para la demostración

Usar `https://100.50.147.57` desde el equipo externo de QA para mostrar el bloqueo
y desbloqueo del actor. Desde el navegador de MGMT el origen observado es la
infraestructura de administración; se notifica, pero no se modifica su bloqueo
global ni se inventa un país GeoLite2 para esa IP privada. MaxMind permanece en
pfSense.

Comprobar «DVWA Security → Low» en la sesión del navegador: una cookie antigua
puede conservar otro nivel. Mantener el softphone 1004 registrado. El enfriamiento
de 120 segundos evita llamadas repetidas; un nuevo ataque puede volver a bloquear
la IP después de un desbloqueo. El desbloqueo no desactiva reglas de Suricata.

Se guardaron copias anteriores junto a los archivos desplegados. Las credenciales
y el resultado detallado de QA permanecen en archivos privados, fuera del repositorio.

## Aclaración posterior: origen público y víctima privada

La prueba de las 20:16 (hora de Chile) volvió a salir desde MGMT hacia DVWA sin
cabecera XFF. Ese evento identifica un origen interno y una víctima privada;
no contiene un origen público que pueda atribuirse al atacante. El evento externo
anterior sí conserva el cliente público en `alert.xff` y `http.xff`, aunque la IP
observada del transporte hacia el backend sea la del proxy. WireGuard no causa
por sí solo la pérdida de identidad en este recorrido.

Se agregaron campos derivados para origen público o privado, víctima privada,
origen observado y método de resolución. El prompt y la consulta de detalles los
presentan con esos roles. Si no existe una IP pública respaldada por la evidencia,
el agente lo indica; no consulta una IP de salida para inventar una atribución.
La regresión ampliada terminó con **67 pruebas y 28 subpruebas aprobadas**.

El cambio se desplegó en pfSense y en el servicio de voz. Se verificó con Gemini
Live real usando ambos eventos registrados y consultas de solo lectura: el caso
interno nombró el origen privado y la víctima, y el externo nombró explícitamente
el origen público y la víctima privada. Ninguno ejecutó mutaciones ni originó una
llamada SIP para esta comprobación. El primer intento del caso externo agotó el
tiempo de espera; una repetición instrumentada completó ambos casos con
`passed: true`. Esto valida las respuestas observadas, no una disponibilidad
garantizada del modelo. Las transcripciones detalladas permanecen privadas.
