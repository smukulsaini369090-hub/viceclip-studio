---
name: trivy
description: Comprehensive security and vulnerability scanner for container images, filesystems, Git repositories, virtual machine images, and Kubernetes. Detects CVE vulnerabilities in application dependencies, IaC misconfigurations, and licenses.
---

# Trivy Vulnerability & Security Scanner

Trivy by Aqua Security is a comprehensive, multi-purpose security scanner. It scans filesystems, software dependencies (npm, pip, maven, cargo, go), container images, and Infrastructure as Code (IaC) templates (Terraform, Dockerfile, Kubernetes, Helm) for known CVE vulnerabilities and configuration flaws.

## Core Capabilities
1. **Dependency Vulnerability Scanning (SCA)**: Analyzes `package-lock.json`, `requirements.txt`, `poetry.lock`, `go.sum`, etc., against the global CVE vulnerability database.
2. **Infrastructure as Code (IaC) Auditing**: Scans Dockerfiles, Terraform scripts, and CloudFormation for misconfigurations and security bad practices.
3. **Container Image Scanning**: Audits base OS packages (Debian, Alpine, Ubuntu, RedHat) and application layers in Docker images.
4. **SBOM Generation**: Generates standard Software Bill of Materials in CycloneDX or SPDX formats for compliance.

---

## Quick Reference CLI Commands

```powershell
# 1. Scan filesystem for dependency vulnerabilities (SCA)
trivy fs .

# 2. Scan filesystem for vulnerabilities and IaC misconfigurations
trivy fs --scanners vuln,misconfig .

# 3. Filter for High and Critical vulnerabilities only
trivy fs --severity HIGH,CRITICAL .

# 4. Scan Dockerfile for best practices and security misconfigurations
trivy config ./Dockerfile

# 5. Scan a built Docker container image
trivy image viceclip-studio:latest

# 6. Generate an SBOM in CycloneDX format
trivy fs --format cyclonedx --output sbom.json .

# 7. Output results to SARIF format for GitHub Security integration
trivy fs --format sarif --output trivy-results.sarif .
```

---

## Standard Workflow

### Step 1: Scan Workspace Dependencies
Run an initial scan focused on severe dependency risks:
```powershell
trivy fs --severity HIGH,CRITICAL --scanners vuln .
```
Trivy outputs:
- Target package manager and library name.
- CVE ID (e.g., `CVE-2024-XXXXX`).
- Severity rating and CVSS score.
- Installed version vs Fixed version.

### Step 2: Remediating Vulnerabilities
1. **Update Pinned Dependencies**: Update packages in `package.json` or `pyproject.toml` to the recommended `Fixed Version`.
2. **Re-generate Lockfiles**: Run `npm update <pkg>` or `pip install --upgrade <pkg>`.
3. **Suppress False Positives with `.trivyignore`**:
   If a CVE has no fix available or is verified non-exploitable in the current context, record it in `.trivyignore`:
   ```text
   # Suppressed after security review: non-exploitable client-side demo
   CVE-2023-12345
   CVE-2024-67890
   ```

### Step 3: Dockerfile Security Audit
Audit your production container configurations:
```powershell
trivy config ./Dockerfile
```
Key checks Trivy enforces:
- Avoid running containers as `root` (enforce `USER nonroot`).
- Use pinned image digests or minimal base images (e.g. `python:3.11-slim` or Alpine).
- Avoid `ADD` when `COPY` is sufficient.
- Avoid leaving secrets in layer cache.

---

## CI/CD Pipeline (GitHub Actions)

Add Trivy scanning to `.github/workflows/security.yml`:
```yaml
name: Trivy Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  trivy:
    name: Trivy Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'HIGH,CRITICAL'
      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```
