# GUÍA RÁPIDA DE DEFENSA: AVANCE SEMANAS 1 A 2 (ACTIVIDAD A1)
### Portafolio de Título (APT122) — Proyecto KRONOS SENTINEL
**Integrantes:** Bruno Urrea Ortiz (Ciberseguridad & Kernel) | Freddy Vásquez Cortés (Networking)  
**Actividad Carta Gantt:** A1 - Setup Base pfSense & Netmap Tuning (Semanas 1 - 2)  
**Estado:** 100% Completado y Validado Técnicamente  

---

## 1. GUION DE APERTURA (30 SEGUNDOS)

> *"Profesor, de acuerdo con la Carta Gantt y el Plan de Trabajo oficial de la asignatura, el avance que nos corresponde presentar para las Semanas 1 a 2 es la **Actividad A1: Setup Base pfSense y Netmap Kernel Tuning**.
> 
> Esta actividad la abordamos de manera modular entre dos integrantes:
> * **Freddy Vásquez** estuvo a cargo del despliegue de la infraestructura de red: instalación de la máquina virtual pfSense CE 2.9.0 en hipervisor, asignación de interfaces WAN y LAN, configuración de gateway y conectividad hacia Internet.
> * **Yo (Bruno Urrea)** asumí la parte de ciberseguridad y arquitectura de kernel: realizamos el **hardening perimetral y el tuning del sistema operativo FreeBSD 14** para acondicionarlo al subsistema **`netmap(4)`**, asegurando que el firewall soporte prevención de intrusiones en hardware sin colapsar."*

---

## 2. DEMOSTRACIÓN TÉCNICA EN VIVO (1 MINUTO)

Para demostrar que el avance está funcionando y probado, ejecuta en tu terminal:

```bash
python src/pfsense_setup/verify_kernel_hardening.py
```

### Qué explicar mientras se ejecuta:
1. **Sysctl `net.inet.ip.fastforwarding = 0`:** *"Profesor, desactivamos el fastforwarding para evitar que el kernel reenvíe paquetes por ruta rápida saltándose la inspección profunda de Packet Filter (`pf`) y la tabla `<snort2c>`."*
2. **Hardware Offloading Desactivado:** *"Desactivamos en hardware el Checksum Offload, TSO (TCP Segmentation Offload) y LRO (Large Receive Offload) en pfSense. Esto es obligatorio para que Netmap reciba paquetes reales de MTU 1500 y no buffers artificiales gigantes de 64 KB que desbordarían la memoria de Suricata."*
3. **Mbufs a 1,000,000 de clusters:** *"Cuadruplicamos los buffers de red en `/boot/loader.conf.local` para prevenir Kernel Panics ante ráfagas de tráfico masivo."*
4. **Evidencia generada:** Mostrar que la herramienta exporta automáticamente el reporte de cumplimiento en `src/pfsense_setup/evidencia_avance_A1_bruno.json`.

---

## 3. RESPUESTAS TÉCNICAS A PREGUNTAS CLAVE DEL DOCENTE

### Pregunta 1: "¿Por qué tuvieron que modificar parámetros de kernel en lugar de dejar pfSense tal como viene instalado?"
* **Respuesta Senior:**  
  *"Porque la configuración por defecto de pfSense está pensada para firewall de estado tradicional o IDS pasivo. Nuestro proyecto implementa **Suricata 7.x en modo Inline IPS** sobre el framework **`netmap(4)`**, el cual trabaja directamente sobre los anillos de memoria compartida de la tarjeta de red. Si dejamos habilitado TSO o LRO, la tarjeta de red ensambla paquetes gigantes antes de entregarlos al IPS, lo que corrompe la memoria compartida de Netmap y provoca la caída inmediata del servicio de red."*

### Pregunta 2: "¿Dónde se persisten estos cambios para que no se pierdan al reiniciar el firewall?"
* **Respuesta Senior:**  
  *"En FreeBSD/pfSense los parámetros estáticos de memoria se persisten en `/boot/loader.conf.local`, lo que garantiza que las directivas como `kern.ipc.nmbclusters="1000000"` y `hw.netmap.ring_size="4096"` se carguen en la etapa temprana del arranque del kernel. Para esto creamos el script automatizado `kernel_netmap_tuning.sh` y el parche exportable `pfsense_tuning_patch.xml`."*

---

## 4. CIERRE Y TRANSICIÓN (15 SEGUNDOS)

> *"Con este hito A1 finalizado con éxito y respaldado en nuestro repositorio GitHub, la plataforma queda técnicamente lista para los siguientes hitos de la Carta Gantt:
> * **Semanas 3 a 4 (Actividad A2):** Freddy implementará la segmentación de las 4 VLANs 802.1Q (Corporativa, DMZ, VoIP y Gestión).
> * **Semanas 5 a 6 (Actividad A3):** Montaremos el motor Suricata 7.x en modo Inline IPS sobre los descriptores de Netmap que dejamos testeados en este avance."*
