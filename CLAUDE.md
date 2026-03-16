# EasyNmap — Complete Project Roadmap
> A beginner-friendly interactive nmap TUI with AI-powered explanations via Gemini Flash (OpenRouter)

---

## 🗺️ Project Overview

| Item | Detail |
|---|---|
| **Tool Name** | `easynmap` |
| **Platform** | Kali Linux |
| **Language** | Python 3 |
| **Core Libraries** | `prompt_toolkit`, `rich`, `subprocess`, `httpx` |
| **AI** | Gemini Flash via OpenRouter API |
| **Distribution** | GitHub + `pip install` |

---

## Phase 0 — Environment Setup
> Goal: Get your Kali machine ready before writing any code.

### Tasks
- [ ] Verify Python 3 is installed: `python3 --version`
- [ ] Install pip if missing: `sudo apt install python3-pip`
- [ ] Install virtualenv: `pip install virtualenv`
- [ ] Create project folder: `mkdir easynmap && cd easynmap`
- [ ] Create virtual environment: `python3 -m venv venv`
- [ ] Activate it: `source venv/bin/activate`
- [ ] Verify nmap is installed: `nmap --version` (pre-installed on Kali)
- [ ] Create a GitHub account if you don't have one
- [ ] Initialize git repo: `git init`
- [ ] Create `.gitignore` with entries: `venv/`, `__pycache__/`, `.env`, `*.pyc`

### Outcome
A clean, isolated Python environment ready for development.

---

## Phase 1 — Project Skeleton
> Goal: Set up the file structure and make the project installable before any features.

### File Structure to Create
```
easynmap/
│
├── easynmap/
│   ├── __init__.py
│   ├── app.py
│   ├── commands.py
│   ├── scanner.py
│   ├── ai.py
│   └── display.py
│
├── config/
│   └── settings.py
│
├── tests/
│   └── test_scanner.py
│
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE
```

### Tasks
- [ ] Create all folders and empty files above
- [ ] Write `requirements.txt` with initial dependencies:
  ```
  prompt_toolkit
  rich
  httpx
  ```
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Write `setup.py` with entry point so `easynmap` becomes a terminal command
- [ ] Add MIT License file (copy from choosealicense.com)
- [ ] Create a bare-bones `README.md` with just the project name and description
- [ ] Do first git commit: `git add . && git commit -m "phase 1: project skeleton"`

### Concept to Understand
`setup.py` tells Python: *"when someone types `easynmap` in the terminal, run the `main()` function inside `app.py`."* This is called an **entry point**.

### Outcome
A structured, installable (but empty) project. Running `pip install .` works without errors.

---

## Phase 2 — Interactive TUI Shell
> Goal: Build the interactive terminal interface with `/` autocomplete. No nmap yet — just the shell.

### What to Build
The app opens, shows a welcome banner, and gives the user an input prompt. Typing `/` shows a dropdown of available commands.

```
╔══════════════════════════════════════════╗
║           EASYNMAP  v1.0                 ║
║   Beginner-friendly nmap wrapper         ║
║   Type / to see commands                 ║
╚══════════════════════════════════════════╝

> /
  /scan      Run a network scan
  /sweep     Discover live hosts
  /vuln      Vulnerability scan
  /ask       Ask AI a question
  /explain   Explain last result
  /report    Generate AI report
  /clear     Clear the screen
  /help      Show all commands
  /exit      Quit easynmap
```

### Tasks
- [ ] Learn how `prompt_toolkit.PromptSession` works (read its docs/examples)
- [ ] Learn how `prompt_toolkit.completion.WordCompleter` works for autocomplete
- [ ] Build the main loop in `app.py`:
  - Show welcome banner using `rich`
  - Start a `PromptSession` with a `WordCompleter` of all `/commands`
  - Loop: read input → identify command → call handler → loop again
- [ ] Build command stubs in `commands.py` (functions that just print "coming soon")
- [ ] Handle unknown input gracefully (show "unknown command, type /help")
- [ ] Handle `Ctrl+C` and `Ctrl+D` to exit cleanly
- [ ] Use `rich` to style the banner with color and borders
- [ ] Test: run `python3 -m easynmap.app`, type `/`, confirm dropdown appears
- [ ] Git commit: `git commit -m "phase 2: interactive TUI shell"`

