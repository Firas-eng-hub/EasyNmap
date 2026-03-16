import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel

from easynmap.commands import COMMANDS, HANDLERS

console = Console()

PROMPT_STYLE = Style.from_dict({
    "prompt": "bold cyan",
})

_DISCLAIMER = (
    "[bold yellow]  ETHICAL USE NOTICE[/bold yellow]\n"
    "  Only scan systems you [bold]own[/bold] or have [bold]explicit written permission[/bold] to test.\n"
    "  Unauthorized network scanning may be [bold red]illegal[/bold red] in your country.\n"
    "  The authors are not responsible for misuse of this tool."
)


def show_banner():
    console.print(Panel(
        "[bold cyan]EASYNMAP  v1.0[/bold cyan]\n"
        "[dim]Beginner-friendly nmap wrapper[/dim]\n"
        "Type [bold cyan]/[/bold cyan] to see commands  •  "
        "[bold cyan]/help[/bold cyan] for details  •  "
        "[bold cyan]/exit[/bold cyan] to quit",
        border_style="cyan",
        expand=False,
        padding=(0, 2),
    ))
    console.print()


def show_disclaimer():
    console.print(Panel(_DISCLAIMER, border_style="yellow", expand=False, padding=(0, 1)))
    console.print()


def _check_nmap():
    """Warn immediately if nmap is not on PATH."""
    import shutil
    if not shutil.which("nmap"):
        console.print(Panel(
            "[bold red]  nmap is not installed![/bold red]\n"
            "  Install it with:  [bold]sudo apt install nmap[/bold]\n"
            "  AI commands (/ask, /explain, /ai, /report) will still work.",
            border_style="red",
            expand=False,
            padding=(0, 1),
        ))
        console.print()


def main():
    no_ai = "--no-ai" in sys.argv

    show_banner()
    show_disclaimer()
    _check_nmap()

    if no_ai:
        console.print("[dim]  Running in --no-ai mode. AI commands are disabled.[/dim]\n")

    completer = WordCompleter(list(COMMANDS.keys()), sentence=True)
    session = PromptSession(completer=completer, style=PROMPT_STYLE)
    state = {"history": [], "no_ai": no_ai}

    while True:
        try:
            raw = session.prompt([("class:prompt", " > ")]).strip()
        except KeyboardInterrupt:
            console.print("\n[dim]  (Ctrl+C — type /exit to quit)[/dim]")
            continue
        except EOFError:
            console.print("\n[dim]  Goodbye.[/dim]")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "/exit":
            console.print("[dim]  Goodbye.[/dim]")
            break

        if cmd in HANDLERS:
            # Block AI commands in --no-ai mode
            if no_ai and cmd in ("/ask", "/explain", "/ai", "/report"):
                console.print(
                    "[yellow]  AI commands are disabled (--no-ai mode).[/yellow]\n"
                    "  Restart without --no-ai to enable them."
                )
                continue
            state["history"].append(raw)
            HANDLERS[cmd](args, state)
        else:
            console.print(
                f"[red]  Unknown command:[/red] [bold]{cmd}[/bold]  "
                "— type [bold cyan]/help[/bold cyan] to see available commands"
            )


if __name__ == "__main__":
    main()
