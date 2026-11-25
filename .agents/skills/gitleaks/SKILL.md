---
name: gitleaks
description: Detect and prevent hardcoded secrets, API tokens, passwords, private keys, and credential leaks in git repositories, commit history, and staged files. Configures custom entropy rules, pre-commit hooks, and remediation workflows.
---

# Gitleaks Secret Detection & Leak Prevention

Gitleaks is a fast, lightweight secret detection tool designed to audit Git repositories, filesystems, and continuous integration pipelines for exposed secrets, API keys, bearer tokens, private SSH keys, database credentials, and certificates.

## Core Capabilities
1. **Full History Audit**: Scan commit history to detect accidentally committed credentials across all branches and commits.
2. **Pre-Commit Protection**: Scan staged files before commit (`gitleaks protect --staged`) to prevent secrets from entering the repository.
3. **Entropy & Pattern Matching**: Uses high-entropy detection combined with regex signatures to catch both known token formats (AWS, GitHub, Stripe, OpenAI) and unstructured passwords.
4. **Custom Rules & Baselines**: Define `.gitleaks.toml` configurations to enforce organization-specific credential formats or whitelist test fixtures with `.gitleaksignore`.

---

## Quick Reference CLI Commands

```powershell
# 1. Detect secrets across the entire git repository history
gitleaks detect --source . -v

# 2. Detect secrets in uncommitted/working tree files
gitleaks detect --source . --no-git -v

# 3. Protect staged changes before committing (ideal for pre-commit hook)
gitleaks protect --staged -v

# 4. Scan a specific commit range
gitleaks detect --log-opts="HEAD~5..HEAD" -v

# 5. Output report in JSON or SARIF format
gitleaks detect --source . --report-format json --report-path gitleaks-report.json
gitleaks detect --source . --report-format sarif --report-path gitleaks-report.sarif

# 6. Baseline / ignore existing accepted findings
gitleaks detect --source . --baseline-path .gitleaksignore
```

---

## Standard Workflow

### Step 1: Initial Discovery Scan
Run an audit across the repository:
```powershell
gitleaks detect --source . --verbose --report-format json --report-path secret-audit.json
```
If leaks are detected:
- Examine the file path, commit hash, and matched secret rule.
- Do NOT simply delete the file in a new commit—the secret remains in Git history.

### Step 2: Emergency Secret Remediation Checklist
1. **Revoke and Rotate Immediately**: Consider any detected token compromised. Invalidate it in the provider console (AWS, OpenAI, GitHub, etc.) and generate a replacement.
2. **Remove Secret from Git History**: Use `git-filter-repo` or BFG Repo-Cleaner to purge the sensitive string from historical commits:
   ```bash
   git filter-repo --replace-text <(echo 'compromised_secret==>REMOVED')
   ```
3. **Update Environment Files**: Store secrets in local `.env` files and verify `.env` is listed in `.gitignore`.

### Step 3: Configure `.gitleaks.toml` Custom Rules
When project-specific tokens (e.g. internal JWT headers or proprietary API keys) need custom rules, create `.gitleaks.toml`:

```toml
[extend]
useDefault = true

[[rules]]
id = "custom-viceclip-api-key"
description = "ViceClip Internal Service API Key"
regex = '''(?i)(viceclip[_-]?api[_-]?key[\s:=]+['"][A-Za-z0-9_\-]{32,64}['"])'''
entropy = 3.5
secretGroup = 1
keywords = ["viceclip"]

[allowlist]
description = "Global allowlist for test mock data"
paths = [
    '''backend/tests/.*''',
    '''frontend/src/tests/.*'''
]
regexes = [
    '''dummy-secret-value-for-testing''',
    '''00000000-0000-0000-0000-000000000000'''
]
```

### Step 4: Pre-Commit Hook Setup
Install Gitleaks as a pre-commit git hook in `.git/hooks/pre-commit`:
```bash
#!/bin/sh
gitleaks protect --staged --verbose
if [ $? -ne 0 ]; then
    echo "Gitleaks detected hardcoded secrets in staged files. Commit rejected."
    exit 1
fi
```
