# KRONOS SENTINEL — continuación comprobada al 2 de octubre de 2026

**Lectura del estado vigente:** este documento conserva los ensayos y correcciones en orden cronológico. Para el estado más reciente, consultar el último corte al final; los fallos anteriores se mantienen como evidencia de recuperación y no describen por sí solos la configuración final.

Este informe complementa el [corte del 1 de octubre](AVANCE_SEMANA7_2026-10-01.md). El avance nuevo es la inspección Inline del tráfico HTTP interno en el trunk de pfSense y su comprobación después de reiniciar. Las pruebas corresponden al **2 de octubre**, hora de Chile; no se retrofechan ni sustituyen la evidencia personal de los responsables académicos. La [Gantt oficial](Informacion_EA2/Plan_Trabajo_Carta_Gantt.md) se conserva como planificación.

**PROVISIONED** identifica infraestructura creada; **CONFIGURED**, ajustes aplicados; **TESTED**, pruebas ejecutadas; **VALIDATED**, criterios verificados dentro del alcance descrito. Un proceso activo por sí solo no demuestra que el IPS esté preparado para descartar tráfico.

## Avance por actividad

| Actividad | Responsable planificado | Ventana Gantt | Estado comprobado | Límite |
|---|---|---|---|---|
| A1 · Base pfSense y tuning | Bruno Urrea / Freddy Vásquez | 17–30 agosto | Base histórica completada; auditoría repetida el 2 de octubre en vtnet0 y vtnet1: PARTIAL, 9 PASS, 0 FAIL, 3 UNSUPPORTED | Los tres OID retirados del kernel no se cuentan como PASS. La corrección adicional del trunk se describe abajo. |
| A2 · VLAN, DHCP y aislamiento | Freddy Vásquez | 31 agosto–13 septiembre | CONFIGURED / TESTED; 16 comprobaciones PASS repetidas con ambos sensores activos | Muestra de accesos y bloqueos TCP/22; no es prueba exhaustiva de todos los puertos. |
| A3 · Suricata Inline WAN y lado protegido | Bruno Urrea / Kevin Retamales | 14–27 septiembre | CONFIGURED / TESTED en WAN y trunk; firmas sin errores ni advertencia de dependencia flowbit | Persiste una ventana de arranque sin descarte IPS, documentada; rendimiento y cobertura integral no medidos. |
| A4 · Reputación y GeoIP | Kevin Retamales | 28 septiembre–11 octubre | CONFIGURED / TESTED en el corte del 1 de octubre | Las capturas actuales no constituyen una nueva prueba de descartes RU/KP del 2 de octubre. FireHOL sigue cargado sin bloqueo. |
| A5 · HAProxy HTTPS y DVWA | Cristóbal Quezada | 12–25 octubre | Planificado; DVWA base responde HTTP interno | No se ha validado frontend HTTPS, terminación TLS, stick-tables ni publicación extremo a extremo. |
| A6 · Correlación KRONOS | Bruno Urrea | 26 octubre–8 noviembre | Planificado | Sin integración ni pruebas extremo a extremo. |
| A7 · Asterisk / AMI | Freddy Vásquez | 9–22 noviembre | Host y contenedor provisionados | AMI, PJSIP y llamadas pendientes. |
| A8 · Gemini Live Voice | Bruno Urrea | 16–29 noviembre | Planificado | Transporte y conversación no validados. |
| A9 · Acceso remoto y softphones | Freddy Vásquez | 23–29 noviembre | Parcial, estimación por hitos de 60%; administración adelantada | Tailnet separada operativa; ACL administrativas y softphones pendientes de validación integral. |
| A10 · QA integral | Equipo completo | 30 noviembre–20 diciembre | Planificado | Este informe aporta evidencia parcial y no demuestra los objetivos de latencia o supresión de falsos positivos. |

A2 y A3 obtienen evidencia técnica después de sus fechas planificadas. La acción correctiva de A3 fue completar el sensor interno, corregir el tratamiento de VLAN/offloading y repetir las pruebas de funcionamiento y persistencia. A4 continúa dentro de su ventana. Ninguna actividad futura se declara completada por disponer de una VM.

