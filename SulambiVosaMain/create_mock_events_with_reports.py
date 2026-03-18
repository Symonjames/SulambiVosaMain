#!/usr/bin/env python3
"""
Create mock external/internal events with complete required fields,
and create one report for each event.

This script targets the local SQLite database used in dev.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


MOCK_EXTERNAL_TITLE = "MOCK External Event - Barangay Digital Literacy"
MOCK_INTERNAL_TITLE = "MOCK Internal Event - Volunteer Skills Bootcamp"


def _backend_dir() -> Path:
    return (
        Path(__file__).resolve().parent
        / "Technology Transfer _ Sulambi VMS"
        / "Source Code"
        / "sulambi-backend-main"
        / "sulambi-backend-main"
    )


def _resolve_db_path() -> Path:
    backend_dir = _backend_dir()
    env_db_path = os.getenv("DB_PATH", "").strip()

    if not env_db_path:
        return backend_dir / "app" / "database" / "database.db"

    env_path = Path(env_db_path)
    if env_path.is_absolute():
        return env_path

    return backend_dir / env_path


def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def _last_insert_id(cursor: sqlite3.Cursor, context: str) -> int:
    row_id = cursor.lastrowid
    if row_id is None:
        raise RuntimeError(f"Failed to read last inserted id for {context}")
    return int(row_id)


def _ensure_tables(cursor: sqlite3.Cursor) -> None:
    needed = {
        "accounts",
        "eventSignatories",
        "externalEvents",
        "internalEvents",
        "externalReport",
        "internalReport",
    }
    missing = [name for name in needed if not _table_exists(cursor, name)]
    if missing:
        raise RuntimeError(
            "Missing required tables: "
            + ", ".join(missing)
            + ". Run `python server.py --init` in backend first."
        )


def _get_admin_id(cursor: sqlite3.Cursor) -> int:
    cursor.execute(
        """
        SELECT id
        FROM accounts
        WHERE username = ?
        ORDER BY id ASC
        LIMIT 1
        """,
        ("Admin",),
    )
    row = cursor.fetchone()
    if not row:
        raise RuntimeError("Admin account not found. Run backend table init first.")
    return int(row[0])


def _create_signatories(cursor: sqlite3.Cursor) -> int:
    cursor.execute(
        """
        INSERT INTO eventSignatories (
            preparedBy,
            reviewedBy,
            recommendingApproval1,
            recommendingApproval2,
            approvedBy
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Mock Event Preparer",
            "Mock Event Reviewer",
            "Mock Recommender 1",
            "Mock Recommender 2",
            "Mock Approver",
        ),
    )
    return _last_insert_id(cursor, "eventSignatories")


def _get_event_id_by_title(cursor: sqlite3.Cursor, table_name: str, title: str) -> int | None:
    cursor.execute(
        f"SELECT id FROM {table_name} WHERE title = ? ORDER BY id DESC LIMIT 1",
        (title,),
    )
    row = cursor.fetchone()
    return int(row[0]) if row else None


def _get_event_id_by_title_prefix(cursor: sqlite3.Cursor, table_name: str, title_prefix: str) -> int | None:
    cursor.execute(
        f"SELECT id FROM {table_name} WHERE title LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{title_prefix}%",),
    )
    row = cursor.fetchone()
    return int(row[0]) if row else None


