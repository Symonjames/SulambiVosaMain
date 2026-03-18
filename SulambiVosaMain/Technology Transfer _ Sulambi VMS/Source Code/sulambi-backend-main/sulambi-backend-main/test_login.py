import requests
import json

# Test the login endpoint
def test_login():
    url = "http://localhost:8000/api/auth/login"
    
    # Test Admin credentials
    admin_data = {
        "username": "Admin",
        "password": "sulambi@2024"
    }
    
    # Test Officer credentials
    officer_data = {
        "username": "Sulambi-Officer", 
        "password": "password@2024"
    }
    
    print("Testing Admin login...")
    try:
        response = requests.post(url, json=admin_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nTesting Officer login...")
    try:
        response = requests.post(url, json=officer_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
