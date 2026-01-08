"""
Show where "Volunteer Dropout Risk" data lives in the database (SQLite).

Current API behavior:
- /api/analytics/volunteer-dropout prefers volunteerParticipationHistory (pre-aggregated per semester)
- If volunteerParticipationHistory is missing/empty, it derives dropout from requirements vs evaluation.

This script prints:
- Whether volunteerParticipationHistory exists + row count
- A semester summary (top few rows)
- Top "at-risk" candidates (derived like the API: inactivity + joined/attended)
"""

import os
import sqlite3
from datetime import datetime


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

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("\n=== volunteerParticipationHistory (primary source) ===")
    has_vph = table_exists(cur, "volunteerParticipationHistory")
    print("table exists:", has_vph)
    vph_rows = scalar(cur, "SELECT COUNT(1) FROM volunteerParticipationHistory") if has_vph else 0
    print("rows:", vph_rows)

    if has_vph and vph_rows:
        print("\n-- semester summary (first 10) --")
        cur.execute(
            """
            SELECT semester,
                   COUNT(DISTINCT volunteerEmail) AS total_volunteers,
                   SUM(eventsJoined) AS total_joined,
                   SUM(eventsAttended) AS total_attended,
                   SUM(eventsDropped) AS total_dropped,
                   ROUND(AVG(attendanceRate), 2) AS avg_attendance_rate
            FROM volunteerParticipationHistory
            GROUP BY semester
            ORDER BY semester
            LIMIT 10
            """
        )
        for row in cur.fetchall():
            print(row)

    print("\n=== Derived 'dropout candidates' (legacy definition) ===")
    # Joined (accepted requirements)
    joined = scalar(cur, "SELECT COUNT(1) FROM requirements WHERE accepted=1")
    attended = scalar(
        cur,
        """
        SELECT COUNT(1)
        FROM requirements r
        INNER JOIN evaluation e ON e.requirementId = r.id
        WHERE r.accepted=1
          AND e.finalized=1
          AND e.criteria IS NOT NULL
          AND LENGTH(TRIM(e.criteria)) > 0
        """,
    )
    dropouts = scalar(
        cur,
        """
        SELECT COUNT(1)
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
    print("requirements accepted (joined):", joined)
    print("attended (finalized + non-empty criteria):", attended)
    print("dropout candidates (joined but not attended):", dropouts)

    print("\n=== At-risk volunteers (computed like the API) ===")
    # Similar to getVolunteerDropoutAnalytics: start from membership accepted+active, LEFT JOIN vph
    now_ms = int(datetime.now().timestamp() * 1000)
    ms_per_day = 1000 * 60 * 60 * 24
    cur.execute(
        """
        SELECT
          m.email,
          m.fullname,
          COALESCE(MAX(vph.lastEventDate), 0) AS most_recent_date,
          COALESCE(SUM(vph.eventsJoined), 0) AS total_joined,
          COALESCE(SUM(vph.eventsAttended), 0) AS total_attended,
          COALESCE(AVG(vph.attendanceRate), 0) AS avg_attendance_rate,
          COALESCE(COUNT(DISTINCT vph.semester), 0) AS semesters_active
        FROM membership m
        LEFT JOIN volunteerParticipationHistory vph ON m.email = vph.volunteerEmail
        WHERE m.accepted = 1 AND m.active = 1
        GROUP BY m.email, m.fullname
        """
    )
    rows = cur.fetchall()

    at_risk = []
    for email, name, most_recent_date, total_joined, total_attended, avg_attendance_rate, semesters_active in rows:
        attendance_rate = float(avg_attendance_rate) if avg_attendance_rate else 0.0
        inactivity_days = 0
        if most_recent_date and most_recent_date > 0:
            inactivity_days = int((now_ms - int(most_recent_date)) / ms_per_day)
        elif total_joined == 0 and total_attended == 0:
            inactivity_days = 365

        risk_score = 0
        if total_joined == 0 and total_attended == 0:
            risk_score += 50
        else:
            if attendance_rate < 50:
                risk_score += 40
            elif attendance_rate < 70:
                risk_score += 25
            elif attendance_rate < 85:
                risk_score += 10

            if total_attended == 0 and total_joined > 0:
                risk_score += 50
            elif total_attended < 2:
                risk_score += 10

        if inactivity_days > 90:
            risk_score += 40
        elif inactivity_days > 60:
            risk_score += 25
        elif inactivity_days > 30:
            risk_score += 15

        if semesters_active == 1:
            risk_score += 10
        elif semesters_active == 0:
            risk_score += 20

        risk_score = min(100, risk_score)
        if risk_score >= 50:
            last_event = "Never"
            if most_recent_date and most_recent_date > 0:
                last_event = datetime.fromtimestamp(int(most_recent_date) / 1000).strftime("%Y-%m-%d")
            at_risk.append((risk_score, name, email, inactivity_days, total_joined, total_attended, round(attendance_rate, 1), last_event))

    at_risk.sort(key=lambda x: x[0], reverse=True)
    for row in at_risk[:10]:
        print(row)

    conn.close()


if __name__ == "__main__":
    main()






