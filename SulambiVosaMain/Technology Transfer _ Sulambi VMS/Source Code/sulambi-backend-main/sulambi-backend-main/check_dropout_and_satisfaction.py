"""
Quick local sanity-check for:
- Dropout logic (joined vs attended vs not answered)
- Satisfaction storage (satisfactionSurveys rows)

Runs against SQLite DB (DB_PATH env var, default: app/database/database.db).
Safe to run: READ-ONLY queries.
"""

import os
import sqlite3


def table_exists(cur: sqlite3.Cursor, name: str) -> bool:
    cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,)
    )
    return cur.fetchone() is not None


def scalar(cur: sqlite3.Cursor, sql: str, params=()) -> int:
    cur.execute(sql, params)
    row = cur.fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def main() -> None:
    db_path = os.getenv("DB_PATH") or os.path.join("app", "database", "database.db")
    print(f"DB_PATH: {db_path}")

    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Core join/answer tables
    joined = scalar(cur, "SELECT COUNT(*) FROM requirements WHERE accepted=1")
    eval_total = scalar(cur, "SELECT COUNT(*) FROM evaluation")
    eval_finalized = scalar(cur, "SELECT COUNT(*) FROM evaluation WHERE finalized=1")
    eval_attended = scalar(
        cur,
        """
        SELECT COUNT(*)
        FROM evaluation
        WHERE finalized=1
          AND criteria IS NOT NULL
          AND LENGTH(TRIM(criteria)) > 0
        """,
    )
    eval_not_finalized = scalar(
        cur, "SELECT COUNT(*) FROM evaluation WHERE finalized=0 OR finalized IS NULL"
    )

    # Dropout candidates (legacy definition): joined but did not "attend"
    dropout_candidates = scalar(
        cur,
        """
        SELECT COUNT(*)
        FROM requirements r
        LEFT JOIN evaluation e ON e.requirementId = r.id
        WHERE r.accepted=1
          AND (
            e.id IS NULL
            OR e.finalized = 0
            OR e.finalized IS NULL
            OR e.criteria IS NULL
            OR LENGTH(TRIM(e.criteria)) = 0
          )
        """,
    )

    # Satisfaction storage
    has_sat = table_exists(cur, "satisfactionSurveys")
    sat_rows = scalar(cur, "SELECT COUNT(*) FROM satisfactionSurveys") if has_sat else 0

    # Participation history (pre-aggregated)
    has_vph = table_exists(cur, "volunteerParticipationHistory")
    vph_rows = (
        scalar(cur, "SELECT COUNT(*) FROM volunteerParticipationHistory") if has_vph else 0
    )

    print("\n=== JOIN / ANSWER STATUS ===")
    print(f"requirements accepted (joined): {joined}")
    print(f"evaluation rows (total templates + submissions): {eval_total}")
    print(f"evaluation finalized=1 (submitted): {eval_finalized}")
    print(f"evaluation finalized=1 with non-empty criteria (attended): {eval_attended}")
    print(f"evaluation not finalized (not answered yet): {eval_not_finalized}")
    print(f"dropout candidates (joined but not attended): {dropout_candidates}")

    print("\n=== SATISFACTION STORAGE ===")
    print(f"satisfactionSurveys table exists: {has_sat}")
    print(f"satisfactionSurveys rows: {sat_rows}")

    print("\n=== PRE-AGGREGATED PARTICIPATION ===")
    print(f"volunteerParticipationHistory table exists: {has_vph}")
    print(f"volunteerParticipationHistory rows: {vph_rows}")
    if has_vph and vph_rows == 0:
        print(
            "ℹ️  Note: dropout analytics will fall back to legacy computation until this table is populated."
        )
        print(
            "   You can populate it by running: python populate_volunteer_participation_history.py"
        )

    conn.close()


if __name__ == '__main__':
    main()






