"""
Add beneficiaryEvaluationPin column to event tables if missing.
Run on app startup so production DBs get the column without manual --init.
"""

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG") == "True"


def run_beneficiary_pin_migration():
    """Add beneficiaryEvaluationPin to internalEvents and externalEvents if missing."""
    try:
        from . import connection
        conn, cursor = connection.cursorInstance()
        is_postgresql = connection.is_postgresql_url(DATABASE_URL)
        try:
            if is_postgresql:
                # PostgreSQL: column created unquoted = lowercase (matches Model normalization)
                cursor.execute(
                    'ALTER TABLE internalevents ADD COLUMN IF NOT EXISTS beneficiaryevaluationpin TEXT'
                )
                cursor.execute(
                    'ALTER TABLE externalevents ADD COLUMN IF NOT EXISTS beneficiaryevaluationpin TEXT'
                )
            else:
                try:
                    cursor.execute(
                        "ALTER TABLE internalEvents ADD COLUMN beneficiaryEvaluationPin TEXT"
                    )
                except Exception:
                    pass
                try:
                    cursor.execute(
                        "ALTER TABLE externalEvents ADD COLUMN beneficiaryEvaluationPin TEXT"
                    )
                except Exception:
                    pass
            conn.commit()
            if DEBUG:
                print("[migrate_beneficiary_pin] OK")
        finally:
            conn.close()
    except Exception as e:
        if DEBUG:
            print(f"[migrate_beneficiary_pin] {e}")


if __name__ == "__main__":
    run_beneficiary_pin_migration()
