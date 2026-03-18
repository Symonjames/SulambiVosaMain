"""
Test the dropout risk analytics endpoint to see if it returns data
"""

import requests
import json

API_URL = "http://localhost:8000/api/analytics/volunteer-dropout"

print("=" * 70)
print("TESTING DROPOUT RISK ANALYTICS ENDPOINT")
print("=" * 70)

try:
    print(f"\n[INFO] Calling endpoint: {API_URL}")
    response = requests.get(API_URL, timeout=10)
    
    print(f"[INFO] Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Request successful!")
        print(f"\nResponse structure:")
        print(f"  - success: {data.get('success')}")
        print(f"  - message: {data.get('message')}")
        
        if data.get('data'):
            semester_data = data['data'].get('semesterData', [])
            at_risk = data['data'].get('atRiskVolunteers', [])
            
            print(f"\nData breakdown:")
            print(f"  - Semester data entries: {len(semester_data)}")
            print(f"  - At-risk volunteers: {len(at_risk)}")
            
            if semester_data:
                print(f"\nFirst semester entry:")
                print(f"  {json.dumps(semester_data[0], indent=2)}")
            
            if at_risk:
                print(f"\nFirst at-risk volunteer:")
                print(f"  {json.dumps(at_risk[0], indent=2)}")
            else:
                print(f"\n[INFO] No at-risk volunteers found (this is OK if all members have good participation)")
            
            print(f"\n[OK] Endpoint is working and returning data!")
        else:
            print(f"\n[WARNING] No data field in response")
            print(f"Full response: {json.dumps(data, indent=2)}")
    else:
        print(f"[ERROR] Request failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print(f"[ERROR] Cannot connect to backend server at {API_URL}")
    print(f"[INFO] Make sure the backend server is running on port 8000")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 70)























