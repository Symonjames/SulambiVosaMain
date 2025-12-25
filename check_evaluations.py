#!/usr/bin/env python3
"""Quick script to check evaluation status"""

import sqlite3
import os

DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM evaluation")
total = cursor.fetchone()[0]
print(f"Total evaluations: {total}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
finalized = cursor.fetchone()[0]
print(f"Finalized evaluations: {finalized}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 0")
not_finalized = cursor.fetchone()[0]
print(f"Not finalized evaluations: {not_finalized}")

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
reqs = cursor.fetchone()[0]
print(f"Accepted requirements: {reqs}")

conn.close()

















