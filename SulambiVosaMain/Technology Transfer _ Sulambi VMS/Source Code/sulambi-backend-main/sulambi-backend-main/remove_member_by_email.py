"""
Script to remove all data for a specific member by email
"""

import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

def remove_member_by_email(email):
    """Remove all data for a member with the given email"""
    print("=" * 60)
    print(f"REMOVING ALL DATA FOR MEMBER: {email}")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Step 1: Find the member
    cursor.execute("SELECT id, email, fullname, username FROM membership WHERE email = ?", (email,))
    member = cursor.fetchone()
    
    if not member:
        print(f"❌ Member with email '{email}' not found")
        conn.close()
        return False
    
    member_id, member_email, member_name, member_username = member
    print(f"\n✓ Found member:")
    print(f"   ID: {member_id}")
    print(f"   Name: {member_name}")
    print(f"   Email: {member_email}")
    print(f"   Username: {member_username}")
    
    # Step 2: Remove evaluations for requirements of this member
    print("\n1. Removing evaluations...")
    cursor.execute("""
        DELETE FROM evaluation
        WHERE requirementId IN (
            SELECT id FROM requirements
            WHERE email = ?
        )
    """, (email,))
    evals_removed = cursor.rowcount
    print(f"   ✓ Removed {evals_removed} evaluations")
    conn.commit()
    
    # Step 3: Remove requirements for this member
    print("2. Removing requirements...")
    cursor.execute("DELETE FROM requirements WHERE email = ?", (email,))
    reqs_removed = cursor.rowcount
    print(f"   ✓ Removed {reqs_removed} requirements")
    conn.commit()
    
    # Step 4: Remove accounts for this member
    print("3. Removing accounts...")
    if member_username:
        cursor.execute("DELETE FROM accounts WHERE username = ?", (member_username,))
        accounts_removed = cursor.rowcount
        print(f"   ✓ Removed {accounts_removed} accounts")
        conn.commit()
    else:
        print("   ⚠ No username found, skipping account removal")
    
    # Step 5: Remove sessions for this member's accounts
    print("4. Removing sessions...")
    cursor.execute("""
        DELETE FROM sessions
        WHERE userid IN (
            SELECT id FROM accounts
            WHERE membershipId = ?
        )
    """, (member_id,))
    sessions_removed = cursor.rowcount
    print(f"   ✓ Removed {sessions_removed} sessions")
    conn.commit()
    
    # Step 6: Remove the member
    print("5. Removing member...")
    cursor.execute("DELETE FROM membership WHERE id = ?", (member_id,))
    members_removed = cursor.rowcount
    print(f"   ✓ Removed {members_removed} member(s)")
    conn.commit()
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✓ Successfully removed all data for {member_name} ({email})")
    print("=" * 60)
    print(f"Summary:")
    print(f"  - Evaluations removed: {evals_removed}")
    print(f"  - Requirements removed: {reqs_removed}")
    print(f"  - Accounts removed: {accounts_removed if member_username else 0}")
    print(f"  - Sessions removed: {sessions_removed}")
    print(f"  - Members removed: {members_removed}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    email = "dannyburke@gmail.com"
    remove_member_by_email(email)

















