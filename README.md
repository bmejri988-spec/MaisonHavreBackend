# AUREA Backend

Django REST API for the AUREA chalet catalog.

## Local setup

```powershell
uv sync
uv run python manage.py migrate
uv run python manage.py seed_catalog
uv run python manage.py runserver
```

Copy `.env.example` to `.env` and set `DATABASE_URL` for Supabase. The settings file loads `.env` locally and uses SQLite only when no database URL is available or when running tests.

## Render deployment

Set the service root directory to `backend`.

Catalog API responses are cached in memory for five minutes by default, reducing
repeated Supabase queries during normal browsing. Override the duration with
`CATALOG_CACHE_TTL_SECONDS` when configuring the deployment.

Build command:

```text
pip install uv && uv sync --frozen
```

Start command:

```text
uv run gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

After the first deploy, run these commands once in the Render shell:

```text
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
uv run python manage.py seed_catalog
```

## Catalog image migration

The image migration uses the explicit mapping in
`catalog/image_migration_manifest.json`. It uploads the `modeles` and
`terrains` folders to the private Supabase Storage bucket `images`, then
stores `storage://images/...` references in the existing `image` and
`gallery`
columns. The API converts those references into short-lived signed URLs.
Objects are stored directly under `images/modeles/` and `images/terrains/`;
there are no per-record subdirectories.

Set these variables in `backend/.env` (never commit the service-role key):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=images
```

Create the private `images` bucket in Supabase Storage before the first real
run. From the repository root, preview the exact files and database updates:

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py migrate_catalog_images --dry-run --source-root ..
```

After reviewing the dry-run output, run the idempotent migration:

```powershell
.\.venv\Scripts\python.exe manage.py migrate_catalog_images --source-root ..
```

The command never deletes source files or records. Existing Storage objects
are skipped, missing/invalid files are reported, and the database is updated
only after its corresponding uploads succeed.

Configure the variables from `.env.example` in the Render dashboard. Never commit the real `.env` file.
