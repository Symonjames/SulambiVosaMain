"""
Quick check of SQLite database for satisfaction data
"""

import os
import sqlite3

DB_PATH = "app/database/database.db"

if not os.path.exists(DB_PATH):
    print(f"❌ Database file not found: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("="*70)
print("SQLite Database Check")
print("="*70)
print(f"Database: {DB_PATH}\n")

# Check satisfactionSurveys
try:
    cursor.execute("SELECT COUNT(*) FROM satisfactionSurveys")
    count = cursor.fetchone()[0]
    print(f"✅ satisfactionSurveys: {count} rows")
    
    if count > 0:
        cursor.execute("SELECT eventId, eventType, overallSatisfaction, finalized FROM satisfactionSurveys LIMIT 5")
        rows = cursor.fetchall()
        print("   Sample rows:")
        for row in rows:
            print(f"   Event {row[0]} ({row[1]}): Satisfaction={row[2]}, Finalized={row[3]}")
except Exception as e:
    print(f"❌ satisfactionSurveys table error: {e}")

# Check semester_satisfaction
try:
    cursor.execute("SELECT COUNT(*) FROM semester_satisfaction")
    count = cursor.fetchone()[0]
    print(f"\n✅ semester_satisfaction: {count} rows")
    
    if count > 0:
        cursor.execute("SELECT year, semester, overall, volunteers, beneficiaries FROM semester_satisfaction ORDER BY year DESC, semester DESC LIMIT 5")
        rows = cursor.fetchall()
        print("   Sample rows:")
        for row in rows:
            print(f"   Year {row[0]}, Semester {row[1]}: Overall={row[2]:.1f}, Vol={row[3]:.1f}, Ben={row[4]:.1f}")
except Exception as e:
    print(f"❌ semester_satisfaction table error: {e}")

# Check evaluation table
try:
    cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
    count = cursor.fetchone()[0]
    print(f"\n✅ evaluation (finalized): {count} rows")
except Exception as e:
    print(f"❌ evaluation table error: {e}")

conn.close()

print("\n" + "="*70)

