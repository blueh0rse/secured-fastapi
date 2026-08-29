# Contributing

## Project layout

```sh
app/
├── main.py             # FastAPI app, middleware, router wiring
├── config.py           # application configuration
├── db.py               # database connection helper
├── auth.py             # token issuance and the current-user dependency
├── models.py           # request/response schemas
└── routers/
    └── users.py        # all endpoints
db/
└── init.sh             # schema and seed data
tests/                  # test suite
```

## Local setup

```sh
uv venv --python 3.13
uv pip install .
make install-hooks
docker compose up -d db
```

`make install-hooks` installs the pre-commit hooks (secret scanning and basic
file checks) so they run on every commit. CI enforces the same checks, so
this step is advisory locally, not a merge gate.

## Running the tests

The test suite runs the application in-process; only PostgreSQL needs to be
running:

```sh
docker compose up -d db
make tests
```

## Development commands

A `Makefile` wraps the common commands:

```sh
make up         # start the stack
make db         # start the database only
make down       # stop the stack
make tests      # run the test suite
make lint       # run the linter
make install-hooks  # install pre-commit hooks
```

## Security scans

```sh
make vuln-report      # dependency CVEs, everything found
make vuln-gate        # the merge gate: exits 1 on fixable CRITICAL/HIGH
make image-report     # application image CVEs
make image-gate       # the merge gate for the image
make db-image-report  # database image, reported only
```

Run the `-gate` targets before you push. They use the same Trivy version and
flags as CI, so a clean run here means a clean run there.

Each scan runs twice in CI on purpose. The report step records every finding
and never fails, so alerts reach code scanning even when the gate blocks the
build. The gate step then fails on CRITICAL or HIGH findings that have a
released fix.

The database image is scanned but not gated. Its findings live in a Go binary
inside the upstream image, which no change here can rebuild.

### Accepting a finding

Add it to `.trivyignore`:

```
# CVE-2026-00000 — <package>
# Reason: not reachable, the affected code path is never called.
# Reviewed by: <handle>  Expires: 2026-12-01
CVE-2026-00000
```

Every entry needs a reason, a reviewer, and an expiry date. Review the file at
each release and re-check anything that expired.
