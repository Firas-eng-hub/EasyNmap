import re
import subprocess
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Target validation
# ---------------------------------------------------------------------------

_IPV4_RE = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}$"
)
_CIDR_RE = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$"
)
_HOSTNAME_RE = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
)
_RANGE_RE = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$"
)


def validate_target(target: str) -> tuple[bool, str]:
    """Return (True, '') if target looks safe, else (False, reason)."""
    t = target.strip()
    if not t:
        return False, "Target cannot be empty."
    if len(t) > 253:
        return False, "Target is too long."
    if (
        _IPV4_RE.match(t)
        or _CIDR_RE.match(t)
        or _RANGE_RE.match(t)
        or _HOSTNAME_RE.match(t)
    ):
        # Extra sanity check for each IPv4 octet
        if _IPV4_RE.match(t) or _CIDR_RE.match(t) or _RANGE_RE.match(t):
            octets = re.findall(r"\d+", t.split("/")[0].split("-")[0])
            if any(int(o) > 255 for o in octets[:4]):
                return False, "Invalid IP address (octet out of range)."
        return True, ""
    return False, f"'{t}' does not look like a valid IP, CIDR range, or hostname."


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ScanResult:
    scan_type: str
    target: str
    command: list[str]
    raw_output: str
    return_code: int
    error: str = ""
    ports: list[dict] = field(default_factory=list)   # parsed port rows
    hosts: list[str] = field(default_factory=list)    # parsed live hosts (sweep)


# ---------------------------------------------------------------------------
# Internal runner
# ---------------------------------------------------------------------------

def _run(cmd: list[str], scan_type: str, target: str) -> ScanResult:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        result = ScanResult(
            scan_type=scan_type,
            target=target,
            command=cmd,
            raw_output=proc.stdout + proc.stderr,
            return_code=proc.returncode,
        )
        if proc.returncode != 0:
            result.error = proc.stderr.strip() or "nmap exited with a non-zero status."
        return result
    except FileNotFoundError:
        return ScanResult(
            scan_type=scan_type, target=target, command=cmd,
            raw_output="", return_code=-1,
            error="nmap is not installed. Install it with: sudo apt install nmap",
        )
    except subprocess.TimeoutExpired:
        return ScanResult(
            scan_type=scan_type, target=target, command=cmd,
            raw_output="", return_code=-1,
            error="Scan timed out after 5 minutes.",
        )


# ---------------------------------------------------------------------------
# Scan functions
# ---------------------------------------------------------------------------

def scan_quick(target: str) -> ScanResult:
    """nmap -T4 -F <target>  — fast scan, top 100 ports."""
    return _run(["nmap", "-T4", "-F", target], "quick", target)


def scan_full(target: str) -> ScanResult:
    """nmap -T4 -p- <target>  — all 65535 ports."""
    return _run(["nmap", "-T4", "-p-", target], "full", target)


def scan_service(target: str) -> ScanResult:
    """nmap -sV <target>  — service/version detection."""
    return _run(["nmap", "-sV", target], "service", target)


def scan_os(target: str) -> ScanResult:
    """nmap -O <target>  — OS detection (requires root)."""
    return _run(["nmap", "-O", target], "os", target)


def scan_sweep(network: str) -> ScanResult:
    """nmap -sn <network>  — ping sweep, find live hosts."""
    return _run(["nmap", "-sn", network], "sweep", network)


def scan_vuln(target: str) -> ScanResult:
    """nmap --script vuln <target>  — vulnerability scripts."""
    return _run(["nmap", "--script", "vuln", target], "vuln", target)
