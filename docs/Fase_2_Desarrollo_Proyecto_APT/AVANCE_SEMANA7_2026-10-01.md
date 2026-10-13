# KRONOS SENTINEL — avance comprobado al 1 de octubre de 2026

Este corte corresponde a la semana 7 y a la preparación de la Evaluación 2 del 6 de octubre. Las fechas planificadas se toman de la [carta Gantt oficial](Informacion_EA2/Plan_Trabajo_Carta_Gantt.md). Las verificaciones descritas aquí se ejecutaron el **1 de octubre**: no se presentan como pruebas realizadas retrospectivamente en agosto o septiembre.

Los responsables son los asignados en la planificación; la automatización de despliegue y auditoría no demuestra por sí sola participación personal de cada integrante. **PROVISIONED** significa recurso creado; **CONFIGURED**, configuración aplicada; **TESTED**, prueba ejecutada; **VALIDATED**, criterios completos verificados.

## Avance y compromisos

| Actividad | Responsable planificado | Fechas Gantt | Estado comprobado en este corte | Evidencia y límite |
|---|---|---|---|---|
| A1 · Base pfSense y tuning Netmap | Bruno Urrea / Freddy Vásquez | 17–30 agosto | Base histórica completada; auditoría actual ejecutada | 9 PASS, 0 FAIL y 3 UNSUPPORTED. La disponibilidad de Netmap no demuestra funcionamiento Inline IPS. |
| A2 · VLAN, DHCP y aislamiento | Freddy Vásquez | 31 agosto–13 septiembre | CONFIGURED / TESTED el 1 de octubre | 16 comprobaciones PASS: DHCP en cuatro VLAN, cinco accesos SSH administrativos y tres controles negativos TCP/22. Alcance de segmentación muestreado, no exhaustivo. |
| A3 · Suricata Inline IPS | Bruno Urrea / Kevin Retamales | 14–27 septiembre | CONFIGURED / TESTED en WAN | Prueba Inline controlada: ping normal 3/3, patrón descartado 0/3 con EVE correlacionado y control posterior 3/3. Inspección HTTP interna prevista en A5. |
| A4 · Reputación y GeoIP pfBlockerNG | Kevin Retamales | 28 septiembre–11 octubre | CONFIGURED / TESTED en WAN | MaxMind descargado y procesado; Spamhaus y países RU/KP comprobados con tráfico sintético en el enlace WAN aislado. FireHOL cargado sin aplicación de bloqueo. |
| A5 · HAProxy HTTPS y DVWA | Cristóbal Quezada | 12–25 octubre | Infraestructura DMZ provisionada; integración prevista | DVWA desplegada previamente; falta validar frontend TLS, límites de tasa y recorrido publicado. |
| A6 · Motor de correlación KRONOS | Bruno Urrea | 26 octubre–8 noviembre | Planificado | Falta verificar lectura EVE, correlación y actuación segura sobre PF. |
| A7 · Asterisk y AMI | Freddy Vásquez | 9–22 noviembre | Host y contenedor provisionados | AMI y llamada de extremo a extremo pendientes; un contenedor activo no completa A7. |
| A8 · Gemini Live Voice | Bruno Urrea | 16–29 noviembre | Planificado | Transporte y conversación extremo a extremo no validados. |
| A9 · Administración Tailscale | Freddy Vásquez | 23–29 noviembre | Parcial: 60%, acceso administrativo adelantado y recuperado | Tailnet del equipo separada, por MGMT; validación de softphones de A9 pendiente. |
| A10 · QA integral y defensa | Equipo completo | 30 noviembre–20 diciembre | Planificado | Las pruebas de este corte aportan evidencia parcial, no sustituyen el QA integral. |

**Desviaciones:** A2 se cierra técnicamente después de su fecha planificada: existía la estructura VLAN, pero faltaba demostrar DHCP y aislamiento en el entorno desplegado. Se aplicó la configuración y se ejecutaron pruebas reales. La comprobación WAN de A3 también se obtuvo después de su ventana prevista; la acción correctiva fue instalar el paquete oficial compatible, corregir sus ajustes y demostrar descarte en Netmap. A4 sigue dentro de su ventana. La dependencia inicial de MaxMind se resolvió cuando el usuario aportó credenciales de forma privada. Las evidencias actuales no se retrofechan.

## Recursos y topología existentes