## Topología realmente existente

```text
Internet → AWS EIP → Ubuntu AWS → WireGuard → VM100 KRONOS-EDGE
                                                  |
                                          10.254.254.1/30
                                                  |
                                           vmbr2 aislado
                                                  |
                          VM101 pfSense CE 2.9.0 / vtnet0 WAN
                                     10.254.254.2/30
                                  Suricata WAN Inline
                                                  |
                              vtnet1 trunk / Suricata Inline
                                                  |
                               vmbr3 aislado, VLAN-aware
                    +-------------+-------------+-------------+
                  VLAN10        VLAN20        VLAN30        VLAN99
                 CORP104        DMZ102        VOIP103        MGMT105
              192.168.10.50  192.168.20.50  192.168.30.50  192.168.99.10
                 Gateway de cada VLAN: pfSense 192.168.<VLAN>.1

Equipo → tailnet separada → MGMT105 → pfSense → destinos autorizados
```

WireGuard termina en Ubuntu Edge; el IPS utiliza Ethernet VirtIO de pfSense. No se añadió una tercera NIC ni una dirección IPv4 al padre `vtnet1`. Se conservaron los bridges de producción, las interfaces físicas, el gateway del host y las VMs ajenas al proyecto. El equipo no recibe acceso a Proxmox ni una ruta hacia su red administrativa.

## Cambios aplicados y recuperación

El sensor WAN conserva UUID **49823** en `vtnet0`. El sensor interno utiliza UUID **62511**: el paquete conserva el nombre de interfaz seleccionada `vtnet1.20` en su directorio de configuración, mientras el dispositivo Netmap y los eventos reales corresponden al **padre trunk `vtnet1`**. Esto permite observar las etiquetas VLAN sin añadir una interfaz de administración alternativa.

La primera activación del sensor interno interrumpió la conectividad de las VLAN del laboratorio. Se recuperó exclusivamente VM101 mediante su consola VGA. No se reinició Proxmox ni se modificó producción. La corrección deshabilita `VLAN_HWTAGGING` y `VLAN_HWFILTER` sobre `vtnet1` antes de activar el sensor. Se dejó una orden idempotente en el mecanismo nativo `system/shellcmd` para aplicarla al arranque:

```sh
/sbin/ifconfig vtnet1 -vlanhwtag -vlanhwfilter -vlanhwcsum
```

La lectura posterior al reinicio todavía muestra `VLAN_HWCSUM` entre las opciones de `vtnet1`: **no se afirma que ese indicador haya desaparecido**. Las opciones de VLAN tag/filter quedaron desactivadas y TSO/LRO/checksum RX/TX continúan deshabilitados según la base configurada. La demostración de compatibilidad es el tráfico normal permitido y el descarte correlacionado, no la suposición de que todas las capacidades VirtIO puedan apagarse.

La advertencia `et.http.PK` del corte anterior se resolvió incorporando la categoría oficial `emerging-info.rules` y su firma SID **2017669**, revisión 7, seguida de reconstrucción nativa con `rebuild_rules=true`. La validación `suricata -T` informó **26.628 reglas WAN y 26.629 reglas trunk**, cero reglas fallidas y sin la advertencia de dependencia flowbit anterior. No se eliminó una firma para ocultar el aviso ni se convierte todo ET Open automáticamente en reglas de descarte.

## Pruebas ejecutadas el 2 de octubre

