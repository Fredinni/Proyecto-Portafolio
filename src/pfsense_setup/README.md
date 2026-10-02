# Auditoría de kernel y base pfSense — A1

**Responsable:** Bruno Urrea Ortiz. **Colaborador:** Freddy Vasquez Cortes.
Actividad: A1, Setup Base pfSense & Netmap Tuning, semanas 1–2.

`verify_kernel_hardening.py` es una auditoría de lectura. Comprueba el sistema
real; no modifica sysctl, interfaces ni el XML de pfSense. Ejecutarlo desde
Windows o Linux devuelve `UNSUPPORTED` con código 2 y no genera valores
simulados ni evidencia de éxito.

## Comprobaciones

| Componente | Criterio | Fuente real |
|---|---|---|
| Cola de entrada IPv4 | `net.inet.ip.intr_queue_maxlen >= 4096` | `sysctl -n` |
| Hash de estados pf | `net.pf.states_hashsize >= 131072` | `sysctl -n` |
| Clusters mbuf | `kern.ipc.nmbclusters >= 1000000` | `sysctl -n` |
| Checksum, TSO y LRO | Desactivados en configuración persistente | Flags de `system` en `/cf/conf/config.xml` |
| Offloading de NIC | Sin RXCSUM/TXCSUM, TSO ni LRO habilitados | Campo **options** de `ifconfig`, nunca capabilities |
| Netmap | `/dev/netmap` es un dispositivo de caracteres | `/bin/test -c /dev/netmap` |
| Tunables históricos | fastforwarding=0, buf_size=2048, ring_size=4096 si existen | `sysctl -n` |

Los OID históricos pueden estar ausentes en la versión instalada de
FreeBSD/pfSense. Su ausencia explícita se registra como `UNSUPPORTED`, separada
de `FAIL`; el resultado global es `PARTIAL`, nunca un PASS completo. Si existen
con un valor incorrecto, fallan. Un error de permisos, timeout u otro fallo de
comando también falla: no se confunde con un OID retirado. El perfil opcional
`--require-legacy-oids` exige todos esos OID y convierte su ausencia en FAIL.

Una tabla hash de 262144 cumple el mínimo sin reducirla a 131072. Los mínimos
son el perfil de este proyecto; no son una garantía de rendimiento ni una
recomendación universal de dimensionamiento. Cambios de memoria requieren
revisar la RAM disponible y validar después del reboot.

## Ejecución en el pfSense desplegado

```sh
python3.11 verify_kernel_hardening.py --interface vtnet0 --interface vtnet1
```

Sin `--interface`, se audita la WAN identificada en `config.xml`. Se pueden
repetir las interfaces para comprobar también el trunk. Para exportar evidencia
nueva explícitamente:

```sh
python3.11 verify_kernel_hardening.py --interface vtnet0 --interface vtnet1 \
  --json --output /root/kronos-a1-audit-20261001.json
```

La salida JSON contiene observaciones, códigos de salida de los comandos y un
resumen de PASS/FAIL/UNSUPPORTED. Nunca serializa el XML completo ni credenciales.
Códigos de salida: **0** todas las comprobaciones PASS; **1** al menos un FAIL o
error al escribir evidencia; **2** comprobaciones no soportadas sin otros fallos.
No se escribe ningún archivo por defecto. Un destino existente se rechaza salvo
que se indique `--overwrite`; la evidencia histórica del repositorio permanece
intacta.

## Alcance de la evidencia

La auditoría verifica prerrequisitos de kernel/offloading y la presencia del
dispositivo Netmap. **No verifica Suricata Inline, bloqueo de ataques, carga,
latencia ni persistencia tras reiniciar.** Esas pruebas requieren evidencia
separada sobre la VM desplegada. La versión de FreeBSD se obtiene en cada
reporte y no se presupone a partir del número de versión de pfSense.

`kernel_netmap_tuning.sh` y `pfsense_tuning_patch.xml` contienen el perfil
histórico. Revisar compatibilidad antes de usarlos: no aplicar OID inexistentes
ni asumir que incluir un valor en loader.conf significa que el kernel lo utiliza.
`evidencia_avance_A1_bruno.json` es un artefacto histórico y no acredita por sí
solo el estado actual; la versión anterior del verificador simulaba valores
fuera de FreeBSD y declaraba offloading correcto sin medirlo. Se necesita una
nueva ejecución real del verificador corregido.
