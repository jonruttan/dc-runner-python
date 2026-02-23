# AGENTS.md

Project-specific instructions for AI agents working in `dc-runner-python`.

- Preserve command and exit-code compatibility expected by Data Contracts.
- Keep this runner compatibility-lane focused (non-blocking lane).
- Keep changes deterministic and contract-driven.
- Always run Python commands from the project venv first:
  - preferred interpreter: `./.venv/bin/python`
  - preferred pip: `./.venv/bin/python -m pip`
- If `.venv` is missing, create and bootstrap it before testing:
  - `python3 -m venv .venv`
  - `./.venv/bin/python -m pip install -e '.[dev]'`
- When invoking `make`, pass or rely on venv Python so tests do not run
  against system Python without `pytest`.