| Prueba | Resultado esperado | Resultado obtenido | Clasificación |
|---|---|---|---|
| Validación nativa de reglas | Configuración válida, sin reglas fallidas ni dependencia flowbit pendiente | WAN 26.628 y trunk 26.629; cero errores de carga y ausencia del aviso previo | PASS para la validación ejecutada |
| HTTP interno de control | DVWA accesible desde MGMT por el firewall | `/login.php` devuelve HTTP 200 antes y después de los marcadores | PASS |
| Marcador HTTP interno SID1000002 | Descartar únicamente la solicitud benigna seleccionada y registrar EVE | Tres solicitudes con timeout; tres eventos nuevos `blocked`/`drop`, origen 192.168.99.10, destino 192.168.20.50:80, interfaz `vtnet1`, VLAN99 | PASS después de que el sensor quedó preparado |
| Control WAN | ICMP normal permitido antes y después | 3/3 respuestas en ambos controles | PASS |
| Marcador WAN SID1000001 | Descartar tres pings seleccionados y registrar eventos nuevos | 0/3 respuestas; tres EVE nuevos `blocked`/`drop` en `vtnet0` | PASS después del arranque de los motores |
| A2 con ambos sensores activos | Mantener DHCP, administración e aislamiento de la muestra | 16 PASS: ocho controles DHCP, cinco accesos administrativos y tres denegaciones TCP/22 | PASS; muestra acotada |
| Persistencia de VM101 | Mantener configuración y recuperar ambos motores tras reiniciar | Reinicio real a las 10:21:52; motores preparados a las 10:23:01/02; pruebas WAN/internas repetidas satisfactoriamente | PASS de persistencia; arranque sin protección continua, ver siguiente fila |
| Descarte durante calentamiento | Mantener protección IPS desde el inicio | A las 10:22:41–44 los tres marcadores HTTP devolvieron 404 y no generaron nuevos eventos de descarte | FAIL del criterio de protección IPS continua durante el arranque; no se presenta como PASS |
| Internet saliente desde pfSense | Mantener conectividad | Ping 1.1.1.1: 2/2 respuestas | PASS del control ejecutado |

Las pruebas internas finales se ejecutaron a las 10:25:25–35 y las WAN a las 10:25:37–39. La correlación utiliza eventos **nuevos del ensayo correspondiente**, no registros previos al reinicio. El HTTP 404 inicial demuestra que el marcador llegó al servidor durante el calentamiento: no se interpreta como bloqueo IPS.

La ventana observada entre arranque y preparación de los motores fue de aproximadamente **70 segundos**. El estado equivale a un calentamiento *fail-open* del IPS; las reglas PF siguen siendo un control distinto, pero no sustituyen la inspección de firmas durante esa ventana. No se implantó un bloqueo automático del tráfico hasta readiness. El startup de VM101 se ajustó a `up=120`, frente a los 60 segundos anteriores, para dar más margen a las VMs dependientes; este delay no garantiza protección continua ni cubre los reinicios aislados de pfSense.

## Operación del sensor interno

Se instaló `/usr/local/sbin/kronos-ips-status` en pfSense. Desde SSH del proyecto, ejecutar ese comando: consulta los sockets activos de ambos motores, exige captura NETMAP con `copy-mode=ips`, interfaces padre/host presentes y reglas cargadas con cero fallos. También verifica que el trunk mantenga deshabilitados el tagging y filtro VLAN por hardware. La ejecución real retornó PASS; no utiliza un mensaje histórico del log como prueba suficiente de readiness. El código está en [infra/proxmox/kronos-ips-status.php](../../infra/proxmox/kronos-ips-status.php).

Antes de aplicar cambios de VLAN en pfSense, detener el sensor trunk desde **Services → Suricata → Interfaces**, conservando el sensor WAN cuando corresponda. Aplicar la configuración de VLAN, ejecutar la orden de `ifconfig` anterior sobre el padre y verificar sus opciones. Reiniciar el sensor interno y esperar el mensaje de motores preparados en su log. Confirmar después HTTP 200 de control, descarte del marcador con EVE nuevo y conectividad administrativa. Tener un proceso presente no basta para considerar recuperado el IPS.

La futura ruta será HTTPS externo → HAProxy termina TLS → HTTP interno hacia DMZ. El sensor WAN ve TLS/metadatos; **no se afirma que pueda inspeccionar SQLi dentro de HTTPS cifrado**. El ensayo de este corte utiliza un marcador HTTP inocuo y no demuestra detección de SQLi ni completa A5.

## Recuperabilidad, espacio y acceso del equipo

