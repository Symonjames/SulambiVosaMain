#!/usr/bin/env python3
"""Test the analytics query to see what it returns"""

import os
import sys

# Add backend directory to path
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

from app.models.MembershipModel import MembershipModel
from app.models.RequirementsModel import RequirementsModel

print("=" * 60)
print("TESTING ANALYTICS QUERY")
print("=" * 60)

# Get all memberships
allMemberships = MembershipModel().getAll()
print(f"\nTotal memberships: {len(allMemberships)}")

ageGroup = {}
sexGroup = {}
counted = 0
skipped_no_reqs = 0

for membership in allMemberships:
    accepted = membership.get("accepted")
    active = membership.get("active")
    
    # Check if accepted and active
    if accepted is None or accepted == False or accepted == 0:
        continue
    if accepted != 1 and accepted != True:
        continue
    if active is None or active == False or active == 0:
        continue
    if active != 1 and active != True:
        continue
    
    # Check if member has accepted requirements
    member_email = membership.get("email")
    if not member_email:
        continue
    
    # Try with True (boolean) - this is what the code was using
    member_requirements_true = RequirementsModel().getAndSearch(["email", "accepted"], [member_email, True])
    
    # Try with 1 (integer) - this is what's in the database
    member_requirements_one = RequirementsModel().getAndSearch(["email", "accepted"], [member_email, 1])
    
    if len(member_requirements_one) == 0:
        skipped_no_reqs += 1
        if len(member_requirements_true) > 0:
            print(f"  ⚠️  {member_email}: Found {len(member_requirements_true)} with True, but 0 with 1")
        continue
    
    if len(member_requirements_true) != len(member_requirements_one):
        print(f"  ⚠️  {member_email}: True={len(member_requirements_true)}, 1={len(member_requirements_one)}")
    
    # Get age and sex
    age_value = membership.get("age")
    if age_value is not None and age_value != "":
        try:
            age_int = int(age_value) if isinstance(age_value, str) else age_value
            age_key = str(age_int)
            if age_key not in ageGroup:
                ageGroup[age_key] = 0
            ageGroup[age_key] += 1
        except (ValueError, TypeError):
            pass
    
    sex_value = membership.get("sex")
    if sex_value is not None and sex_value != "":
        sex_normalized = sex_value.strip().title()
        if sex_normalized not in sexGroup:
            sexGroup[sex_normalized] = 0
        sexGroup[sex_normalized] += 1
    
    counted += 1

print(f"\nResults:")
print(f"  - Members counted: {counted}")
print(f"  - Skipped (no requirements): {skipped_no_reqs}")
print(f"  - Age groups: {ageGroup}")
print(f"  - Sex groups: {sexGroup}")

print("\n" + "=" * 60)
if counted > 0:
    print("✅ Analytics query works with accepted=1!")
else:
    print("❌ No members found - check the query")
print("=" * 60)

















