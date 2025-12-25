"""Check if the requested data exists"""
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime
import math

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("CHECKING REQUESTED DATA")
print("=" * 70)

# Check participation history by semester
print("\n1. Participation History by Semester:")
cursor.execute("""
    SELECT semester, 
           COUNT(DISTINCT volunteerEmail) as volunteers,
           SUM(eventsJoined) as total_joined,
           SUM(eventsAttended) as total_attended,
           SUM(eventsDropped) as total_dropped
    FROM volunteerParticipationHistory
    GROUP BY semester
    ORDER BY semester
""")
semester_data = cursor.fetchall()
for sem, vol, joined, attended, dropped in semester_data:
    print(f"  {sem}: {vol} volunteers, {joined} joined, {attended} attended, {dropped} dropped")

# Check requirements by event month
print("\n2. Requirements by Event Month:")
cursor.execute("""
    SELECT 
        CASE 
            WHEN strftime('%m', datetime(COALESCE(ie.durationStart, ee.durationStart)/1000, 'unixepoch')) = '08' THEN 'August'
            WHEN strftime('%m', datetime(COALESCE(ie.durationStart, ee.durationStart)/1000, 'unixepoch')) = '10' THEN 'October'
            WHEN strftime('%m', datetime(COALESCE(ie.durationStart, ee.durationStart)/1000, 'unixepoch')) = '11' THEN 'November'
            ELSE 'Other'
        END as month,
        COUNT(DISTINCT r.email) as volunteers_joined,
        COUNT(DISTINCT CASE WHEN e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != '' THEN r.email END) as volunteers_attended
    FROM requirements r
    LEFT JOIN evaluation e ON r.id = e.requirementId
    LEFT JOIN internalEvents ie ON r.eventId = ie.id AND r.type = 'internal'
    LEFT JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
    WHERE r.accepted = 1
    GROUP BY month
    ORDER BY month
""")
month_data = cursor.fetchall()
for month, joined, attended in month_data:
    print(f"  {month}: {joined} joined, {attended} attended, {joined - attended} dropouts")

# Check specific requirements
print("\n3. Checking specific requirements:")
cursor.execute("""
    SELECT COUNT(*) FROM requirements 
    WHERE accepted = 1 
    AND id LIKE 'REQ-AUG%'
""")
aug_req = cursor.fetchone()[0]
print(f"  August requirements: {aug_req}")

cursor.execute("""
    SELECT COUNT(*) FROM requirements 
    WHERE accepted = 1 
    AND id LIKE 'REQ-OCT%'
""")
oct_req = cursor.fetchone()[0]
print(f"  October requirements: {oct_req}")

cursor.execute("""
    SELECT COUNT(*) FROM requirements 
    WHERE accepted = 1 
    AND id LIKE 'REQ-NOV%'
""")
nov_req = cursor.fetchone()[0]
print(f"  November requirements: {nov_req}")

# Check evaluations
print("\n4. Checking evaluations:")
cursor.execute("""
    SELECT COUNT(*) FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    AND r.id LIKE 'REQ-AUG%'
""")
aug_eval = cursor.fetchone()[0]
print(f"  August evaluations (attended): {aug_eval}")

cursor.execute("""
    SELECT COUNT(*) FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    AND r.id LIKE 'REQ-NOV%'
""")
nov_eval = cursor.fetchone()[0]
print(f"  November evaluations (attended): {nov_eval}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"August: {aug_req} joined, {aug_eval} attended, {aug_req - aug_eval} dropouts")
print(f"October: {oct_req} joined, 0 attended (all dropouts)")
print(f"November: {nov_req} joined, {nov_eval} attended, {nov_req - nov_eval} dropouts")

conn.close()

