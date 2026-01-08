#!/usr/bin/env python3
"""
Seed a MIX of participation states for analytics:

- Some members: did NOT join any event (no requirements) -> "not participated"
- Some members: joined but did NOT submit the participant form (requirements only) -> "dropout risk"
- Some members: joined AND submitted participant form (requirements + finalized evaluation) -> "participated"

This matches the current analytics assumptions:
- Joined = requirements.accepted = 1
- Attended/Participated = evaluation.finalized = 1 with non-empty criteria for that requirementId
"""

import os
import random
import sqlite3
import time
import json
from dataclasses import dataclass
from typing import List, Tuple

from dotenv import load_dotenv


@dataclass
class EventRef:
    event_id: int
    event_type: str  # "internal" | "external"


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


def _get_accepted_events(conn: sqlite3.Connection) -> List[EventRef]:
    cur = conn.cursor()
    events: List[EventRef] = []
    # Internal
    cur.execute("SELECT id FROM internalEvents WHERE status IN ('accepted','completed') ORDER BY durationStart ASC")
    events += [EventRef(int(r[0]), "internal") for r in cur.fetchall()]
    # External
    cur.execute("SELECT id FROM externalEvents WHERE status IN ('accepted','completed') ORDER BY durationStart ASC")
    events += [EventRef(int(r[0]), "external") for r in cur.fetchall()]
    return events


def _get_active_accepted_members(conn: sqlite3.Connection) -> List[Tuple[int, str, str]]:
    """
    Returns list of (membershipId, email, fullname).
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, email, fullname
        FROM membership
        WHERE accepted = 1 AND active = 1
        ORDER BY id ASC
        """
    )
    return [(int(r[0]), str(r[1]), str(r[2])) for r in cur.fetchall()]


def _ensure_members_are_active_and_accepted(conn: sqlite3.Connection, limit: int = 200) -> int:
    """
    If you have members where accepted is NULL/0, analytics won't include them.
    This function promotes a batch to accepted+active so they can show in analytics.
    """
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE membership
        SET accepted = 1, active = 1
        WHERE id IN (
          SELECT id FROM membership
          WHERE (accepted IS NULL OR accepted = 0) OR (active IS NULL OR active = 0)
          ORDER BY id ASC
          LIMIT ?
        )
        """,
        (int(limit),),
    )
    conn.commit()
    return cur.rowcount or 0


def _make_req_id(email: str, event: EventRef) -> str:
    # requirements.id is a string primary key; keep it unique and readable
    ts = int(time.time() * 1000)
    salt = random.randint(1000, 9999)
    return f"REQ-{ts}-{salt}-{event.event_type[:1].upper()}{event.event_id}-{abs(hash(email)) % 100000}"


def _insert_requirement(conn: sqlite3.Connection, req_id: str, event: EventRef, member_row: Tuple[int, str, str]) -> None:
    membership_id, email, fullname = member_row
    # Pull demographics for better charts (fallback safe)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram, address, contactNum, fblink, affiliation
        FROM membership
        WHERE id = ?
        """,
        (membership_id,),
    )
    r = cur.fetchone()
    if r:
        srcode, age, birthday, sex, campus, college_dept, yrlevel_program, address, contact_num, fblink, affiliation = r
    else:
        srcode, age, birthday, sex, campus, college_dept, yrlevel_program, address, contact_num, fblink, affiliation = (
            "",
            20,
            "January, 01 2000",
            "Male",
            "Main Campus",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
        )

    cur.execute(
        """
        INSERT INTO requirements (
            id, medCert, waiver, type, eventId, affiliation, fullname, email,
            srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
            address, contactNum, fblink, accepted
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            req_id,
            f"documents/med_cert_{req_id}.pdf",
            f"documents/waiver_{req_id}.pdf",
            event.event_type,
            event.event_id,
            str(affiliation or "N/A"),
            fullname,
            email,
            str(srcode or ""),
            int(age or 20),
            str(birthday or "January, 01 2000"),
            str(sex or "Male"),
            str(campus or "Main Campus"),
            str(college_dept or "N/A"),
            str(yrlevel_program or "N/A"),
            str(address or "N/A"),
            str(contact_num or "N/A"),
            str(fblink or "N/A"),
            1,
        ),
    )


def _insert_finalized_evaluation(conn: sqlite3.Connection, req_id: str, base_score: float) -> None:
    cur = conn.cursor()
    score = max(1.0, min(5.0, round(random.gauss(base_score, 0.6), 1)))
    comment_pool = [
        "Well organized and engaging.",
        "Great activity, would join again.",
        "Good coordination but could improve timing.",
        "Enjoyed participating.",
        "Helpful and impactful.",
    ]
    comment = random.choice(comment_pool)
    criteria = {
        "overall": score,
        "satisfaction": score,
        "rating": score,
        "comment": comment,
    }
    cur.execute(
        """
        INSERT INTO evaluation (
            requirementId, criteria, q13, q14, comment, recommendations, finalized
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            req_id,
            json.dumps(criteria),
            str(score),
            str(score),
            comment,
            "Keep improving community engagement.",
            1,
        ),
    )


