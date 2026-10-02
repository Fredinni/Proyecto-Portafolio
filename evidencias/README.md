# Evidencias KRONOS SENTINEL

Assets originales para las presentaciones del equipo: capturas de configuracion y resumenes visuales de pruebas reales. Los PNG se copian sin recortes, recompresion ni cambios de resolucion.

**Para la configuracion mas reciente, usar `2026-10-02/`.** Las otras carpetas conservan el avance historico y pueden mostrar valores o problemas anteriores ya corregidos.

## Colecciones

| Coleccion | Configuraciones WebGUI | Resumenes de pruebas |
|---|---:|---:|
| [2026-09-27](2026-09-27/) | 6 | 3 |
| [2026-10-01](2026-10-01/) | 22 | 10 |
| [2026-10-02](2026-10-02/) | 26 | 13 |

## Uso en PowerPoint

1. Descargar la imagen desde GitHub mediante **Download raw file**, o clonar esta rama del repositorio.
2. En PowerPoint: **Insertar > Imagenes > Este dispositivo** y seleccionar el PNG.
3. Mantener la fecha y explicar que prueba o configuracion demuestra. Las capturas largas requieren recorte visual en la diapositiva o uso como anexo.

Las imagenes de `configuraciones/` son capturas de WebGUI. Las de `pruebas/` son transcripciones/resumenes visuales de comandos ejecutados, identificados en la propia imagen; no son capturas nativas de una consola. Los tres archivos `ppt-*.png` son variantes compactas para diapositivas.

La coleccion historica `2026-09-27` conserva el nombre del conjunto original; el reloj visible dentro de cada captura prevalece para interpretar su fecha. No acredita por si sola la configuracion actual.

Se mantienen ocultos los campos sensibles en las capturas de configuracion. No se incluyen contrasenas, claves privadas, archivos de autenticacion ni el checkpoint de trabajo.

`manifest.json` registra origen y SHA-256 de cada PNG para verificar que es una copia identica.

## Indice de imagenes

### 2026-10-02