### Concepts to Understand
- **PromptSession**: The main object that manages the interactive input loop
- **WordCompleter**: Listens for `/` and shows matching command suggestions
- **Event loop**: Your app runs in a `while True` loop — each iteration is one command

### Outcome
A working interactive shell. No scanning yet, but the UI feels like a real app.

---

## Phase 3 — Nmap Integration
> Goal: Connect real nmap commands behind each `/` command.

### Scan Types to Implement

| Command | Nmap Command Built | Description |
|---|---|---|
| `/scan quick` | `nmap -T4 -F <target>` | Fast scan of top 100 ports |
| `/scan full` | `nmap -T4 -p- <target>` | All 65535 ports |
| `/scan service` | `nmap -sV <target>` | Detect service versions |
| `/scan os` | `nmap -O <target>` | Detect operating system |
| `/sweep` | `nmap -sn <network>` | Ping sweep, find live hosts |
| `/vuln` | `nmap --script vuln <target>` | Run vuln detection scripts |

### Tasks
- [ ] Learn how `subprocess.run()` works with `capture_output=True`
- [ ] Build `scanner.py`:
  - One function per scan type
  - Each function takes a `target` string, builds the command list, runs it, returns output
  - Add a `validate_target()` function to check if the IP/hostname looks valid before scanning
- [ ] Update `commands.py` to:
  - Ask the user for a target IP after they type a scan command
  - Call the right `scanner.py` function
  - Show a "scanning..." spinner using `rich.console.Console.status()`
- [ ] Build `display.py`:
  - Parse nmap raw output and show it in a `rich.table.Table`
  - Highlight open ports in green, closed in red, filtered in yellow
- [ ] Test every scan type against `127.0.0.1` (localhost) or a local VM
- [ ] Git commit: `git commit -m "phase 3: nmap integration"`

### Concepts to Understand
- **subprocess**: Python runs `nmap ...` as a child process, captures its text output, and gives it back to you as a string
- **Input validation**: Always check the target looks like a real IP or hostname before passing it to nmap. Never pass raw unvalidated user input to a system command.

### Outcome
A fully working nmap wrapper. Users open the app, type `/scan`, enter a target, and see a clean colorful result table.

---

## Phase 4 — AI Integration (GLM via OpenRouter)
> Goal: Add AI-powered features using the OpenRouter API.

### AI Features to Build

| Command | What AI Does |
|---|---|
| `/explain` | Explains the last scan result in plain English |
| `/ask <question>` | Answers any nmap/networking question |
| `/ai <plain English>` | Translates natural language into an nmap command and runs it |
| `/report` | Generates a full human-readable security report from scan results |

### Tasks

#### 4a — API Key Setup
- [ ] On first launch, detect if API key exists in `~/.easynmap/config`
- [ ] If not, prompt the user to enter their OpenRouter API key
- [ ] Save it securely to `~/.easynmap/config` (never in the project folder)
- [ ] Load key at startup in `settings.py`

#### 4b — Build `ai.py`
- [ ] Write a base `ask_gemini(prompt)` function that:
  - Sends a POST request to `https://openrouter.ai/api/v1/chat/completions`
  - Uses model `google/gemini-flash-1.5`
  - Returns the text response
- [ ] Write `explain_scan(nmap_output)` — passes scan output, gets plain English explanation
- [ ] Write `natural_language_to_nmap(user_input)` — returns an nmap command string
- [ ] Write `generate_report(all_scan_results)` — returns a full markdown report
- [ ] Handle API errors gracefully (no key, rate limit, network error)

#### 4c — Connect AI to Commands
- [ ] Store the last scan result in memory (app session state)
- [ ] `/explain` calls `explain_scan()` with the stored result
- [ ] `/ask` calls `ask_gemini()` with the user's question
- [ ] `/ai` calls `natural_language_to_nmap()`, shows the generated command, asks user to confirm, then runs it
- [ ] `/report` calls `generate_report()` and offers to save as `.md` or `.txt`
- [ ] Show a spinner while waiting for AI response

- [ ] Git commit: `git commit -m "phase 4: AI integration"`

### Concepts to Understand
- **OpenRouter**: A single API that gives you access to many AI models (Gemini, GPT, etc.) using one API key and one endpoint format
- **Prompt engineering**: The quality of your AI feature depends on *how* you write the prompt you send to Gemini. Be specific — tell it what format to respond in.
- **Session state**: Store the last scan result in a Python variable (e.g., `app_state["last_result"]`) so `/explain` always has something to work with

