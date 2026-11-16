"""Origin/victim labels must follow evidence rather than inferred public egress."""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
for directory in ("pfsense_pfctl_engine", "ai_voice_agent"):
    sys.path.insert(0, str(ROOT / "src" / directory))

from incident_identity import describe_network_identity
from log_correlator import PfctlLogCorrelator
from prompts import build_live_system_prompt
from soar_tools_executor import SoarToolsExecutor


class IncidentIdentityTests(unittest.TestCase):
    def test_public_actor_and_private_victim_are_distinct_from_proxy(self):
        incident = {"attacker_ip": "93.184.216.34", "target_ip": "192.168.20.50",
                    "observed_source_ip": "192.168.20.1", "source_identity": "ACTOR_IP"}
        result = describe_network_identity(incident)
        self.assertEqual(result["attacker_public_ip"], "93.184.216.34")
        self.assertIsNone(result["attacker_private_ip"])
        self.assertEqual(result["victim_private_ip"], "192.168.20.50")
        self.assertEqual(result["origin_resolution"], "trusted_proxy_xff")
        self.assertEqual(result["observed_source_ip"], "192.168.20.1")

    def test_management_origin_does_not_acquire_a_public_address(self):
        result = describe_network_identity({"attacker_ip": "192.168.99.10", "target_ip": "192.168.20.50",
                                            "attacker_public_ip": "93.184.216.34"})
        self.assertIsNone(result["attacker_public_ip"])
        self.assertEqual(result["attacker_private_ip"], "192.168.99.10")
        self.assertEqual(result["attacker_public_ip_status"], "unavailable_internal_origin")

    def test_unresolved_proxy_is_not_a_public_actor_even_if_its_address_is_public(self):
        result = describe_network_identity({"attacker_ip": "93.184.216.34", "source_identity": "UNRESOLVED_PROXY"})
        self.assertIsNone(result["attacker_public_ip"])
        self.assertEqual(result["origin_resolution"], "unresolved_proxy")

    def test_shared_reserved_and_invalid_addresses_are_not_advertised_as_public(self):
        for address in ("100.73.101.28", "198.18.0.254", "203.0.113.45", "127.0.0.1", None, "invalid"):
            with self.subTest(address=address):
                self.assertIsNone(describe_network_identity({"attacker_ip": address})["attacker_public_ip"])

    def test_ipv6_public_origin_and_ula_victim(self):
        result = describe_network_identity({"attacker_ip": "2606:4700:4700::1111", "target_ip": "fd00::50"})
        self.assertEqual(result["attacker_public_ip"], "2606:4700:4700::1111")
        self.assertEqual(result["victim_private_ip"], "fd00::50")

    def test_pipeline_trusts_xff_only_from_the_configured_proxy(self):
        collector = PfctlLogCorrelator()
        self.addCleanup(collector.executor.shutdown, wait=True)
        collector.pfctl.simulation_mode = True
        collector.config["trusted_proxy_ips"] = ["192.168.20.1"]
        event = {"event_type": "alert", "src_ip": "192.168.20.1", "dest_ip": "192.168.20.50",
                 "alert": {"signature": "SQLi fixture", "action": "blocked", "xff": "93.184.216.34"}}
        identity = collector.process_single_event(event, trigger_dispatch=False)["incident"]
        self.assertEqual(identity["attacker_public_ip"], "93.184.216.34")
        self.assertEqual(identity["victim_private_ip"], "192.168.20.50")
        event["src_ip"] = "10.0.0.25"
        identity = collector.process_single_event(event, trigger_dispatch=False)["incident"]
        self.assertIsNone(identity["attacker_public_ip"])
        self.assertEqual(identity["attacker_private_ip"], "10.0.0.25")

    def test_prompt_and_details_include_derived_labels_for_legacy_context(self):
        incident = {"attacker_ip": "192.168.99.10", "target_ip": "192.168.20.50"}
        prompt = build_live_system_prompt(incident)
        encoded = prompt.split("DATOS DE LA SESIÓN (JSON):\n", 1)[1]
        self.assertIsNone(json.loads(encoded)["attacker_public_ip"])
        self.assertIn("víctima privada", prompt)
        details = SoarToolsExecutor(incident=incident).execute_tool_call("get_incident_details", {})["incident"]
        self.assertEqual(details["victim_private_ip"], "192.168.20.50")
        self.assertEqual(details["attacker_private_ip"], "192.168.99.10")


if __name__ == "__main__":
    unittest.main()