Se crearon snapshots de VM101 `pre-a3-trunk-20261002` y `baseline-a3-trunk-20261002`. No se tomaron como sustituto de las pruebas. La lectura posterior mostró aproximadamente **28 MB** de logs Suricata y **15 GB** disponibles en el filesystem raíz de pfSense, con dos procesos de unos 414/417 MB RSS. Son mediciones puntuales, no una prueba de capacidad prolongada.

Permanecen los límites de logs configurados el 1 de octubre: global 500 MB, EVE 100 MB, alertas/estadísticas 5 MB y retención de 24 horas. La rotación bajo carga sostenida sigue pendiente.

Las credenciales operadoras temporales se retiraron del tmpfs de MGMT y se restauró en la PC el perfil de la tailnet del equipo. El acceso WebGUI del proyecto continúa en **https://192.168.99.1:8443**, mediante las rutas autorizadas de esa tailnet. Este documento no contiene contraseñas, claves privadas, PSK ni licencia MaxMind.

## Evidencias y siguientes acciones

Las capturas reales del nuevo corte están en [EA2_Evidencias_2026-10-02](EA2_Evidencias_2026-10-02/). El [registro de captura](EA2_Evidencias_2026-10-02/configuraciones/capturas-observaciones.json) recoge las observaciones; las credenciales se ocultan antes de capturar. Ejemplos:

Se obtuvieron **24 capturas reales de la configuración**. Presentación actualizada: [PowerPoint editable de tres diapositivas](Evaluacion2_Avance_Semana7_2026-10-02.pptx) y [PDF](Evaluacion2_Avance_Semana7_2026-10-02.pdf).

- [Interfaces Suricata](EA2_Evidencias_2026-10-02/configuraciones/09-suricata-interfaces.png), [configuración del sensor trunk](EA2_Evidencias_2026-10-02/configuraciones/09e-suricata-trunk-settings.png) y [selección de interfaz interna](EA2_Evidencias_2026-10-02/configuraciones/09d-suricata-trunk-interface.png).
- [Categorías de firmas](EA2_Evidencias_2026-10-02/configuraciones/09c-suricata-categories.png) y [gestión de SID](EA2_Evidencias_2026-10-02/configuraciones/09c-suricata-SID-management.png).
- [VLAN](EA2_Evidencias_2026-10-02/configuraciones/03-vlan-8021q.png), [offloading configurado](EA2_Evidencias_2026-10-02/configuraciones/05-offloading.png) y [DVWA HTTP](EA2_Evidencias_2026-10-02/configuraciones/11-DVWA-login.png).
- [Pruebas de A2 después del reinicio](EA2_Evidencias_2026-10-02/pruebas/01-a2-postboot.png), [descarte HTTP interno](EA2_Evidencias_2026-10-02/pruebas/02-a3-interno.png) y [descarte WAN](EA2_Evidencias_2026-10-02/pruebas/03-a3-wan.png).
- [Auditoría real del kernel](EA2_Evidencias_2026-10-02/pruebas/04-a1-kernel.png), [estado actual mediante sockets del IPS](EA2_Evidencias_2026-10-02/pruebas/05-ips-health.png) y [ventana de carga sin inspección](EA2_Evidencias_2026-10-02/pruebas/06-startup-window.png).

La WebGUI etiqueta la instancia interna como DMZ (`vtnet1.20`); el generador oficial traduce esa selección al padre `vtnet1`. El proceso, los sockets y los eventos EVE acreditan el trunk efectivo: no se añadieron sensores que compitan por el mismo padre ni una tercera NIC.

Los registros crudos de los ensayos y de la ventana inicial se conservan en evidencia privada local. Las pruebas de reputación/GeoIP y preservación de origen público del 1 de octubre siguen disponibles en el informe anterior; no se cuentan como repeticiones ejecutadas hoy.

Falta decidir y validar la política durante calentamiento/reinicio, medir rendimiento y capacidad de logs, completar A5–A8, softphones/ACL de A9 y QA integral A10. A3 dispone ahora de descarte real WAN e interno y persistencia comprobada, con el límite de arranque explícito. Este corte no declara el proyecto completo.

