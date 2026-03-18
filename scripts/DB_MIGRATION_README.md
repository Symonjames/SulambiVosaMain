# Migrate Render PostgreSQL: Old DB → New DB

## 1. Install pg_dump, psql, and pg_restore (Windows)

Choose one:

### Option A: PostgreSQL installer (recommended)
1. Download: https://www.postgresql.org/download/windows/
2. Run the installer. When prompted, install **Command Line Tools** (and optionally Stack Builder).
3. Add the `bin` folder to your PATH (see **Add PostgreSQL bin to PATH** below).
4. Open a **new** PowerShell window and run:
   ```powershell
   pg_dump --version
   psql --version
   ```

**Add PostgreSQL bin to PATH**

- **Option 1 – Script (run from this repo):**  
  In PowerShell, from the project folder:
  ```powershell
  cd c:\SulambiVosaMain\scripts
  .\add-pg-to-path.ps1
  ```
  If PostgreSQL is in a non-standard location:
  ```powershell
  .\add-pg-to-path.ps1 -BinPath "C:\Program Files\PostgreSQL\16\bin"
  ```
  Then open a **new** terminal so PATH is updated.

- **Option 2 – Manual (GUI):**  
  1. Press **Win + R**, type `sysdm.cpl`, Enter.  
  2. **Advanced** tab → **Environment Variables**.  
  3. Under **User variables**, select **Path** → **Edit** → **New**.  
  4. Add: `C:\Program Files\PostgreSQL\16\bin` (use your version number).  
  5. OK out, then open a **new** PowerShell/terminal.

- **Option 3 – Current session only (PowerShell):**
  ```powershell
  $env:Path += ";C:\Program Files\PostgreSQL\16\bin"
  ```
  Replace `16` with your PostgreSQL version. This lasts only until you close the terminal.

---

### Option B: Winget
```powershell
winget install PostgreSQL.PostgreSQL
```
Then open a **new** terminal and verify:
```powershell
pg_dump --version
```

### Option C: Chocolatey
```powershell
choco install postgresql
```
Then open a **new** terminal and verify as above.

---

## 2. Get your database URLs from Render

- **Old database:** Render Dashboard → your **old** Postgres service → **Connect** → copy **External Database URL**.
- **New database:** Same for the **new** Postgres service.

URLs look like:
`postgresql://user:password@hostname.region.railway.app:5432/database?sslmode=require`

For Render, if there’s no `?sslmode=require`, add it:
`postgresql://user:pass@host:5432/dbname?sslmode=require`

---

## 3. Dump from old database

In PowerShell, set the old URL and run (use one line, no line breaks in the URL):

```powershell
$OLD_URL = "postgresql://USER:PASSWORD@OLD_HOST:5432/DATABASE?sslmode=require"
pg_dump $OLD_URL --no-owner --no-acl -F c -f old_backup.dump
```

Or to create a plain SQL file instead:

```powershell
pg_dump $OLD_URL --no-owner --no-acl -f old_backup.sql
```

---

## 4. Restore into new database

**If you used `.dump` (custom format):**

```powershell
$NEW_URL = "postgresql://USER:PASSWORD@NEW_HOST:5432/DATABASE?sslmode=require"
pg_restore -d $NEW_URL --no-owner --no-acl --clean --if-exists old_backup.dump
```

**If you used `.sql`:**

```powershell
psql $NEW_URL -f old_backup.sql
```

Ignore `pg_restore` exit code 1 if it reports “already exists” or similar; the data is usually restored. Exit code 0 = success.

---

## 5. Using the script (optional)

From the project root:

```powershell
cd c:\SulambiVosaMain\scripts
.\migrate-render-db.ps1 -OldDatabaseUrl "YOUR_OLD_FULL_URL" -NewDatabaseUrl "YOUR_NEW_FULL_URL"
```

Replace the URLs with your real Render External Database URLs (in quotes).

---

## 6. After migration

1. In Render, open your **backend** service.
2. **Environment** → set **DATABASE_URL** to the **new** database connection string.
3. Redeploy the backend.
4. Test the app; then you can delete or stop the old database if no longer needed.
