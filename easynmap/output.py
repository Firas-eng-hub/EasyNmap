"""
Handles all file saving for easynmap.
Output directory: ~/easynmap-results/
"""

from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

from easynmap.scanner import ScanResult

console = Console()

OUTPUT_DIR = Path.home() / "easynmap-results"


def _ensure_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------------------
# Save scan output
# ---------------------------------------------------------------------------

def save_scan(result: ScanResult, fmt: str = "txt") -> Path:
    """
    Save raw scan output to ~/easynmap-results/.
    fmt: 'txt' or 'md'
    Returns the saved path.
    """
    out_dir = _ensure_dir()
    ts = _timestamp()
    ext = "md" if fmt == "md" else "txt"
    filename = f"scan_{result.scan_type}_{result.target.replace('/', '_')}_{ts}.{ext}"
    path = out_dir / filename

    if fmt == "md":
        content = _scan_to_markdown(result)
    else:
        content = result.raw_output

    path.write_text(content, encoding="utf-8")
    return path


def _scan_to_markdown(result: ScanResult) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cmd = " ".join(result.command)
    lines = [
        f"# EasyNmap Scan Report",
        f"",
        f"| Field   | Value |",
        f"|---------|-------|",
        f"| Target  | `{result.target}` |",
        f"| Type    | {result.scan_type} |",
        f"| Command | `{cmd}` |",
        f"| Date    | {ts} |",
        f"",
        f"## Raw Output",
        f"",
        f"```",
        result.raw_output.strip(),
        f"```",
    ]

    if result.ports:
        lines += [
            f"",
            f"## Open Ports",
            f"",
            f"| Port | Proto | State | Service | Version |",
            f"|------|-------|-------|---------|---------|",
        ]
        for p in result.ports:
            lines.append(
                f"| {p['port']} | {p['proto']} | {p['state']} | {p['service']} | {p['version']} |"
            )

    if result.hosts:
        lines += [
            f"",
            f"## Live Hosts",
            f"",
        ]
        for h in result.hosts:
            lines.append(f"- {h}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Save AI report
# ---------------------------------------------------------------------------

def save_report(markdown_text: str) -> Path:
    """Save an AI-generated markdown report. Returns the saved path."""
    out_dir = _ensure_dir()
    path = out_dir / f"report_{_timestamp()}.md"
    path.write_text(markdown_text, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# List saved files
# ---------------------------------------------------------------------------

def list_saved_files() -> None:
    """Print a table of all files in ~/easynmap-results/."""
    out_dir = _ensure_dir()
    files = sorted(out_dir.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)

    if not files:
        console.print(f"[dim]  No saved files yet. Output directory: {out_dir}[/dim]")
        return

    table = Table(
        title=f"[bold cyan]Saved files — {out_dir}[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("#",        justify="right", style="dim", min_width=3)
    table.add_column("Filename", style="bold")
    table.add_column("Size",     justify="right", style="dim")
    table.add_column("Modified", style="dim")

    for i, f in enumerate(files, 1):
        stat = f.stat()
        size = f"{stat.st_size:,} B"
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        table.add_row(str(i), f.name, size, mtime)

    console.print()
    console.print(table)
    console.print()
