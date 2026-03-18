"""Verify participation history table has data"""
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check if table exists
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='volunteerParticipationHistory'
""")
table_exists = cursor.fetchone()

if not table_exists:
    print("❌ Table volunteerParticipationHistory does not exist")
    print("   Run: python populate_volunteer_participation_history.py")
else:
    print("✓ Table exists")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM volunteerParticipationHistory")
    total = cursor.fetchone()[0]
    print(f"✓ Total records: {total}")
    
    # Count by semester
    cursor.execute("""
        SELECT semester, COUNT(*) as count
        FROM volunteerParticipationHistory
        GROUP BY semester
        ORDER BY semester
    """)
    semesters = cursor.fetchall()
    print(f"\nRecords by semester:")
    for sem, count in semesters:
        print(f"  {sem}: {count} records")
    
    # Sample data
    cursor.execute("""
        SELECT volunteerName, semester, eventsJoined, eventsAttended, 
               attendanceRate, lastEventDate, participationConsistency
        FROM volunteerParticipationHistory
        LIMIT 5
    """)
    samples = cursor.fetchall()
    print(f"\nSample records:")
    for name, sem, joined, attended, rate, last_date, consistency in samples:
        print(f"  {name}: {sem} - {joined} joined, {attended} attended, {rate:.1f}% rate, {consistency}")

conn.close()

















