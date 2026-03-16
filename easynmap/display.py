import re

from rich.console import Console
from rich.table import Table
from rich import box

from easynmap.scanner import ScanResult

console = Console()

# Regex to parse a port line like:
#   22/tcp   open   ssh     OpenSSH 8.9p1
_PORT_RE = re.compile(
    r"^(\d+)/(tcp|udp)\s+(\S+)\s+(\S+)(?:\s+(.+))?$"
)

# Regex for sweep host lines like:
#   Nmap scan report for 192.168.1.1
_HOST_RE = re.compile(
    r"^Nmap scan report for (.+)$"
)


def _parse_ports(raw: str) -> list[dict]:
    ports = []
    for line in raw.splitlines():
        m = _PORT_RE.match(line.strip())
        if m:
            ports.append({
                "port":    m.group(1),
                "proto":   m.group(2),
                "state":   m.group(3),
                "service": m.group(4),
                "version": (m.group(5) or "").strip(),
            })
    return ports


def _parse_hosts(raw: str) -> list[str]:
    return [m.group(1) for line in raw.splitlines() if (m := _HOST_RE.match(line.strip()))]


def _state_color(state: str) -> str:
    s = state.lower()
    if s == "open":
        return "green"
    if s in ("closed", "reset"):
        return "red"
    return "yellow"   # filtered / open|filtered


def print_ports_table(result: ScanResult) -> None:
    ports = _parse_ports(result.raw_output)
    result.ports = ports

    if not ports:
        console.print("[yellow]  No port information found in output.[/yellow]")
        _print_raw_fallback(result.raw_output)
        return

    table = Table(
        title=f"[bold cyan]{result.scan_type.upper()} scan — {result.target}[/bold cyan]",
        box=box.ROUNDED,
        show_lines=False,
        header_style="bold cyan",
    )
    table.add_column("Port",    style="bold", justify="right", min_width=7)
    table.add_column("Proto",   justify="center", min_width=5)
    table.add_column("State",   justify="center", min_width=10)
    table.add_column("Service", min_width=10)
    table.add_column("Version")

    for p in ports:
        color = _state_color(p["state"])
        table.add_row(
            p["port"],
            p["proto"],
            f"[{color}]{p['state']}[/{color}]",
            p["service"],
            p["version"],
        )

    console.print()
    console.print(table)
    console.print(f"  [dim]{len(ports)} port(s) found.[/dim]")
    console.print()


def print_sweep_table(result: ScanResult) -> None:
    hosts = _parse_hosts(result.raw_output)
    result.hosts = hosts

    if not hosts:
        console.print("[yellow]  No live hosts found.[/yellow]")
        return

    table = Table(
        title=f"[bold cyan]SWEEP — {result.target}[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("#",    justify="right", style="dim", min_width=3)
    table.add_column("Host / IP", style="bold green")

    for i, host in enumerate(hosts, 1):
        table.add_row(str(i), host)

    console.print()
    console.print(table)
    console.print(f"  [dim]{len(hosts)} host(s) up.[/dim]")
    console.print()


def print_raw(result: ScanResult) -> None:
    """Fallback: dump raw nmap output with a header."""
    console.print()
    console.rule(f"[bold cyan]{result.scan_type.upper()} — {result.target}[/bold cyan]")
    console.print(result.raw_output)
    console.rule()
    console.print()


def _print_raw_fallback(raw: str) -> None:
    console.print("[dim]  Raw output:[/dim]")
    console.print(raw)
