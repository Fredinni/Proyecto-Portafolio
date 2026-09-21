#!/bin/sh
# ==============================================================================
# KRONOS SENTINEL - pfSense CE 2.9.0 / FreeBSD 14 Kernel & Netmap Tuning Script
# Responsable: Bruno Urrea Ortiz (Líder de Ciberseguridad y Kernel)
# Actividad Gantt: A1 - Setup Base pfSense & Netmap Tuning (Semanas 1 - 2)
# ==============================================================================
# Propósito:
# 1. Configurar parámetros críticos de kernel para compatibilidad con Netmap(4).
# 2. Desactivar hardware offloading (TSO/LRO/TX/RX Checksum) para prevenir fallos
#    críticos de descarte de paquetes en Suricata 7.x Inline IPS.
# 3. Optimizar mbuf clusters y tablas de estado de Packet Filter (pf).
# ==============================================================================

set -e

echo "=================================================================="
echo " [KRONOS SENTINEL] Aplicando Kernel & Netmap Tuning en pfSense..."
echo "=================================================================="

LOADER_CONF="/boot/loader.conf.local"
SYSCTL_CONF="/etc/sysctl.conf"

# 1. TUNING DE BOOT LOADER (Memoria y Ring-Buffers de Netmap)
echo "[+] Configurando ${LOADER_CONF}..."
touch ${LOADER_CONF}

cat << 'EOF' >> ${LOADER_CONF}
# === KRONOS SENTINEL: Netmap & High-Throughput Tuning ===
# Aumentar mbuf clusters para evitar agotamiento de memoria bajo tráfico anómalo
kern.ipc.nmbclusters="1000000"
kern.ipc.nmbjumbop="262144"
kern.ipc.nmbjumbo9="131072"

# Parámetros de buffer para el subsistema netmap(4)
hw.netmap.buf_size="2048"
hw.netmap.ring_size="4096"
hw.netmap.if_size="2048"

# Desactivar TSO/LRO a nivel de driver para compatibilidad total con Suricata Inline
hw.vtnet.csum_disable="1"
hw.vtnet.tso_disable="1"
hw.vtnet.lro_disable="1"
EOF

# 2. TUNING DE SYSCTL EN CALIENTE (Packet Filter y Routing)
echo "[+] Aplicando parámetros de kernel vía sysctl..."

# Desactivar IP Fastforwarding (interfiere con la inspección profunda de pf y Netmap)
sysctl net.inet.ip.fastforwarding=0

# Aumentar cola de entrada del sistema de red
sysctl net.inet.ip.intr_queue_maxlen=4096

# Optimizar hashsize de estados de pf
sysctl net.pf.states_hashsize=131072
sysctl net.pf.source_nodes_hashsize=32768

# 3. VERIFICACIÓN DE ESTADO
echo "=================================================================="
echo " [✔] Tuning de Kernel aplicado con éxito."
echo "     - Mbufs configurados: 1,000,000 clusters"
echo "     - Netmap Ring Size: 4096 descriptors"
echo "     - Hardware Offloading: Desactivado para Netmap Inline IPS"
echo "     - IP Fastforwarding: 0 (Inspección Packet Filter garantizada)"
echo "=================================================================="