## Actualización de seguridad — corte de las 11:35 del 2 de octubre

Después del ensayo de arranque descrito arriba se implementó un control nativo PF para cerrar el tráfico de datos del proyecto cuando alguno de los dos motores IPS no está preparado. **Este cambio no borra ni convierte en PASS el fallo inicial de 70 segundos**: aquel resultado corresponde al sistema previo a esta corrección.

Se añadieron cinco reglas floating de alcance KRONOS y el alias persistente `KRONOS_IPS_GUARD`, cuyo valor de arranque es cerrado (`0.0.0.0/0`). Las reglas conservan DHCP y las excepciones necesarias para administración/Tailscale desde MGMT; bloquean el tránsito seleccionado y la publicación WAN TCP/80–443 hasta que ambos sensores superan el verificador. La tabla se vacía solamente al comprobar readiness de WAN49823 y trunk62511. El cierre incluye retirada selectiva de estados de las redes del proyecto, preservando los estados administrativos identificados; no utiliza un vaciado global de estados PF ni selecciona redes de producción.

La capacidad máxima de tablas PF se ajustó a **2.000.000 de entradas**. Este valor es un límite configurado y comprobado, no un recuento de entradas cargadas ni una prueba de capacidad bajo carga.

El supervisor vigila un worker que consulta el estado de ambos sensores. La recuperación explícita `/usr/local/sbin/kronos-ips-recover` utiliza las funciones nativas del paquete Suricata, verifica que sean únicamente los dos sensores esperados, mantiene el guard cerrado durante la recuperación y retira un PID file obsoleto solamente cuando no corresponde a un proceso válido. Las fuentes revisables son:

- [Control del guard](../../infra/proxmox/kronos-ips-guard.sh), [servicio de arranque](../../infra/proxmox/kronos-ips-guard.rc) y [verificador de readiness](../../infra/proxmox/kronos-ips-status.php).
- [Recuperación de sensores](../../infra/proxmox/kronos-ips-recover.php) y [limpieza selectiva de estados MGMT](../../infra/proxmox/kronos-guard-mgmt-states.php).

### Resultados comprobados del guard

| Ensayo | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|
| Hold administrativo | Cerrar sesiones de datos existentes y nuevas sin perder administración | HTTP keep-alive previamente establecido deja de responder; nueva solicitud DVWA termina en timeout; WebGUI pfSense HTTP200, control HTTPS de Tailscale HTTP302 y DNS responden | PASS |
| Resume del hold | Reabrir solamente después de readiness | Guard abierto con ambos motores preparados; DVWA vuelve a HTTP200 | PASS |
| SIGKILL del sensor WAN | Detectar pérdida, cerrar datos y conservar acceso administrativo | Cierre observado a los **0,961 s**; datos bloqueados, WebGUI200 y control Tailscale302; recuperación explícita devuelve ambos sensores preparados y HTTP200 | PASS del escenario ensayado |
| SIGKILL del sensor trunk | Detectar pérdida, cerrar datos y conservar acceso administrativo | Cierre observado a los **0,637 s**; datos bloqueados, WebGUI200 y control Tailscale302; recuperación explícita devuelve HTTP200 | PASS del escenario ensayado |
| SIGKILL del worker | Supervisor recupera su worker | PID nuevo distinto del anterior; guard y readiness vuelven a READY | PASS del escenario ensayado |
| Parser de readiness | Rechazar fixtures inválidos y aceptar estados válidos según contrato | 22 fixtures ejecutados satisfactoriamente | PASS de pruebas de parser; no sustituye pruebas de tráfico |
| Reinicio completo con guard persistente | Mantener cerrados los datos desde arranque hasta readiness | Observador continuo iniciado; resultado final todavía no disponible en este corte | PENDING; no se declara PASS |

