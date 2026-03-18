"""
Script to remove all members from database that are NOT in the Excel file
Keeps only members that exist in member-app.xlsx
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

EXCEL_FILE = os.path.join("data", "member-app.xlsx")

def remove_members_not_in_excel():
    """Remove all members that are NOT in the Excel file"""
    print("=" * 70)
    print("REMOVING MEMBERS NOT IN EXCEL FILE")
    print("=" * 70)
    
    # Step 1: Read emails from Excel file
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Excel file not found: {EXCEL_FILE}")
        return
    
    print(f"Reading Excel file: {EXCEL_FILE}")
    try:
        loadData = pd.read_excel(EXCEL_FILE)
        print(f"✓ Found {len(loadData)} rows in Excel file\n")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return
    
    # Collect all emails from Excel (both regular and GSuite)
    excel_emails = set()
    for index, data in loadData.iterrows():
        if index == 0:  # Skip header
            continue
        
        email = str(data.get("Email Address", "")).strip()
        gsuite_email = str(data.get("Gsuite Email", "")).strip()
        
        if email and email != "nan":
            excel_emails.add(email.lower())
        if gsuite_email and gsuite_email != "nan":
            excel_emails.add(gsuite_email.lower())
    
    print(f"✓ Found {len(excel_emails)} unique emails in Excel file")
    
    # Step 2: Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all members from database
    cursor.execute("SELECT id, email, fullname, username FROM membership")
    all_members = cursor.fetchall()
    
    print(f"✓ Found {len(all_members)} total members in database\n")
    
    # Step 3: Find members to remove (not in Excel)
    members_to_remove = []
    for member_id, member_email, member_name, member_username in all_members:
        if member_email and member_email.lower() not in excel_emails:
            members_to_remove.append((member_id, member_email, member_name, member_username))
    
    if len(members_to_remove) == 0:
        print("✓ All members in database are in the Excel file. Nothing to remove.")
        conn.close()
        return
    
    print(f"⚠ Found {len(members_to_remove)} members to remove (not in Excel file)")
    print(f"✓ Will keep {len(all_members) - len(members_to_remove)} members (from Excel file)\n")
    
    # Confirm
    print("=" * 70)
    print("MEMBERS TO BE REMOVED (first 10):")
    print("=" * 70)
    for i, (member_id, member_email, member_name, _) in enumerate(members_to_remove[:10]):
        print(f"  {i+1}. {member_name} ({member_email})")
    if len(members_to_remove) > 10:
        print(f"  ... and {len(members_to_remove) - 10} more")
    print("=" * 70)
    
    # Step 4: Remove all data for members not in Excel
    removed_evals = 0
    removed_reqs = 0
    removed_accounts = 0
    removed_sessions = 0
    removed_members = 0
    
    member_emails_to_remove = [m[1] for m in members_to_remove]
    member_ids_to_remove = [m[0] for m in members_to_remove]
    member_usernames_to_remove = [m[3] for m in members_to_remove if m[3]]
    
    print("\nRemoving associated data...")
    
    # Remove evaluations
    if member_emails_to_remove:
        placeholders = ','.join(['?' for _ in member_emails_to_remove])
        cursor.execute(f"""
            DELETE FROM evaluation
            WHERE requirementId IN (
                SELECT id FROM requirements
                WHERE email IN ({placeholders})
            )
        """, member_emails_to_remove)
        removed_evals = cursor.rowcount
        conn.commit()
        print(f"   ✓ Removed {removed_evals} evaluations")
    
    # Remove requirements
    if member_emails_to_remove:
        placeholders = ','.join(['?' for _ in member_emails_to_remove])
        cursor.execute(f"""
            DELETE FROM requirements
            WHERE email IN ({placeholders})
        """, member_emails_to_remove)
        removed_reqs = cursor.rowcount
        conn.commit()
        print(f"   ✓ Removed {removed_reqs} requirements")
    
    # Remove accounts
    if member_usernames_to_remove:
        username_placeholders = ','.join(['?' for _ in member_usernames_to_remove])
        cursor.execute(f"""
            DELETE FROM accounts
            WHERE username IN ({username_placeholders})
        """, member_usernames_to_remove)
        removed_accounts = cursor.rowcount
        conn.commit()
        print(f"   ✓ Removed {removed_accounts} accounts")
    
    # Remove sessions
    if member_ids_to_remove:
        id_placeholders = ','.join(['?' for _ in member_ids_to_remove])
        cursor.execute(f"""
            DELETE FROM sessions
            WHERE userid IN (
                SELECT id FROM accounts
                WHERE membershipId IN ({id_placeholders})
            )
        """, member_ids_to_remove)
        removed_sessions = cursor.rowcount
        conn.commit()
        print(f"   ✓ Removed {removed_sessions} sessions")
    
    # Remove members
    if member_ids_to_remove:
        id_placeholders = ','.join(['?' for _ in member_ids_to_remove])
        cursor.execute(f"""
            DELETE FROM membership
            WHERE id IN ({id_placeholders})
        """, member_ids_to_remove)
        removed_members = cursor.rowcount
        conn.commit()
        print(f"   ✓ Removed {removed_members} members")
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM membership")
    final_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("REMOVAL SUMMARY")
    print("=" * 70)
    print(f"Members in Excel file: {len(excel_emails)}")
    print(f"Members before removal: {len(all_members)}")
    print(f"Members removed: {removed_members}")
    print(f"Members after removal: {final_count}")
    print(f"\nAssociated data removed:")
    print(f"  - Evaluations: {removed_evals}")
    print(f"  - Requirements: {removed_reqs}")
    print(f"  - Accounts: {removed_accounts}")
    print(f"  - Sessions: {removed_sessions}")
    print("=" * 70)
    
    return removed_members

if __name__ == "__main__":
    remove_members_not_in_excel()

















