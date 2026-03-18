"""
Script to:
1. Remove all dummy members from the database
2. Import real members from Excel file (data/member-app.xlsx)
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

EXCEL_FILE = os.path.join("data", "member-app.xlsx")

def remove_dummy_members():
    """Remove all dummy/test members from the database"""
    print("=" * 60)
    print("REMOVING DUMMY MEMBERS")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find dummy members - those with:
    # 1. Password = "Password123!" (common dummy password)
    # 2. GSuite emails that are test data (@g.batstate-u.edu.ph with test patterns)
    # 3. Test/dummy names
    cursor.execute("""
        SELECT id, email, fullname, username 
        FROM membership 
        WHERE password = 'Password123!'
           OR (email LIKE '%@g.batstate-u.edu.ph' AND (fullname LIKE '%Test%' OR fullname LIKE '%Dummy%' OR fullname LIKE '%Sample%'))
           OR LOWER(fullname) LIKE 'test user%'
           OR LOWER(fullname) LIKE 'dummy user%'
           OR LOWER(fullname) LIKE 'sample user%'
           OR LOWER(email) LIKE 'test%@%'
           OR LOWER(email) LIKE 'dummy%@%'
           OR LOWER(email) LIKE 'sample%@%'
    """)
    dummy_members = cursor.fetchall()
    
    if len(dummy_members) == 0:
        print("✓ No dummy members found to remove")
        conn.close()
        return 0
    
    print(f"\nFound {len(dummy_members)} dummy members to remove")
    
    # Get emails and IDs
    dummy_emails = [member[1] for member in dummy_members]
    dummy_ids = [member[0] for member in dummy_members]
    dummy_usernames = [member[3] for member in dummy_members if member[3]]
    
    # Step 1: Remove evaluations for requirements of dummy members
    print("\n1. Removing evaluations...")
    if dummy_emails:
        placeholders = ','.join(['?' for _ in dummy_emails])
        cursor.execute(f"""
            DELETE FROM evaluation
            WHERE requirementId IN (
                SELECT id FROM requirements
                WHERE email IN ({placeholders})
            )
        """, dummy_emails)
        evals_removed = cursor.rowcount
        print(f"   ✓ Removed {evals_removed} evaluations")
        conn.commit()
    
    # Step 2: Remove requirements for dummy members
    print("2. Removing requirements...")
    if dummy_emails:
        placeholders = ','.join(['?' for _ in dummy_emails])
        cursor.execute(f"""
            DELETE FROM requirements
            WHERE email IN ({placeholders})
        """, dummy_emails)
        reqs_removed = cursor.rowcount
        print(f"   ✓ Removed {reqs_removed} requirements")
        conn.commit()
    
    # Step 3: Remove accounts for dummy members
    print("3. Removing accounts...")
    if dummy_usernames:
        username_placeholders = ','.join(['?' for _ in dummy_usernames])
        cursor.execute(f"""
            DELETE FROM accounts
            WHERE username IN ({username_placeholders})
        """, dummy_usernames)
        accounts_removed = cursor.rowcount
        print(f"   ✓ Removed {accounts_removed} accounts")
        conn.commit()
    
    # Step 4: Remove sessions for dummy accounts
    print("4. Removing sessions...")
    if dummy_ids:
        id_placeholders = ','.join(['?' for _ in dummy_ids])
        cursor.execute(f"""
            DELETE FROM sessions
            WHERE userid IN (
                SELECT id FROM accounts
                WHERE membershipId IN ({id_placeholders})
            )
        """, dummy_ids)
        sessions_removed = cursor.rowcount
        print(f"   ✓ Removed {sessions_removed} sessions")
        conn.commit()
    
    # Step 5: Remove members
    print("5. Removing members...")
    if dummy_ids:
        id_placeholders = ','.join(['?' for _ in dummy_ids])
        cursor.execute(f"""
            DELETE FROM membership
            WHERE id IN ({id_placeholders})
        """, dummy_ids)
        members_removed = cursor.rowcount
        print(f"   ✓ Removed {members_removed} members")
        conn.commit()
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✓ Successfully removed {members_removed} dummy members and all associated data")
    print("=" * 60)
    
    return members_removed

def import_from_excel():
    """Import members from Excel file"""
    print("\n" + "=" * 60)
    print("IMPORTING MEMBERS FROM EXCEL")
    print("=" * 60)
    
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Excel file not found: {EXCEL_FILE}")
        return 0
    
    print(f"Reading Excel file: {EXCEL_FILE}")
    
    try:
        loadData = pd.read_excel(EXCEL_FILE)
        print(f"✓ Found {len(loadData)} rows in Excel file")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
                print(f"   Processed {inserted} members...")
        
        except Exception as e:
            errors += 1
            print(f"   ❌ Error processing row {index}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully imported: {inserted} members")
    print(f"⚠ Skipped (already exists): {skipped} members")
    print(f"❌ Errors: {errors} rows")
    print("=" * 60)
    
    return inserted

def main():
    print("\n" + "=" * 70)
    print("REMOVE DUMMY MEMBERS AND IMPORT FROM EXCEL")
    print("=" * 70)
    
    # Step 1: Remove dummy members
    removed_count = remove_dummy_members()
    
    # Step 2: Import from Excel
    imported_count = import_from_excel()
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"✓ Removed {removed_count} dummy members")
    print(f"✓ Imported {imported_count} real members from Excel")
    print("=" * 70)

if __name__ == "__main__":
    main()