La respuesta HTTP302 del control de Tailscale comprueba acceso a su endpoint HTTPS; por sí sola no certifica todas las funciones de la tailnet. Los tiempos de cierre se obtuvieron mediante polling: demuestran una recuperación **acotada en los ensayos**, no un cierre instantáneo ni ausencia absoluta de paquetes durante toda transición. La muerte simultánea por SIGKILL del supervisor y del worker no está cubierta por una garantía. Tampoco se ha realizado estrés, medición integral de latencia ni validación de capacidad A10.

Las pruebas de fallo de este corte quedaron registradas en evidencia privada local; no contienen claves ni se publican cookies de sesión. El ensayo de reinicio afecta solamente a VM101 del laboratorio. La prueba de los bloqueos A4 sigue siendo la del 1 de octubre; no se atribuyen nuevos descartes GeoIP a esta actualización. A4 mantiene su ventana **S7–S8 hasta el 11 de octubre**: Spamhaus y GeoIP están probados, pero FireHOL sigue cargado solamente como alias sin aplicación de bloqueo. Por ello se acredita avance de A4, **no el 100% de toda la actividad**. Falta resolver y validar una política FireHOL compatible con las redes privadas del laboratorio. A1 conserva el resultado PARTIAL por tres OID retirados y A5–A10 mantienen sus pendientes anteriores.

## Continuación del cierre S7 — corte de las 12:10

Se completó la política FireHOL mediante la acción nativa **Alias_Deny**, con suppression de RFC1918, CGNAT y loopback para no bloquear las redes privadas usadas por el proyecto. La comprobación de solapamientos arrojó **cero** tanto en el archivo generado como en la tabla PF realmente cargada. Se mantiene la capacidad configurada de dos millones de entradas PF. La actualización nativa terminó con retorno 0; quedaron configuradas dos tareas cron nativas. Esto acredita su configuración y la actualización ejecutada, no el éxito de ejecuciones automáticas futuras.

Las cuatro políticas A4 se probaron nuevamente el **2 de octubre a las 11:59**, con tres tramas UDP benignas por política, dirigidas exclusivamente a pfSense WAN sobre el segmento transit aislado. Los contadores se compararon antes/después: cada regla aumentó en **tres paquetes nuevos**. No se contactaron hosts remotos ni se presenta la prueba GeoIP como tráfico originado físicamente en esos países.

| Política WAN | Entradas PF cargadas | Incremento real de contador | Resultado |
|---|---:|---:|---|
| Spamhaus DROP | 1.692 | +3 | PASS |
| Rusia / RU | 13.178 | +3 | PASS |
| Corea del Norte / KP | 10 | +3 | PASS |
| FireHOL con suppression | 4.643 | +3 | PASS |

La consulta real actual de MaxMind devuelve **US** para la dirección ensayada; demuestra respuesta de la base de datos y no localización física del cliente. A4 dispone ahora de sus componentes base configurados y probados, incluyendo FireHOL aplicado. Se conserva el compromiso de **S7–S8 / 11 de octubre**; observación sostenida, falsos positivos, capacidad y QA integral permanecen pendientes. La limitación FireHOL descrita en los cortes anteriores fue resuelta en esta continuación.

Después del reinicio y con los motores preparados se repitieron A2 (**16 PASS**) y los marcadores A3 WAN e interno (**tres eventos nuevos de descarte por sensor**) alrededor de las 11:56. No se reutilizaron eventos del corte anterior para acreditar estas repeticiones.

### Guard: ensayos adicionales y arranque

El SIGKILL del **supervisor** se detectó con cierre observado a los **0,626 segundos**; su worker huérfano salió y el estado operacional pasó a NOT READY aunque los motores IPS siguieran preparados. El reinicio explícito del guard restituyó READY. La prueba adicional de limpieza selectiva de MGMT seleccionó **dos estados**, preservó **once** y registró **cero fallos**: una conexión SSH existente hacia Edge dejó de responder, mientras el acceso administrativo SSH de pfSense permaneció disponible. Estos resultados prueban los escenarios ejecutados, no una garantía universal ante cualquier combinación de fallos.

