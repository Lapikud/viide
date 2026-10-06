# Viide

Viide is a Flask app for creating short links and QR codes. It stores links in PostgreSQL, QR images in Garage, and authenticates users through FreeIPA.

## Requirements

- Python 3.12, `uv`, Docker with Compose, and OpenSSL
- Access to a working FreeIPA server and a user account on it

Python packages are declared in `pyproject.toml` and installed from `uv.lock`; no separate `pip install` is needed.

## Local setup

Run these commands from the repository root:

```sh
cp .env.example .env
cp garage.example.toml garage.toml
uv sync
```

Before starting services, edit the two copied files:

1. In `garage.toml`, replace `rpc_secret` ([Garage setup reference](https://garagehq.deuxfleurs.fr/documentation/quick-start/)).

   ```sh
   openssl rand -hex 32 # paste the output into rpc_secret
   ```

2. In `.env`, replace the example values.

   ```sh
   openssl rand -hex 16                  # DB_PASSWORD
   printf 'GK%s\n' "$(openssl rand -hex 16)" # STORAGE_ACCESS_KEY: GK + 32 hex characters
   openssl rand -hex 32                  # STORAGE_SECRET_KEY
   openssl rand -hex 32                  # GARAGE_ADMIN_TOKEN
   openssl rand -hex 32                  # SECRET_KEY
   ```

3. In `.env`, replace the `STORAGE_PUBLIC_URL` line with:

   ```dotenv
   STORAGE_PUBLIC_URL=http://localhost:3900
   ```

Keep `.env` and `garage.toml` private; both are ignored by Git. The database name, user, password, storage bucket, and storage keys in `.env` are also passed to the local services by Compose.

Start PostgreSQL and Garage, apply the database migrations, then run the app:

```sh
docker compose up -d postgres garage
uv run alembic upgrade head
uv run viide
```

Open <http://localhost:5000> and sign in with a FreeIPA account. The app requires a reachable FreeIPA server; local Compose does not provide one. Press Ctrl+C to stop the app, then stop the services:

```sh
docker compose down
```

Compose volumes keep the local database and stored QR images between runs.

## Production

`uv run viide` uses Flask's development server. In production, apply the migrations and serve the app with Gunicorn:

```sh
uv sync --frozen --no-dev
uv run --no-dev alembic upgrade head
uv run --no-dev gunicorn --bind 0.0.0.0:8000 --workers 4 "viide.web.app:create_app()"
```

## Configuration

`src/viide/config.py` loads `.env`. The main settings are:

| Setting | Purpose |
| --- | --- |
| `DB_USER`, `DB_PASSWORD`, `DB_NAME` | PostgreSQL credentials and database |
| `DB_HOST`, `DB_PORT` | PostgreSQL address; default to `localhost:5432` |
| `STORAGE_ENDPOINT` | Garage S3 API; `http://localhost:3900` locally |
| `STORAGE_PUBLIC_URL` | Garage URL used in signed QR image links |
| `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_BUCKET` | Garage credentials and bucket |
| `GARAGE_ADMIN_TOKEN` | Garage admin API token used by Compose |
| `SECRET_KEY` | Flask session signing key |
| `PUBLIC_URL` | Base URL for generated short links |
| `FREEIPA_URL` | FreeIPA server used for login |

`garage.toml` configures Garage itself. `LDAP_URL` and `LDAP_BASE_DN` appear in `.env.example`, but the current login path uses `FREEIPA_URL`.

## Project layout

| Location | Purpose |
| --- | --- |
| `src/viide/web/` | Flask routes, templates, and static files |
| `src/viide/app/` | Link, QR code, and authentication logic |
| `src/viide/db/` | Database models and repositories |
| `src/viide/storage/` | Garage S3 client |
| `migrations/` | Alembic database migrations |
| `compose.yaml` | Local PostgreSQL and Garage services |
| `pyproject.toml`, `uv.lock` | Python package definitions and lockfile |

## Development

Run the configured linter with `uv run ruff check .`. The optional Garage web UI can be started with `docker compose --profile dev up -d garage-webui` and is available at <http://localhost:3909>.
