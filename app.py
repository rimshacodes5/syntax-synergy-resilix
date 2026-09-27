import re
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Vulnerability definitions
# ---------------------------------------------------------------------------

VULNERABILITY_RULES = [
    {
        "id": "sql_injection",
        "name": "SQL Injection",
        "patterns": [
            r"(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b.*(\+|%s|f['\"]|\.format\(|str\()",
            r"['\"].*\bOR\b.*['\"]",
            r"execute\s*\(\s*['\"].*\+",
            r"cursor\.execute\s*\(\s*f['\"]",
        ],
        "description": (
            "User-controlled input appears to be concatenated directly into a SQL "
            "statement, allowing an attacker to manipulate the query logic, bypass "
            "authentication, or exfiltrate/destroy data."
        ),
        "severity": "High",
        "patch": (
            "Use parameterised queries or an ORM instead of string concatenation.\n\n"
            "# Before (vulnerable)\n"
            "cursor.execute(\"SELECT * FROM users WHERE id = '\" + user_id + \"'\")\n\n"
            "# After (safe)\n"
            "cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"
        ),
    },
    {
        "id": "null_exception",
        "name": "Unhandled Null Exception",
        "patterns": [
            r"\.\s*(get|post|put|delete|patch)\s*\(.*\)\s*\.",
            r"request\.(json|args|form)\s*\[",
            r"\bNone\b.*\.",
            r"\.json\(\)\s*\[",
            r"response\s*\.\s*\w+\s*\[",
        ],
        "description": (
            "A value that may be None/null is accessed without a prior null-guard. "
            "If the upstream call returns None (e.g. missing JSON key, failed HTTP "
            "request, empty DB result), the code will raise an AttributeError or "
            "TypeError at runtime."
        ),
        "severity": "Medium",
        "patch": (
            "Add explicit null-guards before dereferencing potentially null values.\n\n"
            "# Before (vulnerable)\n"
            "data = request.json['key']\n\n"
            "# After (safe)\n"
            "data = (request.get_json() or {}).get('key')\n"
            "if data is None:\n"
            "    return jsonify({'error': 'Missing required field: key'}), 400"
        ),
    },
    {
        "id": "string_overflow",
        "name": "String Overflow",
        "patterns": [
            r"input\s*\(",
            r"request\.(json|args|form|data)",
            r"\.read\s*\(\s*\)",
            r"sys\.stdin",
            r"open\s*\(.*\)\.read",
        ],
        "description": (
            "Input is read without enforcing a maximum length. An attacker can supply "
            "an arbitrarily large payload, causing excessive memory consumption, slow "
            "processing (ReDoS if regex is applied), or downstream buffer-overflow "
            "conditions in native extensions."
        ),
        "severity": "Medium",
        "patch": (
            "Enforce a maximum length on all user-supplied strings.\n\n"
            "# Before (vulnerable)\n"
            "user_input = request.json.get('field')\n\n"
            "# After (safe)\n"
            "MAX_LEN = 1024\n"
            "user_input = request.json.get('field', '')\n"
            "if len(user_input) > MAX_LEN:\n"
            "    return jsonify({'error': 'Input exceeds maximum allowed length'}), 413"
        ),
    },
    {
        "id": "malformed_payload",
        "name": "Malformed Payload Structure",
        "patterns": [
            r"json\.loads\s*\(",
            r"pickle\.(loads|load)\s*\(",
            r"yaml\.load\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
            r"ast\.literal_eval\s*\(",
            r"request\.data\b",
            r"xmltodict|xml\.etree|lxml",
        ],
        "description": (
            "The code deserialises or evaluates external data without validating its "
            "structure first. Malformed JSON causes unhandled exceptions; pickle/yaml "
            "deserialisation of untrusted data enables remote code execution; eval/exec "
            "on user input is an immediate code-injection vector."
        ),
        "severity": "High",
        "patch": (
            "Validate and sanitise all deserialised payloads; avoid unsafe loaders.\n\n"
            "# Before (vulnerable)\n"
            "data = pickle.loads(request.data)\n\n"
            "# After (safe) — use JSON with schema validation instead\n"
            "import jsonschema\n"
            "schema = {'type': 'object', 'properties': {'name': {'type': 'string'}}}\n"
            "try:\n"
            "    data = request.get_json(force=True)\n"
            "    jsonschema.validate(data, schema)\n"
            "except (jsonschema.ValidationError, TypeError) as exc:\n"
            "    return jsonify({'error': str(exc)}), 400"
        ),
    },
]

# Severity weights used when calculating the resilience score.
SEVERITY_WEIGHT = {"High": 25, "Medium": 15, "Low": 5}


# ---------------------------------------------------------------------------
# Core analysis logic
# ---------------------------------------------------------------------------

def _analyse(source: str) -> dict:
    """
    Scan *source* text for vulnerability patterns and return a structured
    analysis result including detected vulnerabilities and a resilience score.
    """
    detected = []

    for rule in VULNERABILITY_RULES:
        matched = any(
            re.search(pattern, source, re.IGNORECASE | re.DOTALL)
            for pattern in rule["patterns"]
        )
        if matched:
            detected.append(
                {
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "patch": rule["patch"],
                }
            )

    # Resilience score: start at 100, deduct by severity weight per finding.
    penalty = sum(SEVERITY_WEIGHT.get(v["severity"], 0) for v in detected)
    resilience_score = max(0, 100 - penalty)

    # Overall risk label derived from the score.
    if resilience_score >= 80:
        risk_label = "Low Risk"
    elif resilience_score >= 50:
        risk_label = "Moderate Risk"
    else:
        risk_label = "High Risk"

    return {
        "vulnerabilities_found": len(detected),
        "vulnerabilities": detected,
        "resilience_score": resilience_score,
        "risk_label": risk_label,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def health_check():
    """Health-check endpoint."""
    return jsonify({"status": "ok", "service": "Resilix Fuzzing Agent"}), 200


@app.post("/api/fuzz")
def fuzz():
    """
    Accepts a JSON body with one of:
      - code_snippet  : raw source code string to analyse
      - api_endpoint  : URL string (treated as the target identifier)

    Returns a structured vulnerability report with a resilience score.
    """
    body = request.get_json(silent=True) or {}

    code_snippet = body.get("code_snippet", "")
    api_endpoint = body.get("api_endpoint", "")

    if not code_snippet and not api_endpoint:
        return (
            jsonify({"error": "Provide 'code_snippet' or 'api_endpoint' in the request body."}),
            400,
        )

    # Use whichever field was supplied (code_snippet takes precedence).
    source = code_snippet if code_snippet else api_endpoint

    analysis = _analyse(source)

    return (
        jsonify(
            {
                "input_type": "code_snippet" if code_snippet else "api_endpoint",
                "resilience_score": analysis["resilience_score"],
                "risk_label": analysis["risk_label"],
                "vulnerabilities_found": analysis["vulnerabilities_found"],
                "vulnerabilities": analysis["vulnerabilities"],
            }
        ),
        200,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
