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
└── init.sql            # schema and seed data
tests/                  # test suite
```

## Local setup

```sh
uv venv --python 3.9
uv pip install -r requirements.txt
docker compose up -d db
```

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
```
