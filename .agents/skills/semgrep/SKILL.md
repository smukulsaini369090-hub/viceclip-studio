---
name: semgrep
description: Fast, lightweight static application security testing (SAST) and code analysis. Scans code for security vulnerabilities, OWASP Top 10, CWE Top 25, logic flaws, and secret leaks across 30+ languages, and authors custom YAML rules and autofixes.
---

# Semgrep Security Analysis & Custom Rule Engineering

Semgrep is an open-source, lightweight static analysis (SAST) engine designed for finding bugs, security vulnerabilities, API deprecations, and compliance violations across 30+ programming languages (Python, TypeScript, JavaScript, Go, Java, C#, Rust, Ruby, PHP, and more).

## Core Capabilities
1. **Automated Codebase SAST Audits**: Scan repositories against community and security standards (OWASP Top 10, CWE Top 25, CIS Benchmarks).
2. **Custom Rule Authoring**: Write declarative YAML rules using intuitive code patterns, metavariables, and Boolean logic without needing complex AST compilers.
3. **Automated Remediation & Autofix**: Define precise pattern replacements to automatically remediate identified vulnerabilities (`--autofix`).
4. **CI/CD Quality & Security Gates**: Integrate into GitHub Actions, GitLab CI, or pre-commit hooks to block pull requests introducing security regressions.

---

## Quick Reference CLI Commands

```powershell
# 1. Run full auto-scan with default curated security rules
semgrep scan --config auto

# 2. Run standard OWASP Top 10 security ruleset
semgrep scan --config "p/owasp-top-ten"

# 3. Run security audit and CWE Top 25 rulesets
semgrep scan --config "p/security-audit" --config "p/cwe-top-25"

# 4. Scan a specific directory or file only
semgrep scan --config auto ./backend/app

# 5. Output results as SARIF (for GitHub Security tab) or JSON
semgrep scan --config auto --sarif --output semgrep-report.sarif
semgrep scan --config auto --json --output semgrep-report.json

# 6. Run with autofix applied to code
semgrep scan --config auto --autofix --dry-run
semgrep scan --config auto --autofix
```

---

## Standard Workflow

### Step 1: Baseline Scan & Triage
1. Run a baseline scan across the workspace:
   ```powershell
   semgrep scan --config auto --json --output semgrep-baseline.json
   ```
2. Review findings by severity:
   - `ERROR`: Critical/High severity (SQL injection, XSS, RCE, insecure deserialization, SSRF).
   - `WARNING`: Medium severity (deprecated crypto, weak ciphers, CORS misconfigurations).
   - `INFO`: Style and best-practice recommendations.

### Step 2: Custom Rule Development
When standard rules miss project-specific requirements (e.g., custom auth middleware, sensitive logging, custom sanitization), author custom rules in `.semgrep/rules.yaml`.

#### Example Custom Rule: Detect Insecure Database Queries
```yaml
rules:
  - id: raw-sql-format-injection
    languages: [python]
    severity: ERROR
    message: "Detected potential SQL injection: Avoid raw string formatting inside database execute calls."
    metadata:
      cwe: "CWE-89: Improper Neutralization of Special Elements used in an SQL Command"
      owasp: "A03:2021 - Injection"
    patterns:
      - pattern-either:
          - pattern: $DB.execute(f"...", ...)
          - pattern: $DB.execute("..." % (...), ...)
          - pattern: $DB.execute("...".format(...), ...)
      - pattern-not: $DB.execute("SELECT ... WHERE id = %s", ($ID,))
```

#### Example Custom Rule: Prohibit Plaintext Token Logging
```yaml
rules:
  - id: no-plaintext-token-logging
    languages: [typescript, javascript]
    severity: WARNING
    message: "Potential credential leak: sensitive token or password passed directly to logger."
    patterns:
      - pattern: console.$LOG(..., $ARG, ...)
      - metavariable-regex:
          metavariable: $ARG
          regex: (?i).*(password|secret|token|api_?key|auth).*
```

---

## Semgrep Pattern Syntax Guide
- **Ellipsis (`...`)**: Matches zero or more arguments, statements, or characters.
  - `func(...)`: Any call to `func` regardless of argument count.
  - `class $CLASS: ...`: Any class definition regardless of body.
- **Metavariables (`$VAR`)**: Captures AST nodes (variables, expressions, functions) across patterns.
  - `foo($X, $X)`: Matches calls where both arguments are identical.
- **`pattern-inside` & `pattern-not-inside`**: Scopes matches within specific contexts (e.g., inside an authenticated route handler).
- **`pattern-either`**: Logical OR among multiple patterns.
- **`pattern-not`**: Exclusion rule to filter out sanitized or safe implementations.

---

## CI/CD Integration (GitHub Actions)

Create `.github/workflows/semgrep.yml`:
```yaml
name: Semgrep SAST

on:
  push:
    branches: [main, master]
  pull_request:

jobs:
  semgrep:
    name: Scan
    runs-on: ubuntu-latest
    container:
      image: semgrep/semgrep
    steps:
      - uses: actions/checkout@v4
      - run: semgrep scan --config auto --sarif --output=semgrep.sarif
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif
```
