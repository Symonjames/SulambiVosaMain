#!/usr/bin/env python3
"""Verify data is actually in the database"""

import sqlite3
import os

DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("VERIFYING DATABASE DATA")
print("=" * 60)

# Check members
cursor.execute("SELECT COUNT(*) FROM membership")
total_members = cursor.fetchone()[0]
print(f"\n1. Total members: {total_members}")

cursor.execute("SELECT COUNT(*) FROM membership WHERE active = 1 AND accepted = 1")
active_accepted = cursor.fetchone()[0]
print(f"   - Active and accepted: {active_accepted}")

# Check requirements
cursor.execute("SELECT COUNT(*) FROM requirements")
total_reqs = cursor.fetchone()[0]
print(f"\n2. Total requirements: {total_reqs}")

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
accepted_reqs = cursor.fetchone()[0]
print(f"   - Accepted requirements: {accepted_reqs}")

# Check evaluations
cursor.execute("SELECT COUNT(*) FROM evaluation")
total_evals = cursor.fetchone()[0]
print(f"\n3. Total evaluations: {total_evals}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
finalized_evals = cursor.fetchone()[0]
print(f"   - Finalized evaluations: {finalized_evals}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1 AND criteria IS NOT NULL AND criteria != ''")
with_criteria = cursor.fetchone()[0]
print(f"   - With satisfaction criteria: {with_criteria}")

# Check members with requirements
cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
""")
members_with_reqs = cursor.fetchone()[0]
print(f"\n4. Members with accepted requirements: {members_with_reqs}")

# Sample data
print(f"\n5. Sample members (first 5):")
cursor.execute("SELECT fullname, email, age, sex, active, accepted FROM membership LIMIT 5")
for row in cursor.fetchall():
    print(f"   - {row[0]} ({row[1]}), Age: {row[2]}, Sex: {row[3]}, Active: {row[4]}, Accepted: {row[5]}")

print(f"\n6. Sample requirements (first 5):")
cursor.execute("SELECT id, fullname, email, eventId, type, accepted FROM requirements LIMIT 5")
for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]} ({row[2]}), Event: {row[3]}, Type: {row[4]}, Accepted: {row[5]}")

print(f"\n7. Sample evaluations (first 5):")
cursor.execute("SELECT id, requirementId, finalized, LENGTH(criteria) as criteria_len FROM evaluation LIMIT 5")
for row in cursor.fetchall():
    print(f"   - ID: {row[0]}, ReqID: {row[1]}, Finalized: {row[2]}, Criteria length: {row[3]}")

# Check if data will appear in analytics
print(f"\n8. Analytics readiness:")
cursor.execute("""
    SELECT COUNT(*)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 
    AND m.accepted = 1 
    AND r.accepted = 1
    AND m.age IS NOT NULL
    AND m.sex IS NOT NULL
""")
analytics_ready = cursor.fetchone()[0]
print(f"   - Members ready for analytics: {analytics_ready}")

conn.close()

print("\n" + "=" * 60)
if analytics_ready > 0 and with_criteria > 0:
    print("✅ DATA IS IN THE DATABASE!")
    print(f"   - {analytics_ready} members ready for analytics")
    print(f"   - {with_criteria} evaluations with satisfaction data")
else:
    print("❌ DATA MISSING OR INCOMPLETE")
print("=" * 60)

















