"""Check why dropout data is empty"""
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime
import math

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check events
print("=" * 70)
print("CHECKING EVENTS")
print("=" * 70)
cursor.execute("""
    SELECT id, title, durationStart, durationEnd, 'internal' as type
    FROM internalEvents
    WHERE status IN ('accepted', 'completed')
    UNION ALL
    SELECT id, title, durationStart, durationEnd, 'external' as type
    FROM externalEvents
    WHERE status IN ('accepted', 'completed')
    ORDER BY durationStart
""")
events = cursor.fetchall()
print(f"Total events: {len(events)}")

semester_events = {}
for event_id, event_title, event_start, event_end, event_type in events:
    if event_start:
        event_date = datetime.fromtimestamp(event_start / 1000)
        semester_year = event_date.year
        semester_num = math.ceil(event_date.month / 6)
        semester_key = f"{semester_year}-{semester_num}"
        
        if semester_key not in semester_events:
            semester_events[semester_key] = []
        semester_events[semester_key].append((event_id, event_type))
        print(f"  Event {event_id}: {event_title[:30]}... -> {semester_key} ({event_date.strftime('%Y-%m-%d')})")
    else:
        print(f"  Event {event_id}: {event_title[:30]}... -> NO DATE")

print(f"\nSemesters found: {list(semester_events.keys())}")

# Check requirements
print("\n" + "=" * 70)
print("CHECKING REQUIREMENTS")
print("=" * 70)
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
req_count = cursor.fetchone()[0]
print(f"Total accepted requirements: {req_count}")

# Check requirements by event
if events:
    event_ids = [e[0] for e in events]
    placeholders = ','.join(['?' for _ in event_ids])
    cursor.execute(f"""
        SELECT r.eventId, r.type, COUNT(*) as count
        FROM requirements r
        WHERE r.accepted = 1 AND r.eventId IN ({placeholders})
        GROUP BY r.eventId, r.type
    """, event_ids)
    req_by_event = cursor.fetchall()
    print(f"Requirements by event:")
    for event_id, req_type, count in req_by_event:
        print(f"  Event {event_id} ({req_type}): {count} requirements")

# Check evaluations
print("\n" + "=" * 70)
print("CHECKING EVALUATIONS")
print("=" * 70)
cursor.execute("""
    SELECT COUNT(*) 
    FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    AND r.accepted = 1
""")
eval_count = cursor.fetchone()[0]
print(f"Total finalized evaluations: {eval_count}")

conn.close()

















