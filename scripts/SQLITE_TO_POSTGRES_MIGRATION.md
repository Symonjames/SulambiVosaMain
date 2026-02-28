# Migrate SQLite data to the new Render PostgreSQL database

The backend already has a migration script that copies all data from the local SQLite database into your Render PostgreSQL database.

## 1. Prerequisites

- **SQLite file** at the backend path (e.g. `Technology Transfer _ Sulambi VMS/Source Code/sulambi-backend-main/sulambi-backend-main/app/database/database.db`), or set `DB_PATH` to its location.
- **New Render PostgreSQL** database created and empty (or you’re okay overwriting).
- **Python** with `psycopg2-binary` and `python-dotenv` installed in the backend environment.

Install if needed:

```powershell
cd "c:\SulambiVosaMain\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
pip install psycopg2-binary python-dotenv
```

## 2. Ensure PostgreSQL tables exist

The new database must have the same table structure. Either:

- Deploy the backend once against the new DB (it will create tables), or  
- Run the table-creation script against the new DB (see backend’s `create_postgresql_tables.py` or app startup).

## 3. Set environment variables

In the same terminal where you’ll run the script, set:

- **DB_PATH** – path to your SQLite file (optional if it’s at the default `app/database/database.db` relative to the backend).
- **DATABASE_URL** – **new** Render PostgreSQL URL (External Database URL from Render dashboard).

Example (PowerShell):

```powershell
$env:DB_PATH = "C:\full\path\to\app\database\database.db"   # optional
$env:DATABASE_URL = "postgresql://user:password@host.oregon-postgres.render.com/database?sslmode=require"
```

If you get SSL errors, try `?sslmode=no-verify` at the end of `DATABASE_URL`.

## 4. Run the migration

From the **backend** directory (so `app/database/database.db` is found if you use the default `DB_PATH`):

```powershell
cd "c:\SulambiVosaMain\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
python migrate_sqlite_to_postgresql.py
```

Or with explicit paths:

```powershell
$env:DB_PATH = "C:\SulambiVosaMain\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main\app\database\database.db"
$env:DATABASE_URL = "postgresql://YOUR_NEW_RENDER_EXTERNAL_URL?sslmode=require"
python migrate_sqlite_to_postgresql.py
```

## 5. After migration

- Point your backend service on Render to the **new** database by setting **DATABASE_URL** to the new connection string.
- Redeploy the backend.
- Test the app; then you can remove or stop the old database if you no longer need it.
