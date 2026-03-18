#!/usr/bin/env python3
"""Check what's actually in the requirements table"""

import sqlite3
import os

backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("CHECKING REQUIREMENTS TABLE")
print("=" * 60)

# Check table structure
cursor.execute("PRAGMA table_info(requirements)")
columns = cursor.fetchall()
print("\n1. Requirements table columns:")
for col in columns:
    print(f"   - {col[1]} ({col[2]})")

# Check total requirements
cursor.execute("SELECT COUNT(*) FROM requirements")
total = cursor.fetchone()[0]
print(f"\n2. Total requirements: {total}")

# Check requirements with different accepted values
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted IS NULL")
null_count = cursor.fetchone()[0]
print(f"   Requirements with accepted IS NULL: {null_count}")

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 0")
zero_count = cursor.fetchone()[0]
print(f"   Requirements with accepted = 0: {zero_count}")

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
one_count = cursor.fetchone()[0]
print(f"   Requirements with accepted = 1: {one_count}")

# Check all distinct accepted values
cursor.execute("SELECT DISTINCT accepted FROM requirements LIMIT 10")
distinct_values = cursor.fetchall()
print(f"   Distinct accepted values: {distinct_values}")

# Sample requirements
print("\n3. Sample requirements (first 5):")
cursor.execute("SELECT id, email, fullname, accepted, type, eventId FROM requirements LIMIT 5")
for row in cursor.fetchall():
    print(f"   - ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Accepted: {row[3]} (type: {type(row[3])}), Type: {row[4]}, Event: {row[5]}")

# Check if we need to update accepted values
print("\n4. Checking if we need to update accepted values...")
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted IS NULL OR accepted = 0")
needs_update = cursor.fetchone()[0]
print(f"   Requirements that need updating: {needs_update}")

if needs_update > 0:
    print("\n5. Updating requirements to accepted = 1...")
    cursor.execute("UPDATE requirements SET accepted = 1 WHERE accepted IS NULL OR accepted = 0")
    conn.commit()
    print(f"   ✓ Updated {needs_update} requirements")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
    updated_count = cursor.fetchone()[0]
    print(f"   ✓ Total requirements with accepted = 1: {updated_count}")

conn.close()

print("\n" + "=" * 60)
print("CHECK COMPLETE")
print("=" * 60)

















