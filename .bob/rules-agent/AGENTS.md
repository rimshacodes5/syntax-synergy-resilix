# Project Coding Rules (Non-Obvious Only)

- `bob_sessions/` must remain in the repo (kept via `.gitkeep`); it is the runtime output directory for Bob session artifacts.
- No `pyproject.toml` or `requirements.txt` exists yet — create one before adding any imports that require third-party packages.
- Ruff is the expected linter/formatter: run `ruff check .` and `ruff format .` before committing.
- Run a single pytest test: `pytest path/to/test_file.py::TestClass::test_method -v`
- `.env` / `.venv` are gitignored — never commit credentials or virtual environment files.
