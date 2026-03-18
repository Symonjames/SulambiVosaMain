#!/usr/bin/env python3
"""
Remove 300 members from the database
Keep only the 1 real member and the 100 most recent makeup members
"""

import sqlite3
import os
from dotenv import load_dotenv

# Get database path (same as backend)
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(backend_dir, DB_PATH)

print("=" * 60)
print("REMOVING 300 MEMBERS FROM DATABASE")
print("=" * 60)
print(f"Database: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check current member count
cursor.execute("SELECT COUNT(*) FROM membership")
total_members = cursor.fetchone()[0]
print(f"\nCurrent total members: {total_members}")

# Get all members ordered by ID (to keep the most recent 101)
cursor.execute("SELECT id, email, fullname FROM membership ORDER BY id DESC")
all_members = cursor.fetchall()

print(f"Total members found: {len(all_members)}")

# Keep the most recent 101 members (1 real + 100 makeup)
# Remove the rest (oldest 300)
members_to_keep = all_members[:101]  # Most recent 101
members_to_remove = all_members[101:]  # Oldest members

print(f"\nMembers to keep: {len(members_to_keep)}")
print(f"Members to remove: {len(members_to_remove)}")

if len(members_to_remove) == 0:
    print("\n✓ No members to remove. Already at target count.")
    conn.close()
    exit(0)

# Show what will be kept
print(f"\nSample members to keep (first 5):")
for member in members_to_keep[:5]:
    print(f"  - ID: {member[0]}, {member[2]} ({member[1]})")

print(f"\nSample members to remove (first 5):")
for member in members_to_remove[:5]:
    print(f"  - ID: {member[0]}, {member[2]} ({member[1]})")

# Get emails of members to remove
emails_to_remove = [member[1] for member in members_to_remove]
ids_to_remove = [member[0] for member in members_to_remove]

print(f"\nRemoving {len(members_to_remove)} members and their data...")

# Step 1: Remove evaluations for requirements of members to be removed
print("\n1. Removing evaluations...")
placeholders = ','.join(['?' for _ in emails_to_remove])
cursor.execute(f"""
    DELETE FROM evaluation
    WHERE requirementId IN (
        SELECT id FROM requirements
        WHERE email IN ({placeholders})
    )
""", emails_to_remove)
evals_removed = cursor.rowcount
print(f"   ✓ Removed {evals_removed} evaluations")

# Step 2: Remove requirements for members to be removed
print("2. Removing requirements...")
cursor.execute(f"""
    DELETE FROM requirements
    WHERE email IN ({placeholders})
""", emails_to_remove)
reqs_removed = cursor.rowcount
print(f"   ✓ Removed {reqs_removed} requirements")

# Step 3: Remove accounts for members to be removed (accounts table uses username, not email)
print("3. Removing accounts...")
# Get usernames from members to remove
cursor.execute(f"""
    SELECT username FROM membership
    WHERE email IN ({placeholders})
""", emails_to_remove)
usernames_to_remove = [row[0] for row in cursor.fetchall() if row[0]]

if usernames_to_remove:
    username_placeholders = ','.join(['?' for _ in usernames_to_remove])
    cursor.execute(f"""
        DELETE FROM accounts
        WHERE username IN ({username_placeholders})
    """, usernames_to_remove)
    accounts_removed = cursor.rowcount
    print(f"   ✓ Removed {accounts_removed} accounts")
else:
    accounts_removed = 0
    print(f"   ✓ No accounts to remove")

# Step 4: Remove members
print("4. Removing members...")
id_placeholders = ','.join(['?' for _ in ids_to_remove])
cursor.execute(f"""
    DELETE FROM membership
    WHERE id IN ({id_placeholders})
""", ids_to_remove)
members_removed = cursor.rowcount
print(f"   ✓ Removed {members_removed} members")

conn.commit()

# Verify results
cursor.execute("SELECT COUNT(*) FROM membership")
remaining_members = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM membership WHERE active = 1 AND accepted = 1")
active_accepted = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
remaining_reqs = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
remaining_evals = cursor.fetchone()[0]

conn.close()

print("\n" + "=" * 60)
print("✅ MEMBERS REMOVED!")
print("=" * 60)
print(f"\nResults:")
print(f"  - Removed {members_removed} members")
print(f"  - Removed {reqs_removed} requirements")
print(f"  - Removed {evals_removed} evaluations")
print(f"  - Removed {accounts_removed} accounts")
print(f"\nRemaining:")
print(f"  - Total members: {remaining_members}")
print(f"  - Active & accepted: {active_accepted}")
print(f"  - Requirements: {remaining_reqs}")
print(f"  - Evaluations: {remaining_evals}")

print("\n" + "=" * 60)

