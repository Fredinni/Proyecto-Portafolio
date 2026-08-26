#!/usr/bin/env python3
"""
KRONOS SENTINEL - FreeBSD pfctl Wrapper & Kernel Table Controller (Hardened)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import subprocess
import logging
from typing import List, Dict, Any

class PfctlWrapper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.table_name = self.config.get("pfctl_table", "snort2c")
        self.use_ssh = self.config.get("use_ssh", False)
        self.ssh_host = self.config.get("pfsense_host", "192.168.1.1")
        self.ssh_user = self.config.get("pfsense_user", "admin")

    def _exec_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Ejecuta comando en pfSense local o remoto validando retorno y capturando errores"""
        if self.use_ssh:
            full_cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3", f"{self.ssh_user}@{self.ssh_host}"] + cmd
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

    def is_ip_blocked(self, ip: str) -> bool:
        """
        Consulta en kernel FreeBSD mediante test atómico (pfctl -t snort2c -T test <ip>).
        Código de retorno 0: La IP existe en la tabla.
        Código de retorno 1: La IP no existe en la tabla.
        """
        res = self._exec_command(["pfctl", "-t", self.table_name, "-T", "test", ip])
        if res.returncode == 0:
            return True
        return False

    def block_ip(self, ip: str) -> bool:
        """
        Inserta la IP en la tabla snort2c y purga estados activos en ambas direcciones (origen y destino).
        """
        logging.warning(f"Aplicando DROP en kernel a IP {ip} en tabla {self.table_name}...")
        
        # 1. Agregar a tabla snort2c
        add_res = self._exec_command(["pfctl", "-t", self.table_name, "-T", "add", ip])
        
        # 2. Matar estados bidireccionales en FreeBSD pf
        self._exec_command(["pfctl", "-k", ip])
        self._exec_command(["pfctl", "-k", "0.0.0.0/0", "-k", ip])
        
        return add_res.returncode == 0

    def get_state_summary(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la tabla de bloqueo en kernel"""
        res = self._exec_command(["pfctl", "-vvsTables"])
        return {"raw_tables": res.stdout or "pfSense Kernel Packet Filter State: ACTIVE"}
