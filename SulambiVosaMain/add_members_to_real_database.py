#!/usr/bin/env python3
"""
Script to add members to the REAL database that the backend uses
This uses the same DB_PATH from .env that the backend uses
"""

import sqlite3
import os
import sys
from dotenv import load_dotenv

# Load environment variables (same as backend)
load_dotenv(dotenv_path=os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", ".env"))

# Get DB_PATH from environment (same way backend does)
DB_PATH = os.getenv("DB_PATH")

# If not set, use default relative to backend directory
if not DB_PATH:
    backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
else:
    # If DB_PATH is relative, make it relative to backend directory
    if not os.path.isabs(DB_PATH):
        backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
        DB_PATH = os.path.join(backend_dir, DB_PATH)

print("=" * 60)
print("ADDING MEMBERS TO REAL DATABASE")
print("=" * 60)
print(f"Database path: {DB_PATH}")
print(f"Database exists: {os.path.exists(DB_PATH)}")

if not os.path.exists(DB_PATH):
    print(f"\n❌ Database not found at: {DB_PATH}")
    print("Please make sure:")
    print("  1. The backend has been initialized (python server.py --init)")
    print("  2. The .env file has the correct DB_PATH")
    sys.exit(1)

# Import the add_100_people function from the existing script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import faker and other dependencies
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('en_US')

# Override the DB_PATH in the add_100_people script
import add_requirements_to_members
import add_satisfaction_evaluations

# First, add members using the existing script but with the correct DB path
print("\n" + "=" * 60)
print("STEP 1: Adding members to database")
print("=" * 60)

# Check current member count
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM membership")
current_count = cursor.fetchone()[0]
print(f"Current members in database: {current_count}")
conn.close()

# If we need to add members, we'll use a modified version
if current_count < 50:
    print("\nAdding 50 members to the database...")
    
    # Use the same logic from add_100_people.py but with correct DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if events exist
    cursor.execute("SELECT COUNT(*) FROM internalEvents")
    internal_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM externalEvents")
    external_count = cursor.fetchone()[0]
    
    if internal_count == 0 and external_count == 0:
        print("⚠️  No events found! Creating sample events...")
        # Create a sample internal event
        from datetime import datetime
        now = int(datetime.now().timestamp() * 1000)
        cursor.execute("""
            INSERT INTO internalEvents (
                title, durationStart, durationEnd, venue, modeOfDelivery,
                projectTeam, partner, participant, maleTotal, femaleTotal,
                rationale, objectives, description, workPlan, financialRequirement,
                evaluationMechanicsPlan, sustainabilityPlan, createdBy, status,
                toPublic, evaluationSendTime, createdAt, eventProposalType
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Sample Community Service Event", now, now + 86400000, "Main Campus", "Face-to-Face",
            "Volunteer Team", "Community Partners", "Students", "50", "50",
            "Community service", "Help community", "Service event", "[]", "[]",
            "[]", "[]", 1, "accepted", 1, now, now, "[]"
        ))
        conn.commit()
        print("✓ Created sample internal event")
    
    # Get event IDs
    cursor.execute("SELECT id FROM internalEvents LIMIT 3")
    internal_event_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM externalEvents LIMIT 3")
    external_event_ids = [row[0] for row in cursor.fetchall()]
    all_event_ids = internal_event_ids + external_event_ids
    
    if not all_event_ids:
        print("❌ No events available! Cannot create requirements.")
        conn.close()
        sys.exit(1)
    
    # Add 50 members
    count = 50
    inserted = 0
    
    for i in range(count):
        try:
            # Generate member data
            fullname = fake.name()
            srcode = f"{random.randint(20, 24)}-{random.randint(10000, 99999)}"
            email = f"{srcode.replace('-', '')}@g.batstate-u.edu.ph"
            age = random.randint(18, 25)
            birthday = fake.date_of_birth(minimum_age=age, maximum_age=age).strftime("%B, %d %Y")
            sex = random.choice(["Male", "Female"])
            campus = random.choice(["Main", "Alangilan", "Lipa", "Lobo", "Rosario"])
            college_dept = random.choice(["Engineering", "Arts and Sciences", "Education", "Business"])
            yrlevel_program = f"{random.randint(1, 4)} - {random.choice(['BSIT', 'BSCS', 'BSBA', 'BSEd'])}"
            address = f"{random.randint(1, 999)} {fake.street_name()}, {fake.city()}, Batangas"
            contact_num = f"09{random.randint(100000000, 999999999)}"
            fblink = f"https://facebook.com/{fake.user_name()}"
            blood_type = random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            blood_donation = random.choice([0, 1])
            medical_condition = random.choice(["None", "Asthma", "Hypertension", ""])
            payment_option = random.choice(["GCash", "PayMaya", "Bank Transfer"])
            username = email.split('@')[0]
            password = "Password123!"  # Demo password
            
            # Insert into membership
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
                "Student", "Yes", "Morning", "Afternoon",
                "Community Service", fullname, email, "N/A", srcode, age, birthday, sex,
                campus, college_dept, yrlevel_program, address, contact_num, fblink,
                blood_type, blood_donation, medical_condition, payment_option,
                username, password, 1, 1,  # active=1, accepted=1
                "Yes", "Community service", "None",
                "To help", "Community"
            ))
            
            inserted += 1
            
            # Create requirement for this member
            if all_event_ids:
                num_events = random.randint(1, 3)
                selected_events = random.sample(all_event_ids, min(num_events, len(all_event_ids)))
                
                for event_id in selected_events:
                    event_type = "internal" if event_id in internal_event_ids else "external"
                    req_id = f"REQ-{random.randint(10000, 99999)}-{i}-{event_id}"
                    
                    cursor.execute("""
                        INSERT INTO requirements (
                            id, medCert, waiver, type, eventId, affiliation, fullname, email,
                            srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
                            address, contactNum, fblink, accepted
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        req_id, f"documents/med_cert_{req_id}.pdf", f"documents/waiver_{req_id}.pdf",
                        event_type, event_id, "N/A", fullname, email, srcode, age, birthday, sex,
                        campus, college_dept, yrlevel_program, address, contact_num, fblink,
                        1  # accepted = 1
                    ))
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{count} members inserted...")
                conn.commit()
        
        except sqlite3.IntegrityError:
            continue
        except Exception as e:
            print(f"  Error inserting member {i + 1}: {e}")
            continue
    
    conn.commit()
    print(f"\n✓ Added {inserted} members to database")
    conn.close()
else:
    print(f"✓ Database already has {current_count} members")

# Step 2: Add requirements
print("\n" + "=" * 60)
print("STEP 2: Adding requirements")
print("=" * 60)

# Temporarily modify the DB_PATH in the add_requirements script
original_db_path = getattr(add_requirements_to_members, 'DB_PATH', None)
add_requirements_to_members.DB_PATH = DB_PATH

# Run the add_requirements script
try:
    exec(open('add_requirements_to_members.py').read().replace(
        'DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")',
        f'DB_PATH = r"{DB_PATH}"'
    ))
except:
    # If exec fails, just run the script directly with modified path
    import subprocess
    import shutil
    # Create a temporary script with correct path
    with open('add_requirements_to_members.py', 'r') as f:
        content = f.read()
    content = content.replace(
        'DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")',
        f'DB_PATH = r"{DB_PATH}"'
    )
    with open('add_requirements_temp.py', 'w') as f:
        f.write(content)
    subprocess.run([sys.executable, 'add_requirements_temp.py'])
    os.remove('add_requirements_temp.py')

# Step 3: Add evaluations
print("\n" + "=" * 60)
print("STEP 3: Adding satisfaction evaluations")
print("=" * 60)

# Modify the add_satisfaction_evaluations script path
with open('add_satisfaction_evaluations.py', 'r') as f:
    content = f.read()
content = content.replace(
    'DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")',
    f'DB_PATH = r"{DB_PATH}"'
)
with open('add_satisfaction_evaluations_temp.py', 'w') as f:
    f.write(content)
subprocess.run([sys.executable, 'add_satisfaction_evaluations_temp.py'])
os.remove('add_satisfaction_evaluations_temp.py')

# Final verification
print("\n" + "=" * 60)
print("FINAL VERIFICATION")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM membership WHERE active = 1 AND accepted = 1")
members = cursor.fetchone()[0]
print(f"Active & accepted members: {members}")

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
reqs = cursor.fetchone()[0]
print(f"Accepted requirements: {reqs}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
evals = cursor.fetchone()[0]
print(f"Finalized evaluations: {evals}")

cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
""")
analytics_ready = cursor.fetchone()[0]
print(f"Members ready for analytics: {analytics_ready}")

conn.close()

print("\n" + "=" * 60)
if analytics_ready > 0:
    print("✅ DATA SUCCESSFULLY ADDED TO REAL DATABASE!")
    print(f"   - {members} members")
    print(f"   - {reqs} requirements")
    print(f"   - {evals} evaluations")
    print(f"   - {analytics_ready} members ready for analytics")
else:
    print("❌ DATA NOT READY FOR ANALYTICS")
print("=" * 60)

















