import pytest
from easynmap.scanner import validate_target, scan_quick, scan_sweep, scan_service, scan_os, scan_full, scan_vuln


# ---------------------------------------------------------------------------
# validate_target
# ---------------------------------------------------------------------------

class TestValidateTarget:
    def test_valid_ipv4(self):
        ok, _ = validate_target("192.168.1.1")
        assert ok

    def test_valid_localhost(self):
        ok, _ = validate_target("127.0.0.1")
        assert ok

    def test_valid_cidr(self):
        ok, _ = validate_target("10.0.0.0/24")
        assert ok

    def test_valid_hostname(self):
        ok, _ = validate_target("scanme.nmap.org")
        assert ok

    def test_valid_ip_range(self):
        ok, _ = validate_target("192.168.1.1-20")
        assert ok

    def test_empty(self):
        ok, reason = validate_target("")
        assert not ok
        assert "empty" in reason.lower()

    def test_invalid_octet(self):
        ok, reason = validate_target("999.1.1.1")
        assert not ok
        assert "octet" in reason.lower()

    def test_shell_injection(self):
        ok, _ = validate_target("127.0.0.1; rm -rf /")
        assert not ok

    def test_backtick_injection(self):
        ok, _ = validate_target("`whoami`")
        assert not ok

    def test_spaces(self):
        ok, _ = validate_target("192.168.1.1 --script evil")
        assert not ok


# ---------------------------------------------------------------------------
# Command construction (check .command list, don't actually run nmap)
# ---------------------------------------------------------------------------

class TestScanCommands:
    """Verify each scan function builds the correct nmap command."""

    def _cmd(self, result) -> list[str]:
        return result.command

    def test_quick_command(self):
        r = scan_quick.__wrapped__("127.0.0.1") if hasattr(scan_quick, "__wrapped__") else None
        # We test via the ScanResult.command field after calling with a mock
        from unittest.mock import patch
        import subprocess
        fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=fake):
            r = scan_quick("127.0.0.1")
        assert r.command == ["nmap", "-T4", "-F", "127.0.0.1"]

    def test_full_command(self):
        from unittest.mock import patch
        import subprocess
        fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=fake):
            r = scan_full("127.0.0.1")
        assert r.command == ["nmap", "-T4", "-p-", "127.0.0.1"]

    def test_service_command(self):
        from unittest.mock import patch
        import subprocess
        fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=fake):
            r = scan_service("127.0.0.1")
        assert r.command == ["nmap", "-sV", "127.0.0.1"]

    def test_os_command(self):
        from unittest.mock import patch
        import subprocess
        fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=fake):
            r = scan_os("127.0.0.1")
        assert r.command == ["nmap", "-O", "127.0.0.1"]

    def test_sweep_command(self):
        from unittest.mock import patch
        import subprocess
        fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=fake):
            r = scan_sweep("192.168.1.0/24")
        assert r.command == ["nmap", "-sn", "192.168.1.0/24"]

    def test_vuln_command(self):
        from unittest.mock import patch
        import subprocess
        fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=fake):
            r = scan_vuln("127.0.0.1")
        assert r.command == ["nmap", "--script", "vuln", "127.0.0.1"]
