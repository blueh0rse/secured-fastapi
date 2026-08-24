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
uv venv --python 3.9
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
