# ⚡ Resilix — Autonomous Adversarial Agent

> **Break it before attackers do.**
> Resilix is an autonomous AI-powered adversarial testing and input-fuzzing agent that scans code snippets and API endpoints for critical vulnerabilities, scores their resilience, and auto-generates defensive patch suggestions — all in real time.

**Team:** Syntax &amp; Synergy
**Hackathon:** IBM Bob 2.0 Hackathon on [lablab.ai](https://lablab.ai)

---

## Problem Statement

Modern AI systems and REST APIs are increasingly exposed to adversarial inputs: SQL-injected queries, null-dereference payloads, oversized strings, and deliberately malformed data structures. Traditional static analysis tools are slow, require complex setup, and rarely surface the *actionable fix* alongside the finding.

**The gap Resilix closes:**

- Developers ship code without a fast feedback loop on input-handling vulnerabilities.
- AI agents that consume or generate code have no built-in mechanism to evaluate the resilience of that code against adversarial inputs.
- Security reviews happen too late in the development cycle — often only after a breach.

Resilix makes adversarial testing instant: paste a snippet or point it at an endpoint, and within milliseconds you receive a scored vulnerability report with auto-generated defensive patches ready to drop into your codebase.

---

## Features

| Feature | Detail |
|---|---|
| 🔍 **Four-category fuzzing engine** | SQL Injection · Unhandled Null Exception · String Overflow · Malformed Payload Structure |
| 📊 **Dynamic resilience score** | 0–100 score calculated from severity-weighted deductions per detected vulnerability |
| 🩹 **Automated patch suggestions** | Each finding includes a copy-ready defensive code fix |
| 🌑 **Chaos Dashboard** | Dark-mode single-page frontend with a radial score ring, severity badges, and toggleable patch viewer |
| ⚡ **Zero-friction setup** | Pure Python backend + single HTML file — no build step, no bundler |

---

## Architecture

```
┌─────────────────────────────┐        POST /api/fuzz
│   index.html (Frontend)     │  ──────────────────────▶  ┌──────────────────────────┐
│                             │                            │   app.py (Flask)         │
│  • Textarea input           │  ◀──────────────────────  │                          │
│  • Radial resilience score  │        JSON response       │  • CORS-enabled          │
│  • Severity badges          │                            │  • Regex-based fuzzer    │
│  • Patch viewer             │                            │  • Resilience scorer     │
└─────────────────────────────┘                            │  • Patch generator       │
                                                           └──────────────────────────┘
```

### Backend — `app.py`

- **Framework:** Flask + Flask-CORS
- **`GET /`** — health check
- **`POST /api/fuzz`** — accepts `{ "code_snippet": "..." }` or `{ "api_endpoint": "..." }`
- Vulnerability detection uses compiled regex patterns per category; each match deducts from a 100-point resilience score (High −25, Medium −15, Low −5)
- Returns structured JSON: `resilience_score`, `risk_label`, `vulnerabilities_found`, and per-vulnerability `description`, `severity`, and `patch`

### Frontend — `index.html`

- Fully self-contained (no external dependencies, no build step)
- Auto-detects whether input is a URL or a code snippet and routes accordingly
- `Ctrl+Enter` / `Cmd+Enter` keyboard shortcut triggers analysis
- SVG radial arc animates to the resilience score; colour-coded green / amber / red
- Per-vulnerability cards collapse/expand; patch suggestions are toggled independently

---

## IBM Bob 2.0 Usage

Resilix was designed, built, and documented entirely inside **IBM Bob 2.0** — IBM's AI-powered IDE — as part of the IBM Bob 2.0 Hackathon on lablab.ai.

Bob was used at every stage of the project:

1. **Architecture design** — Bob's Plan mode was used to define the Flask backend structure, the four vulnerability categories, the scoring formula, and the frontend layout before a single line of code was written.

2. **Code generation** — Agent mode generated the complete `app.py` (Flask backend with regex-based fuzzing, scoring, and patch logic) and `index.html` (dark-mode dashboard with SVG radial score ring, severity badges, and collapsible patch viewer) from natural-language specifications.

3. **Project scaffolding** — Bob created `requirements.txt`, `AGENTS.md`, and the `.bob/rules-*/AGENTS.md` guidance files to keep the project context sharp across sessions.

4. **Documentation** — This README was drafted and structured by Bob to ensure clarity for judges, contributors, and future agents operating in the repository.

Bob's tight edit-verify loop (syntax checks, inline diffs, live command execution) meant the entire Resilix stack went from blank repository to a working adversarial testing agent in a single session.

---

## Quickstart

### Prerequisites

- Python 3.9 or later
- A modern web browser

### 1. Clone the repository

```bash
git clone https://github.com/your-org/syntax-synergy-resilix.git
cd syntax-synergy-resilix
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. Start the Flask backend

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5000`.

### 4. Open the Chaos Dashboard

Open `index.html` directly in your browser (no server required):

```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

Or simply double-click `index.html` in your file explorer.

### 5. Run your first analysis

Paste the snippet below into the textarea and click **Run Resilix Chaos Agent**:

```python
import sqlite3
user_id = input("Enter user ID: ")
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = '" + user_id + "'")
print(cursor.fetchall())
```

You should see a **High Risk** result with SQL Injection and String Overflow findings, each with a suggested defensive patch.

---

## Project Structure

```
syntax-synergy-resilix/
├── app.py              # Flask backend — fuzzing engine & API
├── index.html          # Single-page Chaos Dashboard frontend
├── requirements.txt    # Python dependencies
├── bob_sessions/       # IBM Bob session artifacts (runtime output)
├── AGENTS.md           # AI agent guidance for this repository
└── .bob/
    ├── rules-agent/AGENTS.md   # Agent-mode coding rules
    ├── rules-ask/AGENTS.md     # Ask-mode documentation context
    └── rules-plan/AGENTS.md    # Plan-mode architecture constraints
```

---

## License

[MIT](LICENSE)
