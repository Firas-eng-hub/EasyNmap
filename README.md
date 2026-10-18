# easynmap

> Beginner-friendly interactive nmap TUI with AI-powered explanations — built for Kali Linux.

## Live web playground

**[Try EasyNmap online →](https://easynmap-showcase-f8ebc9.vercel.app)**

Explore the project in your browser with an interactive terminal demo, upload or paste Nmap scan output for server-side analysis, browse hosts and ports, and download a Markdown report. The responsive interface works on desktop and mobile.

Demo scans use clearly labeled sample data. Uploaded results receive rule-based service guidance; the web app does not run network scans or require an AI key.

The Next.js application lives in [`web/`](web/). See the [web README](web/README.md) for local development and Vercel deployment instructions.

```
╭──────────────────────────────────────────────────────────────────╮
│  EASYNMAP  v1.0                                                  │
│  Beginner-friendly nmap wrapper                                  │
│  Made by OSCUROO                                                 │
│                                                                  │
│  Type / to see commands  •  /help for details  •  /exit to quit  │
╰──────────────────────────────────────────────────────────────────╯
```

---

## Features

- **`/` autocomplete** — type `/` to see every command in a dropdown
- **6 scan types** — quick, full, service version, OS detection, ping sweep, vuln scripts
- **AI explanations** — paste any scan result to Gemini and get plain-English output
- **Natural language → nmap** — describe a scan in English, get the nmap command
- **AI security reports** — full markdown report from scan results
- **Save output** — raw `.txt` or structured `.md` with port tables
- **Root-aware** — automatically re-runs privileged scans with `sudo`
- **Input validation** — blocks shell injection before anything touches `subprocess`
- **`--no-ai` mode** — works fully offline without an API key

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| nmap | any (pre-installed on Kali) |
| OS | Kali Linux (or any Linux with nmap) |

---

## Installation

### From source (recommended for Kali)

```bash
git clone https://github.com/OSCUROO/easynmap.git
cd easynmap
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

The `easynmap` command is now available in your terminal.

### Install dependencies only

```bash
pip install -r requirements.txt
```

---

## API Key Setup

easynmap uses **GLM 4.5** via [OpenRouter](https://openrouter.ai) for AI features.

1. Go to [https://openrouter.ai](https://openrouter.ai) and create a free account
2. Generate an API key from your dashboard
3. On first launch, easynmap will prompt you to paste the key — it is saved to `~/.easynmap/config` and never stored in the project folder

To skip AI setup entirely, run with `--no-ai`:

```bash
easynmap --no-ai
```

---

## Usage

Launch the tool:

```bash
easynmap
# or with no AI
easynmap --no-ai
```

### All commands

| Command | Description |
|---------|-------------|
| `/scan quick` | Fast scan — top 100 ports (`nmap -T4 -F`) |
| `/scan full` | All 65535 ports (`nmap -T4 -p-`) |
| `/scan service` | Service/version detection (`nmap -sV`) |
| `/scan os` | OS detection — auto sudo (`nmap -O`) |
| `/sweep` | Ping sweep, find live hosts (`nmap -sn`) |
| `/vuln` | Vulnerability scripts (`nmap --script vuln`) |
| `/explain` | AI explains the last scan result |
| `/ask` | Ask AI any nmap/networking question |
| `/ai` | Describe a scan in plain English → runs it |
| `/report` | AI generates a full markdown security report |
| `/save` | Save last scan as `.txt` or `.md` |
| `/files` | List all saved output files |
| `/history` | Show commands used this session |
| `/clear` | Clear the screen |
| `/help` | Show all commands |
| `/exit` | Quit easynmap |

### Examples

```
# Quick scan with auto-save
> /scan quick --output

# Ping sweep a whole subnet
> /sweep
  Network: 192.168.1.0/24

# Ask the AI a question
> /ask what does -sV do?

# Describe a scan in plain English
> /ai scan for open web ports on 10.0.0.5

# Explain the last scan
> /explain

# Generate and save a security report
> /report
```

### Flags

| Flag | Effect |
|------|--------|
| `--output` | Auto-save scan result after completing (append to any scan command) |
| `--no-ai` | Disable all AI commands (works fully offline) |
| `--txt` / `--md` | Choose format when using `/save` |

---

## Output files

All saved files go to `~/easynmap-results/`. Use `/files` to list them.

- `scan_<type>_<target>_<timestamp>.txt` — raw nmap output
- `scan_<type>_<target>_<timestamp>.md` — structured markdown with port table
- `report_<timestamp>.md` — AI-generated security report

---

## Running tests

```bash
source venv/bin/activate
pip install pytest
python -m pytest tests/ -v
```

54 tests covering: input validation, injection prevention, all scan commands, output parsing, file saving, error handling.

---

## ⚠️ Ethical Use Disclaimer

This tool is for **educational purposes and authorized security testing only**.

- Only scan systems you **own** or have **explicit written permission** to test
- Unauthorized network scanning may be **illegal** in your country
- The authors are **not responsible** for misuse of this tool

This disclaimer is displayed every time the tool launches.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).

---

*Made by [OSCUROO](https://github.com/OSCUROO)*
