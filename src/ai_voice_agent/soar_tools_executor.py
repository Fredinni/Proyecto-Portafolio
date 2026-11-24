"""Verified firewall operations, bounded by a per-call voice authorization policy."""

import ipaddress
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pfsense_pfctl_engine"))
from pfctl_wrapper import PfctlWrapper
from incident_identity import describe_network_identity
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

    def interrupt_output(self):
        self.policy.interrupt_output()

    def execute_tool_call(self, function_name, arguments):
        if function_name == "get_incident_details":
            fields = ("attacker_ip", "attack_type", "signature", "severity", "timestamp",
                      "target_ip", "target_service", "protocol", "http_endpoint", "http_method",
                      "geoip", "geo_country", "confidence_score", "ast_verified", "action_taken")
            fields += ("classification_source", "sensor_action", "signature_id", "category")
            fields += ("sensor_dropped", "source_protected", "observed_source_ip", "source_identity", "pfctl_blocked")
            details = {k: self.incident[k] for k in fields if k in self.incident}
            details.update(describe_network_identity(self.incident))
            source = "CALL_CONTEXT"
            identity = self.incident.get("incident_id")
            if identity:
                evidence = self.pfctl.get_incident_identity(identity)
                row = evidence.get("incident", {})
                if evidence.get("success") and row.get("attacker_ip") == self.incident.get("attacker_ip") and row.get("target_ip") == self.incident.get("target_ip"):
                    details.update(row)
                    source = "PFSENSE_EVE"
            return {"success": True, "source": source, "identity_query_verified": source == "PFSENSE_EVE", "incident": details,
                    "note": "La telemetría describe el incidente. Consulta el firewall para conocer el bloqueo actual."}
        if function_name == "list_blocked_ips":
            if self.pfctl.simulation_mode:
                return {"success": False, "verified": False, "error": "El firewall está en simulación; no se consultó la tabla real."}
            result = self.pfctl.list_blocked_ips_status()
            if result.get("success"):
                protected = set(self.config.get("protected_ips", []))
                candidates = [entry for entry in result.get("blocked_ips", []) if entry not in protected]
                self.policy.record_offered_ips(candidates)
            return result
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

        if (ip in self.config.get("protected_ips", []) or
                (self.incident.get("source_protected") and ip == self.incident.get("attacker_ip"))):
            return {"success": False, "verified": False, "firewall_touched": False,
                    "error": "Origen de infraestructura protegido. El IPS descarta el payload, pero no se modifica su bloqueo global. Para QA usa un origen separado por la URL publica."}
        allowed, reason = self.policy.authorize(function_name, ip)
        if not allowed:
            log.info("firewall_authorization_denied session=%s operator=%s action=%s ip=%s reason=%s",
                     self.incident.get("session_id"), self.incident.get("operator_extension"),
                     function_name, ip, reason)
            return {"success": False, "verified": False, "firewall_touched": False, "error": reason}
        # No silent simulation in the telephone runtime.
        if self.pfctl.simulation_mode:
            return {"success": False, "verified": False, "firewall_touched": False,
                    "error": "El firewall está en simulación; no se ejecutaron cambios reales."}
        operation = self.pfctl.unblock_ip if function_name == "unblock_ip" else self.pfctl.block_ip
        ok = operation(ip)
        state = self.pfctl.get_ip_status(ip)
        expected = function_name == "block_ip_permanently"
        verified = bool(ok and state["success"] and state["is_blocked"] == expected)
        result = {"success": verified, "verified": verified, "firewall_touched": True, "ip": ip,
                  "action": function_name, "table": self.pfctl.table_name,
                  "is_blocked": state.get("is_blocked"),
                  "status": "Cambio confirmado en la tabla del firewall." if verified else
                            "No se pudo confirmar el cambio en el firewall; no anuncies éxito."}
        if verified and function_name == "unblock_ip":
            result["ips_remains_active"] = True
            result["test_guidance"] = ("Comprueba el acceso con una solicitud normal. Un nuevo SQLi o ataque "
                                       "puede volver a bloquear la IP; no se ha creado una excepción al IPS.")
        log.info("firewall_action session=%s operator=%s action=%s ip=%s verified=%s",
                 self.incident.get("session_id"), self.incident.get("operator_extension"),
                 function_name, ip, verified)
        return result
