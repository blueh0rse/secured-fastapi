# Users API

A small internal service for managing user accounts, built with FastAPI and
PostgreSQL. It provides token-based login, a role-based users API, and a
per-user audit log.

## Features

- JWT-based authentication
- User management with `user` and `admin` roles
- Per-user audit log of account activity
- Interactive API documentation via Swagger UI

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Report whether the service is running |
| `POST` | `/auth/login` | Authenticate and receive an access token |
| `GET` | `/users` | List users, optionally filtered and sorted |
| `GET` | `/users/{id}` | Get a single user by id |
| `POST` | `/users` | Create a user account |
| `PATCH` | `/users/{id}` | Update a user account |
| `DELETE` | `/users/{id}` | Remove a user account |
| `GET` | `/users/{id}/logs` | List a user's audit log entries |

## Quickstart

```sh
docker compose up
```

This starts the API on `http://localhost:8000` and a PostgreSQL database
seeded with a few accounts for local development:

| username | password | role |
| --- | --- | --- |
| `admin` | `Qz7$mVb2LpXt9#eRk4WnD8yA` | admin |
| `alice` | `Jf3&nRt8QmZx5#WpL2vBk9eS` | user |
| `bob` | `Xr9%QwPt4mNl7$YbK2vDe6Zs` | user |
| `carol` | `Wm5#LqTx8nRp3$VbYk6eDz9J` | user (inactive) |
| `dave` | `Nt2$KqXm9LpRw4#VbYs7eDj6` | admin |

Once the stack is running, open `http://localhost:8000/docs` for interactive
API documentation.

> [!NOTE]
> Project layout, local setup, running the tests, and development commands are
> documented in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Release History

### [1.0.0] — Initial release

- Baseline users API: JWT auth, role-based users API, audit log.

## License

MIT — see `LICENSE`.
