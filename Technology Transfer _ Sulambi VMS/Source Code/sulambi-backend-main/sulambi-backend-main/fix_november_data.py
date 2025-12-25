"""Fix November data to be exactly 100 attended, 65 dropouts"""
import sqlite3
import random
from dotenv import load_dotenv
import os

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all November requirements
cursor.execute("""
    SELECT r.id, r.email, r.fullname
    FROM requirements r
    LEFT JOIN internalEvents ie ON r.eventId = ie.id AND r.type = 'internal'
    LEFT JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
    WHERE r.accepted = 1
    AND r.id LIKE 'REQ-NOV%'
    AND (strftime('%m', datetime(COALESCE(ie.durationStart, ee.durationStart)/1000, 'unixepoch')) = '11'
         OR r.id LIKE 'REQ-NOV%')
""")
nov_reqs = cursor.fetchall()

print(f"Found {len(nov_reqs)} November requirements")

# Get current evaluations
cursor.execute("""
    SELECT e.requirementId
    FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    AND r.id LIKE 'REQ-NOV%'
""")
current_evals = {row[0] for row in cursor.fetchall()}
print(f"Current evaluations: {len(current_evals)}")

# We need exactly 100 attended, 65 dropouts
# Remove excess evaluations if we have more than 100
if len(current_evals) > 100:
    excess = list(current_evals)[100:]
    for req_id in excess:
        cursor.execute("DELETE FROM evaluation WHERE requirementId = ?", (req_id,))
    print(f"Removed {len(excess)} excess evaluations")
    current_evals = set(list(current_evals)[:100])

# Add evaluations if we have less than 100
if len(current_evals) < 100:
    needed = 100 - len(current_evals)
    reqs_without_eval = [r[0] for r in nov_reqs if r[0] not in current_evals]
    to_add = reqs_without_eval[:needed]
    
    for req_id in to_add:
        criteria = {'overall': round(random.uniform(3.5, 5.0), 1), 'comment': "Attended"}
        cursor.execute("""
            INSERT INTO evaluation (
                requirementId, criteria, q13, q14, comment, recommendations, finalized
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (req_id, str(criteria), str(round(random.uniform(3.5, 5.0), 1)), "", "Attended", "Good", 1))
    print(f"Added {len(to_add)} evaluations")

conn.commit()

# Verify
cursor.execute("""
    SELECT COUNT(*) FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    AND r.id LIKE 'REQ-NOV%'
""")
final_evals = cursor.fetchone()[0]
print(f"\nFinal November: {len(nov_reqs)} joined, {final_evals} attended, {len(nov_reqs) - final_evals} dropouts")

conn.close()

