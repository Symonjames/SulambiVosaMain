"""
Show what's stored in the satisfactionSurveys table (SQLite).

This prints:
- DB path
- Table schema (PRAGMA table_info)
- Row count
- Latest rows (small subset of columns)
"""

import os
import sqlite3


def main() -> None:
    db_path = os.getenv("DB_PATH") or os.path.join("app", "database", "database.db")
    print(f"DB_PATH: {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Schema
    print("\n=== satisfactionSurveys schema ===")
    cur.execute("PRAGMA table_info(satisfactionSurveys)")
    for cid, name, col_type, notnull, dflt_value, pk in cur.fetchall():
        print(
            f"- {cid}: {name} {col_type}"
            f"{' NOT NULL' if notnull else ''}"
            f"{' PRIMARY KEY' if pk else ''}"
            f"{f' DEFAULT {dflt_value}' if dflt_value is not None else ''}"
        )

    # Count (use COUNT(1) to avoid shell wildcard issues)
    cur.execute("SELECT COUNT(1) FROM satisfactionSurveys")
    count = cur.fetchone()[0] or 0
    print(f"\n=== row count ===\n{count}")

    # Latest rows
    print("\n=== latest rows (top 10) ===")
    cur.execute(
        """
        SELECT
          id, eventId, eventType, requirementId,
          respondentEmail, respondentName,
          overallSatisfaction, submittedAt, finalized
        FROM satisfactionSurveys
        ORDER BY id DESC
        LIMIT 10
        """
    )
    rows = cur.fetchall()
    if not rows:
        print("[]")
    else:
        for r in rows:
            print(r)

    conn.close()


if __name__ == "__main__":
    main()






