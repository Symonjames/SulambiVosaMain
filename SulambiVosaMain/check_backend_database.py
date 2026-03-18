#!/usr/bin/env python3
"""Check the actual backend database file directly"""

import os
import sqlite3

# Check both possible database locations
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
default_db = os.path.join(backend_dir, "app", "database", "database.db")

print("=" * 60)
print("CHECKING BACKEND DATABASE FILE")
print("=" * 60)
print(f"Default database path: {default_db}")
print(f"File exists: {os.path.exists(default_db)}")
print(f"File size: {os.path.getsize(default_db) if os.path.exists(default_db) else 0} bytes")

if not os.path.exists(default_db):
    print("\n❌ Database file not found at default location!")
    print("Checking for .env file...")
    env_path = os.path.join(backend_dir, ".env")
    if os.path.exists(env_path):
        print(f"✓ .env file found at: {env_path}")
        with open(env_path, 'r') as f:
            content = f.read()
            print("Contents:")
            print(content)
    else:
        print("❌ .env file not found")
    exit(1)

# Connect to the database
conn = sqlite3.connect(default_db)
cursor = conn.cursor()

print("\n" + "=" * 60)
print("DATABASE CONTENTS")
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

# Check members with requirements (for analytics)
cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
    AND m.age IS NOT NULL AND m.sex IS NOT NULL
""")
analytics_ready = cursor.fetchone()[0]
print(f"\n4. Members ready for analytics: {analytics_ready}")

# Show sample data
print(f"\n5. Sample members (first 3):")
cursor.execute("SELECT id, fullname, email, age, sex, active, accepted FROM membership LIMIT 3")
for row in cursor.fetchall():
    print(f"   - ID: {row[0]}, {row[1]} ({row[2]}), Age: {row[3]}, Sex: {row[4]}, Active: {row[5]}, Accepted: {row[6]}")

print(f"\n6. Sample requirements (first 3):")
cursor.execute("SELECT id, fullname, email, eventId, type, accepted FROM requirements LIMIT 3")
for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]} ({row[2]}), Event: {row[3]}, Type: {row[4]}, Accepted: {row[5]}")

print(f"\n7. Sample evaluations (first 3):")
cursor.execute("SELECT id, requirementId, finalized, LENGTH(criteria) as criteria_len FROM evaluation LIMIT 3")
for row in cursor.fetchall():
    print(f"   - ID: {row[0]}, ReqID: {row[1]}, Finalized: {row[2]}, Criteria length: {row[3]}")

conn.close()

print("\n" + "=" * 60)
if analytics_ready > 0:
    print("✅ YES! DATA IS IN THE BACKEND DATABASE!")
    print(f"   - {active_accepted} active & accepted members")
    print(f"   - {accepted_reqs} accepted requirements")
    print(f"   - {finalized_evals} finalized evaluations")
    print(f"   - {analytics_ready} members ready for analytics")
else:
    print("❌ NO DATA FOUND - Analytics will not work")
print("=" * 60)

















