"""
Test the satisfaction analytics API endpoint locally
This will help verify if the API is working correctly with SQLite
"""

import requests
import json

# Test the local backend API
url = "http://localhost:8000/api/analytics/satisfaction?year=2025"

print("="*70)
print("Testing Satisfaction Analytics API")
print("="*70)
print(f"URL: {url}\n")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("Response Data:")
        print(json.dumps(data, indent=2))
        
        if data.get('success'):
            satisfaction_data = data.get('data', {}).get('satisfactionData', [])
            print(f"\n[SUCCESS] Found {len(satisfaction_data)} satisfaction data entries")
            for item in satisfaction_data:
                print(f"  - {item.get('semester')}: Score={item.get('score')}, Vol={item.get('volunteers')}, Ben={item.get('beneficiaries')}")
        else:
            print(f"\n[ERROR] API returned success=false")
            print(f"Message: {data.get('message')}")
            print(f"Error: {data.get('error')}")
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Could not connect to http://localhost:8000")
    print("Make sure the backend server is running:")
    print("  python server.py")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")

print("\n" + "="*70)

