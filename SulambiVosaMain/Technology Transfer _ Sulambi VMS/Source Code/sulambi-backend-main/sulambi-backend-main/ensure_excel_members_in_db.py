"""
Script to ensure all members from member-app.xlsx are in the database
and set as accepted and active for dropout risk assessment
"""

import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(SCRIPT_DIR, "data", "member-app.xlsx")

print("=" * 70)
print("ENSURING EXCEL MEMBERS ARE IN DATABASE")
print("=" * 70)

# Check if Excel file exists
if not os.path.exists(EXCEL_FILE):
    print(f"[ERROR] Excel file not found: {EXCEL_FILE}")
    exit(1)

print(f"[OK] Found Excel file: {EXCEL_FILE}")

# Read Excel file
try:
    df = pd.read_excel(EXCEL_FILE)
    print(f"[OK] Read {len(df)} rows from Excel file")
except Exception as e:
    print(f"[ERROR] Failed to read Excel file: {e}")
    exit(1)

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get current members from database
cursor.execute("SELECT email, fullname, accepted, active FROM membership")
db_members = {row[0]: {'name': row[1], 'accepted': row[2], 'active': row[3]} for row in cursor.fetchall()}
print(f"[OK] Found {len(db_members)} members in database")

# Process Excel members
excel_emails = set()
missing_members = []
needs_update = []

for index, row in df.iterrows():
    # Skip header row
    if index == 0:
        continue
    
    # Get email (prefer GSuite email)
    email = str(row.get("Email Address", "")).strip()
    gsuite_email = str(row.get("Gsuite Email", "")).strip()
    final_email = gsuite_email if gsuite_email and gsuite_email != "nan" else email
    
    if not final_email or final_email == "nan":
        continue
    
    fullname = str(row.get("Name (Last Name, First Name, Middle Initial)", "")).strip()
    if not fullname or fullname == "nan":
        continue
    
    excel_emails.add(final_email)
    
    # Check if member exists in database
    if final_email not in db_members:
        missing_members.append({
            'email': final_email,
            'name': fullname,
            'row': index
        })
    else:
        # Check if needs to be updated (not accepted or not active)
        member = db_members[final_email]
        if member['accepted'] != 1 or member['active'] != 1:
            needs_update.append({
                'email': final_email,
                'name': fullname,
                'accepted': member['accepted'],
                'active': member['active']
            })

print(f"\n[INFO] Members in Excel: {len(excel_emails)}")
print(f"[INFO] Members in database: {len(db_members)}")
print(f"[INFO] Missing from database: {len(missing_members)}")
print(f"[INFO] Need update (not accepted/active): {len(needs_update)}")

# Import missing members using the existing import script
if missing_members:
    print(f"\n[ACTION] Importing {len(missing_members)} missing members...")
    try:
        # Import using the existing script
        from import_all_members_from_excel import import_all_from_excel
        imported = import_all_from_excel()
        print(f"[OK] Imported {imported} new members")
        
        # Refresh database members list
        cursor.execute("SELECT email, fullname, accepted, active FROM membership")
        db_members = {row[0]: {'name': row[1], 'accepted': row[2], 'active': row[3]} for row in cursor.fetchall()}
    except Exception as e:
        print(f"[ERROR] Failed to import members: {e}")

# Update members to be accepted and active
if needs_update:
    print(f"\n[ACTION] Updating {len(needs_update)} members to accepted=1 and active=1...")
    updated = 0
    for member in needs_update:
        try:
            cursor.execute("""
                UPDATE membership 
                SET accepted = 1, active = 1 
                WHERE email = ?
            """, (member['email'],))
            updated += 1
        except Exception as e:
            print(f"[ERROR] Failed to update {member['email']}: {e}")
    
    conn.commit()
    print(f"[OK] Updated {updated} members")

# Final verification
cursor.execute("SELECT COUNT(*) FROM membership WHERE accepted = 1 AND active = 1")
active_accepted_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM membership")
total_count = cursor.fetchone()[0]

print("\n" + "=" * 70)
print("FINAL STATUS")
print("=" * 70)
print(f"Total members in database: {total_count}")
print(f"Active and accepted members: {active_accepted_count}")
print(f"Members from Excel: {len(excel_emails)}")
print("=" * 70)

if active_accepted_count >= len(excel_emails):
    print("\n[OK] All Excel members are in the database and ready for dropout risk assessment!")
else:
    print(f"\n[WARNING] Only {active_accepted_count} out of {len(excel_emails)} Excel members are active and accepted")

conn.close()























