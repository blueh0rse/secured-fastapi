.PHONY: up down tests lint db install-hooks \
        secret-scan generate-secret-baseline secret-scan-baseline \
        vuln-report vuln-gate image-build image-report image-gate db-image-report up-prebuilt \
        bandit-report bandit-gate semgrep-report semgrep-sarif semgrep-gate

# === run ===

up:
	docker compose up -d

db:
	docker compose up db -d

down:
	docker compose down -v

# === dev ===

tests:
	uv run python -m pytest

lint:
	uv run flake8 --exclude=.venv

install-hooks:
	uv run pre-commit install

# === security ===

secret-scan:
	docker run -v $$(pwd):/app ghcr.io/gitleaks/gitleaks:v8.30.1 git /app -v

generate-secret-baseline:
	docker run -u $$(id -u):$$(id -g) -v $$(pwd):/app ghcr.io/gitleaks/gitleaks:v8.30.1 git /app --report-path /app/gitleaks-baseline.json --redact

secret-scan-baseline:
	docker run -v $$(pwd):/app ghcr.io/gitleaks/gitleaks:v8.30.1 git /app -v -b /app/gitleaks-baseline.json

# Trivy targets mirror the CI policy. Keep TRIVY_VERSION equal to the
# TRIVY_VERSION in .github/workflows/ci.yml. The action wants a "v" prefix
# and the Docker Hub tag does not, so the strings differ by that alone.
# Different Trivy versions carry different DB schemas, so a clean run here
# is only evidence about CI when the two versions match.
TRIVY_VERSION = 0.74.0
# Every target mounts the repo at /src and runs there, so Trivy reads
# .trivyignore the same way CI does.
TRIVY_RUN  = docker run --rm -v $$(pwd):/src -w /src -v trivy-cache:/root/.cache/trivy
TRIVY_SOCK = -v /var/run/docker.sock:/var/run/docker.sock
TRIVY      = $(TRIVY_RUN) aquasec/trivy:$(TRIVY_VERSION)
TRIVY_IMG  = $(TRIVY_RUN) $(TRIVY_SOCK) aquasec/trivy:$(TRIVY_VERSION)
GATE       = --ignore-unfixed --severity CRITICAL,HIGH --exit-code 1

# The filesystem scan includes the dev group. Those tools run on CI runners
# that hold every repository secret, so their CVEs are in scope.
# The image scan does not, because the image never installs them.
vuln-report:
	$(TRIVY) fs --scanners vuln --include-dev-deps .

vuln-gate:
	$(TRIVY) fs --scanners vuln --include-dev-deps $(GATE) .

image-build:
	docker compose build app

image-report: image-build
	$(TRIVY_IMG) image --scanners vuln secured-api:local

image-gate: image-build
	$(TRIVY_IMG) image --scanners vuln $(GATE) secured-api:local

# The database image is scanned but not gated. See CONTRIBUTING.md.
db-image-report:
	$(TRIVY_IMG) image --scanners vuln $$(docker compose config --images | grep '^postgres')

# Starts the stack without rebuilding, so CI runs the exact image it gated.
up-prebuilt:
	docker compose up -d --no-build

# === SAST ===

SEMGREP       = docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp \
                -v $$(pwd):/src -w /src semgrep/semgrep:1.175.0 semgrep
SEMGREP_RULES = --config=p/python --config=p/security-audit --config=p/jwt
# Semgrep grades findings INFO / WARNING / ERROR. Medium or higher is the
# WARNING and ERROR pair.
SEMGREP_MED   = --severity=WARNING --severity=ERROR

bandit-report:
	uv run bandit -r app --exit-zero

bandit-gate:
	uv run bandit -r app --severity-level medium --confidence-level medium

semgrep-report:
	$(SEMGREP) $(SEMGREP_RULES) .

semgrep-sarif:
	$(SEMGREP) $(SEMGREP_RULES) --sarif --sarif-output=semgrep-results.sarif .

semgrep-gate:
	$(SEMGREP) $(SEMGREP_RULES) $(SEMGREP_MED) --error .
