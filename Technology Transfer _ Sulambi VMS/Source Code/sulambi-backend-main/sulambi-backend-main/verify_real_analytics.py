"""
Verify that analytics are using real data from member-app.xlsx
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
print("VERIFYING REAL ANALYTICS DATA FROM member-app.xlsx")
print("=" * 70)

# Get all accepted and active members with age/sex
cursor.execute("""
    SELECT age, sex 
    FROM membership 
    WHERE accepted = 1 AND active = 1
    AND age IS NOT NULL AND age != '' AND age != '0'
    AND sex IS NOT NULL AND sex != ''
""")
members = cursor.fetchall()

print(f"\nTotal members with valid age and sex: {len(members)}")

# Age distribution
age_counter = Counter()
sex_counter = Counter()

for age, sex in members:
    try:
        age_int = int(age)
        if age_int > 0:
            age_counter[str(age_int)] += 1
    except:
        pass
    
    if sex:
        sex_normalized = sex.strip().title()
        if sex_normalized in ["Male", "Female"]:
            sex_counter[sex_normalized] += 1

print(f"\nAge Distribution (from real data):")
for age in sorted(age_counter.keys(), key=int):
    print(f"  Age {age}: {age_counter[age]} members")
print(f"  Total: {sum(age_counter.values())} members")

print(f"\nSex Distribution (from real data):")
for sex in sorted(sex_counter.keys()):
    print(f"  {sex}: {sex_counter[sex]} members")
print(f"  Total: {sum(sex_counter.values())} members")

# Test the analytics function
print("\n" + "=" * 70)
print("TESTING getAnalytics() FUNCTION")
print("=" * 70)

import sys
sys.path.insert(0, os.path.dirname(__file__))
from app.controllers.dashboard import getAnalytics

result = getAnalytics()
data = result.get('data', {})
age_group = data.get('ageGroup', {})
sex_group = data.get('sexGroup', {})

print(f"\nBackend getAnalytics() returns:")
print(f"  Age groups: {len(age_group)}")
print(f"  Sex groups: {len(sex_group)}")

print(f"\nAge Group Data:")
for age in sorted(age_group.keys(), key=int):
    print(f"  {age}: {age_group[age]}")

print(f"\nSex Group Data:")
for sex in sorted(sex_group.keys()):
    print(f"  {sex}: {sex_group[sex]}")

# Verify match
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

age_match = age_counter == Counter({k: int(v) for k, v in age_group.items()})
sex_match = sex_counter == Counter(sex_group)

print(f"Age data matches: {age_match}")
print(f"Sex data matches: {sex_match}")

if age_match and sex_match:
    print("\n✓ Analytics are correctly using real data from member-app.xlsx")
else:
    print("\n⚠ Warning: There may be a mismatch in the data")

conn.close()

















