#!/usr/bin/env python3
"""
Script to remove the 100 people added by add_100_people.py
This will delete their requirements and membership records
"""

import sqlite3
import os

# Database path
DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

def remove_100_people():
    """Remove the 100 people added by the add_100_people script"""
    print("=" * 60)
    print("REMOVING 100 PEOPLE FROM SULAMBI VMS")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Please make sure the database file exists.")
        return
    
    print(f"✓ Database found: {DB_PATH}\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if membership table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='membership'
    """)
    
    if not cursor.fetchone():
        print("❌ Membership table does not exist!")
        conn.close()
        return
    
    # Find members with the default password "Password123!" (these are our test accounts)
    # Also check for members with GSuite emails that match our pattern
    print("Finding members to remove...")
    cursor.execute("""
        SELECT id, email, fullname, username 
        FROM membership 
        WHERE password = 'Password123!'
           OR email LIKE '%@g.batstate-u.edu.ph'
        ORDER BY id DESC
        LIMIT 150
    """)
    
    members_to_remove = cursor.fetchall()
    
    if not members_to_remove:
        print("⚠️  No members found matching the criteria.")
        print("   (Looking for members with password 'Password123!' or GSuite emails)")
        conn.close()
        return
    
    print(f"Found {len(members_to_remove)} members to remove.\n")
    
    # Show first 10 for confirmation
    print("Sample members to be removed:")
    for i, (member_id, email, fullname, username) in enumerate(members_to_remove[:10]):
        print(f"  {i+1}. {fullname} ({email}) - ID: {member_id}")
    if len(members_to_remove) > 10:
        print(f"  ... and {len(members_to_remove) - 10} more")
    
    print("\n⚠️  WARNING: This will permanently delete:")
    print("  - All membership records")
    print("  - All associated requirements (volunteer registrations)")
    print("  - All associated accounts")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Operation cancelled.")
        conn.close()
        return
    
    print("\nRemoving members and their data...")
    
    removed_members = 0
    removed_requirements = 0
    removed_accounts = 0
    
    for member_id, email, fullname, username in members_to_remove:
        try:
            # 1. Delete requirements (volunteer registrations) first
            cursor.execute("DELETE FROM requirements WHERE email = ?", (email,))
            req_deleted = cursor.rowcount
            removed_requirements += req_deleted
            
            # 2. Delete associated accounts
            cursor.execute("DELETE FROM accounts WHERE membershipId = ?", (member_id,))
            acc_deleted = cursor.rowcount
            removed_accounts += acc_deleted
            
            # 3. Delete the membership record
            cursor.execute("DELETE FROM membership WHERE id = ?", (member_id,))
            if cursor.rowcount > 0:
                removed_members += 1
            
        except Exception as e:
            print(f"  Error removing member {member_id} ({fullname}): {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ REMOVAL COMPLETE!")
    print("=" * 60)
    print(f"\nRemoved:")
    print(f"  - {removed_members} membership records")
    print(f"  - {removed_requirements} requirement records (volunteer registrations)")
    print(f"  - {removed_accounts} account records")
    print("\nThe 100 people have been removed from the system.")

if __name__ == "__main__":
    remove_100_people()

















