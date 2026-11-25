---
name: nuclei
description: Fast, customizable vulnerability assessment and defensive security scanning using community and custom YAML DSL templates. Audits HTTP endpoints, APIs, misconfigurations, exposure risks, and TLS/DNS hygiene on authorized services.
---

# Nuclei Vulnerability Assessment & Defensive Auditing Engine

Nuclei by ProjectDiscovery is a template-driven vulnerability scanner designed for automated security assessments, misconfiguration detection, exposure auditing, and regression testing across HTTP services, APIs, DNS, and cloud endpoints.

## Core Capabilities
1. **Defensive Endpoint Auditing**: Assess local staging, testing, or deployed application services against known misconfigurations, credential disclosures, and outdated components.
2. **Custom YAML DSL Rule Authoring**: Create simple, declarative security test cases using matchers, extractors, and request sequences.
3. **Exposure & Header Hygiene Checking**: Detect missing security headers (CSP, HSTS, X-Frame-Options), CORS flaws, exposed git folders, and debug endpoints.
4. **Scoping & Rate Control**: Built-in concurrency controls, rate limits, and target filtering to ensure non-disruptive, safe assessments.

---

## Quick Reference CLI Commands

```powershell
# 1. Scan a local or authorized target for misconfigurations
nuclei -u http://localhost:8000 -tags misconfiguration

# 2. Check HTTP security headers and SSL/TLS hygiene
nuclei -u http://localhost:8000 -tags ssl,headers

# 3. Run defensive exposure checks (e.g. exposed env files, git metadata, debug routes)
nuclei -u http://localhost:8000 -tags exposure

# 4. Run a specific custom template
nuclei -u http://localhost:8000 -t ./templates/security-headers.yaml

# 5. Safe scanning mode (low concurrency, non-invasive)
nuclei -u http://localhost:8000 -rate-limit 30 -concurrency 5 -silent

# 6. Output scan results as JSON or markdown
nuclei -u http://localhost:8000 -json -o nuclei-findings.json
nuclei -u http://localhost:8000 -markdown-export ./reports/
```

---

## Standard Workflow

### Step 1: Scoping & Defensive Policy
* **Target Authorization**: Only scan services you own, manage, or have explicit written permission to test (such as `localhost:8000` or staging clusters).
* **Non-Destructive Scanning**: By default, use read-only tags (`exposure`, `misconfiguration`, `headers`, `technologies`). Never execute destructive write operations on production state.

### Step 2: Auditing Web Application Endpoints
Scan the local development server for common misconfigurations:
```powershell
nuclei -u http://localhost:8000 -tags misconfiguration,exposure -rate-limit 50
```

### Step 3: Authoring Custom Defensive Verification Templates
Author project-specific security checks in YAML templates to verify security controls continuously.

#### Example: Verify Missing Security Headers Template (`templates/check-security-headers.yaml`)
```yaml
id: missing-security-headers
info:
  name: Missing HTTP Security Headers Check
  author: viceclip-security
  severity: low
  description: Verifies presence of defense-in-depth security headers (CSP, X-Content-Type-Options, HSTS).

http:
  - method: GET
    path:
      - "{{BaseURL}}/"

    matchers-condition: or
    matchers:
      - type: dsl
        dsl:
          - "!contains(to_lower(all_headers), 'x-content-type-options')"
          - "!contains(to_lower(all_headers), 'content-security-policy')"
```

#### Example: Verify Protected Admin / Debug Endpoints (`templates/debug-endpoints-closed.yaml`)
```yaml
id: verify-debug-routes-closed
info:
  name: Verify Debug and Profiler Routes are Inaccessible
  author: viceclip-security
  severity: medium
  description: Asserts that dev debug endpoints return 401/403/404 in production.

http:
  - method: GET
    path:
      - "{{BaseURL}}/_debug/"
      - "{{BaseURL}}/telemetry/raw"
      - "{{BaseURL}}/.env"

    matchers:
      - type: status
        status:
          - 200
```

---

## Template Matchers & DSL Operators
- **`status`**: HTTP response status codes.
- **`words`**: Substring matching with `condition: and` / `condition: or`.
- **`regex`**: Regular expression validation against headers or bodies.
- **`dsl`**: Boolean logic statements (e.g. `status_code == 200 && contains(body, "admin")`).
- **`extractors`**: Pull dynamic tokens or version strings from responses.
