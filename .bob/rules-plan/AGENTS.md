# Project Architecture Rules (Non-Obvious Only)

- No architecture exists yet — this is an empty scaffold. Any architecture created should be proposed fresh.
- `bob_sessions/` is pre-designated as the session/output storage directory; design around it rather than introducing a competing store.
- Python is the confirmed language (`.gitignore` is Python-specific). Framework choice (Django vs Flask vs FastAPI vs Streamlit) is open.
- Ruff + pytest are the assumed toolchain — align any CI or Makefile targets to these.
