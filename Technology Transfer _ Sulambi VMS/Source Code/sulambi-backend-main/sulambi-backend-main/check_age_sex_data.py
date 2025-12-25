"""
Check age and sex data for all members
"""

import sqlite3
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("AGE AND SEX DATA ANALYSIS")
print("=" * 70)

# Get all members
cursor.execute("SELECT id, email, fullname, age, sex, accepted, active FROM membership")
all_members = cursor.fetchall()

print(f"\nTotal members: {len(all_members)}")

# Count by status
cursor.execute("SELECT accepted, active, COUNT(*) FROM membership GROUP BY accepted, active")
status_counts = cursor.fetchall()
print("\nMembers by status (accepted, active):")
for accepted, active, count in status_counts:
    print(f"  accepted={accepted}, active={active}: {count} members")

# Age distribution
cursor.execute("SELECT age, COUNT(*) FROM membership WHERE age IS NOT NULL AND age != '' GROUP BY age ORDER BY CAST(age AS INTEGER)")
age_data = cursor.fetchall()
print(f"\nAge Distribution ({len(age_data)} unique ages):")
age_counter = Counter()
for age, count in age_data:
    age_counter[age] = count
    print(f"  Age {age}: {count} members")

# Sex distribution
cursor.execute("SELECT sex, COUNT(*) FROM membership WHERE sex IS NOT NULL AND sex != '' GROUP BY sex")
sex_data = cursor.fetchall()
print(f"\nSex Distribution ({len(sex_data)} unique values):")
sex_counter = Counter()
for sex, count in sex_data:
    sex_counter[sex] = count
    print(f"  {sex}: {count} members")

# Members with both age and sex
cursor.execute("SELECT COUNT(*) FROM membership WHERE age IS NOT NULL AND age != '' AND sex IS NOT NULL AND sex != ''")
both_count = cursor.fetchone()[0]
print(f"\nMembers with both age AND sex: {both_count}")

# Members with requirements
cursor.execute("""
    SELECT COUNT(DISTINCT m.id) 
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE r.accepted = 1
""")
with_reqs = cursor.fetchone()[0]
print(f"Members with accepted requirements: {with_reqs}")

# What analytics would show currently
cursor.execute("""
    SELECT m.age, m.sex 
    FROM membership m
    WHERE m.accepted = 1 AND m.active = 1
    AND EXISTS (
        SELECT 1 FROM requirements r 
        WHERE r.email = m.email AND r.accepted = 1
    )
    AND m.age IS NOT NULL AND m.age != ''
    AND m.sex IS NOT NULL AND m.sex != ''
""")
analytics_members = cursor.fetchall()
print(f"\nMembers that would appear in analytics (accepted=1, active=1, has requirements): {len(analytics_members)}")

if len(analytics_members) > 0:
    analytics_age = Counter([str(r[0]) for r in analytics_members])
    analytics_sex = Counter([r[1].strip().title() for r in analytics_members])
    print(f"  Age distribution: {dict(analytics_age)}")
    print(f"  Sex distribution: {dict(analytics_sex)}")
else:
    print("  ⚠ No members would appear in analytics with current filters!")

conn.close()

















