#!/usr/bin/env python3
"""Debug why analytics disappeared"""

import sqlite3
import os

backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")

print("=" * 60)
print("DEBUGGING ANALYTICS")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check what accepted values actually are in requirements
print("\n1. Checking accepted values in requirements table:")
cursor.execute("SELECT DISTINCT accepted FROM requirements LIMIT 10")
accepted_values = cursor.fetchall()
print(f"   Distinct accepted values: {accepted_values}")

# Check requirements with accepted = 1
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
count_1 = cursor.fetchone()[0]
print(f"   Requirements with accepted = 1: {count_1}")

# Check requirements with accepted = True (as string)
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 'True'")
count_true_str = cursor.fetchone()[0]
print(f"   Requirements with accepted = 'True' (string): {count_true_str}")

# Check requirements with accepted = True (as boolean in SQL)
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1 AND accepted IS NOT NULL")
count_1_check = cursor.fetchone()[0]
print(f"   Requirements with accepted = 1 (verified): {count_1_check}")

# Test the actual query that getAnalytics uses
print("\n2. Testing the exact query from getAnalytics:")
cursor.execute("""
    SELECT m.email, m.age, m.sex, m.accepted, m.active
    FROM membership m
    WHERE m.accepted = 1 AND m.active = 1
    AND EXISTS (
        SELECT 1 FROM requirements r 
        WHERE r.email = m.email AND r.accepted = 1
    )
    LIMIT 5
""")
members_with_reqs = cursor.fetchall()
print(f"   Members found: {len(members_with_reqs)}")
for row in members_with_reqs:
    print(f"   - {row[0]}: Age={row[1]}, Sex={row[2]}, Accepted={row[3]}, Active={row[4]}")

# Count age groups
print("\n3. Counting age groups:")
cursor.execute("""
    SELECT m.age, COUNT(*) as count
    FROM membership m
    WHERE m.accepted = 1 AND m.active = 1
    AND EXISTS (
        SELECT 1 FROM requirements r 
        WHERE r.email = m.email AND r.accepted = 1
    )
    AND m.age IS NOT NULL AND m.age != ''
    GROUP BY m.age
    ORDER BY CAST(m.age AS INTEGER)
""")
age_groups = cursor.fetchall()
print(f"   Age groups found: {len(age_groups)}")
for row in age_groups:
    print(f"   - Age {row[0]}: {row[1]} members")

# Count sex groups
print("\n4. Counting sex groups:")
cursor.execute("""
    SELECT m.sex, COUNT(*) as count
    FROM membership m
    WHERE m.accepted = 1 AND m.active = 1
    AND EXISTS (
        SELECT 1 FROM requirements r 
        WHERE r.email = m.email AND r.accepted = 1
    )
    AND m.sex IS NOT NULL AND m.sex != ''
    GROUP BY m.sex
""")
sex_groups = cursor.fetchall()
print(f"   Sex groups found: {len(sex_groups)}")
for row in sex_groups:
    print(f"   - {row[0]}: {row[1]} members")

# Check if there's a mismatch in email format
print("\n5. Checking email matching:")
cursor.execute("SELECT email FROM membership WHERE accepted = 1 AND active = 1 LIMIT 3")
member_emails = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT email FROM requirements WHERE accepted = 1 LIMIT 3")
req_emails = [row[0] for row in cursor.fetchall()]
print(f"   Sample member emails: {member_emails}")
print(f"   Sample requirement emails: {req_emails}")

# Check if emails match
cursor.execute("""
    SELECT COUNT(DISTINCT m.email)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.accepted = 1 AND m.active = 1 AND r.accepted = 1
""")
matching_emails = cursor.fetchone()[0]
print(f"   Members with matching requirement emails: {matching_emails}")

conn.close()

print("\n" + "=" * 60)
if len(age_groups) > 0 and len(sex_groups) > 0:
    print("✅ DATA EXISTS - Analytics should work!")
else:
    print("❌ NO DATA FOUND - Check the queries above")
print("=" * 60)

















