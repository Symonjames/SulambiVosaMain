#!/usr/bin/env python3
"""Verify data is in the REAL backend database"""

import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
sys.path.insert(0, backend_dir)

# Load environment variables (same as backend)
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

# Set DB_PATH to absolute path if it's relative
db_path = os.getenv("DB_PATH", "app/database/database.db")
if not os.path.isabs(db_path):
    # Make it relative to backend directory
    db_path = os.path.join(backend_dir, db_path)
os.environ["DB_PATH"] = db_path

# Use backend's connection method
from app.database.connection import cursorInstance

print("=" * 60)
print("VERIFYING REAL BACKEND DATABASE")
print("=" * 60)

conn, cursor = cursorInstance()

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

# Sample data
print(f"\n5. Sample members (first 3):")
cursor.execute("SELECT fullname, email, age, sex, active, accepted FROM membership LIMIT 3")
for row in cursor.fetchall():
    print(f"   - {row[0]} ({row[1]}), Age: {row[2]}, Sex: {row[3]}, Active: {row[4]}, Accepted: {row[5]}")

conn.close()

print("\n" + "=" * 60)
if analytics_ready > 0:
    print("✅ DATA IS IN THE REAL DATABASE!")
    print(f"   - {active_accepted} active & accepted members")
    print(f"   - {accepted_reqs} accepted requirements")
    print(f"   - {finalized_evals} finalized evaluations")
    print(f"   - {analytics_ready} members ready for analytics")
else:
    print("❌ DATA NOT READY FOR ANALYTICS")
print("=" * 60)