```text
Internet → AWS EIP → Ubuntu AWS → WireGuard → VM100 KRONOS-EDGE
                                                  |
                                         10.254.254.1/30
                                                  |
                                          vmbr2 (aislado)
                                                  |
                            VM101 pfSense CE 2.9.0 — vtnet0 WAN
                                         10.254.254.2/30
                                         vtnet1 trunk
                                                  |
                                   vmbr3 (VLAN-aware, aislado)
                              +----------+----------+----------+
                            VLAN10     VLAN20     VLAN30     VLAN99
                            VM104      VM102      VM103      VM105
                            CORP       DMZ        VOIP       MGMT
                          .10.50     .20.50      .30.50      .99.10
                       (192.168.x.x/24; gateway pfSense 192.168.x.1)

Equipo → tailnet separada → KRONOS-MGMT → pfSense → VLAN autorizada
```

WireGuard termina en Ubuntu Edge, no en pfSense. pfSense recibe Ethernet VirtIO normal por `vtnet0`, donde Suricata Inline/Netmap ya fue probado. Los bridges protegidos no tienen IP ni interfaces físicas del host; Proxmox no funciona como router alternativo entre VLAN. Se conservaron los bridges y proyectos de producción. El equipo no recibe acceso a Proxmox ni a su red administrativa.

## Pruebas realmente ejecutadas

| Prueba | Resultado esperado | Resultado obtenido | Clasificación |
|---|---|---|---|
| Auditoría A1 sobre pfSense real | Offloading deshabilitado y tuning compatible | 9 PASS, 0 FAIL, 3 UNSUPPORTED; cola 4096, mbufs ≥1 millón, hash de estados 262.144; offloading deshabilitado en configuración y ejecución, también tras reiniciar | PARTIAL por tres parámetros no soportados; no se contabilizan como PASS |
| DHCP VLAN10/20/30/99 | Discover → Offer → Request → ACK con IP, gateway y DNS de su VLAN | DORA/ACK y release observados en las cuatro VLAN; opciones correspondientes a cada segmento | PASS: 8 comprobaciones |
| Acceso administrativo desde MGMT | SSH a los cinco destinos permitidos | Los cinco accesos probados respondieron | PASS: 5 comprobaciones |
| Controles de aislamiento TCP/22 | Denegar las tres conexiones inter-VLAN ensayadas | Las tres conexiones fueron denegadas | PASS: 3 comprobaciones; no implica bloqueo probado de todos los puertos |
| Policy routing Edge tras reiniciar networkd y la VM | Regla prioridad 100 hacia tabla 51820 y default del propio Edge conservado | Se corrigió la pérdida de la regla con un drop-in persistente; WireGuard 4/4 tras networkd y AWS 3/3 tras reiniciar VM100; gateway original conservado | PASS |
| Recuperación de MGMT | Restablecer administración del equipo sin bypass | Conectividad MGMT recuperada manteniendo la NIC exclusivamente en VLAN99 | TESTED |
| Suricata Inline / descarte real | Firma benigna descartada, EVE correlacionado y tráfico de control permitido | ICMP normal 3/3 → patrón 0/3 con evento SID1000001 `blocked/drop` → ICMP normal 3/3; proceso Netmap en WAN | PASS |
| MaxMind GeoIP | Descarga autenticada, procesamiento y consulta geográfica | Descarga nativa retornó 0; CSV/binario procesados; consulta de 8.8.8.8 devolvió US | PASS; geolocalización de base de datos, no ubicación física demostrada |
| Reputación Spamhaus | Regla WAN bloquea la fuente incluida en tabla | 1.692 entradas cargadas; tres paquetes sintéticos bloqueados; entrada temporal retirada y ausencia verificada | PASS |
| GeoIP RU/KP | Fuentes de las tablas de país bloqueadas por reglas WAN explícitas | Tablas RU: 13.178 redes; KP: 10 redes; tres paquetes sintéticos por país bloqueados y coincidentes con sus tablas PF | PASS; prueba local sobre enlace aislado, no desde países reales |
| Persistencia pfSense tras reinicio | WAN, tuning, DHCP y servicios disponibles | Arranque a las 20:16:20; cola 4096, MTU WAN 1420, DHCP en cuatro interfaces, servicios automáticos y tablas RU/KP conservados; A2 nuevamente 16 PASS | PASS para los componentes verificados |
| Inline después del reinicio | Mantener descarte y tráfico de control | Tres eventos EVE blocked/drop entre 20:18:28 y 20:18:30; ping normal 3/3 antes y después | PASS |
| Preservación del origen público | IP del cliente igual en wg0 y transit hacia WAN pfSense | Tres SYN TCP/80 vistos en wg0 y eth1 con la misma IP pública del cliente, comprobada independientemente por HTTPS | PASS; timeout HTTP esperado porque A5 sigue pendiente |

