from rich.console import Console

console = Console()

COMMANDS = {
    "/scan":    "Run a network scan",
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


def handle_scan(_args, _state):
    console.print("[yellow]  /scan — coming in Phase 3[/yellow]")


def handle_sweep(_args, _state):
    console.print("[yellow]  /sweep — coming in Phase 3[/yellow]")


def handle_vuln(_args, _state):
    console.print("[yellow]  /vuln — coming in Phase 3[/yellow]")


def handle_ask(_args, _state):
    console.print("[yellow]  /ask — coming in Phase 4[/yellow]")


def handle_explain(_args, _state):
    console.print("[yellow]  /explain — coming in Phase 4[/yellow]")


def handle_ai(_args, _state):
    console.print("[yellow]  /ai — coming in Phase 4[/yellow]")


def handle_report(_args, _state):
    console.print("[yellow]  /report — coming in Phase 4[/yellow]")


def handle_save(_args, _state):
    console.print("[yellow]  /save — coming in Phase 5[/yellow]")


def handle_history(_args, state):
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
