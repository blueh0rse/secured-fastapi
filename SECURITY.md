# Security policy

## Reporting a vulnerability

Report privately through
[GitHub security advisories](https://github.com/blueh0rse/secured-fastapi/security/advisories/new).
Do not open a public issue.

## Supported versions

Only the latest commit on `main` receives fixes.

## Automated scanning

Every pull request runs Gitleaks for secrets, Trivy for dependency and
container CVEs, and Bandit plus Semgrep for flaws in the source. Results
appear under **Security → Code scanning**.

A merge is blocked by:

- a CVE rated CRITICAL or HIGH that has a released fix
- a Bandit finding at MEDIUM severity and MEDIUM confidence or above
- a Semgrep finding rated WARNING or ERROR

CVEs with no available fix are recorded, not blocked.

Contributors: see [CONTRIBUTING.md](CONTRIBUTING.md#security-scans) for the
local commands and the exception process.