### Outcome
The tool now has a built-in AI assistant. Beginners can ask questions, get explanations, and even describe scans in plain English.

---

## Phase 5 — Output & Reporting
> Goal: Let users save their results.

### Tasks
- [ ] Add `/save` command — saves last scan output as `.txt`
- [ ] Add `--output` option to scan commands — saves result immediately after scanning
- [ ] Save AI-generated reports as `.md` files with timestamp in filename
- [ ] Create output folder automatically at `~/easynmap-results/` if it doesn't exist
- [ ] Show the saved file path after saving
- [ ] Git commit: `git commit -m "phase 5: output and reporting"`

### Outcome
Users can keep records of their scans and AI-generated reports.

---

## Phase 6 — Error Handling & Polish
> Goal: Make the tool robust, safe, and pleasant to use.

### Tasks
- [ ] Handle: nmap not installed → show install instructions
- [ ] Handle: scan requires root (`-O`, `-sS`) → auto re-run with `sudo` or show a clear message
- [ ] Handle: invalid IP entered → show error, ask again
- [ ] Handle: no internet (AI calls fail) → graceful message, tool still works without AI
- [ ] Handle: user presses Ctrl+C mid-scan → stop cleanly, don't crash
- [ ] Add `/history` command — show commands used in this session
- [ ] Add a `--no-ai` flag for users who don't want to set up an API key
- [ ] Review all output for readability — test with someone who has never used nmap
- [ ] Git commit: `git commit -m "phase 6: error handling and polish"`

### Outcome
The tool never crashes unexpectedly and always gives the user a clear next step.

---

## Phase 7 — Testing
> Goal: Verify everything works correctly before publishing.

### Tasks
- [ ] Write tests in `tests/test_scanner.py`:
  - Test that each scan type builds the correct nmap command string
  - Test that `validate_target()` correctly accepts/rejects inputs
- [ ] Manually test every `/command` end to end
- [ ] Test on a local VM target (set up a simple Linux VM on VirtualBox/VMware)
- [ ] Test with no API key set (AI features should degrade gracefully)
- [ ] Test with an invalid API key
- [ ] Test `pip install .` from scratch in a fresh virtual environment
- [ ] Git commit: `git commit -m "phase 7: tests"`

---

## Phase 8 — GitHub Release
> Goal: Publish a clean, professional open-source project.

### Tasks

#### README.md (write these sections)
- [ ] Project title + one-line description
- [ ] Screenshot or demo GIF of the tool running (use `asciinema` to record terminal)
- [ ] Features list
- [ ] Installation instructions
- [ ] How to use (with examples of each command)
- [ ] How to get an OpenRouter API key
- [ ] ⚠️ Ethical use disclaimer — only scan systems you own or have permission to test
- [ ] Contributing guide
- [ ] License

#### GitHub Setup
- [ ] Create GitHub repo named `easynmap`
- [ ] Push all code: `git remote add origin <url> && git push -u origin main`
- [ ] Add topics to the repo: `nmap`, `kali-linux`, `security`, `cli`, `python`, `beginner`
- [ ] Create a `v1.0.0` release tag on GitHub
- [ ] Add a `CONTRIBUTING.md` file for future contributors

### Outcome
A public, professional GitHub repository that anyone can install and use.

---

## 📦 Final `requirements.txt`
```
prompt_toolkit>=3.0
rich>=13.0
httpx>=0.27
```

---

## ⚠️ Ethical & Legal Disclaimer
> Include this in your README and display it on first launch inside the tool.

This tool is for **educational purposes and authorized security testing only**.
Only scan systems you own or have **explicit written permission** to test.
Unauthorized network scanning may be **illegal** in your country.
The authors are not responsible for misuse of this tool.

---

## 🧱 Technology Summary

| Component | Technology |
|---|---|
| Language | Python 3 |
| Interactive shell | `prompt_toolkit` |
| Terminal UI & colors | `rich` |
| Nmap execution | `subprocess` |
| AI features | Gemini Flash via OpenRouter (`httpx`) |
| Distribution | GitHub + `pip install .` |
| Testing platform | Kali Linux |
