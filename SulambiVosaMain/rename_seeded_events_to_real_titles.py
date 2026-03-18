#!/usr/bin/env python3
"""
Rename generic seeded events (e.g., "Community Service Event 2025-1-3") to realistic titles.

Targets:
- internalEvents titles starting with "Community Service Event "
- optionally, older "TEST Analytics ..." titles (if present)

Safe behavior:
- Only updates rows that match known patterns.
- Keeps the year/semester/month suffix for traceability.
"""

import os
import re
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


THEMES = [
    "Beach Cleaning",
    "Coastal Cleanup",
    "Tree Planting",
    "Mangrove Restoration",
    "Community Feeding Program",
    "Food Distribution Drive",
    "School Supply Donation",
    "Clothing Donation Drive",
    "Blood Donation Activity",
    "Medical Mission",
    "Environmental Awareness Campaign",
    "Clean-Up Drive",
    "Recycling Program",
    "Community Outreach Program",
    "Disaster Relief Operation",
]


def _pick_theme(year: int, sem: int, month: int) -> str:
    # Deterministic: same (year, sem, month) always maps to same theme.
    idx = (year * 100 + sem * 10 + month) % len(THEMES)
    return THEMES[idx]


def main() -> None:
    db_path = _resolve_db_path()
    print("=" * 70)
    print("RENAMING SEEDED EVENTS TO REALISTIC TITLES")
    print("=" * 70)
    print(f"Database: {db_path}")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        # Ensure internalEvents exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='internalEvents'")
        if not cur.fetchone():
            raise RuntimeError("internalEvents table not found. Start the backend once to initialize tables.")

        # Rename "Community Service Event YYYY-S-M" (legacy)
        cur.execute("SELECT id, title FROM internalEvents WHERE title LIKE 'Community Service Event %'")
        rows = cur.fetchall()

        legacy_pattern = re.compile(r"^Community Service Event (\d{4})-(\d)-(\d{1,2})$")
        # Also rename any already-human titles that include the seed suffix "(YYYY S# M#)"
        # so they can be remapped to the user's preferred theme list.
        cur.execute("SELECT id, title FROM internalEvents WHERE title LIKE '%(____ S_ M_)%' OR title LIKE '%(____ S_ M__)%'")
        rows_with_suffix = cur.fetchall()
        rows += rows_with_suffix

        suffix_pattern = re.compile(r"^(.+?) \((\d{4}) S(\d) M(\d{1,2})\)(?: #\d+)?$")
        updated = 0
        skipped = 0

        seen_ids = set()
        for event_id, title in rows:
            if event_id in seen_ids:
                continue
            seen_ids.add(event_id)

            t = (title or "").strip()
            m1 = legacy_pattern.match(t)
            m2 = suffix_pattern.match(t)
            if m1:
                year = int(m1.group(1))
                sem = int(m1.group(2))
                month = int(m1.group(3))
            elif m2:
                year = int(m2.group(2))
                sem = int(m2.group(3))
                month = int(m2.group(4))
            else:
                skipped += 1
                continue

            theme = _pick_theme(year, sem, month)
            new_title = f"{theme} ({year} S{sem} M{month})"

            # Avoid collision: if another event already has same title, append id
            cur.execute("SELECT id FROM internalEvents WHERE title = ? LIMIT 1", (new_title,))
            existing = cur.fetchone()
            if existing and int(existing[0]) != int(event_id):
                new_title = f"{new_title} #{event_id}"

            cur.execute("UPDATE internalEvents SET title = ? WHERE id = ?", (new_title, event_id))
            updated += 1

        conn.commit()
        print(f"[OK] Renamed {updated} internal events.")
        if skipped:
            print(f"[OK] Skipped {skipped} internal events (pattern mismatch).")

        # Also rename older "TEST Analytics ..." if present (optional cleanup)
        year_now = datetime.now().year
        cur.execute("SELECT id, title FROM internalEvents WHERE title = ?", (f"TEST Analytics Internal Event ({year_now}-S1)",))
        row = cur.fetchone()
        if row:
            event_id, _ = row
            cur.execute(
                "UPDATE internalEvents SET title = ? WHERE id = ?",
                (f"Beach Cleanup Drive ({year_now} S1)", event_id),
            )
            conn.commit()
            print("[OK] Renamed legacy TEST internal event title.")

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='externalEvents'")
        if cur.fetchone():
            cur.execute("SELECT id, title FROM externalEvents WHERE title = ?", (f"TEST Analytics External Event ({year_now}-S2)",))
            row = cur.fetchone()
            if row:
                event_id, _ = row
                cur.execute(
                    "UPDATE externalEvents SET title = ? WHERE id = ?",
                    (f"Community Feeding Program ({year_now} S2)", event_id),
                )
                conn.commit()
                print("[OK] Renamed legacy TEST external event title.")

        print("Done. Refresh the app event list to see the new titles.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