- [01-dashboard-interfaces.png](2026-10-02/configuraciones/01-dashboard-interfaces.png) - configuraciones
- [01b-interfaces-resumen.png](2026-10-02/configuraciones/01b-interfaces-resumen.png) - configuraciones
- [02-wan.png](2026-10-02/configuraciones/02-wan.png) - configuraciones
- [03-vlan-8021q.png](2026-10-02/configuraciones/03-vlan-8021q.png) - configuraciones
- [04-dhcp-VLAN10-CORP.png](2026-10-02/configuraciones/04-dhcp-VLAN10-CORP.png) - configuraciones
- [04-dhcp-VLAN20-DMZ.png](2026-10-02/configuraciones/04-dhcp-VLAN20-DMZ.png) - configuraciones
- [04-dhcp-VLAN30-VOIP.png](2026-10-02/configuraciones/04-dhcp-VLAN30-VOIP.png) - configuraciones
- [04-dhcp-VLAN99-MGMT.png](2026-10-02/configuraciones/04-dhcp-VLAN99-MGMT.png) - configuraciones
- [05-offloading.png](2026-10-02/configuraciones/05-offloading.png) - configuraciones
- [06-system-tunables.png](2026-10-02/configuraciones/06-system-tunables.png) - configuraciones
- [07-rules-CORP.png](2026-10-02/configuraciones/07-rules-CORP.png) - configuraciones
- [08-rules-DMZ.png](2026-10-02/configuraciones/08-rules-DMZ.png) - configuraciones
- [08b-rules-WAN-reputation.png](2026-10-02/configuraciones/08b-rules-WAN-reputation.png) - configuraciones
- [08c-ips-readiness-guard.png](2026-10-02/configuraciones/08c-ips-readiness-guard.png) - configuraciones
- [08d-pf-table-capacity.png](2026-10-02/configuraciones/08d-pf-table-capacity.png) - configuraciones
- [09-suricata-interfaces.png](2026-10-02/configuraciones/09-suricata-interfaces.png) - configuraciones
- [09b-suricata-WAN-settings.png](2026-10-02/configuraciones/09b-suricata-WAN-settings.png) - configuraciones
- [09c-suricata-categories.png](2026-10-02/configuraciones/09c-suricata-categories.png) - configuraciones
- [09c-suricata-SID-management.png](2026-10-02/configuraciones/09c-suricata-SID-management.png) - configuraciones
- [09d-suricata-trunk-interface.png](2026-10-02/configuraciones/09d-suricata-trunk-interface.png) - configuraciones
- [09e-suricata-trunk-settings.png](2026-10-02/configuraciones/09e-suricata-trunk-settings.png) - configuraciones
- [10-pfBlocker-IP-settings.png](2026-10-02/configuraciones/10-pfBlocker-IP-settings.png) - configuraciones
- [10b-pfBlocker-IPv4-lists.png](2026-10-02/configuraciones/10b-pfBlocker-IPv4-lists.png) - configuraciones
- [10c-pfBlocker-summary-1.png](2026-10-02/configuraciones/10c-pfBlocker-summary-1.png) - configuraciones
- [10c-pfBlocker-summary-2.png](2026-10-02/configuraciones/10c-pfBlocker-summary-2.png) - configuraciones
- [11-DVWA-login.png](2026-10-02/configuraciones/11-DVWA-login.png) - configuraciones
- [01-a2-postboot.png](2026-10-02/pruebas/01-a2-postboot.png) - pruebas
- [02-a3-interno.png](2026-10-02/pruebas/02-a3-interno.png) - pruebas
- [03-a3-wan.png](2026-10-02/pruebas/03-a3-wan.png) - pruebas
- [04-a1-kernel.png](2026-10-02/pruebas/04-a1-kernel.png) - pruebas
- [05-ips-health.png](2026-10-02/pruebas/05-ips-health.png) - pruebas
- [06-startup-window.png](2026-10-02/pruebas/06-startup-window.png) - pruebas
- [07-guard-arranque.png](2026-10-02/pruebas/07-guard-arranque.png) - pruebas
- [08-guard-caidas.png](2026-10-02/pruebas/08-guard-caidas.png) - pruebas
- [09-a4-actual.png](2026-10-02/pruebas/09-a4-actual.png) - pruebas
- [10-a1-compatible.png](2026-10-02/pruebas/10-a1-compatible.png) - pruebas
- [ppt-a2.png](2026-10-02/pruebas/ppt-a2.png) - pruebas
- [ppt-a3.png](2026-10-02/pruebas/ppt-a3.png) - pruebas
- [ppt-a4.png](2026-10-02/pruebas/ppt-a4.png) - pruebas

### 2026-10-01

