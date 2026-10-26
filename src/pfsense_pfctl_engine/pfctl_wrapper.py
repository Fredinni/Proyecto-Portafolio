#!/usr/bin/env python3
"""
KRONOS SENTINEL - FreeBSD pfctl Wrapper & Kernel Table Controller (Hardened)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
Project: KRONOS SENTINEL - Autonomous AI-IPS & Live Voice Incident Response
"""

import ipaddress
import logging
import shutil
import subprocess
from typing import List, Dict, Any, Set, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [KRONOS-PFCTL] %(message)s'
)


class PfctlWrapper:
    """
    Controlador de tablas de paquetes en memoria kernel de FreeBSD pfctl.
    Permite verificar pertenencia atómica a la tabla 'snort2c', insertar IPs bloqueadas
    y purgar estados de conexión activos bidireccionales ('pfctl -k').
    Soporta ejecución nativa en pfSense, SSH remoto y modo emulación/test para CI/CD.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.table_name = self.config.get("pfctl_table", "snort2c")
        self.use_ssh = self.config.get("use_ssh", False)
        self.ssh_host = self.config.get("pfsense_host", "192.168.1.1")
        self.ssh_user = self.config.get("pfsense_user", "admin")

        # Detección de binario pfctl local; si no existe y no es SSH, opera en modo simulación
        self.has_local_pfctl = shutil.which("pfctl") is not None
        self.simulation_mode = self.config.get(
            "simulation_mode",
            not self.has_local_pfctl and not self.use_ssh
        )

        # Estructura en memoria para auditoría y pruebas
        self._simulated_table: Set[str] = set()
        self._simulated_killed_states: List[str] = []

        if self.simulation_mode:
            logging.info(
                f"Modo simulación pfctl ACTIVO para tabla '{self.table_name}' "
                f"(Entorno: {'Local sin FreeBSD' if not self.has_local_pfctl else 'Configurado'})."
            )

    def _validate_ip(self, ip: str) -> bool:
        """Valida que la cadena sea una dirección IPv4 o IPv6 sintácticamente correcta"""
        if not ip or not isinstance(ip, str):
            return False
        clean_ip = ip.strip()
        try:
            ipaddress.ip_address(clean_ip)
            return True
        except ValueError:
            try:
                ipaddress.ip_network(clean_ip, strict=False)
                return True
            except ValueError:
                return False

    def _exec_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Ejecuta comando en pfSense (local, SSH o simulación) validando retorno"""
        if self.simulation_mode:
            return self._exec_simulated(cmd)

        if self.use_ssh:
            full_cmd = [
                "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3",
                f"{self.ssh_user}@{self.ssh_host}"
            ] + cmd
        else:
            full_cmd = cmd

        try:
            return subprocess.run(full_cmd, capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout ejecutando pfctl: {' '.join(full_cmd)}")
            return subprocess.CompletedProcess(args=full_cmd, returncode=124, stdout="", stderr="Timeout")
        except Exception as e:
            logging.error(f"Excepción al ejecutar pfctl: {e}")
            return subprocess.CompletedProcess(args=full_cmd, returncode=1, stdout="", stderr=str(e))

    def _exec_simulated(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Simulador atómico de llamadas pfctl para desarrollo y testing"""
        # Formato: pfctl -t snort2c -T test <ip>
        if len(cmd) >= 6 and cmd[0] == "pfctl" and cmd[1] == "-t" and cmd[3] == "-T" and cmd[4] == "test":
            target_ip = cmd[5]
            is_present = target_ip in self._simulated_table
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0 if is_present else 1,
                stdout="1/1 matches.\n" if is_present else "0/1 matches.\n",
                stderr=""
            )

        # Formato: pfctl -t snort2c -T add <ip>
        if len(cmd) >= 6 and cmd[0] == "pfctl" and cmd[1] == "-t" and cmd[3] == "-T" and cmd[4] == "add":
            target_ip = cmd[5]
            self._simulated_table.add(target_ip)
            logging.info(f"[SIMULACIÓN KERNEL] IP {target_ip} insertada exitosamente en tabla <{self.table_name}>")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=f"1/1 addresses added to {self.table_name}.\n",
                stderr=""
            )

        # Formato: pfctl -t snort2c -T delete <ip>
        if len(cmd) >= 6 and cmd[0] == "pfctl" and cmd[1] == "-t" and cmd[3] == "-T" and cmd[4] == "delete":
            target_ip = cmd[5]
            self._simulated_table.discard(target_ip)
            logging.info(f"[SIMULACIÓN KERNEL] IP {target_ip} eliminada de tabla <{self.table_name}>")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=f"1/1 addresses deleted from {self.table_name}.\n",
                stderr=""
            )

        # Formato: pfctl -t snort2c -T show
        if len(cmd) >= 5 and cmd[0] == "pfctl" and cmd[1] == "-t" and cmd[3] == "-T" and cmd[4] == "show":
            body = "\n".join(sorted(self._simulated_table)) + ("\n" if self._simulated_table else "")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=body, stderr="")

        # Formato: pfctl -k <ip> (kill states)
        if len(cmd) >= 3 and cmd[0] == "pfctl" and cmd[1] == "-k":
            target = " ".join(cmd[2:])
            self._simulated_killed_states.append(target)
            logging.info(f"[SIMULACIÓN KERNEL] Estados de conexión activos purgados (kill states): {target}")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=f"killed states matching {target}\n",
                stderr=""
            )

        # Formato general de estado
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=f"Simulated pfctl response for table {self.table_name}\n",
            stderr=""
        )

    def is_ip_blocked(self, ip: str) -> bool:
        """
        Consulta en kernel FreeBSD mediante test atómico (pfctl -t snort2c -T test <ip>).
        Código de retorno 0: La IP existe en la tabla.
        Código de retorno 1: La IP no existe en la tabla.
        """
        if not self._validate_ip(ip):
            return False
        res = self._exec_command(["pfctl", "-t", self.table_name, "-T", "test", ip.strip()])
        return res.returncode == 0

    def block_ip(self, ip: str) -> bool:
        """
        Inserta la IP en la tabla snort2c y purga estados activos en ambas direcciones (origen y destino).
        """
        if not self._validate_ip(ip):
            logging.error(f"IP inválida rechazada por pfctl wrapper: '{ip}'")
            return False

        clean_ip = ip.strip()
        logging.warning(f"Aplicando DROP en kernel a IP {clean_ip} en tabla {self.table_name}...")

        # 1. Agregar a tabla snort2c
        add_res = self._exec_command(["pfctl", "-t", self.table_name, "-T", "add", clean_ip])

        # 2. Matar estados bidireccionales en FreeBSD pf
        self._exec_command(["pfctl", "-k", clean_ip])
        self._exec_command(["pfctl", "-k", "0.0.0.0/0", "-k", clean_ip])

        return add_res.returncode == 0

    def unblock_ip(self, ip: str) -> bool:
        """Elimina una IP de la tabla snort2c (para expiración o desbaneo manual)"""
        if not self._validate_ip(ip):
            return False
        clean_ip = ip.strip()
        res = self._exec_command(["pfctl", "-t", self.table_name, "-T", "delete", clean_ip])
        return res.returncode == 0

    def list_blocked_ips(self) -> List[str]:
        """Retorna lista de todas las IPs actualmente registradas en la tabla"""
        res = self._exec_command(["pfctl", "-t", self.table_name, "-T", "show"])
        if res.returncode == 0:
            return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return []

    def get_state_summary(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la tabla de bloqueo en kernel"""
        blocked_list = self.list_blocked_ips()
        return {
            "table_name": self.table_name,
            "total_blocked": len(blocked_list),
            "blocked_ips": blocked_list,
            "simulation_mode": self.simulation_mode,
            "kernel_filter_status": "ACTIVE"
        }
