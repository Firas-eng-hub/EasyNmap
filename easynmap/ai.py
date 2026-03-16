from openai import OpenAI, APIError, APIConnectionError, AuthenticationError, RateLimitError

from config.settings import OPENROUTER_BASE_URL, AI_MODEL, load_api_key

# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

_client: OpenAI | None = None


def _get_client() -> OpenAI | None:
    global _client
    if _client is not None:
        return _client
    key = load_api_key()
    if not key:
        return None
    _client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=key,
        default_headers={
            "X-OpenRouter-Title": "easynmap",
        },
    )
    return _client


def _chat(system: str, user: str) -> tuple[str, str]:
    """
    Send a chat request.  Returns (response_text, error_message).
    error_message is '' on success.
    """
    client = _get_client()
    if client is None:
        return "", "No API key configured. Run /ask to be prompted for one."

    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return completion.choices[0].message.content.strip(), ""

    except AuthenticationError:
        return "", "Invalid API key. Check ~/.easynmap/config."
    except RateLimitError:
        return "", "Rate limit hit. Wait a moment and try again."
    except APIConnectionError:
        return "", "Cannot reach OpenRouter. Check your internet connection."
    except APIError as e:
        return "", f"API error: {e}"


# ---------------------------------------------------------------------------
# Public AI functions
# ---------------------------------------------------------------------------

_EXPLAIN_SYSTEM = (
    "You are a friendly cybersecurity tutor helping beginners understand nmap scan results. "
    "Explain the output clearly in plain English. "
    "Describe what each open port means, what services are running, and any security implications. "
    "Keep the explanation concise (under 300 words) and avoid jargon where possible."
)

_ASK_SYSTEM = (
    "You are an expert in nmap and network security. "
    "Answer the user's question clearly and concisely. "
    "If relevant, include a practical nmap command example. "
    "Keep answers under 250 words."
)

_NL_TO_NMAP_SYSTEM = (
    "You are an nmap command generator. "
    "The user will describe a scan in plain English. "
    "Respond with ONLY the nmap command — no explanation, no markdown, no code fences. "
    "Example output: nmap -sV -p 80,443 192.168.1.1"
)

_REPORT_SYSTEM = (
    "You are a professional penetration tester writing a security report. "
    "Given nmap scan results, produce a structured markdown report with these sections:\n"
    "## Summary\n## Open Ports & Services\n## Risk Assessment\n## Recommendations\n"
    "Be concise but thorough. Use markdown formatting."
)


def explain_scan(nmap_output: str) -> tuple[str, str]:
    """Explain nmap output in plain English. Returns (text, error)."""
    return _chat(
        _EXPLAIN_SYSTEM,
        f"Please explain this nmap scan result:\n\n{nmap_output}",
    )


def ask_question(question: str) -> tuple[str, str]:
    """Answer a networking/nmap question. Returns (text, error)."""
    return _chat(_ASK_SYSTEM, question)


def natural_language_to_nmap(description: str) -> tuple[str, str]:
    """
    Convert a plain-English description to an nmap command.
    Returns (command_string, error).
    """
    text, err = _chat(
        _NL_TO_NMAP_SYSTEM,
        f"Generate an nmap command for: {description}",
    )
    if err:
        return "", err
    # Strip any accidental markdown fences the model might add
    cmd = text.strip().strip("`").strip()
    if cmd.startswith("```"):
        cmd = cmd.split("\n", 1)[-1].split("```")[0].strip()
    return cmd, ""


def generate_report(nmap_output: str) -> tuple[str, str]:
    """Generate a full markdown security report. Returns (markdown_text, error)."""
    return _chat(
        _REPORT_SYSTEM,
        f"Generate a security report for this nmap scan:\n\n{nmap_output}",
    )
