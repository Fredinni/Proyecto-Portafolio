# Modulo de Tuning de Kernel y Setup Base pfSense CE 2.9.0

## Portafolio de Titulo (APT122) - Proyecto KRONOS SENTINEL
* **Actividad segun Carta Gantt:** A1 - Setup Base pfSense & Netmap Tuning (Semanas 1 - 2)
* **Responsable:** Bruno Urrea Ortiz (Lider de Ciberseguridad y Kernel)
* **Colaborador:** Freddy Vasquez Cortes (Configuracion de Red e Interfaces)

---

## 1. Descripcion del Avance Tecnico

En el marco de la **Actividad A1**, la responsabilidad del area de ciberseguridad consistio en acondicionar el sistema operativo FreeBSD 14 subyacente en pfSense CE 2.9.0 para soportar la operacion sin caidas ni degradacion de rendimiento de **Suricata 7.x en modo Inline IPS** mediante el subsistema de red `netmap(4)`.

El modo Inline tradicional en tarjetas de red virtuales suele fallar por corrupcion de paquetes cuando las caracteristicas de hardware offloading estan habilitadas. Este modulo provee la solucion tecnica formal implementada para el proyecto.

---

## 2. Ajustes de Kernel Aplicados

### A. Desactivacion de Hardware Offloading
Para habilitar el paso directo de paquetes hacia el ring-buffer de Netmap sin interferencias del driver o de la emulacion de hardware, se desactivaron las siguientes caracteristicas en pfSense (`System > Advanced > Networking`):
1. **Hardware Checksum Offload (`disablechecksumoffloading: yes`):** Asegura que el checksum sea calculado por el stack y no por la NIC virtual, evitando falsos descartes.
2. **Hardware TCP Segmentation Offload - TSO (`disablesegmentationoffloading: yes`):** Obligatorio para Netmap; si TSO esta activo, paquetes superiores a MTU 1500 rompen la memoria compartida del motor IPS.
3. **Hardware Large Receive Offload - LRO (`disablelargereceiveoffloading: yes`):** Previene que la NIC agrupe paquetes entrantes antes de que Suricata pueda analizarlos individualmente.

### B. Parametros de Boot Loader (`/boot/loader.conf.local`)
* `kern.ipc.nmbclusters="1000000"`: Incrementa la reserva de clusters de memoria mbuf a 1 millon para tolerar rafagas de escaneos y ataques sin saturacion de memoria.
* `hw.netmap.buf_size="2048"`: Estandariza los buffers de intercambio entre interfaz y Suricata.
* `hw.netmap.ring_size="4096"`: Cuadruplica el tamano de los anillos RX/TX para eliminar latencia en el descarte de paquetes maliciosos.

### C. Variables Dinamicas de Kernel (`sysctl`)
* `net.inet.ip.fastforwarding=0`: Garantiza que ningun paquete IPv4 sea reenviado por ruta rapida sin cruzar el motor Packet Filter (`pf`) y la tabla `<snort2c>`.
* `net.pf.states_hashsize=131072`: Dimensiona la tabla de hash de estados en memoria RAM para rastreo eficiente de conexiones.

---

## 3. Archivos del Modulo

* `kernel_netmap_tuning.sh`: Script en shell FreeBSD para automatizar la inyeccion de parametros en `/boot/loader.conf.local` y aplicar `sysctl` en caliente.
* `pfsense_tuning_patch.xml`: Fragmento XML exportable para importar las politicas de hardware offloading y variables de sistema en pfSense WebGUI.
* `verify_kernel_hardening.py`: Herramienta de auditoria tecnica que evalua el cumplimiento de cada parametro y exporta el reporte JSON de evidencia.
* `evidencia_avance_A1_bruno.json`: Reporte de auditoria generado tras la ejecucion de pruebas tecnicas.

---

## 4. Ejecucion y Verificacion

Para verificar los parametros en consola de pfSense o en entorno de desarrollo:

```bash
python verify_kernel_hardening.py
```

Salida esperada:
```text
[1] Verificacion de Parametros de Kernel (sysctl):
  - net.inet.ip.fastforwarding: 0 -> [PASS]
  - net.inet.ip.intr_queue_maxlen: 4096 -> [PASS]
  - net.pf.states_hashsize: 131072 -> [PASS]

[2] Verificacion de Hardware Offloading (Advanced > Networking):
  - Hardware Checksum Offload: Desactivado -> [CONFIGURADO]
  - Hardware TCP Segmentation Offload (TSO): Desactivado -> [CONFIGURADO]
  - Hardware Large Receive Offload (LRO): Desactivado -> [CONFIGURADO]

[3] Dimensionamiento de Memoria para Netmap:
  - kern.ipc.nmbclusters: 1000000 (Buffer disponible para rafagas)
  - hw.netmap.ring_size: 4096 (Anillo de descriptores sin latencia)

[OK] Evidencia tecnica exportada: evidencia_avance_A1_bruno.json
```