def main() -> None:
    random.seed(42)  # reproducible mix
    db_path = _resolve_db_path()
    print("=" * 70)
    print("SEEDING MIXED PARTICIPATION FOR ANALYTICS")
    print("=" * 70)
    print(f"Database: {db_path}")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        promoted = _ensure_members_are_active_and_accepted(conn, limit=500)
        if promoted:
            print(f"[OK] Promoted {promoted} member(s) to accepted+active for analytics.")

        members = _get_active_accepted_members(conn)
        if len(members) == 0:
            print("[WARN] No accepted+active members found. Seed members first (Mockaroo loader or seed script).")
            return

        events = _get_accepted_events(conn)
        if len(events) == 0:
            print("[WARN] No accepted/completed events found. Create events first (create_two_test_events.py).")
            return

        # --- Mix configuration ---
        # 50% will join at least one event, 50% will not join anything.
        join_rate = 0.50
        # Of those who joined: 65% will submit the form (finalized evaluation), 35% will not (dropout risk).
        attend_rate_given_join = 0.65
        # Each joiner will join 1-2 events.
        min_events_per_joiner = 1
        max_events_per_joiner = 2

        total = len(members)
        joiners_target = int(total * join_rate)
        joiners = random.sample(members, k=min(joiners_target, total))
        non_joiners = [m for m in members if m not in joiners]

        # Among joiners, pick attenders
        attenders_target = int(len(joiners) * attend_rate_given_join)
        attenders = set(random.sample(joiners, k=min(attenders_target, len(joiners))))
        dropouts = [m for m in joiners if m not in attenders]

        print(f"[OK] Members total: {total}")
        print(f"[OK] Not participated (no joins): {len(non_joiners)}")
        print(f"[OK] Joined but did NOT submit form (dropout risk): {len(dropouts)}")
        print(f"[OK] Participated (joined + submitted form): {len(attenders)}")

        # Insert requirements/evaluations
        cur = conn.cursor()
        inserted_reqs = 0
        inserted_evals = 0

        for member in joiners:
            num_events = random.randint(min_events_per_joiner, max_events_per_joiner)
            chosen_events = random.sample(events, k=min(num_events, len(events)))
            for ev in chosen_events:
                req_id = _make_req_id(member[1], ev)
                try:
                    _insert_requirement(conn, req_id, ev, member)
                    inserted_reqs += 1
                except sqlite3.IntegrityError:
                    continue

                if member in attenders:
                    _insert_finalized_evaluation(conn, req_id, base_score=4.1)
                    inserted_evals += 1

        conn.commit()

        # Print quick stats
        cur.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
        total_reqs = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1 AND criteria IS NOT NULL AND criteria != ''")
        total_attended = cur.fetchone()[0] or 0

        print("\n" + "=" * 70)
        print("[OK] MIXED PARTICIPATION SEEDED")
        print("=" * 70)
        print(f"[OK] Inserted requirements (joins): {inserted_reqs}")
        print(f"[OK] Inserted finalized evaluations (forms submitted): {inserted_evals}")
        print(f"[OK] DB totals: requirements={total_reqs}, finalizedEvaluations={total_attended}")
        print("\nNext: run populate_volunteer_participation_history.py to refresh dropout analytics.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()












