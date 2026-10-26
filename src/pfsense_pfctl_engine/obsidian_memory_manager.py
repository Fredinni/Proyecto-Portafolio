#!/usr/bin/env python3
"""
KRONOS SENTINEL - Obsidian Vault & Incident Memory Manager
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
Description:
    Manages persistent incident correlation and updates the Obsidian markdown vault.
    Tracks recurrence counts per attacker IP and generates prompt context for Gemini Live.
"""

import os
import json
import time
from typing import Dict, Any, Tuple

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "obsidian_vault"))
MEMORY_JSON = os.path.join(VAULT_DIR, "incident_memory.json")
LOG_MD = os.path.join(VAULT_DIR, "01_HISTORIAL_INCIDENTES_CORRELACIONADOS.md")

class ObsidianMemoryManager:
    def __init__(self, vault_dir: str = VAULT_DIR):
        self.vault_dir = vault_dir
        self.memory_file = os.path.join(vault_dir, "incident_memory.json")
        self.md_file = os.path.join(vault_dir, "01_HISTORIAL_INCIDENTES_CORRELACIONADOS.md")
        os.makedirs(self.vault_dir, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    def load_memory(self) -> Dict[str, Any]:
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _format_tautologies(self, tautologies: list) -> list:
        res = []
        if not tautologies:
            return res
        for t in tautologies:
            if isinstance(t, dict):
                res.append(t.get("expression", str(t)))
            else:
                res.append(str(t))
        return res

    def record_incident(self, attacker_ip: str, attack_type: str, target_service: str = "DVWA en DMZ",
                        tautologies: list = None, action_taken: str = "DROP en snort2c & State Kill") -> Tuple[int, Dict[str, Any]]:
        """
        Registra o actualiza el incidente en la memoria persistente.
        Retorna (recurrence_count, incident_record).
        """
        memory = self.load_memory()
        now_utc = time.strftime("%Y-%m-%d %H:%M:%S")
        iso_now = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        formatted_tauts = self._format_tautologies(tautologies)

        if attacker_ip not in memory:
            memory[attacker_ip] = {
                "count": 1,
                "first_seen": iso_now,
                "last_seen": iso_now,
                "attack_types": [attack_type],
                "target_services": [target_service],
                "tautologies": formatted_tauts,
                "actions": [action_taken],
                "notes": f"Primer ataque registrado desde {attacker_ip}."
            }
            count = 1
        else:
            memory[attacker_ip]["count"] += 1
            count = memory[attacker_ip]["count"]
            memory[attacker_ip]["last_seen"] = iso_now
            if attack_type not in memory[attacker_ip]["attack_types"]:
                memory[attacker_ip]["attack_types"].append(attack_type)
            if target_service not in memory[attacker_ip]["target_services"]:
                memory[attacker_ip]["target_services"].append(target_service)
            if formatted_tauts:
                for t in formatted_tauts:
                    if t not in memory[attacker_ip]["tautologies"]:
                        memory[attacker_ip]["tautologies"].append(t)
            memory[attacker_ip]["notes"] = f"Ataque reincidente detectado #{count}."

        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

        # Actualizar Markdown en Obsidian Vault
        self._update_markdown_vault(attacker_ip, attack_type, target_service, formatted_tauts, action_taken, count, now_utc)

        return count, memory[attacker_ip]

    def _update_markdown_vault(self, attacker_ip: str, attack_type: str, target_service: str,
                               tautologies: list, action_taken: str, count: int, timestamp: str):
        """Añade o actualiza la entrada en el markdown de Obsidian"""
        taut_str = ", ".join(self._format_tautologies(tautologies)) if tautologies else "N/A"
        reincidencia_badge = f"**x{count}**" if count == 1 else f"⚠️ **x{count} (REINCIDENTE)**"

        new_row = f"| {count} | {timestamp} | `{attacker_ip}` | {attack_type} | `{taut_str}` | {action_taken} | {reincidencia_badge} | En curso |\n"

        if os.path.exists(self.md_file):
            with open(self.md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Insertar en la tabla si existe
            if "| # | Timestamp (UTC) |" in content:
                table_split = content.split("## 2. Detalle de Incidentes Registrados")
                header_table = table_split[0]
                tail = "## 2. Detalle de Incidentes Registrados" + table_split[1] if len(table_split) > 1 else ""

                # Añadir fila a la tabla
                updated_content = header_table.rstrip() + "\n" + new_row + "\n" + tail
            else:
                updated_content = content + "\n\n" + new_row

            # Añadir sección de detalle del incidente al final
            detail_section = (
                f"\n### Caso #{count:03d} - Reincidencia {reincidencia_badge}: {attack_type}\n"
                f"* **Timestamp:** {timestamp} UTC\n"
                f"* **IP Atacante:** `{attacker_ip}`\n"
                f"* **Objetivo:** {target_service}\n"
                f"* **Tautologías AST:** `{taut_str}`\n"
                f"* **Acción de Mitigación:** {action_taken}\n"
                f"* **Frecuencia:** Este origen ha intentado atacar {count} veces.\n"
                f"* **Correlación:** [[00_PERSONALIDAD_IA_KRONOS]], [[02_TOPOLOGIA_Y_REGLAS_PFSENSE]]\n"
            )
            updated_content += detail_section

            with open(self.md_file, "w", encoding="utf-8") as f:
                f.write(updated_content)

    def get_prompt_guidelines(self, attacker_ip: str, attack_type: str, target_service: str = "DVWA en DMZ") -> Dict[str, str]:
        """Genera directivas para el prompt de Gemini basadas en la reincidencia de la IP"""
        memory = self.load_memory()
        rec = memory.get(attacker_ip, {})
        count = rec.get("count", 1)

        if count >= 2:
            alert_guidance = (
                f"IMPORTANTE: Esta IP {attacker_ip} es REINCIDENTE (ya van {count} ataques detectados). "
                f"DEBES mencionarlo expresamente: '¡Aló Bruno! Oye, este compadre de la {attacker_ip} ya van {count} veces que nos tira {attack_type}, revísalo. "
                "El pfSense ya le chantó DROP en snort2c y mató los estados. ¿Lo dejamos bloqueado nomás?'"
            )
        else:
            alert_guidance = (
                f"Saluda con '¿Aló, Bruno? Oye...' y dile que frenaste un {attack_type} desde la IP {attacker_ip} hacia {target_service}. "
                "El pfSense ya le chantó DROP en snort2c y mató los estados. Pregúntale si lo dejamos bloqueado nomás."
            )

        return {
            "count": count,
            "guidance": alert_guidance
        }

if __name__ == "__main__":
    mgr = ObsidianMemoryManager()
    count, rec = mgr.record_incident(
        attacker_ip="185.220.101.5",
        attack_type="Inyección SQL Crítica",
        target_service="DVWA en DMZ",
        tautologies=["'1'='1"],
        action_taken="DROP en snort2c & State Kill"
    )
    print(f"[*] Incidente registrado en Obsidian: Conteo={count}")
    guidelines = mgr.get_prompt_guidelines("185.220.101.5", "Inyección SQL Crítica")
    print(f"[*] Directiva para Gemini:\n{guidelines['guidance']}")
