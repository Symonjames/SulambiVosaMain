"""
Check SQLite database for satisfaction data
Run this from the backend directory
"""

import os
import sqlite3
import sys

# Get the database path
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

# Also try relative path
if not os.path.exists(db_path):
    db_path = "app/database/database.db"
    if not os.path.exists(db_path):
        # Try from backend root
        db_path = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

if not os.path.exists(db_path):
    print(f"❌ Database file not found!")
    print(f"Tried: {db_path}")
    print(f"\nCurrent directory: {os.getcwd()}")
    print(f"\nPlease run this script from the backend directory:")
    print(f'cd "Technology Transfer _ Sulambi VMS/Source Code/sulambi-backend-main/sulambi-backend-main"')
    sys.exit(1)

print("="*70)
print("SQLite Database Satisfaction Data Check")
print("="*70)
print(f"Database: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check satisfactionSurveys
try:
    cursor.execute("SELECT COUNT(*) FROM satisfactionSurveys")
    count = cursor.fetchone()[0]
    print(f"✅ satisfactionSurveys table: {count} rows")
    
    if count > 0:
        cursor.execute("SELECT eventId, eventType, overallSatisfaction, finalized FROM satisfactionSurveys LIMIT 5")
        rows = cursor.fetchall()
        print("   Sample rows:")
        for row in rows:
            print(f"   Event {row[0]} ({row[1]}): Satisfaction={row[2]}, Finalized={bool(row[3])}")
    else:
        print("   ⚠️  Table is empty")
except Exception as e:
    print(f"❌ satisfactionSurveys table error: {e}")

# Check semester_satisfaction
try:
    cursor.execute("SELECT COUNT(*) FROM semester_satisfaction")
    count = cursor.fetchone()[0]
    print(f"\n✅ semester_satisfaction table: {count} rows")
    
    if count > 0:
        cursor.execute("SELECT year, semester, overall, volunteers, beneficiaries FROM semester_satisfaction ORDER BY year DESC, semester DESC LIMIT 5")
        rows = cursor.fetchall()
        print("   Sample rows (latest 5):")
        for row in rows:
            print(f"   Year {row[0]}, Semester {row[1]}: Overall={row[2]:.1f}, Vol={row[3]:.1f}, Ben={row[4]:.1f}")
    else:
        print("   ⚠️  Table is empty")
except Exception as e:
    print(f"❌ semester_satisfaction table error: {e}")

# Check evaluation table
try:
    cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
    count = cursor.fetchone()[0]
    print(f"\n✅ evaluation table (finalized): {count} rows")
except Exception as e:
    print(f"❌ evaluation table error: {e}")

conn.close()

print("\n" + "="*70)
if count == 0:
    print("💡 No satisfaction data found in SQLite database.")
    print("   Your data is likely in PostgreSQL after migration.")
    print("   To test with real data, use PostgreSQL locally by setting DATABASE_URL")
print("="*70)

