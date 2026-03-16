# Contributing to easynmap

Thanks for your interest in contributing! Here's how to get started.

---

## Setup

```bash
git clone https://github.com/OSCUROO/easynmap.git
cd easynmap
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest
```

---

## Project structure

```
easynmap/
├── easynmap/
│   ├── app.py        # Entry point, main loop, banner
│   ├── commands.py   # All / command handlers
│   ├── scanner.py    # nmap subprocess wrappers + input validation
│   ├── display.py    # Rich tables and output formatting
│   ├── ai.py         # OpenRouter / Gemini AI functions
│   └── output.py     # File saving (txt/md/report)
├── config/
│   └── settings.py   # API key loading
├── tests/
│   └── test_scanner.py
├── requirements.txt
└── setup.py
```

---

## Running tests

```bash
python -m pytest tests/ -v
```

All 54 tests must pass before submitting a PR.

---

## Guidelines

- **New scan type?** Add a function to `scanner.py`, a handler stub to `commands.py`, and tests in `test_scanner.py`
- **New AI feature?** Add the function to `ai.py` and wire it up in `commands.py`
- **Input from users always goes through `validate_target()`** before being passed to subprocess — never bypass this
- Keep PRs focused — one feature or fix per PR
- Match the existing code style (no type annotations on new code unless the surrounding code has them)

---

## Reporting bugs

Open an issue with:
1. What you typed
2. What you expected
3. What actually happened (paste the error or output)
4. Your OS and Python version

---

## Code of Conduct

Be respectful. This is a beginner-friendly project — questions and beginner PRs are welcome.
