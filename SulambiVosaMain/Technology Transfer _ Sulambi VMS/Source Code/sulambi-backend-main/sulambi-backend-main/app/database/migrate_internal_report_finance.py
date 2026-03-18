"""
Add approvedBudget and approvedBudgetSrc columns to internalReport if missing.
Run on app startup so existing databases are migrated automatically.
"""

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG") == "True"


def run_internal_report_finance_migration():
    """Add officer-submitted internal report finance columns if they do not exist."""
    try:
        from . import connection

        conn, cursor = connection.cursorInstance()
        is_postgresql = connection.is_postgresql_url(DATABASE_URL)
        try:
            if is_postgresql:
                # Prefer lowercase table name for compatibility with unquoted PostgreSQL tables.
                cursor.execute(
                    "ALTER TABLE internalreport ADD COLUMN IF NOT EXISTS approvedbudget INTEGER NOT NULL DEFAULT 0"
                )
                cursor.execute(
                    "ALTER TABLE internalreport ADD COLUMN IF NOT EXISTS approvedbudgetsrc TEXT NOT NULL DEFAULT ''"
                )

                # Ensure camelCase aliases exist for application queries.
                try:
                    cursor.execute(
                        'ALTER TABLE internalreport RENAME COLUMN approvedbudget TO "approvedBudget"'
                    )
                except Exception:
                    pass
                try:
                    cursor.execute(
                        'ALTER TABLE internalreport RENAME COLUMN approvedbudgetsrc TO "approvedBudgetSrc"'
                    )
                except Exception:
                    pass
            else:
                try:
                    cursor.execute(
                        "ALTER TABLE internalReport ADD COLUMN approvedBudget INTEGER NOT NULL DEFAULT 0"
                    )
                except Exception:
                    pass
                try:
                    cursor.execute(
                        "ALTER TABLE internalReport ADD COLUMN approvedBudgetSrc STRING NOT NULL DEFAULT ''"
                    )
                except Exception:
                    pass

            conn.commit()
            if DEBUG:
                print("[migrate_internal_report_finance] OK")
        finally:
            conn.close()
    except Exception as e:
        if DEBUG:
            print(f"[migrate_internal_report_finance] {e}")


if __name__ == "__main__":
    run_internal_report_finance_migration()
