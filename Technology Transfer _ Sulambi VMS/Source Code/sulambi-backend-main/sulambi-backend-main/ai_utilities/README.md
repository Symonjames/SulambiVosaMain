# AI-Generated Utilities & Important Scripts

This folder documents important AI-generated scripts and components that are critical for the application.

## Auto-Running Migration Scripts (app/database/)

These scripts run **automatically on server startup** and should NOT be moved:

### ✅ migrate_beneficiary_pin.py
- **Purpose**: Adds `beneficiaryEvaluationPin` column to event tables
- **Auto-runs**: On Flask startup
- **Status**: REQUIRED for production

### ✅ migrate_internal_report_finance.py
- **Purpose**: Adds finance columns to internal reports (`approvedBudget`, `approvedBudgetSrc`, etc.)
- **Auto-runs**: On Flask startup
- **Status**: REQUIRED for production

### ✅ migrate_photo_captions.py
- **Purpose**: Adds `photoCaptions` column to report tables
- **Auto-runs**: On server init command (`python server.py --migrate-photo-captions`)
- **Status**: REQUIRED for production

## Database Connection & ORM (app/models/)

### Model.py
- **Purpose**: Base ORM class with PostgreSQL/SQLite abstraction
- **Key Fix**: PostgreSQL column name normalization to handle mixed lowercase/camelCase schemas
- **Location**: `app/models/Model.py`
- **Status**: CRITICAL - handles all database queries

## Important Configuration Files

### app/database/connection.py
- **Purpose**: Database connection factory (PostgreSQL primary, SQLite fallback)
- **Key Features**: 
  - Automatic database type detection
  - Boolean/placeholder conversion for DB compatibility
  - Connection pooling
- **Status**: CRITICAL - core backend infrastructure


## Development Notes


1. **Keep migration scripts in app/database/** - they must be importable by Flask startup
2. **Test locally with both databases** - use SQLite for local dev, PostgreSQL for production testing
3. **Column naming** - PostgreSQL stores unquoted names as lowercase; quoted names as provided. Model.py normalizes this automatically.
4. **Deploy after schema changes** - Always redeploy the backend after database migrations so they run on startup
