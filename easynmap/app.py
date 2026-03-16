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


def main():
    show_banner()

    completer = WordCompleter(list(COMMANDS.keys()), sentence=True)
    session = PromptSession(completer=completer, style=PROMPT_STYLE)
    state = {"history": []}

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
            state["history"].append(raw)
            HANDLERS[cmd](args, state)
        else:
            console.print(
                f"[red]  Unknown command:[/red] [bold]{cmd}[/bold]  "
                "— type [bold cyan]/help[/bold cyan] to see available commands"
            )


if __name__ == "__main__":
    main()
