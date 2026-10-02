# Auditoría de kernel y base pfSense — A1

**Responsable:** Bruno Urrea Ortiz. **Colaborador:** Freddy Vasquez Cortes.
Actividad A1: Setup Base pfSense & Netmap Tuning, semanas 1–2.

El verificador mide el kernel, el XML persistente y las opciones activas de
las NIC. No aplica cambios, simula observaciones ni prueba el IPS por sí solo.
La compatibilidad se declara por un perfil explícito; no se ocultan los
resultados históricos para convertir una auditoría parcial en PASS.

## Perfil actual: pfSense CE 2.9.0 / FreeBSD 16

```sh
python3.11 verify_kernel_hardening.py --profile current \
  --interface vtnet0 --interface vtnet1 --json
```

Este perfil comprueba primero `platform.system()`, `platform.release()` y el
contenido real de `/etc/version`. Un sistema diferente, una versión distinta
o un error de lectura produce FAIL; no existe un fallback de éxito.

| Componente | Criterio obligatorio | Fuente real |
|---|---|---|
| Routing IPv4 | `net.inet.ip.forwarding = 1` | `sysctl -n` |
| Cola de entrada | `net.inet.ip.intr_queue_maxlen >= 4096` | `sysctl -n` |
| Hash de estados | `net.pf.states_hashsize >= 131072` | `sysctl -n` |
| Clusters mbuf | `kern.ipc.nmbclusters >= 1000000` | `sysctl -n` |
| Buffer Netmap configurado | `dev.netmap.buf_size = 2048` | `sysctl -n` |
| Buffer Netmap efectivo | `dev.netmap.buf_curr_size = 2048` | `sysctl -n` |
| Objeto ring Netmap efectivo | `dev.netmap.ring_curr_size > 0` bytes | `sysctl -n` |
| Checksum, TSO y LRO | Desactivados en configuración persistente | Flags `system` de `/cf/conf/config.xml` |
| Offloading de NIC | Sin RXCSUM/TXCSUM, TSO ni LRO activos en cada NIC elegida | Campo `options` de `ifconfig`, nunca `capabilities` |
| Dispositivo Netmap | `/dev/netmap` es un dispositivo de caracteres | `/bin/test -c /dev/netmap` |

Con WAN y trunk son **14 comprobaciones obligatorias**. Cualquier OID
obligatorio ausente, valor incorrecto, comando fallido o XML inválido falla.
El tamaño `dev.netmap.ring_size` se registra como diagnóstico en bytes:
**no representa 4096 descriptores de NIC** y no se fuerza a ese valor.
Los mínimos de recursos son criterios del laboratorio; no garantizan
rendimiento, ausencia de pérdidas ni una capacidad universal de conexiones.

`net.inet.ip.fastforwarding`, `hw.netmap.buf_size` y `hw.netmap.ring_size`
pertenecen al perfil histórico. En el perfil actual sus resultados reales
quedan en `legacy_diagnostics`, fuera del conjunto de aceptación. Su ausencia
no se convierte en un PASS, ni se escribe un nombre retirado en loader.conf.
Tampoco se inventa un reemplazo `net.inet.ip.tryforwarding`. La protección
real se verifica con Packet Filter y pruebas separadas de Suricata/Netmap.

## Perfil histórico: compatibilidad de la evidencia

```sh
python3.11 verify_kernel_hardening.py --profile legacy \
  --interface vtnet0 --interface vtnet1 --json
```

`legacy` sigue siendo el perfil predeterminado para mantener comparables las
auditorías anteriores. En el kernel desplegado puede producir 9 PASS y
3 UNSUPPORTED: los tres OID históricos ausentes hacen el resultado PARTIAL.
No se modifica esa evidencia. Si un OID existe con un valor incorrecto o el
comando falla por permisos/timeout, se registra FAIL. `--require-legacy-oids`
exige también esos nombres y solamente puede usarse con el perfil `legacy`.

## Scripts y persistencia

`kernel_netmap_tuning.sh` ahora es un punto de entrada **solo lectura** que
ejecuta el verificador con `--profile current`; ya no añade bloques repetidos
a `/boot/loader.conf.local`, escribe `/etc/sysctl.conf` ni anuncia cambios
de offloading sin medirlos. Requiere `python3.11` y devuelve el código real
de la auditoría.

`pfsense_tuning_patch.xml` es un **fragmento de referencia**, no un respaldo
restaurable. Contiene solamente flags de offloading y los tres mínimos de
recursos, con la estructura nativa `sysctl/item`. No cambia hostname, SSH,
gateway, reglas o asignaciones de interfaces. Aplicar valores por los
controles nativos de pfSense después de un backup, preservando cualquier
valor actual mayor que el mínimo. No impone los tamaños del allocator
Netmap. Los controles son **System → Advanced → Networking** para
offloading y **System → Advanced → System Tunables** para los tunables.
La persistencia efectiva requiere medir nuevamente después de reiniciar.

## Evidencia y códigos de salida

```sh
python3.11 verify_kernel_hardening.py --profile current \
  --interface vtnet0 --interface vtnet1 --json \
  --output /root/kronos-a1-current-audit.json
```

No se escribe evidencia por defecto. Un archivo existente se rechaza salvo
`--overwrite`; los reportes contienen solo observaciones no secretas, nunca
el XML completo. Códigos: **0** aceptación PASS; **1** algún FAIL o error al
guardar; **2** perfil histórico con UNSUPPORTED sin otros fallos. El perfil
actual devuelve FAIL en Windows/Linux; el histórico devuelve UNSUPPORTED.

`evidencia_avance_A1_bruno.json` es histórica: la versión original simulaba
valores fuera de FreeBSD y no medía offloading. No acredita el estado actual.

## Pruebas del verificador y alcance

```sh
python -m unittest discover -s src/pfsense_setup/tests -v
```

Los tests cubren perfiles, OID obligatorio ausente, buffers diferentes,
ring efectivo vacío, forwarding deshabilitado, valores inválidos, errores de
comando, plataformas incompatibles y distinción entre capabilities y options.
Son pruebas del parser/criterios, no evidencia de la VM. Un PASS de A1 no
demuestra bloqueo de ataques, logs, carga, latencia o persistencia del IPS:
esas comprobaciones requieren ejecutar el healthcheck y tráfico de prueba
sobre las instancias reales WAN y trunk.
