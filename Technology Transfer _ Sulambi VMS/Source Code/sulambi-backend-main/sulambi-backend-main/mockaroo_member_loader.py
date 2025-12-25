import requests
import pandas as pd
import json
import random
from datetime import datetime

# Configuration
API_ENDPOINT = "http://localhost:8000/api/auth/register"
CSV_FILE_PATH = "mockaroo_members.csv"  # Update this to your CSV file path

def generate_username(fullname, index):
    """Generate username from fullname"""
    name_parts = fullname.lower().replace(",", "").split()
    if len(name_parts) >= 2:
        return f"{name_parts[0]}{name_parts[1][0]}{index}"
    return f"user{index}"

def generate_password():
    """Generate random password"""
    passwords = ["password123", "member2024", "sulambi2024", "volunteer2024", "batstate2024"]
    return random.choice(passwords)

def format_areas_of_interest(areas_str):
    """Format areas of interest as JSON array"""
    if pd.isna(areas_str) or areas_str == "":
        return "[]"
    
    # Split by comma and clean up
    areas = [area.strip() for area in str(areas_str).split(",")]
    return json.dumps(areas)

def format_birthday(birthday_str):
    """Format birthday to match expected format"""
    if pd.isna(birthday_str):
        return "January, 1 2000"
    
    try:
        # Try to parse different date formats
        if isinstance(birthday_str, str):
            # If already in correct format
            if "," in birthday_str and " " in birthday_str:
                return birthday_str
            # Try to parse and reformat
            date_obj = pd.to_datetime(birthday_str)
            return date_obj.strftime("%B, %d %Y")
        else:
            return birthday_str.strftime("%B, %d %Y")
    except:
        return "January, 1 2000"

def insert_member(data):
    """Insert member data via API"""
    try:
        response = requests.post(
            API_ENDPOINT, 
            json=data, 
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully registered: {data['username']}")
            return True
        else:
            print(f"❌ Failed to register {data['username']}: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error registering {data['username']}: {str(e)}")
        return False

def load_members_from_csv(csv_file):
    """Load and process members from CSV file"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} records from {csv_file}")
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            # Generate username and password
            username = generate_username(row['fullname'], index + 1)
            password = generate_password()
            
            # Format areas of interest
            areas_of_interest = format_areas_of_interest(row.get('areasOfInterest', ''))
            
            # Format birthday
            birthday = format_birthday(row.get('birthday', ''))
            
            # Prepare data for API
            member_data = {
                "applyingAs": str(row.get('applyingAs', 'Student')),
                "volunterismExperience": bool(row.get('volunterismExperience', False)),
                "weekdaysTimeDevotion": str(row.get('weekdaysTimeDevotion', '1-2 hours')),
                "weekendsTimeDevotion": str(row.get('weekendsTimeDevotion', '1-2 hours')),
                "areasOfInterest": areas_of_interest,
                "fullname": str(row.get('fullname', '')),
                "email": str(row.get('email', '')),
                "affiliation": str(row.get('affiliation', 'Batangas State University')),
                "srcode": str(row.get('srcode', f'24-{index+1:05d}')),
                "age": int(row.get('age', 20)),
                "birthday": birthday,
                "sex": str(row.get('sex', 'Male')),
                "campus": str(row.get('campus', 'Main Campus')),
                "collegeDept": str(row.get('collegeDept', 'College of Engineering')),
                "yrlevelprogram": str(row.get('yrlevelprogram', '1st Year - BS Computer Science')),
                "address": str(row.get('address', 'Batangas City')),
                "contactNum": str(row.get('contactNum', '+63 912 345 6789')),
                "fblink": str(row.get('fblink', 'https://facebook.com')),
                "bloodType": str(row.get('bloodType', 'O+')),
                "bloodDonation": str(row.get('bloodDonation', 'Yes')),
                "medicalCondition": str(row.get('medicalCondition', 'None')),
                "paymentOption": str(row.get('paymentOption', 'GCash')),
                "username": username,
                "password": password,
                "volunteerExpQ1": str(row.get('volunteerExpQ1', '')),
                "volunteerExpQ2": str(row.get('volunteerExpQ2', '')),
                "volunteerExpProof": str(row.get('volunteerExpProof', '')),
                "reasonQ1": str(row.get('reasonQ1', 'I want to help the community')),
                "reasonQ2": str(row.get('reasonQ2', 'I can contribute my skills and time'))
            }
            
            # Insert member
            if insert_member(member_data):
                success_count += 1
            else:
                error_count += 1
            
            # Add small delay to avoid overwhelming the server
            import time
            time.sleep(0.1)
        
        print(f"\n📈 Summary:")
        print(f"✅ Successfully registered: {success_count}")
        print(f"❌ Failed to register: {error_count}")
        print(f"📊 Total processed: {success_count + error_count}")
        
    except FileNotFoundError:
        print(f"❌ Error: CSV file '{csv_file}' not found!")
        print("Please make sure the CSV file exists in the same directory.")
    except Exception as e:
        print(f"❌ Error loading CSV file: {str(e)}")

def main():
    """Main function"""
    print("🚀 Sulambi VMS Member Data Loader")
    print("=" * 50)
    
    # Check if CSV file exists
    import os
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ CSV file '{CSV_FILE_PATH}' not found!")
        print("\n📝 Instructions:")
        print("1. Generate data from Mockaroo using the provided schema")
        print("2. Save the CSV file as 'mockaroo_members.csv' in this directory")
        print("3. Run this script again")
        return
    
    # Load members
    load_members_from_csv(CSV_FILE_PATH)

if __name__ == "__main__":
    main()
























