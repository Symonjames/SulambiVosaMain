#!/usr/bin/env python3
"""Check evaluation details"""

import sqlite3
import os

DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check evaluations
cursor.execute("SELECT COUNT(*) FROM evaluation")
total = cursor.fetchone()[0]
print(f"Total evaluations: {total}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
finalized = cursor.fetchone()[0]
print(f"Finalized evaluations: {finalized}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1 AND criteria IS NOT NULL AND criteria != ''")
with_criteria = cursor.fetchone()[0]
print(f"Finalized with criteria: {with_criteria}")

# Sample a few evaluations
cursor.execute("SELECT id, requirementId, criteria, finalized FROM evaluation LIMIT 5")
samples = cursor.fetchall()
print(f"\nSample evaluations:")
for sample in samples:
    print(f"  ID: {sample[0]}, ReqID: {sample[1]}, Finalized: {sample[3]}, Criteria length: {len(sample[2]) if sample[2] else 0}")

# Check requirements
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
reqs = cursor.fetchone()[0]
print(f"\nAccepted requirements: {reqs}")

# Check if evaluations are linked to requirements
cursor.execute("""
    SELECT COUNT(*) 
    FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    WHERE e.finalized = 1
""")
linked = cursor.fetchone()[0]
print(f"Evaluations linked to requirements: {linked}")

conn.close()

















