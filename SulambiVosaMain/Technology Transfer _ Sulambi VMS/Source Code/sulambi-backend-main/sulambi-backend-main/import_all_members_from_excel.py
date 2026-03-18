"""
Script to import ALL members from Excel file into the database
Skips duplicates based on email address
"""

import sqlite3
import pandas as pd
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Excel file path relative to script location
# Try multiple filename variations (including with spaces)
EXCEL_FILE = os.path.join(SCRIPT_DIR, "data", "member-app.xlsx")
EXCEL_FILE_ALT1 = os.path.join(SCRIPT_DIR, "data", "member- app.xlsx")  # With space
EXCEL_FILE_ALT2 = os.path.join(SCRIPT_DIR, "data", "members-app.xlsx")
EXCEL_FILE_ALT3 = os.path.join(SCRIPT_DIR, "data", "member_app.xlsx")
EXCEL_FILE_ALT4 = os.path.join(SCRIPT_DIR, "data", "members_app.xlsx")
EXCEL_FILE_ALT5 = os.path.join(SCRIPT_DIR, "data", "member app.xlsx")  # With space, no dash

def import_all_from_excel():
    """Import all members from Excel file, skipping duplicates"""
    print("=" * 70)
    print("IMPORTING ALL MEMBERS FROM EXCEL")
    print("=" * 70)
    
    # Try to find the Excel file with different possible names
    excel_file_to_use = None
    for file_path in [EXCEL_FILE, EXCEL_FILE_ALT1, EXCEL_FILE_ALT2, EXCEL_FILE_ALT3, EXCEL_FILE_ALT4, EXCEL_FILE_ALT5]:
        if os.path.exists(file_path):
            excel_file_to_use = file_path
            break
    
    # If still not found, try to find any .xlsx file in data folder that contains "member"
    if not excel_file_to_use:
        data_dir = os.path.join(SCRIPT_DIR, "data")
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.xlsx') and 'member' in file.lower():
                    excel_file_to_use = os.path.join(data_dir, file)
                    print(f"⚠️  Found Excel file with 'member' in name: {file}")
                    break
    
    if not excel_file_to_use:
        print(f"❌ Excel file not found. Tried:")
        print(f"   - {EXCEL_FILE}")
        print(f"   - {EXCEL_FILE_ALT1} (with space)")
        print(f"   - {EXCEL_FILE_ALT2}")
        print(f"   - {EXCEL_FILE_ALT3}")
        print(f"   - {EXCEL_FILE_ALT4}")
        print(f"   - {EXCEL_FILE_ALT5}")
        print(f"\nPlease ensure the Excel file exists in the 'data' folder.")
        print(f"Looking in: {os.path.join(SCRIPT_DIR, 'data')}")
        return 0
    
    print(f"✓ Found Excel file: {excel_file_to_use}")
    print(f"Reading Excel file: {excel_file_to_use}")
    
    try:
        loadData = pd.read_excel(excel_file_to_use)
        total_rows = len(loadData)
        print(f"✓ Found {total_rows} rows in Excel file (including header)")
        print(f"✓ Expected {total_rows - 1} members to import\n")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current count
    cursor.execute("SELECT COUNT(*) FROM membership")
    before_count = cursor.fetchone()[0]
    print(f"Current members in database: {before_count}\n")
    
    inserted = 0
    skipped = 0
    errors = 0
    
    for index, data in loadData.iterrows():
        try:
            # Skip header row
            if index == 0:
                continue
            
            # Extract data from Excel columns
            fullname = str(data.get("Name (Last Name, First Name, Middle Initial)", "")).strip()
            email = str(data.get("Email Address", "")).strip()
            gsuite_email = str(data.get("Gsuite Email", "")).strip()
            
            # Use GSuite email if available, otherwise use regular email
            final_email = gsuite_email if gsuite_email and gsuite_email != "nan" else email
            
            if not final_email or final_email == "nan" or not fullname or fullname == "nan":
                skipped += 1
                continue
            
            # Check if member already exists
            cursor.execute("SELECT id FROM membership WHERE email = ?", (final_email,))
            if cursor.fetchone():
                skipped += 1
                continue
            
            # Extract all required fields
            applying_as = str(data.get("I'm applying as", "")).strip()
            volunterism_experience = str(data.get("Do you have any prior volunteerism experience?", "")).strip().lower()
            volunterism_experience_bool = volunterism_experience in ['yes', 'true', '1']
            
            weekdays_time = str(data.get("How much time can you devote for volunteering activities on weekdays?", "")).strip()
            weekends_time = str(data.get("How much time can you devote for volunteering activities on weekends?", "")).strip()
            
            areas_of_interest = data.get("What areas or interests do you want to volunteer in? Check the area(s) that interest you. ", "")
            if pd.isna(areas_of_interest):
                areas_of_interest = ""
            areas_of_interest = str(areas_of_interest).strip()
            
            srcode = str(data.get("Sr-Code", "")).strip()
            age = data.get("Age", 0)
            if pd.isna(age):
                age = 0
            age = int(age) if isinstance(age, (int, float)) else 0
            
            birthday = data.get("Birthday", "")
            if pd.isna(birthday):
                birthday = ""
            elif isinstance(birthday, pd.Timestamp):
                birthday = birthday.strftime("%B %d, %Y")
            else:
                birthday = str(birthday).strip()
            
            sex = str(data.get("Sex", "")).strip()
            campus = str(data.get("Campus", "")).strip()
            college_dept = str(data.get("College/Department", "")).strip()
            yrlevel_program = str(data.get("Year Level & Program", "")).strip()
            address = str(data.get("Address", "")).strip()
            contact_num = str(data.get("Contact Number", "")).strip()
            fblink = str(data.get("Facebook Link", "")).strip()
            blood_type = str(data.get("Blood Type", "")).strip()
            blood_donation = str(data.get("Blood Donation", "")).strip()
            medical_condition = str(data.get("Do you have any existing medical condition/s? If yes, please specify. If none, type N/A.", "")).strip()
            if not medical_condition or medical_condition == "nan":
                medical_condition = "N/A"
            payment_option = str(data.get("Payment Options", "")).strip()
            
            # Volunteer experience questions
            volunteer_exp_q1 = str(data.get("1. What volunteering activities of Sulambi VOSA last Academic Year did you join?", "")).strip()
            if pd.isna(volunteer_exp_q1):
                volunteer_exp_q1 = ""
            volunteer_exp_q2 = str(data.get("2. What volunteering activities did you join outside Sulambi VOSA and/or the University?", "")).strip()
            if pd.isna(volunteer_exp_q2):
                volunteer_exp_q2 = ""
            volunteer_exp_proof = str(data.get("2.1 Upload proof for the volunteering activities you joined outside(e.g. Pictures, Certificate)", "")).strip()
            if pd.isna(volunteer_exp_proof):
                volunteer_exp_proof = ""
            
            # Reason questions
            reason_q1 = str(data.get("Why do you want to become a member?", "")).strip()
            if pd.isna(reason_q1):
                reason_q1 = ""
            reason_q2 = str(data.get("What can you contribute to the organization?", "")).strip()
            if pd.isna(reason_q2):
                reason_q2 = ""
            
            # Generate username from first part of name
            username = fullname.split(" ")[0].replace(" ", "").replace(",", "") + str(index)
            password = "password"  # Default password
            
            # Insert into membership table (31 columns excluding id)
            cursor.execute("""
                INSERT INTO membership (
                    applyingAs, volunterismExperience, weekdaysTimeDevotion, weekendsTimeDevotion,
                    areasOfInterest, fullname, email, affiliation, srcode, age, birthday, sex,
                    campus, collegeDept, yrlevelprogram, address, contactNum, fblink,
                    bloodType, bloodDonation, medicalCondition, paymentOption,
                    username, password, active, accepted,
                    volunteerExpQ1, volunteerExpQ2, volunteerExpProof,
                    reasonQ1, reasonQ2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                applying_as, volunterism_experience_bool, weekdays_time, weekends_time,
                areas_of_interest, fullname, final_email, "Batangas State University", srcode, age, birthday, sex,
                campus, college_dept, yrlevel_program, address, contact_num, fblink,
                blood_type, blood_donation, medical_condition, payment_option,
                username, password, 1, None,  # active=1, accepted=None (pending)
                volunteer_exp_q1 or "", volunteer_exp_q2 or "", volunteer_exp_proof or "",
                reason_q1 or "", reason_q2 or ""
            ))
            
            inserted += 1
            
            if inserted % 10 == 0:
                conn.commit()
                print(f"   Processed {inserted} new members...")
        
        except Exception as e:
            errors += 1
            print(f"   ❌ Error processing row {index}: {e}")
            continue
    
    conn.commit()
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM membership")
    after_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"Members in Excel file: {total_rows - 1}")
    print(f"Members before import: {before_count}")
    print(f"✓ Successfully imported: {inserted} new members")
    print(f"⚠ Skipped (already exists): {skipped} members")
    print(f"❌ Errors: {errors} rows")
    print(f"Members after import: {after_count}")
    print(f"Total members now: {after_count}")
    print("=" * 70)
    
    return inserted

if __name__ == "__main__":
    import_all_from_excel()