Los tres OID no soportados reflejan incompatibilidades con el kernel FreeBSD desplegado; no se fabricaron valores ni se conservaró una simulación de PASS. `/dev/netmap` presente acredita disponibilidad del dispositivo, no descarte de paquetes ni latencia IPS.

## Alcance de A3 y A4

Se instaló el paquete oficial Suricata `7.0.9`, con motor `8.0.5` suministrado por el repositorio de pfSense. Esto ajusta la versión 7.x indicada en la Gantt a la disponible oficialmente. La instancia Inline usa **WAN/vtnet0**, no `wg0`. La actualización ET Open finalizó a las 19:59:52; se seleccionaron las categorías malware, exploit y web_server, junto con reglas incorporadas. La validación posterior al reinicio informó **22.142 reglas y cero fallos**; el contador separado de firmas procesadas indicó 22.144. La gestión automática de SID mediante `dropsid.conf` convierte la firma ET2008327 seleccionada a descarte; otras firmas ET permanecen en alerta. No se afirma que todas las firmas de malware bloqueen tráfico.

La Gantt incluye inspección WAN/LAN: **A3 integral no está completada**. El sensor interno sigue pendiente y aparece por separado, con 0%, en la presentación; deberá coordinarse con el tramo HTTP de A5 tras la terminación TLS. El 100% de la tarea WAN se limita a la configuración y prueba de esa interfaz.

Los errores iniciales de validación relativos a PGSQL, JA3 y estadísticas se corrigieron mediante ajustes nativos. Permanece una advertencia de flowbit `et.http.PK` en dos reglas: debe revisarse antes de afirmar cobertura completa de esas firmas. Se configuraron límites de logs: global 500 MB, EVE 100.000 KB (100 MB), alertas/estadísticas 5.000 KB (5 MB), retención de 24 horas y tarea cada cinco minutos en `/etc/crontab`. La comprobación nativa de esa tarea se ejecutó con retorno 0; no se realizó una prueba de estrés que fuerce rotación.

En A4, Spamhaus se aplica mediante una regla WAN explícita; FireHOL contiene 4.660 líneas y se conserva sin regla de bloqueo porque incluye redes bogon que podrían interferir con el laboratorio. Los bloqueos WAN de Rusia (RU) y Corea del Norte (KP) fueron autorizados por el usuario. Las pruebas utilizaron tramas ICMP sintéticas solamente en el segmento WAN aislado hacia pfSense: no contactaron hosts externos ni ejecutaron ataques. Una selección inicial de dirección KP cayó fuera de una entrada /32 y se corrigió; el resultado final se contrastó contra la tabla exacta. GeoIP depende de la clasificación de MaxMind y puede producir falsos positivos; no acredita la ubicación real de un cliente.

Las selecciones RU/KP se guardaron mediante el esquema nativo de países y persistieron después del reinicio. Los resultados de pertenencia a tabla y contadores PF son la evidencia del bloqueo; el resumen gráfico puede mostrar `GeoIP Unk` para las fuentes sintéticas. Eso no convierte la prueba en un ataque originado realmente en Rusia o Corea del Norte.

## Seguridad y recuperabilidad

Antes del trabajo se creó el snapshot de VM101 `pre-week7-20261001` y una copia remota de configuración con permisos 600. Después de las pruebas se creó `baseline-week7-20261001`. El respaldo completo contiene secretos y permanece fuera de Git. Este informe no contiene contraseñas, claves privadas ni configuración completa de pfSense.

Se corrigió la persistencia de routing únicamente en KRONOS-EDGE. No se cambió el gateway del host Proxmox, no se modificaron VMs de producción ni se añadió una NIC que evite pfSense. Los accesos del equipo pasan por MGMT y por las reglas del firewall.

La credencial operadora temporal y su archivo de hosts conocidos se retiraron del tmpfs de MGMT antes de restaurar en la PC la sesión de la tailnet del equipo. No se entregaron credenciales de Proxmox a los compañeros.

## Criterios de aceptación y próximos pasos

