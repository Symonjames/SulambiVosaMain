#!/usr/bin/env python3
"""
Create 2 accepted test events (1 internal, 1 external) for dashboard analytics.

- Uses the same DB_PATH resolution approach as other scripts in this repo.
- Inserts events only if they don't already exist (by title).
"""

import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv


def _backend_dir() -> str:
    return os.path.join(
        "Technology Transfer _ Sulambi VMS",
        "Source Code",
        "sulambi-backend-main",
        "sulambi-backend-main",
    )


def _resolve_db_path() -> str:
    backend_dir = _backend_dir()
    load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
    db_path = os.getenv("DB_PATH")
    if not db_path:
        return os.path.join(backend_dir, "app", "database", "database.db")
    if not os.path.isabs(db_path):
        return os.path.join(backend_dir, db_path)
    return db_path


def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _ensure_tables_exist(conn: sqlite3.Connection) -> None:
    # Table initializer is normally run when backend starts; this is a lightweight guard.
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('internalEvents','externalEvents')"
    )
    rows = {r[0] for r in cur.fetchall()}
    if "internalEvents" not in rows or "externalEvents" not in rows:
        raise RuntimeError(
            "Missing events tables. Start the backend once (it creates tables), then re-run this script."
        )


def main() -> None:
    db_path = _resolve_db_path()
    print("=" * 70)
    print("CREATING 2 TEST EVENTS FOR ANALYTICS")
    print("=" * 70)
    print(f"Database: {db_path}")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        _ensure_tables_exist(conn)
        cur = conn.cursor()

        # Put them in different semesters for nicer charts (Jan and Aug of current year).
        now = datetime.now()
        year = now.year

        internal_start = datetime(year, 1, 15, 9, 0, 0)
        internal_end = datetime(year, 1, 15, 17, 0, 0)
        external_start = datetime(year, 8, 20, 9, 0, 0)
        external_end = datetime(year, 8, 20, 17, 0, 0)

        # Friendly, realistic titles (what you'll see in the UI)
        internal_title = f"Beach Cleaning ({year} S1)"
        external_title = f"Community Feeding Program ({year} S2)"

        # Previous titles used by earlier versions of this script (for rename-on-run)
        old_internal_title = f"TEST Analytics Internal Event ({year}-S1)"
        old_external_title = f"TEST Analytics External Event ({year}-S2)"
        old_internal_title_2 = f"Beach Cleanup Drive ({year} S1)"

        # INTERNAL EVENT
        # If an old test title exists, rename it to the new title so UI looks nicer.
        for prev in (old_internal_title, old_internal_title_2):
            cur.execute("SELECT id FROM internalEvents WHERE title = ? LIMIT 1", (prev,))
            old_internal_row = cur.fetchone()
            if old_internal_row:
                old_id = old_internal_row[0]
                cur.execute("UPDATE internalEvents SET title = ? WHERE id = ?", (internal_title, old_id))
                internal_id = old_id
                print(f"[OK] Renamed internal event: id={internal_id} '{prev}' -> '{internal_title}'")
        cur.execute("SELECT id FROM internalEvents WHERE title = ? LIMIT 1", (internal_title,))
        internal_row = cur.fetchone()
        if internal_row:
            internal_id = internal_row[0]
            print(f"[OK] Internal event already exists: id={internal_id} title='{internal_title}'")
        else:
            cur.execute(
                """
                INSERT INTO internalEvents (
                    title, durationStart, durationEnd, venue, modeOfDelivery,
                    projectTeam, partner, participant, maleTotal, femaleTotal,
                    rationale, objectives, description, workPlan, financialRequirement,
                    evaluationMechanicsPlan, sustainabilityPlan, createdBy, status,
                    toPublic, evaluationSendTime, eventProposalType
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    internal_title,
                    _ms(internal_start),
                    _ms(internal_end),
                    "Main Campus",
                    "Face-to-Face",
                    "[]",
                    "Test Partner",
                    "Students",
                    10,
                    10,
                    "Test rationale for analytics dashboard.",
                    "Test objectives for analytics dashboard.",
                    "This is a seeded internal test event.",
                    "[]",
                    "[]",
                    "[]",
                    "[]",
                    1,  # createdBy (Admin)
                    "accepted",
                    1,  # toPublic
                    _ms(internal_start),
                    "[]",
                ),
            )
            internal_id = cur.lastrowid
            print(f"[OK] Created internal event: id={internal_id} title='{internal_title}'")

        # EXTERNAL EVENT
        # If an old test title exists, rename it to the new title so UI looks nicer.
        cur.execute("SELECT id FROM externalEvents WHERE title = ? LIMIT 1", (old_external_title,))
        old_external_row = cur.fetchone()
        if old_external_row:
            old_id = old_external_row[0]
            cur.execute("UPDATE externalEvents SET title = ? WHERE id = ?", (external_title, old_id))
            external_id = old_id
            print(f"[OK] Renamed external event: id={external_id} '{old_external_title}' -> '{external_title}'")
        cur.execute("SELECT id FROM externalEvents WHERE title = ? LIMIT 1", (external_title,))
        external_row = cur.fetchone()
        if external_row:
            external_id = external_row[0]
            print(f"[OK] External event already exists: id={external_id} title='{external_title}'")
        else:
            cur.execute(
                """
                INSERT INTO externalEvents (
                    extensionServiceType, title, location, durationStart, durationEnd, sdg,
                    orgInvolved, programInvolved, projectLeader, partners, beneficiaries,
                    totalCost, sourceOfFund, rationale, objectives, expectedOutput, description,
                    financialPlan, dutiesOfPartner, evaluationMechanicsPlan, sustainabilityPlan,
                    createdBy, status, evaluationSendTime, toPublic, externalServiceType, eventProposalType
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Community Outreach",
                    external_title,
                    "Batangas City",
                    _ms(external_start),
                    _ms(external_end),
                    "SDG 3 - Good Health and Well-being",
                    "Test Org",
                    "Test Program",
                    "Test Leader",
                    "Test Partners",
                    "Community",
                    0.0,
                    "N/A",
                    "Test rationale for analytics dashboard.",
                    "Test objectives for analytics dashboard.",
                    "Test expected output.",
                    "This is a seeded external test event.",
                    "[]",
                    "[]",
                    "[]",
                    "[]",
                    1,  # createdBy (Admin)
                    "accepted",
                    _ms(external_start),
                    1,  # toPublic
                    "Community Outreach",
                    "[]",
                ),
            )
            external_id = cur.lastrowid
            print(f"[OK] Created external event: id={external_id} title='{external_title}'")

        conn.commit()
        print("\nDone. These 2 events should now appear in the app (and can be used for analytics).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


