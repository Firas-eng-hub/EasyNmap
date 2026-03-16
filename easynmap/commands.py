from prompt_toolkit import prompt as pt_prompt
from rich.console import Console

from easynmap import scanner
from easynmap.display import print_ports_table, print_sweep_table, print_raw

console = Console()

COMMANDS = {
    "/scan":    "Run a network scan  (subcommands: quick | full | service | os)",
    "/sweep":   "Discover live hosts on a network",
    "/vuln":    "Run vulnerability detection scripts",
    "/ask":     "Ask AI a networking/nmap question",
    "/explain": "Explain the last scan result",
    "/ai":      "Translate plain English into an nmap command",
    "/report":  "Generate an AI security report",
    "/save":    "Save last scan output to a file",
    "/history": "Show commands used this session",
    "/clear":   "Clear the screen",
    "/help":    "Show all commands",
    "/exit":    "Quit easynmap",
}

SCAN_SUBCOMMANDS = {
    "quick":   "Fast scan — top 100 ports  (nmap -T4 -F)",
    "full":    "Full scan — all 65535 ports  (nmap -T4 -p-)",
    "service": "Service/version detection  (nmap -sV)",
    "os":      "OS detection — requires root  (nmap -O)",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ask_target(prompt_text: str = "  Target IP / hostname / CIDR: ") -> str | None:
    """Prompt for a target; return None if user cancels."""
    try:
        return pt_prompt(prompt_text).strip()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]  Cancelled.[/dim]")
        return None


def _validate_and_run(scan_fn, target: str, state: dict):
    ok, reason = scanner.validate_target(target)
    if not ok:
        console.print(f"[red]  Invalid target:[/red] {reason}")
        return

    with console.status("[cyan]  Scanning…[/cyan]", spinner="dots"):
        result = scan_fn(target)

    if result.error:
        _handle_error(result)
        return

    state["last_result"] = result

    if result.scan_type == "sweep":
        print_sweep_table(result)
    elif result.scan_type == "vuln":
        print_raw(result)
    else:
        print_ports_table(result)


def _handle_error(result):
    console.print(f"[red]  Scan failed:[/red] {result.error}")
    if result.return_code == 1 and (
        "requires root" in result.error.lower()
        or "tcp connect" in result.error.lower()
        or "you requested a scan type" in result.error.lower()
    ):
        console.print("[yellow]  Tip: OS detection (-O) requires root. Try running easynmap with sudo.[/yellow]")


# ---------------------------------------------------------------------------
# /scan
# ---------------------------------------------------------------------------

def handle_scan(args: list[str], state: dict):
    sub = args[0].lower() if args else ""

    if sub not in SCAN_SUBCOMMANDS:
        console.print()
        console.print("  [bold cyan]/scan[/bold cyan] subcommands:")
        for name, desc in SCAN_SUBCOMMANDS.items():
            console.print(f"    [cyan]{name:<10}[/cyan] {desc}")
        console.print()
        try:
            sub = pt_prompt("  Choose scan type: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]  Cancelled.[/dim]")
            return
        if sub not in SCAN_SUBCOMMANDS:
            console.print(f"[red]  Unknown scan type:[/red] {sub}")
            return

    target = _ask_target()
    if target is None:
        return

    scan_fns = {
        "quick":   scanner.scan_quick,
        "full":    scanner.scan_full,
        "service": scanner.scan_service,
        "os":      scanner.scan_os,
    }
    _validate_and_run(scan_fns[sub], target, state)


# ---------------------------------------------------------------------------
# /sweep
# ---------------------------------------------------------------------------

def handle_sweep(_args, state: dict):
    target = _ask_target("  Network (e.g. 192.168.1.0/24): ")
    if target is None:
        return
    _validate_and_run(scanner.scan_sweep, target, state)


# ---------------------------------------------------------------------------
# /vuln
# ---------------------------------------------------------------------------

def handle_vuln(_args, state: dict):
    target = _ask_target()
    if target is None:
        return
    console.print("[yellow]  Warning: vuln scripts can be intrusive. Only scan systems you own or have permission to test.[/yellow]")
    try:
        confirm = pt_prompt("  Continue? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]  Cancelled.[/dim]")
        return
    if confirm != "y":
        console.print("[dim]  Cancelled.[/dim]")
        return
    _validate_and_run(scanner.scan_vuln, target, state)


# ---------------------------------------------------------------------------
# Phase 4 stubs
# ---------------------------------------------------------------------------

def handle_ask(_args, _state):
    console.print("[yellow]  /ask — coming in Phase 4[/yellow]")


def handle_explain(_args, _state):
    console.print("[yellow]  /explain — coming in Phase 4[/yellow]")


def handle_ai(_args, _state):
    console.print("[yellow]  /ai — coming in Phase 4[/yellow]")


def handle_report(_args, _state):
    console.print("[yellow]  /report — coming in Phase 4[/yellow]")


# ---------------------------------------------------------------------------
# Phase 5 stub
# ---------------------------------------------------------------------------

def handle_save(_args, _state):
    console.print("[yellow]  /save — coming in Phase 5[/yellow]")


# ---------------------------------------------------------------------------
# Utility commands
# ---------------------------------------------------------------------------

def handle_history(_args, state: dict):
    history = state.get("history", [])
    if not history:
        console.print("[dim]  No commands used yet.[/dim]")
        return
    for i, cmd in enumerate(history, 1):
        console.print(f"  [dim]{i}.[/dim] {cmd}")


def handle_clear(_args, _state):
    console.clear()


def handle_help(_args, _state):
    console.print()
    for cmd, desc in COMMANDS.items():
        console.print(f"  [bold cyan]{cmd:<12}[/bold cyan] {desc}")
    console.print()


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

HANDLERS = {
    "/scan":    handle_scan,
    "/sweep":   handle_sweep,
    "/vuln":    handle_vuln,
    "/ask":     handle_ask,
    "/explain": handle_explain,
    "/ai":      handle_ai,
    "/report":  handle_report,
    "/save":    handle_save,
    "/history": handle_history,
    "/clear":   handle_clear,
    "/help":    handle_help,
}
