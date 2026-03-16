import subprocess
from unittest.mock import patch, MagicMock

import pytest

from easynmap.scanner import (
    validate_target,
    needs_root,
    scan_quick, scan_full, scan_service, scan_os, scan_sweep, scan_vuln,
    ScanResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_proc(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode,
                                       stdout=stdout, stderr=stderr)


def _patched_run(fn, target, **kwargs):
    """Run a scan function with subprocess.run mocked."""
    fake = _fake_proc(**kwargs)
    with patch("subprocess.run", return_value=fake):
        return fn(target)


# ---------------------------------------------------------------------------
# validate_target — valid inputs
# ---------------------------------------------------------------------------

class TestValidateTargetValid:
    def test_ipv4(self):
        ok, _ = validate_target("192.168.1.1")
        assert ok

    def test_localhost(self):
        ok, _ = validate_target("127.0.0.1")
        assert ok

    def test_cidr_24(self):
        ok, _ = validate_target("10.0.0.0/24")
        assert ok

    def test_cidr_16(self):
        ok, _ = validate_target("172.16.0.0/16")
        assert ok

    def test_hostname_simple(self):
        ok, _ = validate_target("scanme.nmap.org")
        assert ok

    def test_hostname_single_label(self):
        ok, _ = validate_target("localhost")
        assert ok

    def test_ip_range(self):
        ok, _ = validate_target("192.168.1.1-20")
        assert ok

    def test_class_a(self):
        ok, _ = validate_target("10.0.0.1")
        assert ok


# ---------------------------------------------------------------------------
# validate_target — invalid inputs
# ---------------------------------------------------------------------------

class TestValidateTargetInvalid:
    def test_empty(self):
        ok, reason = validate_target("")
        assert not ok
        assert "empty" in reason.lower()

    def test_whitespace_only(self):
        ok, _ = validate_target("   ")
        assert not ok

    def test_invalid_octet_too_high(self):
        ok, reason = validate_target("999.1.1.1")
        assert not ok
        assert "octet" in reason.lower()

    def test_invalid_octet_256(self):
        ok, _ = validate_target("256.0.0.1")
        assert not ok

    def test_shell_semicolon(self):
        ok, _ = validate_target("127.0.0.1; rm -rf /")
        assert not ok

    def test_shell_ampersand(self):
        ok, _ = validate_target("127.0.0.1 && cat /etc/passwd")
        assert not ok

    def test_backtick_injection(self):
        ok, _ = validate_target("`whoami`")
        assert not ok

    def test_dollar_injection(self):
        ok, _ = validate_target("$(id)")
        assert not ok

    def test_extra_flag_injection(self):
        ok, _ = validate_target("192.168.1.1 --script evil")
        assert not ok

    def test_too_long(self):
        ok, _ = validate_target("a" * 254)
        assert not ok


# ---------------------------------------------------------------------------
# needs_root
# ---------------------------------------------------------------------------

class TestNeedsRoot:
    def test_requires_root(self):
        assert needs_root("You requested a scan type which requires root")

    def test_requires_privileged(self):
        assert needs_root("requires privileged access")

    def test_operation_not_permitted(self):
        assert needs_root("Operation not permitted")

    def test_raw_sockets(self):
        assert needs_root("raw sockets not available")

    def test_tcp_connect(self):
        assert needs_root("TCP connect scan requires root")

    def test_normal_error_false(self):
        assert not needs_root("Host is up")

    def test_not_installed_false(self):
        assert not needs_root("nmap is not installed")

    def test_empty_false(self):
        assert not needs_root("")


# ---------------------------------------------------------------------------
# Scan command construction
# ---------------------------------------------------------------------------

class TestScanCommands:
    def test_quick_command(self):
        r = _patched_run(scan_quick, "127.0.0.1")
        assert r.command == ["nmap", "-T4", "-F", "127.0.0.1"]

    def test_full_command(self):
        r = _patched_run(scan_full, "127.0.0.1")
        assert r.command == ["nmap", "-T4", "-p-", "127.0.0.1"]

    def test_service_command(self):
        r = _patched_run(scan_service, "127.0.0.1")
        assert r.command == ["nmap", "-sV", "127.0.0.1"]

    def test_os_command(self):
        r = _patched_run(scan_os, "127.0.0.1")
        assert r.command == ["nmap", "-O", "127.0.0.1"]

    def test_sweep_command(self):
        r = _patched_run(scan_sweep, "192.168.1.0/24")
        assert r.command == ["nmap", "-sn", "192.168.1.0/24"]

    def test_vuln_command(self):
        r = _patched_run(scan_vuln, "127.0.0.1")
        assert r.command == ["nmap", "--script", "vuln", "127.0.0.1"]


# ---------------------------------------------------------------------------
# ScanResult fields
# ---------------------------------------------------------------------------

class TestScanResult:
    def test_success_has_no_error(self):
        r = _patched_run(scan_quick, "127.0.0.1", stdout="Nmap done", stderr="")
        assert r.return_code == 0
        assert r.error == ""

    def test_failure_captures_error(self):
        r = _patched_run(scan_quick, "127.0.0.1",
                         returncode=1, stdout="", stderr="Permission denied")
        assert r.return_code == 1
        assert "permission denied" in r.error.lower()

    def test_raw_output_combines_stdout_stderr(self):
        r = _patched_run(scan_quick, "127.0.0.1",
                         stdout="stdout text", stderr="stderr text")
        assert "stdout text" in r.raw_output
        assert "stderr text" in r.raw_output

    def test_scan_type_stored(self):
        r = _patched_run(scan_quick, "10.0.0.1")
        assert r.scan_type == "quick"

    def test_target_stored(self):
        r = _patched_run(scan_sweep, "10.0.0.0/24")
        assert r.target == "10.0.0.0/24"

    def test_nmap_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            r = scan_quick("127.0.0.1")
        assert r.return_code == -1
        assert "not installed" in r.error.lower()

    def test_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="nmap", timeout=300)):
            r = scan_quick("127.0.0.1")
        assert r.return_code == -1
        assert "timed out" in r.error.lower()

    def test_keyboard_interrupt(self):
        with patch("subprocess.run", side_effect=KeyboardInterrupt):
            r = scan_quick("127.0.0.1")
        assert r.return_code == -1
        assert "interrupted" in r.error.lower()


