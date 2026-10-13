"""Exercise acceptance against measured fixtures, without a pfSense mutation."""
import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import patch

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "verify_kernel_hardening.py"
SPEC = importlib.util.spec_from_file_location("a1_audit", SOURCE)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class SupportedProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = pathlib.Path(self.temp.name) / "config.xml"
        self.config.write_text("""<pfsense><system>
          <disablechecksumoffloading/><disablesegmentationoffloading/>
          <disablelargereceiveoffloading/></system>
          <interfaces><wan><if>vtnet0</if></wan></interfaces></pfsense>""")
        self.values = {key: str(spec.get("expected", spec.get("minimum")))
                       for key, spec in audit.CURRENT_SYSCTLS.items()}
        self.values["net.pf.states_hashsize"] = "262144"
        self.values["dev.netmap.ring_size"] = "36864"
        self.version = "2.9.0-RELEASE"
        self.options = "options=800800<VLAN_MTU,LINKSTATE>\ncapabilities=ffff<RXCSUM,TXCSUM,TSO4,LRO>"
        self.errors = {}

    def command(self, args):
        if args[0] == "sysctl":
            if args[-1] in self.errors:
                return self.errors[args[-1]]
            if args[-1] not in self.values:
                return {"returncode": 1, "stdout": "", "stderr": "unknown oid"}
            value = self.values[args[-1]]
        elif args[0] == "/bin/cat":
            value = self.version
        elif args[0] == "ifconfig":
            value = self.options
        elif args[0] == "/bin/test":
            value = ""
        else:
            raise AssertionError(args)
        return {"returncode": 0, "stdout": value, "stderr": ""}

    def report(self, profile="current", system="FreeBSD", release="16.0-CURRENT"):
        with patch.object(audit.platform, "system", return_value=system), \
                patch.object(audit.platform, "release", return_value=release), \
                patch.object(audit, "run_cmd", side_effect=self.command):
            return audit.audit_kernel(str(self.config), ["vtnet0", "vtnet1"], profile=profile)

    def test_current_requires_real_supported_values_and_separates_retired_oids(self):
        report = self.report()
        self.assertEqual(report["estado_general"], "PASS")
        self.assertEqual(report["summary"], {"PASS": 14, "FAIL": 0, "UNSUPPORTED": 0})
        self.assertEqual(len(report["legacy_diagnostics"]), 3)
        self.assertTrue(all(not d["acceptance_requirement"] for d in report["legacy_diagnostics"]))
        self.assertEqual(report["netmap_diagnostics"][0]["unit"], "bytes")

    def test_legacy_keeps_historical_partial(self):
        report = self.report("legacy")
        self.assertEqual(report["summary"], {"PASS": 9, "FAIL": 0, "UNSUPPORTED": 3})
        self.assertEqual(report["exit_code"], 2)

    def test_missing_mandatory_oid_fails_current(self):
        del self.values["dev.netmap.buf_curr_size"]
        self.assertEqual(self.report()["estado_general"], "FAIL")

    def test_current_buffer_mismatch_fails(self):
        self.values["dev.netmap.buf_curr_size"] = "4096"
        self.assertEqual(self.report()["estado_general"], "FAIL")

    def test_current_ring_zero_fails(self):
        self.values["dev.netmap.ring_curr_size"] = "0"
        self.assertEqual(self.report()["estado_general"], "FAIL")

    def test_disabled_forwarding_fails(self):
        self.values["net.inet.ip.forwarding"] = "0"
        self.assertEqual(self.report()["estado_general"], "FAIL")

    def test_noninteger_value_fails(self):
        self.values["kern.ipc.nmbclusters"] = "not an integer"
        self.assertEqual(self.report()["estado_general"], "FAIL")

    def test_permission_error_is_not_unsupported(self):
        self.errors["net.pf.states_hashsize"] = {"returncode": 1, "stdout": "", "stderr": "Permission denied"}
        self.assertEqual(self.report()["summary"]["FAIL"], 1)

    def test_current_rejects_wrong_os_freebsd_release_and_pfsense_version(self):
        for system, release, version in [("Windows", "10", "2.9.0"),
                                         ("FreeBSD", "14.0", "2.9.0"),
                                         ("FreeBSD", "16.0", "2.8.1")]:
            with self.subTest(system=system, release=release, version=version):
                self.version = version
                self.assertEqual(self.report(system=system, release=release)["estado_general"], "FAIL")

    def test_capabilities_do_not_mean_enabled_offloads(self):
        self.assertEqual(self.report()["estado_general"], "PASS")
        self.options = "options=ffff<RXCSUM,TXCSUM,TSO4,LRO>"
        self.assertEqual(self.report()["summary"]["FAIL"], 2)

    def test_invalid_or_missing_enabled_options_fail(self):
        self.options = "capabilities=ffff<RXCSUM>"
        self.assertEqual(self.report()["summary"]["FAIL"], 2)

    def test_config_missing_flags_fails(self):
        self.config.write_text("<pfsense><system/><interfaces><wan><if>vtnet0</if></wan></interfaces></pfsense>")
        self.assertEqual(self.report()["summary"]["FAIL"], 3)

    def test_invalid_xml_fails(self):
        self.config.write_text("<broken>")
        self.assertGreater(self.report()["summary"]["FAIL"], 0)

    def test_current_cannot_silently_require_legacy(self):
        with self.assertRaises(ValueError):
            audit.audit_kernel(profile="current", require_legacy=True)


if __name__ == "__main__":
    unittest.main()
