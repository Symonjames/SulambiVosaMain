"""
Test what the analytics function will return
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.controllers.dashboard import getAnalytics

print("=" * 70)
print("TESTING ANALYTICS OUTPUT")
print("=" * 70)

result = getAnalytics()

print("\nAnalytics Result:")
print(f"Message: {result.get('message')}")

data = result.get('data', {})
age_group = data.get('ageGroup', {})
sex_group = data.get('sexGroup', {})

print(f"\nAge Group Distribution:")
if age_group:
    for age, count in sorted(age_group.items(), key=lambda x: int(x[0])):
        print(f"  Age {age}: {count} members")
    print(f"  Total: {sum(age_group.values())} members")
else:
    print("  No age data")

print(f"\nSex Group Distribution:")
if sex_group:
    for sex, count in sorted(sex_group.items()):
        print(f"  {sex}: {count} members")
    print(f"  Total: {sum(sex_group.values())} members")
else:
    print("  No sex data")

print("\n" + "=" * 70)

















