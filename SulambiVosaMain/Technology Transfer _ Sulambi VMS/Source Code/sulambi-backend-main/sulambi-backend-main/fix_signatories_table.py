"""
Fix the signatories table and restore default values
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
print("FIXING SIGNATORIES TABLE")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check if table exists
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='eventSignatories'
""")
table_exists = cursor.fetchone()

if not table_exists:
    print("[INFO] Creating eventSignatories table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventSignatories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preparedBy STRING DEFAULT "NAME",
            reviewedBy STRING DEFAULT "NAME",
            recommendingApproval1 STRING DEFAULT "NAME",
            recommendingApproval2 STRING DEFAULT "NAME",
            approvedBy STRING DEFAULT "NAME",
            preparedTitle STRING DEFAULT "Asst. Director, GAD Advocacies/GAD Head Secretariat/Coordinator",
            reviewedTitle STRING DEFAULT "Director, Extension Services/Head, Extension Services",
            approvedTitle STRING DEFAULT "University President/Chancellor",
            recommendingSignatory1 STRING DEFAULT "Vice President/Vice Chancellor for Research, Development and Extension Services",
            recommendingSignatory2 STRING DEFAULT "Vice President/Vice Chancellor for Administration and Finance"
        )
    """)
    conn.commit()
    print("[OK] Table created")
else:
    print("[OK] Table exists")
    
    # Check if approvedTitle column has the typo issue
    cursor.execute("PRAGMA table_info(eventSignatories)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if "approvedTitle" not in column_names:
        print("[INFO] approvedTitle column missing, adding it...")
        try:
            cursor.execute("""
                ALTER TABLE eventSignatories 
                ADD COLUMN approvedTitle STRING DEFAULT "University President/Chancellor"
            """)
            conn.commit()
            print("[OK] Column added")
        except Exception as e:
            print(f"[WARNING] Could not add column: {e}")

# Check current signatories count
cursor.execute("SELECT COUNT(*) FROM eventSignatories")
count = cursor.fetchone()[0]
print(f"\n[INFO] Current signatories in database: {count}")

# Get all signatories to check if they have proper values
cursor.execute("SELECT * FROM eventSignatories LIMIT 5")
signatories = cursor.fetchall()

if signatories:
    print(f"\n[INFO] Sample signatories:")
    for sig in signatories:
        print(f"  ID {sig[0]}: preparedBy={sig[1]}, reviewedBy={sig[2]}, approvedBy={sig[5]}")
else:
    print("\n[INFO] No signatories found in database")
    print("[INFO] This is normal - signatories are created when events are created")

# Check for events that have signatoriesId but signatories are missing/null
cursor.execute("""
    SELECT COUNT(*) FROM internalEvents 
    WHERE signatoriesId IS NOT NULL
""")
internal_with_sig = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM externalEvents 
    WHERE signatoriesId IS NOT NULL
""")
external_with_sig = cursor.fetchone()[0]

print(f"\n[INFO] Events with signatories:")
print(f"  - Internal events: {internal_with_sig}")
print(f"  - External events: {external_with_sig}")

# Check for events with signatoriesId that don't exist
cursor.execute("""
    SELECT ie.id, ie.title, ie.signatoriesId 
    FROM internalEvents ie
    WHERE ie.signatoriesId IS NOT NULL 
    AND NOT EXISTS (SELECT 1 FROM eventSignatories WHERE id = ie.signatoriesId)
    LIMIT 5
""")
orphaned_internal = cursor.fetchall()

cursor.execute("""
    SELECT ee.id, ee.title, ee.signatoriesId 
    FROM externalEvents ee
    WHERE ee.signatoriesId IS NOT NULL 
    AND NOT EXISTS (SELECT 1 FROM eventSignatories WHERE id = ee.signatoriesId)
    LIMIT 5
""")
orphaned_external = cursor.fetchall()

if orphaned_internal or orphaned_external:
    print(f"\n[WARNING] Found events with missing signatories:")
    if orphaned_internal:
        print(f"  Internal events with missing signatories: {len(orphaned_internal)}")
        for event in orphaned_internal:
            print(f"    - Event ID {event[0]}: {event[1]} (signatoriesId: {event[2]})")
    if orphaned_external:
        print(f"  External events with missing signatories: {len(orphaned_external)}")
        for event in orphaned_external:
            print(f"    - Event ID {event[0]}: {event[1]} (signatoriesId: {event[2]})")
    
    print(f"\n[ACTION] Creating missing signatories...")
    created = 0
    
    # Create signatories for orphaned internal events
    for event in orphaned_internal:
        event_id, title, sig_id = event
        try:
            cursor.execute("""
                INSERT INTO eventSignatories (
                    preparedBy, reviewedBy, recommendingApproval1, recommendingApproval2, approvedBy,
                    preparedTitle, reviewedTitle, approvedTitle, recommendingSignatory1, recommendingSignatory2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "NAME", "NAME", "NAME", "NAME", "NAME",
                "Asst. Director, GAD Advocacies/GAD Head Secretariat/Coordinator",
                "Director, Extension Services/Head, Extension Services",
                "University President/Chancellor",
                "Vice President/Vice Chancellor for Research, Development and Extension Services",
                "Vice President/Vice Chancellor for Administration and Finance"
            ))
            new_sig_id = cursor.lastrowid
            # Update the event to use the new signatory ID
            cursor.execute("UPDATE internalEvents SET signatoriesId = ? WHERE id = ?", (new_sig_id, event_id))
            created += 1
        except Exception as e:
            print(f"  [ERROR] Failed to create signatory for event {event_id}: {e}")
    
    # Create signatories for orphaned external events
    for event in orphaned_external:
        event_id, title, sig_id = event
        try:
            cursor.execute("""
                INSERT INTO eventSignatories (
                    preparedBy, reviewedBy, recommendingApproval1, recommendingApproval2, approvedBy,
                    preparedTitle, reviewedTitle, approvedTitle, recommendingSignatory1, recommendingSignatory2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "NAME", "NAME", "NAME", "NAME", "NAME",
                "Asst. Director, GAD Advocacies/GAD Head Secretariat/Coordinator",
                "Director, Extension Services/Head, Extension Services",
                "University President/Chancellor",
                "Vice President/Vice Chancellor for Research, Development and Extension Services",
                "Vice President/Vice Chancellor for Administration and Finance"
            ))
            new_sig_id = cursor.lastrowid
            # Update the event to use the new signatory ID
            cursor.execute("UPDATE externalEvents SET signatoriesId = ? WHERE id = ?", (new_sig_id, event_id))
            created += 1
        except Exception as e:
            print(f"  [ERROR] Failed to create signatory for event {event_id}: {e}")
    
    if created > 0:
        conn.commit()
        print(f"[OK] Created {created} missing signatories")
else:
    print(f"\n[OK] No orphaned signatories found")

conn.close()

print("\n" + "=" * 70)
print("FIX COMPLETE")
print("=" * 70)