- [01-dashboard-interfaces.png](2026-10-01/configuraciones/01-dashboard-interfaces.png) - configuraciones
- [01b-interfaces-resumen.png](2026-10-01/configuraciones/01b-interfaces-resumen.png) - configuraciones
- [02-wan.png](2026-10-01/configuraciones/02-wan.png) - configuraciones
- [03-vlan-8021q.png](2026-10-01/configuraciones/03-vlan-8021q.png) - configuraciones
- [04-dhcp-VLAN10-CORP.png](2026-10-01/configuraciones/04-dhcp-VLAN10-CORP.png) - configuraciones
- [04-dhcp-VLAN20-DMZ.png](2026-10-01/configuraciones/04-dhcp-VLAN20-DMZ.png) - configuraciones
- [04-dhcp-VLAN30-VOIP.png](2026-10-01/configuraciones/04-dhcp-VLAN30-VOIP.png) - configuraciones
- [04-dhcp-VLAN99-MGMT.png](2026-10-01/configuraciones/04-dhcp-VLAN99-MGMT.png) - configuraciones
- [05-offloading.png](2026-10-01/configuraciones/05-offloading.png) - configuraciones
- [06-system-tunables.png](2026-10-01/configuraciones/06-system-tunables.png) - configuraciones
- [07-rules-CORP.png](2026-10-01/configuraciones/07-rules-CORP.png) - configuraciones
- [08-rules-DMZ.png](2026-10-01/configuraciones/08-rules-DMZ.png) - configuraciones
- [08b-rules-WAN-reputation.png](2026-10-01/configuraciones/08b-rules-WAN-reputation.png) - configuraciones
- [09-suricata-interfaces.png](2026-10-01/configuraciones/09-suricata-interfaces.png) - configuraciones
- [09b-suricata-WAN-settings.png](2026-10-01/configuraciones/09b-suricata-WAN-settings.png) - configuraciones
- [09c-suricata-categories.png](2026-10-01/configuraciones/09c-suricata-categories.png) - configuraciones
- [09c-suricata-SID-management.png](2026-10-01/configuraciones/09c-suricata-SID-management.png) - configuraciones
- [10-pfBlocker-IP-settings.png](2026-10-01/configuraciones/10-pfBlocker-IP-settings.png) - configuraciones
- [10b-pfBlocker-IPv4-lists.png](2026-10-01/configuraciones/10b-pfBlocker-IPv4-lists.png) - configuraciones
- [10c-pfBlocker-summary-1.png](2026-10-01/configuraciones/10c-pfBlocker-summary-1.png) - configuraciones
- [10c-pfBlocker-summary-2.png](2026-10-01/configuraciones/10c-pfBlocker-summary-2.png) - configuraciones
- [11-DVWA-login.png](2026-10-01/configuraciones/11-DVWA-login.png) - configuraciones
- [01-a2-dhcp-aislamiento.png](2026-10-01/pruebas/01-a2-dhcp-aislamiento.png) - pruebas
- [02-edge-persistencia.png](2026-10-01/pruebas/02-edge-persistencia.png) - pruebas
- [03-a1-kernel.png](2026-10-01/pruebas/03-a1-kernel.png) - pruebas
- [04-suricata-ips.png](2026-10-01/pruebas/04-suricata-ips.png) - pruebas
- [05-pfblocker.png](2026-10-01/pruebas/05-pfblocker.png) - pruebas
- [06-source-preservation.png](2026-10-01/pruebas/06-source-preservation.png) - pruebas
- [07-geoip-country-policy.png](2026-10-01/pruebas/07-geoip-country-policy.png) - pruebas
- [ppt-a2.png](2026-10-01/pruebas/ppt-a2.png) - pruebas
- [ppt-a3.png](2026-10-01/pruebas/ppt-a3.png) - pruebas
- [ppt-a4.png](2026-10-01/pruebas/ppt-a4.png) - pruebas

### 2026-09-27

- [01-pfsense-dashboard.png](2026-09-27/configuraciones/01-pfsense-dashboard.png) - configuraciones
- [01b-pfsense-version.png](2026-09-27/configuraciones/01b-pfsense-version.png) - configuraciones
- [01c-pfsense-interfaces.png](2026-09-27/configuraciones/01c-pfsense-interfaces.png) - configuraciones
- [02-pfsense-wan.png](2026-09-27/configuraciones/02-pfsense-wan.png) - configuraciones
- [03-pfsense-offloading.png](2026-09-27/configuraciones/03-pfsense-offloading.png) - configuraciones
- [04-dvwa-login.png](2026-09-27/configuraciones/04-dvwa-login.png) - configuraciones
- [05-edge.png](2026-09-27/pruebas/05-edge.png) - pruebas
- [06-pfsense-kernel.png](2026-09-27/pruebas/06-pfsense-kernel.png) - pruebas
- [07-tailscale.png](2026-09-27/pruebas/07-tailscale.png) - pruebas
