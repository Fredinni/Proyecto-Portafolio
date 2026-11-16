"""Verified firewall operations, bounded by a per-call voice authorization policy."""

import ipaddress
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pfsense_pfctl_engine"))
from pfctl_wrapper import PfctlWrapper
from voice_policy import VoiceActionPolicy, mentioned_ips

log = logging.getLogger(__name__)


class SoarToolsExecutor:
    def __init__(self, config=None, incident=None, pfctl=None):
        self.config = config or {}
        self.pfctl = pfctl or PfctlWrapper(self.config)
        self.incident = incident or {}
        self.policy = VoiceActionPolicy(self.incident, self.config.get("authorized_extensions", []))

    def observe_input(self, text):
        self.policy.observe_input(text)

    def observe_output(self, text):
        self.policy.observe_output(text)

    def finish_turn(self):
        self.policy.finish_turn()

    def execute_tool_call(self, function_name, arguments):
        if function_name == "get_incident_details":
            fields = ("attacker_ip", "attack_type", "signature", "severity", "timestamp",
                      "target_ip", "target_service", "protocol", "http_endpoint", "http_method",
                      "geoip", "geo_country", "confidence_score", "ast_verified", "action_taken")
            return {"success": True, "incident": {k: self.incident[k] for k in fields if k in self.incident},
                    "note": "La telemetría describe el incidente. Consulta el firewall para conocer el bloqueo actual."}
        if function_name not in {"get_firewall_states", "unblock_ip", "block_ip_permanently"}:
            return {"success": False, "error": "Herramienta no disponible."}
        try:
            ip = str(ipaddress.ip_address(arguments.get("ip", "")))
        except (ValueError, TypeError):
            return {"success": False, "error": "Se requiere una dirección IP individual válida."}
        if function_name == "get_firewall_states":
            result = self.pfctl.get_ip_status(ip)
            if result["success"] and (ip == self.incident.get("attacker_ip") or ip in mentioned_ips(self.policy.input_text)):
                self.policy.focus_ip = ip
            return result

        allowed, reason = self.policy.authorize(function_name, ip)
        if not allowed:
            return {"success": False, "verified": False, "error": reason}
        # No silent simulation in the telephone runtime.
        if self.pfctl.simulation_mode:
            return {"success": False, "verified": False, "error": "El firewall está en simulación; no se ejecutaron cambios reales."}
        operation = self.pfctl.unblock_ip if function_name == "unblock_ip" else self.pfctl.block_ip
        ok = operation(ip)
        state = self.pfctl.get_ip_status(ip)
        expected = function_name == "block_ip_permanently"
        verified = bool(ok and state["success"] and state["is_blocked"] == expected)
        result = {"success": verified, "verified": verified, "ip": ip,
                  "action": function_name, "table": self.pfctl.table_name,
                  "is_blocked": state.get("is_blocked"),
                  "status": "Cambio confirmado en la tabla del firewall." if verified else
                            "No se pudo confirmar el cambio en el firewall; no anuncies éxito."}
        log.info("firewall_action session=%s operator=%s action=%s ip=%s verified=%s",
                 self.incident.get("session_id"), self.incident.get("operator_extension"),
                 function_name, ip, verified)
        return result
