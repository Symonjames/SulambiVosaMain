"""
Insert finalized volunteer rows into satisfactionSurveys (PostgreSQL) from a CSV.

Use this when volunteers did not submit via the app but you want analytics to count them.

Run from sulambi-backend-main with DATABASE_URL pointing at the target DB:

  # Preview (no writes)
  python backfill_volunteer_satisfaction_from_csv.py --csv data/volunteer_backfill.csv --dry-run

  # Apply (prompts unless --yes)
  python backfill_volunteer_satisfaction_from_csv.py --csv data/volunteer_backfill.csv --apply --yes

CSV columns (header row, extra columns ignored):
  email, name, event_id, event_type, overall_satisfaction
Optional:
  submitted_at_ms, comment, recommendations, q13, q14,
  organization_rating, communication_rating, materials_rating, support_rating, venue_rating

event_type must be "internal" or "external".
overall_satisfaction must be between 1 and 5 (decimals allowed).
Do not use respondent emails matching seeded_%@example.com (excluded from analytics).
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from app.database.connection import (  # noqa: E402
    DATABASE_URL,
    convert_boolean_value,
    is_postgresql_url,
)
from app.models.SatisfactionSurveyModel import SatisfactionSurveyModel  # noqa: E402


def _norm_header(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_")


def _row_dict(raw: dict) -> dict:
    return {_norm_header(k): (v or "").strip() if isinstance(v, str) else v for k, v in raw.items()}


def _float01_5(val: str, field: str) -> float:
    try:
        x = float(str(val).strip())
    except (TypeError, ValueError) as e:
        raise ValueError(f"{field}: invalid number {val!r}") from e
    if x < 1 or x > 5:
        raise ValueError(f"{field}: must be between 1 and 5, got {x}")
    return x


def _existing_volunteer_survey(db: SatisfactionSurveyModel, event_id: int, event_type: str, email: str) -> bool:
    rows = db.getAndSearch(
        ["eventId", "eventType", "respondentEmail", "respondentType"],
        [event_id, event_type, email, "Volunteer"],
    )
    return len(rows) > 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print plan; do not write")
    parser.add_argument("--apply", action="store_true", help="Perform inserts")
    parser.add_argument("--yes", action="store_true", help="With --apply, skip confirmation prompt")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Specify --dry-run and/or --apply.")
        return 2

    if not is_postgresql_url(DATABASE_URL):
        print("DATABASE_URL must be a PostgreSQL URL. This script does not use SQLite.")
        return 2

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        print(f"CSV not found: {csv_path}")
        return 2

    db = SatisfactionSurveyModel()
    planned = []
    errors: list[str] = []

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("CSV has no header row.")
            return 2
        for i, raw in enumerate(reader, start=2):
            if not raw or not any((v or "").strip() for v in raw.values()):
                continue
            d = _row_dict(raw)
            try:
                email = (d.get("email") or "").strip()
                name = (d.get("name") or "").strip()
                event_id = int(d.get("event_id") or d.get("eventid") or 0)
                event_type = (d.get("event_type") or d.get("eventtype") or "").strip().lower()
                overall = _float01_5(d.get("overall_satisfaction") or d.get("overall") or "", "overall_satisfaction")
            except (ValueError, TypeError) as e:
                errors.append(f"Row {i}: {e}")
                continue

            if not email:
                errors.append(f"Row {i}: email is required")
                continue
            el = email.lower()
            if el.startswith("seeded_") and el.endswith("@example.com"):
                errors.append(f"Row {i}: email matches seeded demo pattern; use a real email")
                continue
            if event_type not in ("internal", "external"):
                errors.append(f"Row {i}: event_type must be internal or external, got {event_type!r}")
                continue
            if event_id <= 0:
                errors.append(f"Row {i}: event_id must be a positive integer")
                continue

            sub_ms = d.get("submitted_at_ms") or d.get("submittedat")
            if sub_ms not in (None, ""):
                try:
                    submitted_at = int(float(str(sub_ms).strip()))
                except (ValueError, TypeError):
                    errors.append(f"Row {i}: submitted_at_ms invalid")
                    continue
            else:
                submitted_at = int(time.time() * 1000)

            org = _optional_rating(d.get("organization_rating"), overall)
            comm = _optional_rating(d.get("communication_rating"), overall)
            mat = _optional_rating(d.get("materials_rating"), overall)
            sup = _optional_rating(d.get("support_rating"), overall)
            venue_raw = d.get("venue_rating")
            venue = None
            if venue_raw not in (None, ""):
                try:
                    venue = _float01_5(venue_raw, "venue_rating")
                except ValueError as e:
                    errors.append(f"Row {i}: {e}")
                    continue

            q13 = (d.get("q13") or "").strip() or str(overall)
            q14 = (d.get("q14") or "").strip() or "-"
            comment = (d.get("comment") or "").strip() or "Administrative backfill."
            recommendations = (d.get("recommendations") or "").strip() or "N/A"

            planned.append(
                {
                    "line": i,
                    "email": email,
                    "name": name,
                    "event_id": event_id,
                    "event_type": event_type,
                    "overall": overall,
                    "submitted_at": submitted_at,
                    "org": org,
                    "comm": comm,
                    "mat": mat,
                    "sup": sup,
                    "venue": venue,
                    "q13": q13,
                    "q14": q14,
                    "comment": comment,
                    "recommendations": recommendations,
                }
            )

    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    if not planned:
        print("No data rows to import.")
        return 1

    skip_existing: list[str] = []
    to_insert: list[dict] = []
    for p in planned:
        if _existing_volunteer_survey(db, p["event_id"], p["event_type"], p["email"]):
            skip_existing.append(f"row {p['line']}: {p['email']} event {p['event_id']} ({p['event_type']})")
            continue
        to_insert.append(p)

    print(f"Rows in CSV: {len(planned)}")
    print(f"Would insert: {len(to_insert)}")
    print(f"Skip (already have volunteer survey for event+email): {len(skip_existing)}")
    for s in skip_existing[:20]:
        print(f"  skip: {s}")
    if len(skip_existing) > 20:
        print(f"  ... and {len(skip_existing) - 20} more")

    if args.dry_run:
        print("\nDry run — no database writes.")
        for p in to_insert[:10]:
            print(
                f"  insert row {p['line']}: email={p['email']} event={p['event_id']} "
                f"type={p['event_type']} overall={p['overall']}"
            )
        if len(to_insert) > 10:
            print(f"  ... and {len(to_insert) - 10} more")
        return 0

    if not args.apply:
        return 0

    if not args.yes:
        confirm = input(f"Insert {len(to_insert)} rows into production database? Type YES: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return 1

    is_pg = is_postgresql_url(DATABASE_URL)
    finalized_val = convert_boolean_value(True) if is_pg else True

    inserted = 0
    for p in to_insert:
        overall = float(p["overall"])
        would_rec = convert_boolean_value(overall >= 4) if is_pg else (overall >= 4)
        pos = p["comment"] if overall >= 4 else ""

        db.create(
            eventId=int(p["event_id"]),
            eventType=str(p["event_type"]),
            requirementId=str(uuid.uuid4()),
            respondentType="Volunteer",
            respondentEmail=p["email"],
            respondentName=p["name"],
            overallSatisfaction=overall,
            volunteerRating=overall,
            beneficiaryRating=None,
            organizationRating=float(p["org"]),
            communicationRating=float(p["comm"]),
            venueRating=p["venue"],
            materialsRating=float(p["mat"]),
            supportRating=float(p["sup"]),
            q13=p["q13"],
            q14=p["q14"],
            comment=p["comment"],
            recommendations=p["recommendations"],
            wouldRecommend=would_rec,
            areasForImprovement="",
            positiveAspects=pos,
            submittedAt=int(p["submitted_at"]),
            finalized=finalized_val,
        )
        inserted += 1

    print(f"Done. Inserted {inserted} satisfaction survey row(s).")
    return 0


def _optional_rating(raw, default: float) -> float:
    if raw in (None, ""):
        return float(default)
    return _float01_5(raw, "rating")


if __name__ == "__main__":
    raise SystemExit(main())
