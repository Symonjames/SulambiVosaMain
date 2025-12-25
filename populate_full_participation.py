#!/usr/bin/env python3
"""
Populate full participation:
- Approve all members
- Ensure five events exist (internal)
- Create participation (requirements) entries for every member across all five events
- Fix event timestamps to milliseconds if needed
- Create finalized evaluations for each participation to count as attended
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

EVENT_TITLES = [
  "Blood Donation Part 2",
  "Blood Donation",
  "Example",
  "Animal Adoption",
  "EXAMPLE7",
]

def fix_events_timestamp_ms(conn):
  """Ensure durationStart/durationEnd are stored in milliseconds."""
  cur = conn.cursor()
  cur.execute("SELECT id, title, durationStart, durationEnd FROM internalEvents")
  rows = cur.fetchall()
  updated = 0
  for eid, title, ds, de in rows:
    # Heuristic: if value is in seconds (10 digits), convert to ms
    if ds is not None and de is not None and ds < 10_000_000_000 and de < 10_000_000_000:
      cur.execute(
        "UPDATE internalEvents SET durationStart = ?, durationEnd = ? WHERE id = ?",
        (int(ds * 1000), int(de * 1000), eid),
      )
      updated += 1
  if updated:
    conn.commit()
  return updated

def ensure_events(conn):
  cursor = conn.cursor()
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='internalEvents'")
  if not cursor.fetchone():
    raise RuntimeError("internalEvents table not found. Run backend init first.")

  existing = {}
  cursor.execute("SELECT id, title FROM internalEvents")
  for row in cursor.fetchall():
    existing[row[1]] = row[0]

  ids = {}
  now = datetime.now()
  for title in EVENT_TITLES:
    if title in existing:
      ids[title] = existing[title]
      continue
    start = now + timedelta(days=random.randint(1, 30))
    end = start + timedelta(days=random.randint(1, 3))
    cursor.execute(
      """
      INSERT INTO internalEvents (
        title, durationStart, durationEnd, venue, modeOfDelivery,
        projectTeam, partner, participant, maleTotal, femaleTotal,
        rationale, objectives, description, workPlan, financialRequirement,
        evaluationMechanicsPlan, sustainabilityPlan, createdBy, status,
        toPublic, evaluationSendTime, signatoriesId, createdAt, feedback_id, eventProposalType
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      """,
      (
        title,
        int(start.timestamp() * 1000),
        int(end.timestamp() * 1000),
        "Main Hall",
        "Face-to-Face",
        "Team A, Team B",
        "Partner Org",
        "Students",
        "0",
        "0",
        "Auto-created for testing",
        "Objectives",
        "Description",
        "[]",
        "[]",
        "[]",
        "Sustainability",
        1,
        "accepted",
        True,
        0,
        None,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        None,
        "[]",
      )
    )
    ids[title] = cursor.lastrowid
  conn.commit()
  return ids

def approve_all_members(conn):
  cursor = conn.cursor()
  cursor.execute("UPDATE membership SET accepted = 1 WHERE accepted IS NULL OR accepted <> 1")
  conn.commit()


def create_participations(conn, event_ids):
  cursor = conn.cursor()

  # Fetch all members with needed info
  cursor.execute("SELECT id, fullname, email, srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram, address, contactNum, fblink FROM membership")
  members = cursor.fetchall()

  # Build a quick existence check by deterministic id (avoid duplicates)
  def req_id(member_id: int, event_id: int) -> str:
    return f"REQ-M{member_id}-E{event_id}"

  # Insert participation per member per event
  inserted = 0
  for m in members:
    (member_id, fullname, email, srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram, address, contactNum, fblink) = m

    sex_norm = (sex or "").strip().title() if sex else "Unknown"

    for title, event_id in event_ids.items():
      rid = req_id(member_id, event_id)

      cursor.execute("SELECT 1 FROM requirements WHERE id = ?", (rid,))
      if cursor.fetchone():
        continue

      cursor.execute(
        """
        INSERT INTO requirements (
          id, medCert, waiver, type, eventId, affiliation,
          curriculum, destination, firstAid, fees, personnelInCharge, personnelRole,
          fullname, email, srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
          address, contactNum, fblink, accepted
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
          rid,
          f"documents/med_cert_{rid}.pdf",
          f"documents/waiver_{rid}.pdf",
          "internal",
          event_id,
          "N/A",
          None,
          None,
          None,
          None,
          None,
          None,
          fullname,
          email,
          srcode,
          int(age) if isinstance(age, (int, float, str)) and str(age).isdigit() else 20,
          birthday or datetime.now().strftime("%Y-%m-%d"),
          sex_norm,
          campus or "Main Campus",
          collegeDept or "College",
          yrlevelprogram or "1st Year",
          address or "",
          contactNum or "",
          fblink or "",
          1,
        ),
      )
      inserted += 1

      if inserted % 500 == 0:
        conn.commit()
  conn.commit()
  return inserted


def create_evaluations_for_participations(conn):
  """Create a finalized evaluation for every accepted requirement if none exists."""
  cur = conn.cursor()
  cur.execute("SELECT id FROM requirements WHERE accepted = 1")
  req_ids = [r[0] for r in cur.fetchall()]
  inserted = 0
  for rid in req_ids:
    cur.execute("SELECT 1 FROM evaluation WHERE requirementId = ?", (rid,))
    if cur.fetchone():
      continue
    cur.execute(
      """
      INSERT INTO evaluation (
        criteria, q13, q14, comment, recommendations, requirementId, finalized
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
      """,
      (
        "{}",  # criteria JSON placeholder
        "4",   # satisfaction component
        "4",   # satisfaction component
        "Good event",  # comment
        "Keep it up",  # recommendations non-empty to count attended
        rid,
        1,
      ),
    )
    inserted += 1
    if inserted % 1000 == 0:
      conn.commit()
  conn.commit()
  return inserted


def main():
  if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at: {DB_PATH}")
    return

  conn = sqlite3.connect(DB_PATH)
  try:
    print("Approving all members...")
    approve_all_members(conn)
    print("Ensuring events exist...")
    event_ids = ensure_events(conn)
    print("Fixing event timestamps (ms check)...")
    ms_fixed = fix_events_timestamp_ms(conn)
    if ms_fixed:
      print(f"  ✅ Fixed {ms_fixed} events to ms timestamps")
    print(f"Events: {event_ids}")
    print("Creating participations (this may take a minute)...")
    inserted = create_participations(conn, event_ids)
    print(f"✅ Inserted {inserted} participation records.")
    print("Creating finalized evaluations for each participation...")
    evals = create_evaluations_for_participations(conn)
    print(f"✅ Inserted {evals} evaluation records.")
  finally:
    conn.close()

if __name__ == "__main__":
  main()
