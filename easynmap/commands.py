from prompt_toolkit import prompt as pt_prompt
from rich.console import Console
from rich.markdown import Markdown

from easynmap import scanner, ai
from easynmap.display import print_ports_table, print_sweep_table, print_raw
from easynmap import output as outfile

console = Console()

COMMANDS = {
    "/scan":    "Run a network scan  (subcommands: quick | full | service | os)",
    "/sweep":   "Discover live hosts on a network",
    "/vuln":    "Run vulnerability detection scripts",
    "/ask":     "Ask AI a networking/nmap question",
    "/explain": "Explain the last scan result",
    "/ai":      "Translate plain English into an nmap command",
    "/report":  "Generate an AI security report",
    "/save":    "Save last scan output  (--txt | --md)",
    "/files":   "List all saved output files",
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


def _validate_and_run(scan_fn, target: str, state: dict, auto_save: bool = False):
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

    if auto_save:
        path = outfile.save_scan(result, fmt="txt")
        console.print(f"  [green]Output saved:[/green] {path}")


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
    auto_save = "--output" in args
    args = [a for a in args if a != "--output"]
    sub = args[0].lower() if args else ""

    if sub not in SCAN_SUBCOMMANDS:
        console.print()
        console.print("  [bold cyan]/scan[/bold cyan] subcommands:")
        for name, desc in SCAN_SUBCOMMANDS.items():
            console.print(f"    [cyan]{name:<10}[/cyan] {desc}")
        console.print(f"  [dim]Append --output to save result automatically, e.g. /scan quick --output[/dim]")
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
    _validate_and_run(scan_fns[sub], target, state, auto_save=auto_save)


# ---------------------------------------------------------------------------
# /sweep
# ---------------------------------------------------------------------------

def handle_sweep(args: list[str], state: dict):
    auto_save = "--output" in args
    target = _ask_target("  Network (e.g. 192.168.1.0/24): ")
    if target is None:
        return
    _validate_and_run(scanner.scan_sweep, target, state, auto_save=auto_save)


# ---------------------------------------------------------------------------
# /vuln
# ---------------------------------------------------------------------------

def handle_vuln(args: list[str], state: dict):
    auto_save = "--output" in args
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
    _validate_and_run(scanner.scan_vuln, target, state, auto_save=auto_save)


# ---------------------------------------------------------------------------
# /ask
# ---------------------------------------------------------------------------

def handle_ask(args: list[str], _state):
    question = " ".join(args).strip()
    if not question:
        try:
            question = pt_prompt("  Your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]  Cancelled.[/dim]")
            return
    if not question:
        return

    with console.status("[cyan]  Asking AI…[/cyan]", spinner="dots"):
        text, err = ai.ask_question(question)

    if err:
        console.print(f"[red]  AI error:[/red] {err}")
        return

    console.print()
    console.print(Markdown(text))
    console.print()


# ---------------------------------------------------------------------------
# /explain
# ---------------------------------------------------------------------------

def handle_explain(_args, state: dict):
    result = state.get("last_result")
    if result is None:
        console.print("[yellow]  No scan result to explain yet. Run a scan first.[/yellow]")
        return

    with console.status("[cyan]  Asking AI to explain scan…[/cyan]", spinner="dots"):
        text, err = ai.explain_scan(result.raw_output)

    if err:
        console.print(f"[red]  AI error:[/red] {err}")
        return

    console.print()
    console.print(Markdown(text))
    console.print()


# ---------------------------------------------------------------------------
# /ai  (natural language → nmap)
# ---------------------------------------------------------------------------

def handle_ai(args: list[str], state: dict):
    description = " ".join(args).strip()
    if not description:
        try:
            description = pt_prompt("  Describe the scan you want: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]  Cancelled.[/dim]")
            return
    if not description:
        return

    with console.status("[cyan]  Generating nmap command…[/cyan]", spinner="dots"):
        cmd_str, err = ai.natural_language_to_nmap(description)

    if err:
        console.print(f"[red]  AI error:[/red] {err}")
        return

    console.print()
    console.print(f"  [bold cyan]Generated command:[/bold cyan] [bold]{cmd_str}[/bold]")
    console.print()

    # Validate it starts with nmap
    if not cmd_str.lower().startswith("nmap"):
        console.print("[yellow]  AI returned an unexpected response. Not running it.[/yellow]")
        return

    try:
        confirm = pt_prompt("  Run this command? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]  Cancelled.[/dim]")
        return

    if confirm != "y":
        console.print("[dim]  Cancelled.[/dim]")
        return

    # Parse args from the AI-generated command and extract target (last token)
    parts = cmd_str.split()
    if len(parts) < 2:
        console.print("[red]  Command too short to run safely.[/red]")
        return

    target = parts[-1]
    ok, reason = scanner.validate_target(target)
    if not ok:
        console.print(f"[red]  Generated target '{target}' failed validation:[/red] {reason}")
        return

    import subprocess
    with console.status("[cyan]  Scanning…[/cyan]", spinner="dots"):
        proc = subprocess.run(parts, capture_output=True, text=True, timeout=300)

    from easynmap.scanner import ScanResult
    result = ScanResult(
        scan_type="ai",
        target=target,
        command=parts,
        raw_output=proc.stdout + proc.stderr,
        return_code=proc.returncode,
    )
    state["last_result"] = result
    print_raw(result)


# ---------------------------------------------------------------------------
# /report
# ---------------------------------------------------------------------------

def handle_report(_args, state: dict):
    result = state.get("last_result")
    if result is None:
        console.print("[yellow]  No scan result available. Run a scan first.[/yellow]")
        return

    with console.status("[cyan]  Generating security report…[/cyan]", spinner="dots"):
        text, err = ai.generate_report(result.raw_output)

    if err:
        console.print(f"[red]  AI error:[/red] {err}")
        return

    console.print()
    console.print(Markdown(text))
    console.print()

    # Offer to save
    try:
        save = pt_prompt("  Save report to file? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return

    if save == "y":
        path = outfile.save_report(text)
        console.print(f"  [green]Saved:[/green] {path}")


# ---------------------------------------------------------------------------
# /save
# ---------------------------------------------------------------------------

def handle_save(args: list[str], state: dict):
    result = state.get("last_result")
    if result is None:
        console.print("[yellow]  No scan result to save. Run a scan first.[/yellow]")
        return

    # Determine format
    fmt = "txt"
    if "--md" in args or "--markdown" in args:
        fmt = "md"
    elif "--txt" in args:
        fmt = "txt"
    else:
        # Interactive choice
        console.print("  Format: [cyan]txt[/cyan] (raw output) or [cyan]md[/cyan] (markdown with table)")
        try:
            choice = pt_prompt("  Save as [txt/md] (default txt): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]  Cancelled.[/dim]")
            return
        if choice in ("md", "markdown"):
            fmt = "md"

    path = outfile.save_scan(result, fmt=fmt)
    console.print(f"  [green]Saved:[/green] {path}")


# ---------------------------------------------------------------------------
# /files  — list saved output
# ---------------------------------------------------------------------------

def handle_files(_args, _state):
    outfile.list_saved_files()


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
    "/files":   handle_files,
    "/history": handle_history,
    "/clear":   handle_clear,
    "/help":    handle_help,
}
