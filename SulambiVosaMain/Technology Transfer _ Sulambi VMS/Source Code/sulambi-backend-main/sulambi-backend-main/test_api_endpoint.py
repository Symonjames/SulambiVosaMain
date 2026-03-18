"""
Test the actual API endpoint response
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.controllers.dashboard import getAnalytics
import json

print("=" * 70)
print("TESTING API ENDPOINT RESPONSE")
print("=" * 70)

result = getAnalytics()

print("\nFull API Response:")
print(json.dumps(result, indent=2))

print("\n" + "=" * 70)
print("DATA STRUCTURE:")
print("=" * 70)

if 'data' in result:
    data = result['data']
    print(f"Has 'data' key: ✓")
    
    if 'ageGroup' in data:
        age_group = data['ageGroup']
        print(f"Has 'ageGroup' key: ✓")
        print(f"Age group type: {type(age_group)}")
        print(f"Age group keys: {list(age_group.keys())}")
        print(f"Age group values: {age_group}")
    else:
        print(f"Has 'ageGroup' key: ✗")
    
    if 'sexGroup' in data:
        sex_group = data['sexGroup']
        print(f"Has 'sexGroup' key: ✓")
        print(f"Sex group type: {type(sex_group)}")
        print(f"Sex group keys: {list(sex_group.keys())}")
        print(f"Sex group values: {sex_group}")
    else:
        print(f"Has 'sexGroup' key: ✗")
else:
    print(f"Has 'data' key: ✗")
    print(f"Response keys: {list(result.keys())}")

















