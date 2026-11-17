# Identidad en pfSense y estabilidad de la llamada

## Identidad pública y privada

La prueba externa de QA quedó registrada en WAN con el cliente público y en el
sensor HTTP interno con el proxy como origen de transporte, XFF del cliente y
DVWA como destino privado. Esto permite verificar el recorrido en pfSense sin
inferir una IP pública a partir del túnel. Los intentos dirigidos a la IP privada
por Tailscale/MGMT tienen un recorrido distinto y no deben atribuirse a una
dirección pública sin evidencia adicional.

El recolector conserva campos de identidad del evento en
`/var/db/kronos/incidents/<sha256>.json`, antes del despacho. El comando SSH
forzado admite `kronos-incident-identity <sha256>`: solo acepta un identificador
hexadecimal completo y ejecuta un lector fijo. No permite rutas arbitrarias,
shell, payloads HTTP ni otros archivos. La configuración del recolector y la del
comando forzado deben declarar el mismo `incident_store_dir`.

`get_incident_details` puede leer esa evidencia directamente desde pfSense. El
resultado identifica `source=PFSENSE_EVE` e `identity_query_verified=true`; una
lectura fallida conserva el contexto de llamada y declara que no hubo una nueva
verificación. Se comprueba que la identidad leída corresponda al origen y destino
de la llamada. El preflight consulta identidad y tabla en paralelo, con espera
acotada. El bloqueo actual se verifica por separado de la evidencia del ataque.

La consulta real a la evidencia del evento público de QA devolvió origen público,
víctima privada y sensor de respaldo en **0,376 segundos**. Las direcciones de los
participantes y la evidencia completa permanecen en archivos privados. Para
comprobar la ruta nueva se releyó un evento real conservando su fecha original;
no se fabricó tráfico ni se alteró la tabla para esa comprobación.

## Qué pasó con el desbloqueo

La llamada pública de QA registró `unblock_ip` con verificación exitosa. Después
se observó otra coincidencia SQLi del mismo origen y una nueva inserción en la
tabla. Por eso el acceso volvió a quedar bloqueado. No se cambió esta política:
el desbloqueo no crea una excepción al IPS. Tras liberarlo, comprobar primero
una petición normal; un nuevo SQLi puede volver a activar la contención.

## Correcciones de estabilidad

- La traza del proveedor mostró respuestas terminadas con `generationComplete`
  sin un `turnComplete` posterior. Se reconocen ambas señales y se finaliza la
  respuesta una sola vez, conservando la autorización mientras haya herramientas
  pendientes. Esto permite registrar la pregunta de desbloqueo y reconocer el
  sí posterior. Una interrupción descarta una pregunta incompleta sin borrar una
  orden nueva del operador.
- Un sí reciente y contextual después de la pregunta ya formulada se procesa
  con la política y el ejecutor del controlador, sin depender de que el modelo
  decida pedir otra confirmación. Se espera fin de actividad y estabilidad de la
  transcripción. Los mismos límites de anexo, IP protegida y verificación siguen
  aplicándose. Un recibo por turno evita repetir la operación si el modelo también
  solicita la herramienta; el modelo recibe el resultado real para comunicarlo.
  La apertura de una alerta con bloqueo verificado pide específicamente
  «¿Quieres que desbloquee esta IP?», evitando tratar un sí a una pregunta abierta
  como autorización. En llamadas directas y orígenes protegidos no se formula esa
  oferta automáticamente.
- El micrófono se drena desde que abre AudioSocket, incluso durante conexión y
  consultas iniciales. Un búfer de 50 tramas conserva aproximadamente un segundo
  de audio reciente y descarta el atrasado; evita acumular una conversación vieja
  detrás de un arranque lento.
- Se mantiene escucha continua con VAD automático del servicio y una puerta local
  de energía con prefijo. Al terminar actividad se envía `audioStreamEnd`. Esto no
  desconecta la sesión ni convierte el agente en un reproductor por turnos.
- El establecimiento WebSocket tiene tiempos acotados y un reintento antes de
  completar setup. La sesión puede recuperarse una vez ante ausencia inicial de
  audio, una desconexión o una respuesta detenida, si no se intentó una mutación.
