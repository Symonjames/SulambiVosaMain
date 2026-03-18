"""Verify the dropout analytics API endpoint"""
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check requirements
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
req_count = cursor.fetchone()[0]

# Check evaluations
cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1 AND criteria IS NOT NULL AND criteria != ''")
eval_count = cursor.fetchone()[0]

print("=" * 70)
print("DATABASE VERIFICATION")
print("=" * 70)
print(f"Requirements (joined): {req_count}")
print(f"Evaluations (attended): {eval_count}")
print(f"Dropouts (joined but didn't attend): {req_count - eval_count}")
print()

# Test the function directly
print("=" * 70)
print("TESTING BACKEND FUNCTION")
print("=" * 70)
from app.controllers.analytics import getVolunteerDropoutAnalytics
result = getVolunteerDropoutAnalytics()

if result.get('success'):
    data = result.get('data', {})
    semester_data = data.get('semesterData', [])
    at_risk = data.get('atRiskVolunteers', [])
    
    print(f"✓ API Function working!")
    print(f"  Semester Data: {len(semester_data)} semesters")
    for sem in semester_data:
        print(f"    {sem['semester']}: {sem['volunteers']} joined, {sem['attended']} attended, {sem['dropouts']} dropouts")
    print(f"  At-Risk Volunteers: {len(at_risk)}")
else:
    print(f"✗ Error: {result.get('error')}")

conn.close()

















