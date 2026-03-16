import os
from pathlib import Path

from prompt_toolkit import prompt as pt_prompt
from rich.console import Console

console = Console()

CONFIG_DIR = Path.home() / ".easynmap"
CONFIG_FILE = CONFIG_DIR / "config"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
AI_MODEL = "z-ai/glm-4.5-air:free"


def _read_key_from_file() -> str:
    """Return the stored API key, or '' if not found."""
    if not CONFIG_FILE.exists():
        return ""
    for line in CONFIG_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    return ""


def _save_key(key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(f"OPENROUTER_API_KEY={key}\n")
    CONFIG_FILE.chmod(0o600)


def load_api_key() -> str:
    """
    Return the OpenRouter API key.
    Order: env var → config file → interactive prompt (saved for future use).
    """
    # 1. Environment variable
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key

    # 2. Config file
    key = _read_key_from_file()
    if key:
        return key

    # 3. First-launch interactive prompt
    console.print()
    console.print("[bold yellow]  No OpenRouter API key found.[/bold yellow]")
    console.print("  Get a free key at [cyan]https://openrouter.ai[/cyan]")
    console.print()
    try:
        key = pt_prompt("  Paste your OpenRouter API key: ").strip()
    except (KeyboardInterrupt, EOFError):
        return ""

    if key:
        _save_key(key)
        console.print(f"  [green]Key saved to {CONFIG_FILE}[/green]")

    return key
