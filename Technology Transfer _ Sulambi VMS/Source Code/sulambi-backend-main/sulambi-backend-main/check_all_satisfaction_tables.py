"""
Check all satisfaction-related tables in SQLite database
"""

import sqlite3
import os

db_path = "app/database/database.db"

if not os.path.exists(db_path):
    print(f"❌ Database file not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*70)
print("Comprehensive Satisfaction Data Check")
print("="*70)
print(f"Database: {db_path}\n")

# Check satisfactionSurveys
try:
    cursor.execute("SELECT COUNT(*) FROM satisfactionSurveys")
    count = cursor.fetchone()[0]
    print(f"✅ satisfactionSurveys: {count} rows")
except Exception as e:
    print(f"❌ satisfactionSurveys error: {e}")

# Check semester_satisfaction
try:
    cursor.execute("SELECT COUNT(*) FROM semester_satisfaction")
    count = cursor.fetchone()[0]
    print(f"✅ semester_satisfaction: {count} rows")
    
    if count > 0:
        cursor.execute("SELECT year, semester, overall, volunteers, beneficiaries FROM semester_satisfaction ORDER BY year DESC, semester DESC LIMIT 5")
        rows = cursor.fetchall()
        print("   Sample data (latest 5):")
        for row in rows:
            print(f"   Year {row[0]}, Semester {row[1]}: Overall={row[2]:.1f}, Vol={row[3]:.1f}, Ben={row[4]:.1f}")
except Exception as e:
    print(f"❌ semester_satisfaction error: {e}")

# Check evaluation table (source data)
try:
    cursor.execute("SELECT COUNT(*) FROM evaluation")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
    finalized = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1 AND criteria IS NOT NULL AND criteria != ''")
    with_criteria = cursor.fetchone()[0]
    
    print(f"\n✅ evaluation table:")
    print(f"   Total rows: {total}")
    print(f"   Finalized: {finalized}")
    print(f"   With criteria (usable for satisfaction): {with_criteria}")
    
    if with_criteria > 0:
        print(f"\n   💡 You have {with_criteria} evaluations that could be used for satisfaction analytics")
        print(f"   These need to be processed into satisfactionSurveys or semester_satisfaction tables")
except Exception as e:
    print(f"❌ evaluation error: {e}")

conn.close()

print("\n" + "="*70)
print("Summary:")
print("  - satisfactionSurveys: Empty (data was migrated to PostgreSQL)")
print("  - semester_satisfaction: Check count above")
print("  - evaluation: Check count above (source data)")
print("\n💡 To test with your real data, use PostgreSQL by setting DATABASE_URL")
print("="*70)

