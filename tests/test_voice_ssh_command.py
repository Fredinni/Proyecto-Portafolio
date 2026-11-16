import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pfsense_pfctl_engine"))
from voice_ssh_command import validate_command


class ForcedCommandTests(unittest.TestCase):
    def test_table_read_and_individual_mutations(self):
        for command in ("pfctl -t snort2c -T show", "pfctl -t snort2c -T add 198.18.0.254",
                        "pfctl -t snort2c -T delete 198.18.0.254", "pfctl -k 198.18.0.254",
                        "pfctl -k 0.0.0.0/0 -k 198.18.0.254"):
            self.assertEqual(validate_command(command, "snort2c")[0], "/sbin/pfctl")

    def test_shell_flush_other_tables_networks_and_protected_hosts_denied(self):
        for command in ("id", "sh", "pfctl -t snort2c -T flush", "pfctl -d",
                        "pfctl -t bogons -T show", "pfctl -t snort2c -T delete 0.0.0.0/0",
                        "pfctl -t snort2c -T delete 1.1.1.1; reboot",
                        "pfctl -k 127.0.0.1", "pfctl -k 192.168.99.1"):
            with self.subTest(command=command), self.assertRaises(ValueError):
                validate_command(command, "snort2c", ["192.168.99.1"])
