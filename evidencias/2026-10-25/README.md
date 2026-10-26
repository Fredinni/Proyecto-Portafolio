# Evidencia nativa A4 · pfBlockerNG, reputación IP y GeoIP (25 de octubre de 2026)

**Responsable:** Kevin Retamales · **Actividad:** A4, semanas 7 y 8 (28 de septiembre al 11 de octubre de 2026).

Salidas de consola de pfSense (VM101) obtenidas por Kevin Retamales el 25/10/2026, entre las 22:33 y las 22:37 (-03), en **Diagnostics → Command Prompt**, con comandos de solo lectura. Los `.txt` son copia textual de la salida; cada uno comienza con el comando y la hora del sistema (`date`). La captura de alertas se tomó a las 22:39; solo se difuminó la foto del perfil del navegador.

Complementa los resúmenes visuales de [2026-10-01](../2026-10-01/) y [2026-10-02](../2026-10-02/) con evidencia a nivel de sistema operativo.

## Archivos

| Archivo | Comando / origen | Qué demuestra |
|---|---|---|
| [a4-01-tablas-pfblockerng.txt](pruebas/a4-01-tablas-pfblockerng.txt) | `pfctl -s Tables \| grep pfB_` | Las cuatro tablas de A4 están cargadas en el kernel. |
| [a4-02-entradas-por-tabla.txt](pruebas/a4-02-entradas-por-tabla.txt) | `pfctl -t <tabla> -T show \| wc -l` | Cantidad de redes en cada tabla. |
| [a4-03-reglas-y-contadores.txt](pruebas/a4-03-reglas-y-contadores.txt) | `pfctl -vvs rules \| grep -A2 "KRONOS A4"` | Las cuatro reglas `block drop` en la WAN (`vtnet0`), con registro y contadores de paquetes bloqueados. |
| [a4-04-limite-tablas.txt](pruebas/a4-04-limite-tablas.txt) | `pfctl -s memory` | Límite de entradas de tablas PF en 2.000.000. |
| [a4-05-log-pfblockerng.txt](pruebas/a4-05-log-pfblockerng.txt) | `tail -n 40 /var/log/pfblockerng/pfblockerng.log` | Actualización automática diaria (00:00) de GeoIP, Spamhaus DROP y FireHOL L1. |
| [a4-06-base-maxmind.txt](pruebas/a4-06-base-maxmind.txt) | `ls -l /usr/local/share/GeoIP/` | Base GeoLite2 Country instalada y actualizada (23/10/2026). |
| [a4-07-pfblockerng-alertas.png](pruebas/a4-07-pfblockerng-alertas.png) | Firewall → pfBlockerNG → Reports → Alerts | Bloqueos reales registrados con regla, país (GeoIP) y lista de origen. |

## Resultados

| Regla (orden) | Tabla | Entradas S7 (01–02/10) | Entradas 25/10 | Paquetes bloqueados | Estados abiertos |
|---|---|---:|---:|---:|---:|
| @74 KRONOS A4 GeoIP RU WAN | `pfB_Europe_v4` | 13.178 | 13.190 | 54 | 0 |
| @75 KRONOS A4 GeoIP KP WAN | `pfB_Asia_v4` | 10 | 11 | 6 | 0 |
| @76 KRONOS A4 Spamhaus DROP WAN | `pfB_KRONOS_DROP_v4` | 1.692 | 1.687 | 1.296 | 0 |
| @77 KRONOS A4 FireHOL WAN | `pfB_KRONOS_FIREHOL_v4` | 4.643 | 4.623 | 1.574 | 0 |
| **Total** | | | | **2.930** | **0** |

| Criterio | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Tablas cargadas en el kernel | 4 tablas `pfB_` | 4 tablas | PASS |
| Reglas aplicadas en la WAN | 4 reglas `block drop … log quick on vtnet0` | 4 reglas (@74 a @77) | PASS |
| Bloqueo de tráfico real | Contadores > 0 y ningún estado abierto | 2.930 paquetes bloqueados, 0 estados | PASS |
| Capacidad de tablas | `table-entries` = 2.000.000 | 2.000.000 | PASS |
| Actualización automática | Proceso diario sin errores | 25/10 a las 00:00; GeoIP, Spamhaus (200 OK) y FireHOL completados | PASS |
| Supresión en FireHOL | Se eliminan entradas que no deben bloquearse | 4.624 → 4.623 | PASS |
| Base GeoIP vigente | GeoLite2 Country reciente | `GeoLite2-Country.mmdb` del 23/10/2026 | PASS |
| Precisión de GeoIP (muestra) | Una IP bloqueada como RU pertenece a un proveedor ruso | `95.105.71.239` → RU, DNS inverso `*.ufanet.ru` | PASS (muestra de 1 IP) |

## Análisis de QA

- **Pasamos de pruebas sintéticas a tráfico real.** El 01/10 se probaron 3 tramas por regla (12/12 DROP). Ahora los contadores registran 2.930 paquetes reales de Internet bloqueados, ninguno con conexión establecida (`States: 0`). Las fuentes de `a4-07` son IP públicas originales que llegan a `10.254.254.2:80` y `:443`: esto confirma que el borde AWS preserva la IP de origen (sin SNAT), condición necesaria para que funcionen GeoIP y la reputación.
- **Las listas cambian a diario y el sistema lo absorbe.** Las cantidades varían respecto de la semana 7 (FireHOL: 15 redes agregadas y 23 eliminadas en la actualización del 25/10) sin recargar las reglas.
- **Solapamiento de listas.** En `a4-07`, varias IP bloqueadas por la regla Spamhaus muestran FireHOL L1 como lista de origen. FireHOL Level 1 incluye Spamhaus DROP entre sus fuentes y la regla @76 se evalúa antes que la @77, por lo que las IP presentes en ambas listas se contabilizan en Spamhaus. No es un error; se documenta para interpretar los contadores.
- **Nombres de tablas.** `pfB_Europe_v4` contiene solo Rusia y `pfB_Asia_v4` solo Corea del Norte; los nombres provienen de la agrupación por continente de pfBlockerNG.
- **Pendiente.** Se aplican 2 de los 6 países planificados (RU y KP de CN, RU, IR, KP, VN y NG). Falta documentar la justificación de este alcance o ampliarlo.
