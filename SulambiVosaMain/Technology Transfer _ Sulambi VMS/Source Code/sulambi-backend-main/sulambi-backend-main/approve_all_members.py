"""
Script to approve all pending members in the database
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

print("=" * 70)
print("APPROVING ALL PENDING MEMBERS")
print("=" * 70)

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get count of pending members
cursor.execute("SELECT COUNT(*) FROM membership WHERE accepted IS NULL")
pending_count = cursor.fetchone()[0]

print(f"\n📊 Found {pending_count} pending members to approve\n")

if pending_count == 0:
    print("✓ No pending members to approve!")
    conn.close()
    exit(0)

# Get all pending members
cursor.execute("SELECT id, fullname, email FROM membership WHERE accepted IS NULL")
pending_members = cursor.fetchall()

print(f"Approving {pending_count} members...\n")

approved_count = 0
error_count = 0

for member_id, fullname, email in pending_members:
    try:
        # Update accepted to 1 (approved)
        cursor.execute("UPDATE membership SET accepted = 1 WHERE id = ?", (member_id,))
        
        # Create account for this member
        # First, get the member's username and password
        cursor.execute("SELECT username, password FROM membership WHERE id = ?", (member_id,))
        member_data = cursor.fetchone()
        
        if member_data:
            username, password = member_data
            
            # Check if account already exists
            cursor.execute("SELECT id FROM accounts WHERE username = ?", (username,))
            existing_account = cursor.fetchone()
            
            if not existing_account:
                # Create new account
                cursor.execute("""
                    INSERT INTO accounts (accountType, username, password, active, membershipId)
                    VALUES (?, ?, ?, ?, ?)
                """, ("member", username, password, 1, member_id))
            else:
                # Update existing account to link to membership
                account_id = existing_account[0]
                cursor.execute("""
                    UPDATE accounts 
                    SET membershipId = ?, active = 1 
                    WHERE id = ?
                """, (member_id, account_id))
        
        approved_count += 1
        
        if approved_count % 10 == 0:
            conn.commit()
            print(f"   ✓ Approved {approved_count}/{pending_count} members...")
    
    except Exception as e:
        error_count += 1
        print(f"   ❌ Error approving member {member_id} ({fullname}): {e}")
        continue

# Final commit
conn.commit()

# Verify the update
cursor.execute("SELECT COUNT(*) FROM membership WHERE accepted = 1")
approved_total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM membership WHERE accepted IS NULL")
still_pending = cursor.fetchone()[0]

conn.close()

print("\n" + "=" * 70)
print("APPROVAL SUMMARY")
print("=" * 70)
print(f"✓ Successfully approved: {approved_count} members")
print(f"❌ Errors: {error_count} members")
print(f"\n📊 Current Status:")
print(f"   Total approved members: {approved_total}")
print(f"   Still pending: {still_pending}")
print("=" * 70)

if approved_count > 0:
    print("\n✅ All members have been approved!")
    print("💡 Refresh the Membership Approval page to see the changes.")
else:
    print("\n⚠️  No members were approved. Check for errors above.")