La integración de hooks de arranque se corrigió tras comprobar que el arranque nativo del paquete ejecuta los archivos `.sh` de forma asíncrona, incluyendo el hook de cierre. El hook actualizado distingue argumentos: ignora la invocación de arranque y realiza el cierre en la invocación nativa sin argumentos correspondiente al apagado. La prueba de regresión del marcador de hold administrativo pasó; la corrección no elimina una retención solicitada explícitamente por el operador.

Se conservan las siguientes evidencias de iteración:

- Ensayos de arranque 1, 3 y 5: FAIL; no se presentan como resultados finales satisfactorios.
- Ensayo 2: PARTIAL, necesitó resume manual.
- Ensayo 4: PASS en su configuración intermedia, con 27 muestras, diez observaciones de guard cerrado, cero marcadores escapados y recuperación automática a los 108,35 segundos.
- **Ensayo 6 de la configuración corregida: PASS.** El JSON final nuevo, cerrado a las **12:10:33** (15:10:33 UTC), contiene 27 muestras, diez observaciones de guard cerrado durante el arranque, **cero respuestas HTTP200 sin inspección y cero marcadores escapados**, con recuperación automática a los **112,45 segundos**. Es la prueba final del hook corregido; el PASS intermedio del ensayo 4 se conserva separado.

El control mediante polling mantiene los límites descritos antes: no se promete cierre instantáneo ni protección garantizada ante SIGKILL simultáneo de supervisor y worker. El resultado PARTIAL de A1, los ensayos prolongados A10 y las integraciones A5–A9 conservan sus pendientes. No se modificó infraestructura de producción.

La presentación de este corte está disponible como [PowerPoint editable](Evaluacion2_Avance_Semana7_2026-10-02.pptx) y [PDF](Evaluacion2_Avance_Semana7_2026-10-02.pdf). Los resúmenes visuales de [A2 después del reinicio](EA2_Evidencias_2026-10-02/pruebas/01-a2-postboot.png), [A3 interno](EA2_Evidencias_2026-10-02/pruebas/02-a3-interno.png), [A3 WAN](EA2_Evidencias_2026-10-02/pruebas/03-a3-wan.png) y [ventana inicial de arranque](EA2_Evidencias_2026-10-02/pruebas/06-startup-window.png) transcriben pruebas reales e identifican su alcance. La captura histórica de la ventana inicial se conserva para mostrar el problema que motivó la corrección; no representa por sí sola el resultado del guard final.


## Estado final entregado - pruebas posteriores al ensayo 6

El 2 de octubre, entre las 12:11 y 12:12 de Chile, se repitieron las pruebas con la configuracion definitiva: **A2: 16 PASS**, A3: tres descartes WAN y tres descartes internos nuevos con controles normales, A4: tres incrementos nuevos por cada una de las cuatro reglas. La auditoria A1 mantiene **9 PASS, 0 FAIL, 3 UNSUPPORTED**; no se convierten en PASS los parametros retirados.

El aviso de coordinacion de Tailscale en MGMT se resolvio reiniciando solamente su servicio tailscaled. La comprobacion posterior mostro Running, Online=true y Health vacio. Desde esta PC conectada a la tailnet separada del equipo se obtuvieron tres respuestas de KRONOS-MGMT por DERP y HTTP200 de la WebGUI de pfSense. No se acredita una conexion directa entre pares. El equipo no recibe acceso al host Proxmox ni a su red de produccion. Se retiraron las claves temporales del operador de MGMT.

A las 12:20 se capturaron tres paquetes SYN en wg0 y tres en eth1 de Edge: la misma direccion publica original del cliente llego a ambos lados. **PASS: preservacion de origen**. La solicitud HTTP publica termino en timeout, resultado esperado mientras HAProxy/publicacion A5 sigan pendientes; no se declara servicio web publico funcional.

Se creo **baseline-s7-20261002** tras las pruebas finales. Es un snapshot sin memoria, consistente con caida; no se ensaya ni se acredita restauracion. El storage VM-SSD conservaba aproximadamente 120 GiB disponibles. No se crearon nuevas VMs ni discos en este cierre y no se modifico produccion.

### Evidencias finales