def _create_external_event(cursor: sqlite3.Cursor, admin_id: int) -> int:
    now = datetime.now()
    start = now + timedelta(days=14)
    end = start + timedelta(hours=6)
    title = MOCK_EXTERNAL_TITLE

    existing_id = _get_event_id_by_title_prefix(cursor, "externalEvents", MOCK_EXTERNAL_TITLE)
    if existing_id is not None:
        return existing_id

    signatory_id = _create_signatories(cursor)

    cursor.execute(
        """
        INSERT INTO externalEvents (
            extensionServiceType,
            title,
            location,
            durationStart,
            durationEnd,
            sdg,
            orgInvolved,
            programInvolved,
            projectLeader,
            partners,
            beneficiaries,
            totalCost,
            sourceOfFund,
            rationale,
            objectives,
            expectedOutput,
            description,
            financialPlan,
            dutiesOfPartner,
            evaluationMechanicsPlan,
            sustainabilityPlan,
            createdBy,
            status,
            evaluationSendTime,
            toPublic,
            externalServiceType,
            eventProposalType,
            signatoriesId,
            beneficiaryEvaluationPin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Community Outreach",
            title,
            "Barangay Batangas City",
            _ms(start),
            _ms(end),
            "SDG 4 - Quality Education",
            "BatStateU Extension Office",
            "Digital Inclusion Program",
            "Prof. Mock Leader",
            json.dumps(["LGU", "Local School", "SK Federation"]),
            "Out-of-school youth and community members",
            25000.0,
            "University Extension Fund",
            "Community members requested basic digital training and online safety guidance.",
            "Train beneficiaries in basic productivity tools and safe internet practices.",
            "At least 60 trained participants with completed learning checklist.",
            "A one-day outreach workshop with lecture and guided hands-on sessions.",
            json.dumps(
                [
                    {"item": "Training Kits", "amount": 8000},
                    {"item": "Meals and Snacks", "amount": 12000},
                    {"item": "Transport", "amount": 5000},
                ]
            ),
            "Partner institutions will provide venue support and participant mobilization.",
            json.dumps(
                {
                    "preTest": True,
                    "postTest": True,
                    "feedbackForm": True,
                    "targetCompletionRate": 0.85,
                }
            ),
            "Create a quarterly follow-up mentoring group for participants.",
            admin_id,
            "accepted",
            _ms(start + timedelta(days=7)),
            1,
            json.dumps(["Training", "Technology Transfer"]),
            json.dumps(["Extension", "External"]),
            signatory_id,
            "12345",
        ),
    )
    return _last_insert_id(cursor, "externalEvents")


def _create_internal_event(cursor: sqlite3.Cursor, admin_id: int) -> int:
    now = datetime.now()
    start = now + timedelta(days=10)
    end = start + timedelta(hours=4)
    title = MOCK_INTERNAL_TITLE

    existing_id = _get_event_id_by_title_prefix(cursor, "internalEvents", MOCK_INTERNAL_TITLE)
    if existing_id is not None:
        return existing_id

    signatory_id = _create_signatories(cursor)

    cursor.execute(
        """
        INSERT INTO internalEvents (
            title,
            durationStart,
            durationEnd,
            venue,
            modeOfDelivery,
            projectTeam,
            partner,
            participant,
            maleTotal,
            femaleTotal,
            rationale,
            objectives,
            description,
            workPlan,
            financialRequirement,
            evaluationMechanicsPlan,
            sustainabilityPlan,
            createdBy,
            status,
            toPublic,
            evaluationSendTime,
            eventProposalType,
            signatoriesId,
            beneficiaryEvaluationPin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            _ms(start),
            _ms(end),
            "BatStateU Main Campus AVR",
            "Face-to-Face",
            json.dumps(["Program Chair", "Training Facilitator", "Documentation Team"]),
            "BatStateU Student Organizations",
            "Volunteer Officers and New Volunteers",
            22,
            28,
            "Internal volunteers need standardized training before large-scale deployments.",
            "Equip volunteers with event operations, safety, and documentation skills.",
            "Half-day bootcamp with drills, role-play, and protocol walkthrough.",
            json.dumps(
                [
                    {"activity": "Orientation and Safety Briefing", "duration": "45m"},
                    {"activity": "Roles and Responsibilities Workshop", "duration": "60m"},
                    {"activity": "Simulation and Debrief", "duration": "90m"},
                ]
            ),
            json.dumps(
                {
                    "materials": 6000,
                    "food": 5000,
                    "logistics": 3000,
                    "total": 14000,
                }
            ),
            json.dumps(
                {
                    "attendanceCheck": True,
                    "skillsDemo": True,
                    "postTrainingQuiz": True,
                    "targetPassRate": 0.8,
                }
            ),
            "Create a reusable training kit and onboarding checklist for future cycles.",
            admin_id,
            "accepted",
            1,
            _ms(start + timedelta(days=5)),
            json.dumps(["Internal", "Capability Building"]),
            signatory_id,
            "67890",
        ),
    )
    return _last_insert_id(cursor, "internalEvents")