# ---------------------------------------------------------------------------
# display — port parser
# ---------------------------------------------------------------------------

class TestPortParser:
    def test_parses_open_port(self):
        from easynmap.display import _parse_ports
        raw = "22/tcp   open  ssh     OpenSSH 8.9p1\n"
        ports = _parse_ports(raw)
        assert len(ports) == 1
        assert ports[0]["port"] == "22"
        assert ports[0]["state"] == "open"
        assert ports[0]["service"] == "ssh"

    def test_parses_closed_port(self):
        from easynmap.display import _parse_ports
        raw = "80/tcp   closed  http\n"
        ports = _parse_ports(raw)
        assert ports[0]["state"] == "closed"

    def test_parses_filtered_port(self):
        from easynmap.display import _parse_ports
        raw = "443/tcp  filtered  https\n"
        ports = _parse_ports(raw)
        assert ports[0]["state"] == "filtered"

    def test_multiple_ports(self):
        from easynmap.display import _parse_ports
        raw = (
            "22/tcp  open   ssh\n"
            "80/tcp  closed http\n"
            "443/tcp open   https  nginx 1.24\n"
        )
        ports = _parse_ports(raw)
        assert len(ports) == 3

    def test_empty_output(self):
        from easynmap.display import _parse_ports
        assert _parse_ports("") == []

    def test_no_ports_in_output(self):
        from easynmap.display import _parse_ports
        raw = "Nmap done: 1 IP address scanned\nHost is up.\n"
        assert _parse_ports(raw) == []


# ---------------------------------------------------------------------------
# display — sweep host parser
# ---------------------------------------------------------------------------

class TestHostParser:
    def test_parses_single_host(self):
        from easynmap.display import _parse_hosts
        raw = "Nmap scan report for 192.168.1.1\n"
        hosts = _parse_hosts(raw)
        assert hosts == ["192.168.1.1"]

    def test_parses_multiple_hosts(self):
        from easynmap.display import _parse_hosts
        raw = (
            "Nmap scan report for 192.168.1.1\n"
            "Nmap scan report for router.local (192.168.1.254)\n"
        )
        hosts = _parse_hosts(raw)
        assert len(hosts) == 2

    def test_empty_output(self):
        from easynmap.display import _parse_hosts
        assert _parse_hosts("") == []


# ---------------------------------------------------------------------------
# output — save functions
# ---------------------------------------------------------------------------

class TestOutput:
    def test_save_scan_txt_creates_file(self, tmp_path, monkeypatch):
        from easynmap import output as outfile
        monkeypatch.setattr(outfile, "OUTPUT_DIR", tmp_path)
        r = ScanResult("quick", "127.0.0.1", ["nmap", "-T4", "-F", "127.0.0.1"],
                       "PORT  STATE SERVICE\n22/tcp open ssh\n", 0)
        path = outfile.save_scan(r, fmt="txt")
        assert path.exists()
        assert path.read_text() == r.raw_output

    def test_save_scan_md_creates_file(self, tmp_path, monkeypatch):
        from easynmap import output as outfile
        monkeypatch.setattr(outfile, "OUTPUT_DIR", tmp_path)
        r = ScanResult("quick", "127.0.0.1", ["nmap", "-T4", "-F", "127.0.0.1"],
                       "22/tcp open ssh\n", 0)
        path = outfile.save_scan(r, fmt="md")
        assert path.exists()
        content = path.read_text()
        assert "# EasyNmap Scan Report" in content
        assert "127.0.0.1" in content

    def test_save_report_creates_md_file(self, tmp_path, monkeypatch):
        from easynmap import output as outfile
        monkeypatch.setattr(outfile, "OUTPUT_DIR", tmp_path)
        path = outfile.save_report("# My Report\n\nAll good.")
        assert path.exists()
        assert path.suffix == ".md"
        assert "My Report" in path.read_text()

    def test_save_scan_filename_includes_scan_type(self, tmp_path, monkeypatch):
        from easynmap import output as outfile
        monkeypatch.setattr(outfile, "OUTPUT_DIR", tmp_path)
        r = ScanResult("service", "10.0.0.1", [], "raw", 0)
        path = outfile.save_scan(r, fmt="txt")
        assert "service" in path.name

    def test_output_dir_created_if_missing(self, tmp_path, monkeypatch):
        from easynmap import output as outfile
        new_dir = tmp_path / "new_results"
        monkeypatch.setattr(outfile, "OUTPUT_DIR", new_dir)
        r = ScanResult("quick", "127.0.0.1", [], "raw", 0)
        outfile.save_scan(r, fmt="txt")
        assert new_dir.exists()
