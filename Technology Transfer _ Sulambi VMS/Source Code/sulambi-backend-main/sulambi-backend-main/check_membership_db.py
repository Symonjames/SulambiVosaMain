"""
Quick script to check membership data in database
"""
import sqlite3
import os

# Get database path
db_path = os.path.join("app", "database", "database.db")

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if membership table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='membership'")
if not cursor.fetchone():
    print("❌ Membership table does not exist!")
    conn.close()
    exit(1)

# Get total count
cursor.execute("SELECT COUNT(*) FROM membership")
total = cursor.fetchone()[0]
print(f"📊 Total members in database: {total}")

if total == 0:
    print("\n❌ No members found in database!")
    print("💡 Run the import script: python import_all_members_from_excel.py")
    conn.close()
    exit(0)

# Get sample members
cursor.execute("SELECT id, fullname, email, accepted, active FROM membership LIMIT 10")
rows = cursor.fetchall()

print(f"\n📋 Sample members (first 10):")
print("-" * 80)
print(f"{'ID':<5} {'Name':<30} {'Email':<35} {'Accepted':<10} {'Active':<10}")
print("-" * 80)

for row in rows:
    member_id, fullname, email, accepted, active = row
    accepted_str = "None" if accepted is None else str(accepted)
    active_str = "None" if active is None else str(active)
    name_display = (fullname[:27] + "...") if fullname and len(fullname) > 30 else (fullname or "N/A")
    email_display = (email[:32] + "...") if email and len(email) > 35 else (email or "N/A")
    print(f"{member_id:<5} {name_display:<30} {email_display:<35} {accepted_str:<10} {active_str:<10}")

# Get status breakdown
print(f"\n📈 Status Breakdown:")
cursor.execute("SELECT accepted, COUNT(*) FROM membership GROUP BY accepted")
status_breakdown = cursor.fetchall()
for status, count in status_breakdown:
    status_str = "None (Pending)" if status is None else ("Approved" if status == 1 else "Rejected")
    print(f"  {status_str}: {count}")

# Get active breakdown
print(f"\n📈 Active Status Breakdown:")
cursor.execute("SELECT active, COUNT(*) FROM membership GROUP BY active")
active_breakdown = cursor.fetchall()
for active, count in active_breakdown:
    active_str = "None" if active is None else ("Active" if active == 1 else "Inactive")
    print(f"  {active_str}: {count}")

conn.close()
print("\n✓ Database check complete!")



