#!/usr/bin/env python3
"""
Script to add requirements (volunteer registrations) to existing members
so they appear in analytics
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

# Database path
# Try to get DB_PATH from environment (backend's .env), otherwise use default
from dotenv import load_dotenv
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    # If relative path, make it relative to backend directory
    DB_PATH = os.path.join(backend_dir, DB_PATH)

def get_or_create_events(conn):
    """Get existing events or create some if none exist"""
    cursor = conn.cursor()
    
    # Get existing accepted events
    cursor.execute("SELECT id FROM internalEvents WHERE status = 'accepted' LIMIT 5")
    internal_event_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM externalEvents WHERE status = 'accepted' LIMIT 5")
    external_event_ids = [row[0] for row in cursor.fetchall()]
    
    # If no events exist, create a few
    if not internal_event_ids and not external_event_ids:
        print("  No events found. Creating sample events...")
        
        # Create 3 internal events
        for i in range(3):
            start_date = datetime.now() + timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(1, 3))
            
            cursor.execute("""
                INSERT INTO internalEvents (
                    title, durationStart, durationEnd, venue, modeOfDelivery,
                    projectTeam, partner, participant, maleTotal, femaleTotal,
                    rationale, objectives, description, workPlan, financialRequirement,
                    evaluationMechanicsPlan, sustainabilityPlan, createdBy, status,
                    toPublic, evaluationSendTime, signatoriesId, createdAt, feedback_id, eventProposalType
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"Community Outreach Event {i+1}",
                int(start_date.timestamp() * 1000),
                int(end_date.timestamp() * 1000),
                "Main Campus",
                "Face-to-Face",
                "Team A, Team B",
                "Community Partner",
                "Students and Community",
                "50",
                "50",
                "Community service and outreach",
                "Serve the community",
                "Various community service activities",
                "[]",
                "[]",
                "[]",
                "Ongoing community engagement",
                1,
                "accepted",
                1,
                0,
                None,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                None,
                "[]"
            ))
            internal_event_ids.append(cursor.lastrowid)
        
        conn.commit()
        print(f"  ✓ Created {len(internal_event_ids)} internal events")
    
    return internal_event_ids, external_event_ids

def add_requirements_to_members():
    """Add requirements to existing members so they appear in analytics"""
    print("=" * 60)
    print("ADDING REQUIREMENTS TO EXISTING MEMBERS")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get or create events
    print("Checking for events...")
    internal_event_ids, external_event_ids = get_or_create_events(conn)
    all_event_ids = internal_event_ids + external_event_ids
    
    if not all_event_ids:
        print("❌ No events available. Cannot create requirements.")
        conn.close()
        return
    
    print(f"✓ Found {len(all_event_ids)} events\n")
    
    # Get all accepted and active members without requirements
    print("Finding members without requirements...")
    cursor.execute("""
        SELECT m.id, m.email, m.fullname, m.age, m.birthday, m.sex, 
               m.campus, m.collegeDept, m.yrlevelprogram, m.address, 
               m.contactNum, m.fblink, m.srcode
        FROM membership m
        WHERE m.accepted = 1 AND m.active = 1
        AND NOT EXISTS (
            SELECT 1 FROM requirements r 
            WHERE r.email = m.email AND r.accepted = 1
        )
    """)
    
    members = cursor.fetchall()
    
    if not members:
        print("✓ All members already have requirements!")
        conn.close()
        return
    
    print(f"Found {len(members)} members without requirements\n")
    print("Adding requirements...\n")
    
    added = 0
    errors = 0
    
    for member in members:
        member_id, email, fullname, age, birthday, sex, campus, college_dept, yrlevel_program, address, contact_num, fblink, srcode = member
        
        try:
            # Randomly assign member to 1-3 events
            num_events = random.randint(1, 3)
            selected_events = random.sample(all_event_ids, min(num_events, len(all_event_ids)))
            
            for event_id in selected_events:
                # Determine if it's internal or external
                event_type = "internal" if event_id in internal_event_ids else "external"
                
                # Generate unique requirement ID
                req_id = f"REQ-{random.randint(10000, 99999)}-{member_id}-{event_id}-{random.randint(100, 999)}"
                
                # Check if this requirement ID already exists
                cursor.execute("SELECT id FROM requirements WHERE id = ?", (req_id,))
                if cursor.fetchone():
                    req_id = f"REQ-{random.randint(100000, 999999)}-{member_id}-{event_id}"
                
                # Create requirement record (volunteer registration)
                cursor.execute("""
                    INSERT INTO requirements (
                        id, medCert, waiver, type, eventId, affiliation, fullname, email,
                        srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
                        address, contactNum, fblink, accepted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    req_id,
                    f"documents/med_cert_{req_id}.pdf",
                    f"documents/waiver_{req_id}.pdf",
                    event_type,
                    event_id,
                    "N/A",
                    fullname,
                    email,
                    srcode,
                    age,
                    birthday,
                    sex,
                    campus,
                    college_dept,
                    yrlevel_program,
                    address,
                    contact_num,
                    fblink,
                    1  # accepted = 1 (approved requirement)
                ))
            
            added += 1
            if added % 10 == 0:
                print(f"  Progress: {added}/{len(members)} members processed...")
                conn.commit()
        
        except sqlite3.IntegrityError as e:
            # Skip duplicates
            errors += 1
            continue
        except Exception as e:
            print(f"  Error adding requirements for {fullname}: {e}")
            errors += 1
            continue
    
    conn.commit()
    
    # Verify the results
    cursor.execute("""
        SELECT COUNT(DISTINCT m.email)
        FROM membership m
        INNER JOIN requirements r ON m.email = r.email
        WHERE m.accepted = 1 AND m.active = 1 AND r.accepted = 1
    """)
    members_in_analytics = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
    total_reqs = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ REQUIREMENTS ADDED!")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  - Added requirements to {added} members")
    if errors > 0:
        print(f"  - Errors: {errors}")
    print(f"  - Total accepted requirements: {total_reqs}")
    print(f"  - Members now in analytics: {members_in_analytics}")
    print("\nThese members will now appear in:")
    print("  ✓ Predictive Analytics (Sex and Age breakdown)")
    print("  ✓ Dashboard charts")

if __name__ == "__main__":
    add_requirements_to_members()

