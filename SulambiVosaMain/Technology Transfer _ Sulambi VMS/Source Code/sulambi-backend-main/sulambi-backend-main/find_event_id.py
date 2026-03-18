import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Find event with "ecaluation" in title
cursor.execute("""
    SELECT id, title, 'internal' as type FROM internalEvents 
    WHERE title LIKE '%ecaluation%' OR title LIKE '%evaluation%'
    UNION ALL
    SELECT id, title, 'external' as type FROM externalEvents 
    WHERE title LIKE '%ecaluation%' OR title LIKE '%evaluation%'
""")
events = cursor.fetchall()

print("Events matching 'ecaluation form':")
for e in events:
    print(f"  ID: {e[0]}, Title: {e[1]}, Type: {e[2]}")

# Check satisfaction surveys for this event
if events:
    event_id, event_title, event_type = events[0]
    cursor.execute("""
        SELECT COUNT(*), 
               AVG(overallSatisfaction),
               AVG(CASE WHEN volunteerRating IS NOT NULL THEN volunteerRating END),
               AVG(CASE WHEN beneficiaryRating IS NOT NULL THEN beneficiaryRating END)
        FROM satisfactionSurveys
        WHERE eventId = ? AND eventType = ?
    """, (event_id, event_type))
    stats = cursor.fetchone()
    print(f"\nSatisfaction surveys for event {event_id} ({event_title}):")
    print(f"  Total: {stats[0]}")
    print(f"  Avg Overall: {stats[1]:.2f}" if stats[1] else "  Avg Overall: None")
    print(f"  Avg Volunteer: {stats[2]:.2f}" if stats[2] else "  Avg Volunteer: None")
    print(f"  Avg Beneficiary: {stats[3]:.2f}" if stats[3] else "  Avg Beneficiary: None")

conn.close()

















