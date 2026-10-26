# Evidencias A5 · HAProxy HTTPS y DVWA (17–18 de octubre de 2026)

**Responsable:** Cristóbal Quezada · **Actividad:** A5, semanas 9 y 10 (12 al 25 de octubre de 2026).

Capturas originales de la WebGUI de pfSense (VM101) y de la consola de KRONOS-EDGE (VM100). La CA y el certificado se crearon el 17/10/2026 a las 23:11–23:18; las pruebas con `curl` se ejecutaron el 18/10/2026 a las 06:12 GMT (03:12 en Chile). En `a5-16` se ocultaron los valores de las cookies `PHPSESSID`; el resto de las imágenes son copias idénticas.

## Configuración (`configuraciones/`)

| Imagen | Qué demuestra |
|---|---|
| [a5-01-haproxy-settings](configuraciones/a5-01-haproxy-settings.jpg) | HAProxy 3.2.19 habilitado en pfSense, con un máximo de 4.096 conexiones por proceso. |
| [a5-02-ca-kronos](configuraciones/a5-02-ca-kronos.jpg) | Autoridad certificadora interna `KRONOS-CA` (autofirmada, válida hasta 2036). |
| [a5-03-certificado-dvwa](configuraciones/a5-03-certificado-dvwa.jpg) | Certificado de servidor `kronos-dvwa` (CN `dvwa.kronos.lab`) emitido por KRONOS-CA y en uso por HAProxy. |
| [a5-04-frontend-lista](configuraciones/a5-04-frontend-lista.jpg) | Frontend `fe_kronos_wan` «A5 HTTPS DVWA» en `10.254.254.2:443` (SSL) y `:80`, con el backend `bk_dvwa_dmz`. |
| [a5-05-frontend-ssl-offloading](configuraciones/a5-05-frontend-ssl-offloading.jpg) | SSL Offloading con el certificado `kronos-dvwa`: HAProxy termina TLS y envía HTTP interno a la DMZ. |
| [a5-06-frontend-advanced-pass-thru](configuraciones/a5-06-frontend-advanced-pass-thru.jpg) | Stick-table por IP de origen, rechazo por conexiones simultáneas y por tasa, respuestas 429 por tasa de peticiones y de errores, límite específico para `/login.php`, cabeceras de seguridad (HSTS, X-Frame-Options, nosniff, Referrer-Policy), eliminación de `Server` y `X-Powered-By`, y redirección 301 a HTTPS. |
| [a5-07-backend-servidor](configuraciones/a5-07-backend-servidor.jpg) | Backend `bk_dvwa_dmz` con el servidor `dvwa_node1` en `192.168.20.50:80` (VM102, VLAN 20 DMZ). |
| [a5-08-backend-health-check](configuraciones/a5-08-backend-health-check.jpg) | Verificación de salud HTTP `GET /login.php` cada 3.000 ms, con registro de cambios de estado. |
| [a5-09-backend-stick-table](configuraciones/a5-09-backend-stick-table.jpg) | Stick-table del backend (50k entradas, expiración de 5 min, tasa de peticiones). |
| [a5-10-regla-wan-web-ports](configuraciones/a5-10-regla-wan-web-ports.jpg) | Regla WAN: permite TCP solo desde KRONOS-EDGE (`10.254.254.1`) hacia la dirección WAN en el alias `WEB_PORTS`. |

## Pruebas (`pruebas/`)

| Imagen | Resultado |
|---|---|
| [a5-11-haproxy-validacion-config](pruebas/a5-11-haproxy-validacion-config.jpg) | `haproxy -c` sin errores (salida vacía). |
| [a5-12-haproxy-validacion-codigo-0](pruebas/a5-12-haproxy-validacion-codigo-0.jpg) | La misma validación con su código de salida: **0** (configuración válida). |
| [a5-13-sockstat-puertos](pruebas/a5-13-sockstat-puertos.jpg) | HAProxy escucha en `10.254.254.2:443`, `10.254.254.2:80` y en `127.0.0.1:2200` (estadísticas locales). |
| [a5-14-stick-tables](pruebas/a5-14-stick-tables.jpg) | Stick-tables activas: `fe_kronos_wan` (102.400) y `bk_dvwa_dmz_ipvANY` (51.200). |
| [a5-15-haproxy-stats](pruebas/a5-15-haproxy-stats.jpg) | `dvwa_node1` **UP** con chequeo `L7OK/200 in 4ms`; 24 peticiones denegadas en el frontend. |
| [a5-16-curl-pruebas-edge](pruebas/a5-16-curl-pruebas-edge.jpg) | Pruebas desde KRONOS-EDGE (detalle abajo). |

Detalle de `a5-16`:

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| `curl -kI https://10.254.254.2/login.php` | HTTP 200 por TLS con cabeceras de seguridad | `HTTP/2 200`, HSTS, X-Frame-Options, nosniff y Referrer-Policy; sin `Server` | PASS |
| `curl -I http://10.254.254.2/` | Redirección a HTTPS | `301` → `https://10.254.254.2/` | PASS |
| 120 peticiones seguidas a `/` | Rechazo al superar la tasa de conexiones | 30 × `302` y 90 × `000` (conexión rechazada) | PASS |
| 15 peticiones a `/login.php` | Límite estricto en el login | 5 × `200` y luego 10 × `429` | PASS |
| 40 rutas inexistentes | Límite por errores | 23 × `404`, 7 × `429` y 10 × `000` | PASS |
| 120 peticiones concurrentes (`xargs`) | Límite por tasa de peticiones | 80 × `302` y 40 × `429` | PASS |
| `curl -m 5 -I http://192.168.20.50/` desde EDGE | La DMZ no es accesible sin pasar por el proxy | Timeout a los 5 s | PASS |

## Observaciones de QA (Kevin Retamales)

- Las pruebas se ejecutaron desde KRONOS-EDGE hacia la WAN de pfSense. **Falta evidenciar la publicación extremo a extremo desde Internet** (cliente externo → IP elástica de AWS → EDGE → HAProxy), que es el criterio de cierre de A5.
- El código `000` indica que HAProxy cerró la conexión a nivel TCP (regla `tcp-request connection reject`); es el comportamiento esperado, pero conviene explicarlo en la presentación.
- Las reglas de `a5-06` aparecen cortadas por el ancho del cuadro de texto. Para la evaluación, se recomienda adjuntar el texto completo de la sección (sin secretos) o una captura de `haproxy.cfg`.
- Estas pruebas validan la protección L7 contra fuerza bruta y fuzzing; la detección de SQLi corresponde a A6 (motor KRONOS) y a la QA de A10.