- Al recuperar se descarta la autorización anterior, se vuelve a consultar el
  estado cuando corresponde y se pide repetir la solicitud. No se reproducen
  órdenes. Una mutación intentada impide esa recuperación automática para evitar
  una ejecución duplicada o un resultado ambiguo.
- Se registran tiempos de setup, primer audio, fin de actividad, primer audio de
  respuesta, consultas, reconexión y descarte de audio atrasado. Los códigos de
  cierre se registran sin URL WebSocket ni credenciales.

Se observó un timeout de conexión antes del ajuste y se reprodujo una falla de
respuesta en una tanda intermedia. No se atribuyen todos los silencios antiguos
a una causa única porque no existían esas métricas. La ruta TLS, respuestas Pong
y MSS fueron inspeccionados; no se cambiaron el routing, el MTU ni la ruta por
defecto. También se probó una alternativa de modelo, sin demostrar que por sí
sola eliminara el problema; el servicio conserva Gemini Flash Live configurado.

## Llamadas finales por Tailscale

Cinco llamadas autenticadas de QA al anexo 1000, sin registrar un teléfono nuevo
ni hacer sonar a personas. Se usaron audio de entrada sintético y SIP/RTP reales,
con el servicio y Gemini reales. Los tiempos se midieron en el cliente de QA.

| Prueba | Primer audio desde respuesta SIP | Respuesta desde fin de voz | Resultado |
|---|---:|---:|---|
| 1 | 2,031 s | 1,188 s | PASS |
| 2 | 1,937 s | 1,141 s | PASS |
| 3 | 2,093 s | 1,188 s | PASS |
| 4 | 1,953 s | 1,437 s | PASS |
| 5 | 1,969 s | 1,188 s | PASS |

Después de corregir la señal de fin de respuesta se repitió una llamada completa:
primer audio **1,859 s**, respuesta a la voz **1,172 s**, PASS.

La conversación de verificación de origen solicitó `get_incident_details` y
recibió `PFSENSE_EVE` con verificación real; el modelo comunicó el origen público
y la víctima privada. La prueba de política contra una IP reservada conservó el
bloqueo ante la negativa y la consulta de detalles, y lo retiró con verificación
tras una orden expresa. Un segundo caso independiente confirmó el desbloqueo
con «Sí, por favor» después de la pregunta específica. Las entradas de audio de
QA fueron sintéticas; se reutilizaron frases almacenadas y voz local española
para evitar que la generación de esas frases fuera una dependencia del ensayo.
La IP reservada se retiró al finalizar. No se desbloqueó automáticamente la IP
del participante para estas comprobaciones.

La regresión local terminó con **80 pruebas y 28 subpruebas aprobadas**, incluidas
lectura restringida de identidad, rechazo de rutas, identidad discordante,
límites del búfer, señal de fin de actividad y recuperación de una sesión inicial
sin audio conservando la misma llamada AudioSocket.
La prueba TCP/WebSocket de autorización usa una pregunta terminada únicamente
con `generationComplete`, un sí del operador y una señal de generación junto a
la solicitud de herramienta; comprueba que no se borre la autorización pendiente.
Otro caso verifica que la confirmación contextual se ejecute exactamente una vez
aunque el modelo no proponga la acción y después la solicite de nuevo.

Estos resultados prueban los escenarios ejecutados; no constituyen un SLA ni
garantizan ausencia de fallas futuras del proveedor, VPN, teléfono o red. El
enfriamiento de avisos continúa en 120 segundos y no es una cola durable de
incidentes. Una llamada suprimida no significa que el IPS haya dejado de bloquear.

Referencias técnicas: [VAD híbrido y audioStreamEnd](https://aistudio.google.com/docs/live-api/capabilities#hybrid-vad),
[protocolo AudioSocket](https://docs.asterisk.org/Configuration/Channel-Drivers/AudioSocket/)
y [keepalive WebSocket](https://websockets.readthedocs.io/en/stable/topics/keepalive.html).