- [Guard al reiniciar: ensayo final](EA2_Evidencias_2026-10-02/pruebas/07-guard-arranque.png): 27 muestras, diez observaciones cerradas, cero marcadores escapados y recuperacion automatica en 112,45 segundos.
- [Fallos y recuperacion controlados](EA2_Evidencias_2026-10-02/pruebas/08-guard-caidas.png): cierre medido de sensores y administracion preservada.
- [Cuatro bloqueos A4](EA2_Evidencias_2026-10-02/pruebas/09-a4-actual.png): contadores nuevos posteriores al reinicio.
- [Reglas del guard en WebGUI](EA2_Evidencias_2026-10-02/configuraciones/08c-ips-readiness-guard.png) y [capacidad de tablas PF](EA2_Evidencias_2026-10-02/configuraciones/08d-pf-table-capacity.png).

La entrega contiene **26 capturas nativas de configuracion** y **12 resumenes visuales de pruebas reales**, identificados como transcripciones y no como consolas nativas. La PPT tiene tres diapositivas; conserva responsables y fechas de la Gantt, desviaciones y criterios medibles. A4 base queda configurada y probada antes del cierre S8. No se acredita participacion personal por ejecutar automatizaciones. A5-A10, pruebas prolongadas, falsos positivos y garantia ante fallos simultaneos siguen fuera de lo validado.


## Correccion final de compatibilidad A1 - perfil actual

Se ejecuta directamente en pfSense CE 2.9.0 / FreeBSD 16 el nuevo perfil explicito `--profile current`: **14 PASS, 0 FAIL, 0 UNSUPPORTED**. Comprueba version, forwarding=1, recursos de colas/mbufs/PF, buffers efectivos Netmap de 2048 bytes, allocator de rings positivo, flags persistentes y opciones reales de las dos NIC, y dispositivo Netmap. No simula valores ni cuenta los tres OID retirados como PASS: los conserva como diagnostico separado. El perfil `legacy` mantiene su resultado historico PARTIAL.

El antiguo `fastforwarding` no tiene un reemplazo sysctl que deba instalarse: el forwarding moderno sigue pasando por los hooks de filtrado. Los nombres actuales de buffers son `dev.netmap.buf_size` y `dev.netmap.buf_curr_size`. Los rings del allocator medidos en 36864 bytes no son 4096 descriptores. El arranque del driver muestra TX256/RX512 slots en las dos NIC. Las fuentes primarias y criterios estan enlazados en `src/pfsense_setup/README.md`.

Se corrigen el script de tuning y el fragmento XML del repositorio: ya no agregan parametros inexistentes ni cambian identidad o SSH. El script realiza una auditoria real de lectura; no declara garantias de inspeccion sin medirla. **14 pruebas unitarias** verifican que parametros obligatorios ausentes, valores incorrectos, offloading activo, permisos y plataforma incompatible produzcan FAIL.

Se repiten pruebas funcionales en la tarde del 2 de octubre: A2 16 PASS; A3 tres descartes nuevos por sensor y controles normales; A4 tres incrementos nuevos por cada regla. No se reetiquetan eventos antiguos como nuevos. [Evidencia de A1 compatible](EA2_Evidencias_2026-10-02/pruebas/10-a1-compatible.png). La entrega actual contiene 26 capturas de configuracion y 13 resumenes de pruebas. La incompatibilidad del perfil antiguo queda resuelta para la aceptacion del sistema actual; no queda un defecto funcional A1 atribuido a esos OID. Las actividades futuras de la Gantt no se presentan como ya realizadas.


Se instalo y ejecuto en pfSense `/usr/local/libexec/kronos-a1/kernel_netmap_tuning.sh --interface vtnet0 --interface vtnet1 --json`: sintaxis POSIX y auditoria compatibles PASS14/14. La repeticion de fallos de sensores de la tarde tambien paso: cierre observado WAN **0,926 s** e interno **1,177 s**, administracion preservada y recuperacion correcta de ambos sensores y del worker. El guard termino **READY**, sin hold, con los dos motores preparados. Se eliminaron claves temporales del operador y se restauro la tailnet del equipo en esta PC.