| Entregable | Actividades | Criterio verificable | Compromiso Gantt |
|---|---|---|---|
| Base de firewall compatible | A1 | Auditoría real sin FAIL; incompatibilidades documentadas y offloading deshabilitado | 30 agosto; revalidado 1 octubre |
| Segmentación operativa | A2 | DHCP correcto en cuatro VLAN y accesos/denegaciones acordes con la matriz | 13 septiembre; probado 1 octubre |
| IPS Inline verificable | A3 | Descarte de una firma controlada, evento EVE correlacionado y prueba de control positiva | 27 septiembre; WAN probado el 1 octubre |
| Inteligencia de reputación y GeoIP | A4 | Feeds actualizados, política de bloqueo demostrada y base GeoIP autenticada | 11 octubre; pruebas locales obtenidas el 1 octubre |
| Publicación HTTPS segura | A5 | HTTPS termina en HAProxy y responde DVWA; inspección HTTP interna separada de TLS en WAN | 25 octubre |
| Respuesta y notificación integrada | A6–A9 | Evento correlacionado produce acción y notificación; acceso autorizado sin exposición pública administrativa | 29 noviembre |
| Evidencia de éxito integral | A10 | Pruebas completas, mediciones repetibles y manuales de operación | 20 diciembre |

## Evidencia visual disponible

Estas capturas presentan salidas reales de las pruebas del corte; no sustituyen capturas de la WebGUI ni atribuyen resultados simulados al sistema:

- [DHCP y aislamiento A2](EA2_Evidencias_2026-10-01/pruebas/01-a2-dhcp-aislamiento.png).
- [Persistencia de Edge](EA2_Evidencias_2026-10-01/pruebas/02-edge-persistencia.png).
- [Auditoría de kernel A1](EA2_Evidencias_2026-10-01/pruebas/03-a1-kernel.png).
- [Descarte Inline y controles A3](EA2_Evidencias_2026-10-01/pruebas/04-suricata-ips.png).
- [Reputación y GeoIP A4](EA2_Evidencias_2026-10-01/pruebas/05-pfblocker.png).
- [IP pública original preservada](EA2_Evidencias_2026-10-01/pruebas/06-source-preservation.png).
- [Contadores del bloqueo RU/KP](EA2_Evidencias_2026-10-01/pruebas/07-geoip-country-policy.png).

Se obtuvieron **22 capturas de la WebGUI real**. El [registro de capturas](EA2_Evidencias_2026-10-01/configuraciones/capturas-observaciones.json) identifica las observaciones. Una selección breve para el equipo:

- [VLAN 802.1Q](EA2_Evidencias_2026-10-01/configuraciones/03-vlan-8021q.png) y [DHCP CORP](EA2_Evidencias_2026-10-01/configuraciones/04-dhcp-VLAN10-CORP.png).
- [Offloading](EA2_Evidencias_2026-10-01/configuraciones/05-offloading.png) y [tuning](EA2_Evidencias_2026-10-01/configuraciones/06-system-tunables.png).
- [Suricata WAN](EA2_Evidencias_2026-10-01/configuraciones/09b-suricata-WAN-settings.png), [categorías](EA2_Evidencias_2026-10-01/configuraciones/09c-suricata-categories.png) y [gestión de SID](EA2_Evidencias_2026-10-01/configuraciones/09c-suricata-SID-management.png).
- [Listas IPv4 pfBlockerNG](EA2_Evidencias_2026-10-01/configuraciones/10b-pfBlocker-IPv4-lists.png), [reglas WAN](EA2_Evidencias_2026-10-01/configuraciones/08b-rules-WAN-reputation.png) y [DVWA](EA2_Evidencias_2026-10-01/configuraciones/11-DVWA-login.png).

Presentación de tres diapositivas: [PowerPoint editable](Evaluacion2_Avance_Semana7_2026-10-01.pptx) y [PDF](Evaluacion2_Avance_Semana7_2026-10-01.pdf). Incluye responsables, fechas Gantt, criterios medibles y contraste entre resultados esperados y obtenidos. Se comprobó visualmente el contenido y el layout sin desbordamientos.

Los registros crudos permanecen en evidencia privada local. Las configuraciones base de semana 7 y su persistencia están probadas dentro del alcance descrito. Faltan las integraciones posteriores: HAProxy, motor KRONOS, AMI, Gemini y QA extremo a extremo, además de revisar el flowbit advertido y ensayar rotación sostenida. Suricata en WAN puede observar TLS/metadatos; la inspección de SQLi HTTP requiere el tramo posterior a la terminación TLS. Ninguna actividad futura se declara completada por disponer de sus VMs.
