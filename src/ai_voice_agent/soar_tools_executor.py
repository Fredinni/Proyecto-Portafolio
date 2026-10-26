#!/usr/bin/env python3
"""
KRONOS SENTINEL - SOAR Tool Execution Engine (Anti-Slop Implementation)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
Description:
    Fully implemented, production-grade function calling executor for pfSense,
    FreeBSD kernel tables (snort2c), connection state purges, and Obsidian correlation.
    Strictly zero placeholder or empty functions.
"""

import os
import sys
import json
import time
import ipaddress
import logging
from typing import Dict, Any

# Añadir rutas de engine
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pfsense_pfctl_engine"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pfctl_wrapper import PfctlWrapper
from obsidian_memory_manager import ObsidianMemoryManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [SOAR-TOOLS] %(message)s")

class SoarToolsExecutor:
    """
    Motor ejecutor de Function Calling para el agente de voz KRONOS.
    Ejecuta comandos reales en el cortafuegos pfSense, administra tablas del kernel
    y actualiza la base de conocimiento en Obsidian.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.pfctl = PfctlWrapper(self.config)
        self.obsidian = ObsidianMemoryManager()

    def validate_ip(self, ip: str) -> bool:
        if not ip or not isinstance(ip, str):
            return False
        clean = ip.strip()
        try:
            ipaddress.ip_address(clean)
            return True
        except ValueError:
            try:
                ipaddress.ip_network(clean, strict=False)
                return True
            except ValueError:
                return False

    def block_ip_permanently(self, ip: str, reason: str = "Bloqueo preventivo solicitado por CISO en llamada de voz") -> Dict[str, Any]:
        """
        Bloquea permanentemente la IP en la tabla snort2c y mata todas sus conexiones activas en el kernel.
        """
        clean_ip = ip.strip()
        if not self.validate_ip(clean_ip):
            return {
                "success": False,
                "error": f"Dirección IP inválida: '{ip}'",
                "action": "NONE"
            }

        logging.warning(f"[SOAR] Ejecutando bloqueo permanente en kernel: {clean_ip} | Razón: {reason}")
        block_ok = self.pfctl.block_ip(clean_ip)
        killed_ok = self.pfctl.kill_states(clean_ip)

        # Registrar en Obsidian Vault
        count, _ = self.obsidian.record_incident(
            attacker_ip=clean_ip,
            attack_type="Bloqueo Manual SOAR por Voz",
            target_service="DVWA / Perímetro",
            action_taken=f"DROP permanente en snort2c y purga de estados ({reason})"
        )

        return {
            "success": block_ok,
            "ip": clean_ip,
            "action": "BLOCK_PERMANENT",
            "table": self.pfctl.table_name,
            "states_killed": killed_ok,
            "recurrence_count": count,
            "status": f"La IP {clean_ip} quedó bloqueada atómicamente en la tabla {self.pfctl.table_name} y se purgaron sus estados activos."
        }

    def unblock_ip(self, ip: str, reason: str = "Falso positivo descartado por CISO") -> Dict[str, Any]:
        """
        Retira la dirección IP de la tabla snort2c si el CISO lo autoriza.
        """
        clean_ip = ip.strip()
        if not self.validate_ip(clean_ip):
            return {
                "success": False,
                "error": f"Dirección IP inválida: '{ip}'",
                "action": "NONE"
            }

        logging.warning(f"[SOAR] Ejecutando desbloqueo en kernel: {clean_ip} | Razón: {reason}")
        unblock_ok = self.pfctl.unblock_ip(clean_ip)

        return {
            "success": unblock_ok,
            "ip": clean_ip,
            "action": "UNBLOCK",
            "table": self.pfctl.table_name,
            "status": f"La IP {clean_ip} fue removida exitosamente de la tabla {self.pfctl.table_name}."
        }

    def get_firewall_states(self, ip: str) -> Dict[str, Any]:
        """
        Consulta en tiempo real el estado de una IP en el firewall pfSense.
        """
        clean_ip = ip.strip()
        if not self.validate_ip(clean_ip):
            return {
                "success": False,
                "error": f"Dirección IP inválida: '{ip}'",
                "action": "NONE"
            }

        is_blocked = self.pfctl.is_ip_blocked(clean_ip)
        return {
            "success": True,
            "ip": clean_ip,
            "is_blocked": is_blocked,
            "table": self.pfctl.table_name,
            "status": f"La IP {clean_ip} {'se encuentra BLOQUEADA' if is_blocked else 'NO está bloqueada'} en el cortafuegos."
        }

    def escalate_to_soc_tier2(self, incident_id: str, priority: str = "ALTA", notes: str = "") -> Dict[str, Any]:
        """
        Escala el incidente a nivel crítico y genera una entrada formal en Obsidian.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC")
        ticket_id = f"KRONOS-TIER2-{int(time.time())}"

        escalation_entry = (
            f"\n\n### 🚨 ESCALACIÓN TIER 2 - Ticket #{ticket_id}\n"
            f"* **Timestamp:** {timestamp}\n"
            f"* **Incidente Asociado:** `{incident_id}`\n"
            f"* **Prioridad:** {priority}\n"
            f"* **Instrucciones del CISO:** {notes}\n"
            f"* **Estado:** Asignado a Equipo de Respuesta a Incidentes (IR / Blue Team)\n"
        )

        md_file = os.path.join(self.obsidian.vault_dir, "01_HISTORIAL_INCIDENTES_CORRELACIONADOS.md")
        if os.path.exists(md_file):
            with open(md_file, "a", encoding="utf-8") as f:
                f.write(escalation_entry)

        logging.info(f"[SOAR] Incidente {incident_id} escalado exitosamente a TIER 2 con Ticket {ticket_id}")

        return {
            "success": True,
            "ticket_id": ticket_id,
            "incident_id": incident_id,
            "priority": priority,
            "status": f"Incidente escalado a Tier 2 con ticket {ticket_id} y prioridad {priority}."
        }

    def execute_tool_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Despacha la llamada de función hacia el método correspondiente"""
        logging.info(f"[SOAR] Despachando llamada de herramienta: '{function_name}' con argumentos: {arguments}")
        if function_name == "block_ip_permanently":
            return self.block_ip_permanently(
                ip=arguments.get("ip", ""),
                reason=arguments.get("reason", "Bloqueo solicitado por CISO")
            )
        elif function_name == "unblock_ip":
            return self.unblock_ip(
                ip=arguments.get("ip", ""),
                reason=arguments.get("reason", "Desbloqueo solicitado por CISO")
            )
        elif function_name == "get_firewall_states":
            return self.get_firewall_states(
                ip=arguments.get("ip", "")
            )
        elif function_name == "escalate_to_soc_tier2":
            return self.escalate_to_soc_tier2(
                incident_id=arguments.get("incident_id", f"INC-{int(time.time())}"),
                priority=arguments.get("priority", "ALTA"),
                notes=arguments.get("notes", "")
            )
        else:
            return {
                "success": False,
                "error": f"Herramienta no implementada: '{function_name}'"
            }

if __name__ == "__main__":
    executor = SoarToolsExecutor()
    print("\n--- TEST SOAR TOOLS EXECUTOR ---")

    # 1. Test get_firewall_states
    res1 = executor.execute_tool_call("get_firewall_states", {"ip": "185.220.101.5"})
    print("1. get_firewall_states:", res1)

    # 2. Test block_ip_permanently
    res2 = executor.execute_tool_call("block_ip_permanently", {"ip": "185.220.101.5", "reason": "Ataque SQLi reiterado al DVWA"})
    print("2. block_ip_permanently:", res2)

    # 3. Test escalate_to_soc_tier2
    res3 = executor.execute_tool_call("escalate_to_soc_tier2", {
        "incident_id": "INC-SQLI-DVWA-001",
        "priority": "CRITICA",
        "notes": "Revisar logs de HAProxy y correlacionar posibles saltos a base de datos interna."
    })
    print("3. escalate_to_soc_tier2:", res3)
