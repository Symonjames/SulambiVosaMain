"""
Quick script to delete dummy volunteers - Run this to delete immediately
"""
import requests
import json

def delete_dummy_volunteers():
    url = "http://localhost:8000/api/analytics/dev/delete-dummy-volunteers"
    
    try:
        print("Calling deletion API...")
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("\n✅ SUCCESS! Dummy data deleted.")
                print(f"Total records deleted: {data.get('data', {}).get('total_deleted', 0)}")
            else:
                print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server.")
        print("Make sure your backend is running on http://localhost:8000")
        print("\nTo start backend:")
        print("  cd sulambi-backend-main/sulambi-backend-main")
        print("  python server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    delete_dummy_volunteers()





