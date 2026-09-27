# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project

**Resilix** — autonomous AI-powered adversarial testing & resilience agent, built for the IBM Bob 2.0 Hackathon. Python project, currently in initial scaffold stage.

## Repository State

- No source code exists yet — only `README.md`, `.gitignore`, and `bob_sessions/` (a placeholder directory kept via `.gitkeep`).
- `bob_sessions/` is the designated output/storage directory for Bob session data; do not delete it.
- `.gitignore` covers Python (pytest, ruff, mypy), Django, Flask, Streamlit, Marimo, Redis, RabbitMQ, Celery — the intended stack is Python but the specific frameworks are not yet determined.

## Conventions to Follow When Adding Code

- **Linter**: Ruff is the expected linter/formatter (`.ruff_cache/` in `.gitignore`).
- **Tests**: pytest is the expected test runner (`.pytest_cache/` in `.gitignore`).
- **Env management**: `.env` / `.envrc` / `.venv` are gitignored — use a virtual environment, do not commit secrets.
- **Run a single test**: `pytest path/to/test_file.py::test_function_name -v`
- **Lint**: `ruff check .` / `ruff format .`

## Notes

- No `pyproject.toml`, `requirements.txt`, or `setup.py` exists yet — create one before adding dependencies.
- No CI/CD configuration exists yet.