def _report_exists(cursor: sqlite3.Cursor, table_name: str, event_id: int) -> bool:
    cursor.execute(
        f"SELECT 1 FROM {table_name} WHERE eventId = ? LIMIT 1",
        (event_id,),
    )
    return cursor.fetchone() is not None


def _get_event_signatory_id(cursor: sqlite3.Cursor, table_name: str, event_id: int) -> int:
    cursor.execute(
        f"SELECT signatoriesId FROM {table_name} WHERE id = ? LIMIT 1",
        (event_id,),
    )
    row = cursor.fetchone()
    if not row or row[0] is None:
        raise RuntimeError(f"Event {event_id} in {table_name} has no signatoriesId")
    return int(row[0])


def _create_external_report(cursor: sqlite3.Cursor, event_id: int, signatory_id: int) -> int | None:
    if _report_exists(cursor, "externalReport", event_id):
        return None

    cursor.execute(
        """
        INSERT INTO externalReport (
            eventId,
            narrative,
            photos,
            photoCaptions,
            signatoriesId
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            "The outreach session was completed successfully with active beneficiary participation and positive learning outcomes.",
            "mock_external_photo_1.jpg,mock_external_photo_2.jpg",
            "Opening session,Hands-on training",
            signatory_id,
        ),
    )
    return _last_insert_id(cursor, "externalReport")


def _create_internal_report(cursor: sqlite3.Cursor, event_id: int, signatory_id: int) -> int | None:
    if _report_exists(cursor, "internalReport", event_id):
        return None

    cursor.execute(
        """
        INSERT INTO internalReport (
            eventId,
            narrative,
            approvedBudget,
            approvedBudgetSrc,
            budgetUtilized,
            budgetUtilizedSrc,
            psAttribution,
            psAttributionSrc,
            photos,
            photoCaptions,
            signatoriesId
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            "Volunteer bootcamp concluded with strong attendance and successful simulation outputs.",
            15000,
            "Approved GAD internal allocation based on committee review.",
            13000,
            "Fund disbursement summary attached in finance records.",
            50,
            "Participant roster and facilitator attendance sheets.",
            "mock_internal_photo_1.jpg,mock_internal_photo_2.jpg",
            "Skills drill,Closing photo",
            signatory_id,
        ),
    )
    return _last_insert_id(cursor, "internalReport")


def main() -> None:
    db_path = _resolve_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        _ensure_tables(cur)

        admin_id = _get_admin_id(cur)

        external_event_id = _create_external_event(cur, admin_id)
        internal_event_id = _create_internal_event(cur, admin_id)

        ext_signatory_id = _get_event_signatory_id(cur, "externalEvents", external_event_id)
        int_signatory_id = _get_event_signatory_id(cur, "internalEvents", internal_event_id)

        external_report_id = _create_external_report(cur, external_event_id, ext_signatory_id)
        internal_report_id = _create_internal_report(cur, internal_event_id, int_signatory_id)

        conn.commit()

        print("DB:", db_path)
        print("Admin account id:", admin_id)
        print("External event id:", external_event_id)
        print("Internal event id:", internal_event_id)
        print("External report id:", external_report_id if external_report_id is not None else "already exists")
        print("Internal report id:", internal_report_id if internal_report_id is not None else "already exists")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
