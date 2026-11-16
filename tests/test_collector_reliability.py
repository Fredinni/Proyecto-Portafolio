"""Regression checks for dropped IPS alerts, EVE rotation and dispatch failures."""

import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pfsense_pfctl_engine"))
from log_correlator import PfctlLogCorrelator


class ScriptedStop:
    """Advance the producer at each reader poll without timing-dependent sleeps."""

    def __init__(self, *actions):
        self.actions = iter(actions)
        self.stopped = False

    def is_set(self):
        return self.stopped

    def wait(self, timeout):
        action = next(self.actions, None)
        if action is None:
            self.stopped = True
        else:
            action()


class CollectorReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.correlator = PfctlLogCorrelator()
        self.addCleanup(self.correlator.executor.shutdown, wait=True)

    def test_rotation_drains_old_file_and_reads_existing_replacement_records(self):
        # Separate physical files also exercise rotation on Windows, where an
        # open file cannot necessarily be renamed by a test process.
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "old.json"
            replacement = Path(directory) / "new.json"
            old.write_bytes(b'{"historical":true}\n')
            replacement.write_bytes(b'{"new":1}\n{"new":2}\n')
            active = [old]
            self.correlator.eve_log_path = "virtual-eve.json"

            def rotate():
                with old.open("ab") as writer:
                    writer.write(b'{"old":1}\n')
                active[0] = replacement

            stop = ScriptedStop(rotate)
            real_stat = __import__("os").stat
            with patch("log_correlator.open", side_effect=lambda *a, **k: active[0].open("rb")), \
                    patch("log_correlator.os.stat", side_effect=lambda p: real_stat(active[0])):
                records = list(self.correlator._follow_eve_lines(stop))
            self.assertEqual([json.loads(line) for line in records], [{"old": 1}, {"new": 1}, {"new": 2}])

    def test_partial_json_and_copytruncate_preserve_next_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "eve.json"
            path.write_bytes(b"historical record longer than replacement\n")
            self.correlator.eve_log_path = str(path)

            def append(data):
                with path.open("ab") as writer:
                    writer.write(data)

            stop = ScriptedStop(lambda: append(b'{"partial":'), lambda: append(b'1}\n'),
                                lambda: path.write_bytes(b'{"truncated":2}\n'))
            records = list(self.correlator._follow_eve_lines(stop))
            self.assertEqual([json.loads(line) for line in records], [{"partial": 1}, {"truncated": 2}])

    def test_processing_failure_does_not_discard_following_events(self):
        self.correlator._follow_eve_lines = Mock(return_value=iter([
            b'{"first":1}\n', b'invalid\n', b'[]\n', b'{"next":2}\n']))
        self.correlator.process_event = Mock(side_effect=[RuntimeError("temporary fault"), None])
        with self.assertLogs(level="ERROR"):
            self.correlator.tail_eve_log()
        self.assertEqual(self.correlator.process_event.call_args_list[-1].args, ({"next": 2},))
        self.assertEqual(self.correlator.process_event.call_count, 2)

    def test_firewall_query_failure_still_schedules_notification_with_unknown_state(self):
        self.correlator.pfctl = Mock(table_name="snort2c")
        self.correlator.pfctl.is_ip_blocked.side_effect = RuntimeError("pfctl unavailable")
        self.correlator.executor.submit = Mock()
        with self.assertLogs(level="ERROR"):
            result = self.correlator.process_single_event({
                "event_type": "alert", "src_ip": "198.18.0.254", "dest_ip": "192.0.2.10",
                "alert": {"signature": "SQLi", "action": "blocked"}})
        self.assertEqual(result["status"], "CONFIRMED_BLOCK_STATUS_UNKNOWN")
        self.assertIsNone(result["incident"]["pfctl_blocked"])
        self.assertIsNone(result["incident"]["http_method"])
        self.correlator.pfctl.block_ip.assert_not_called()
        self.correlator.executor.submit.assert_called_once()

    @staticmethod
    def response():
        response = io.BytesIO(b'{"status":"DISPATCHED","call_initiated":true}')
        response.status = 200
        return response

    def test_protected_management_drop_notifies_without_blocking_management(self):
        self.correlator.config["protected_ips"] = ["192.168.99.10"]
        self.correlator.pfctl.simulation_mode = True
        self.correlator.executor.submit = Mock()
        result = self.correlator.process_single_event({
            "event_type": "alert", "src_ip": "192.168.99.10", "dest_ip": "192.0.2.10",
            "alert": {"signature": "SQLi", "action": "blocked"}})
        self.assertTrue(result["incident"]["sensor_dropped"])
        self.assertTrue(result["incident"]["source_protected"])
        self.assertFalse(result["incident"]["pfctl_blocked"])
        self.assertEqual(result["incident"]["source_identity"], "PROTECTED_INFRASTRUCTURE")
        self.assertEqual(self.correlator.pfctl._simulated_table, set())
        self.correlator.executor.submit.assert_called_once()

    def test_missing_proxy_identity_is_reported_without_blocking_proxy(self):
        self.correlator.config.update({"protected_ips": ["192.0.2.1"], "trusted_proxy_ips": ["192.0.2.1"]})
        self.correlator.pfctl.simulation_mode = True
        result = self.correlator.process_single_event({
            "event_type": "alert", "src_ip": "192.0.2.1",
            "alert": {"signature": "SQLi", "action": "blocked"}}, trigger_dispatch=False)
        self.assertEqual(result["incident"]["source_identity"], "UNRESOLVED_PROXY")
        self.assertEqual(self.correlator.pfctl._simulated_table, set())

    def test_dispatch_retries_network_and_server_errors(self):
        incident = {"attack_type": "SQLi", "attacker_ip": "198.18.0.254", "pfctl_blocked": True}
        error = urllib.error.HTTPError("http://localhost/incident", 503, "Unavailable", {}, None)
        with patch("log_correlator.urllib.request.urlopen", side_effect=[
                urllib.error.URLError("connection reset"), error, self.response()]) as request, \
                patch("log_correlator.time.sleep") as sleep, self.assertLogs():
            self.assertTrue(self.correlator.dispatch_voice_alert(incident))
        self.assertEqual(request.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])

    def test_invalid_auth_is_not_retried_or_reported_as_mitigated(self):
        error = urllib.error.HTTPError("http://localhost/incident", 401, "Unauthorized", {}, None)
        with patch("log_correlator.urllib.request.urlopen", side_effect=error) as request, \
                patch("log_correlator.time.sleep") as sleep, self.assertLogs() as logs:
            self.assertFalse(self.correlator.dispatch_voice_alert({
                "attack_type": "SQLi", "attacker_ip": "198.18.0.254", "pfctl_blocked": None}))
        request.assert_called_once()
        sleep.assert_not_called()
        self.assertIn("bloqueo pfctl=None", " ".join(logs.output))


if __name__ == "__main__":
    unittest.main()
