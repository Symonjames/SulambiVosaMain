#!/usr/bin/env python3
"""Test the exact queries the backend uses to see if they work"""

import os
import sys

# Add backend directory to path
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

from app.models.MembershipModel import MembershipModel
from app.models.RequirementsModel import RequirementsModel
from app.models.EvaluationModel import EvaluationModel

print("=" * 60)
print("TESTING BACKEND QUERIES")
print("=" * 60)

# Test getAnalytics query
print("\n1. Testing getAnalytics() query:")
allMemberships = MembershipModel().getAll()
print(f"   Total memberships: {len(allMemberships)}")

ageGroup = {}
sexGroup = {}
counted = 0

for membership in allMemberships:
    accepted = membership.get("accepted")
    active = membership.get("active")
    
    if accepted is None or accepted == False or accepted == 0:
        continue
    if accepted != 1 and accepted != True:
        continue
    if active is None or active == False or active == 0:
        continue
    if active != 1 and active != True:
        continue
    
    member_email = membership.get("email")
    if not member_email:
        continue
    
    # This is the query from getAnalytics - using 1 instead of True
    member_requirements = RequirementsModel().getAndSearch(["email", "accepted"], [member_email, 1])
    if len(member_requirements) == 0:
        continue
    
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

print(f"   Members counted: {counted}")
print(f"   Age groups: {ageGroup}")
print(f"   Sex groups: {sexGroup}")

# Test getActiveMemberData query
print("\n2. Testing getActiveMemberData() query:")
# Using 1 instead of True
activeMembers = MembershipModel().getAndSearch(["active", "accepted"], [1, 1])
print(f"   Active members found: {len(activeMembers)}")

members_with_data = 0
for activeMember in activeMembers[:5]:  # Test first 5
    userEmailIndicator = activeMember["email"]
    userFullname = activeMember["fullname"]
    
    matchedRequirements = RequirementsModel().getAndSearch(["email", "accepted"], [userEmailIndicator, 1])
    if len(matchedRequirements) == 0:
        continue
    
    participation_count = 0
    for requirement in matchedRequirements:
        matchedEvaluation = EvaluationModel().getAndSearch(["requirementId", "finalized"], [requirement["id"], 1])
        if len(matchedEvaluation) == 0:
            continue
        
        matchedEvaluation = matchedEvaluation[0]
        if matchedEvaluation["recommendations"] != "":
            participation_count += 1
    
    print(f"   - {userFullname}: {participation_count} participations")
    members_with_data += 1

print(f"   Members with participation data: {members_with_data}")

print("\n" + "=" * 60)
if counted > 0 and len(ageGroup) > 0 and len(sexGroup) > 0:
    print("✅ BACKEND QUERIES WORK! Data should display.")
else:
    print("❌ BACKEND QUERIES NOT WORKING - Check the queries above")
print("=" * 60)

















