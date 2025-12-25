#!/usr/bin/env python3
"""
Add 100 makeup/dummy members to the database for analytics
These are for design/demo purposes only
"""

import sqlite3
import os
import random
import json
from faker import Faker
from datetime import datetime, timedelta

# Get database path (same as backend)
from dotenv import load_dotenv
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(backend_dir, DB_PATH)

fake = Faker('en_US')

def generate_philippine_address():
    """Generate a realistic Philippine address"""
    cities = ["Batangas City", "Lipa City", "Tanauan City", "Calamba", "Los Baños", "San Pablo", "Alaminos", "Balayan", "Lemery", "Taal"]
    barangays = ["Poblacion", "San Isidro", "San Jose", "San Antonio", "San Miguel", "Sta. Cruz", "Sta. Maria", "Sta. Ana", "San Juan", "San Pedro"]
    
    street_num = random.randint(1, 999)
    street = random.choice(["Rizal Street", "Mabini Street", "Bonifacio Street", "Aguinaldo Street", "Quezon Avenue", "Luna Street", "Del Pilar Street"])
    barangay = random.choice(barangays)
    city = random.choice(cities)
    
    return f"{street_num} {street}, {barangay}, {city}, Batangas"

def get_or_create_events(conn):
    """Get existing events or create some if none exist"""
    cursor = conn.cursor()
    
    # Get existing accepted events
    cursor.execute("SELECT id FROM internalEvents WHERE status = 'accepted' LIMIT 5")
    internal_event_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM externalEvents WHERE status = 'accepted' LIMIT 5")
    external_event_ids = [row[0] for row in cursor.fetchall()]
    
    all_event_ids = internal_event_ids + external_event_ids
    
    # If no events exist, create a sample event
    if not all_event_ids:
        print("⚠️  No events found! Creating sample event...")
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
            "Community Service Event", now, now + 86400000, "Main Campus", "Face-to-Face",
            "Volunteer Team", "Community Partners", "Students", "50", "50",
            "Community service", "Help community", "Service event", "[]", "[]",
            "[]", "[]", 1, "accepted", 1, now, now, "[]"
        ))
        conn.commit()
        cursor.execute("SELECT id FROM internalEvents WHERE status = 'accepted' LIMIT 5")
        internal_event_ids = [row[0] for row in cursor.fetchall()]
        all_event_ids = internal_event_ids
    
    return internal_event_ids, external_event_ids

def generate_satisfaction_criteria():
    """Generate realistic satisfaction criteria data"""
    satisfaction_scores = [4, 4, 4, 5, 5, 3, 4, 5, 4, 4, 3, 5, 4, 4, 5, 3, 4, 4, 5, 4]
    overall_satisfaction = random.choice(satisfaction_scores)
    
    ratings = {
        'excellent': 0,
        'very_satisfactory': 0,
        'satisfactory': 0,
        'fair': 0,
        'poor': 0
    }
    
    if overall_satisfaction == 5:
        ratings['excellent'] = 1
    elif overall_satisfaction == 4:
        ratings['very_satisfactory'] = 1
    elif overall_satisfaction == 3:
        ratings['satisfactory'] = 1
    elif overall_satisfaction == 2:
        ratings['fair'] = 1
    else:
        ratings['poor'] = 1
    
    comments = [
        "", "", "",
        "Great event, well organized",
        "Enjoyed participating",
        "Very informative and helpful",
        "Good communication throughout",
        "Would participate again",
        "Excellent coordination",
        "Helpful for community"
    ]
    
    comment = random.choice(comments)
    
    criteria = {
        'overall': overall_satisfaction,
        'satisfaction': overall_satisfaction,
        'rating': overall_satisfaction,
        **ratings
    }
    
    if comment:
        criteria['comment'] = comment
        criteria['comments'] = comment
    
    return json.dumps(criteria), overall_satisfaction

def add_100_makeup_members():
    """Add 100 makeup members with requirements and evaluations"""
    print("=" * 60)
    print("ADDING 100 MAKEUP MEMBERS FOR ANALYTICS")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get or create events
    internal_event_ids, external_event_ids = get_or_create_events(conn)
    all_event_ids = internal_event_ids + external_event_ids
    
    if not all_event_ids:
        print("❌ No events available! Cannot create requirements.")
        conn.close()
        return
    
    print(f"✓ Found {len(all_event_ids)} events\n")
    
    # Add 100 members
    print("Adding 100 makeup members...\n")
    inserted = 0
    skipped = 0
    
    for i in range(100):
        try:
            # Generate member data
            fullname = fake.name()
            srcode = f"{random.randint(20, 24)}-{random.randint(10000, 99999)}"
            email = f"{srcode.replace('-', '')}@g.batstate-u.edu.ph"
            age = random.randint(18, 25)
            birthday = fake.date_of_birth(minimum_age=age, maximum_age=age).strftime("%B, %d %Y")
            sex = random.choice(["Male", "Female"])
            campus = random.choice(["Main", "Alangilan", "Lipa", "Lobo", "Rosario"])
            college_dept = random.choice(["Engineering", "Arts and Sciences", "Education", "Business", "Nursing"])
            yrlevel_program = f"{random.randint(1, 4)} - {random.choice(['BSIT', 'BSCS', 'BSBA', 'BSEd', 'BSN'])}"
            address = generate_philippine_address()
            contact_num = f"09{random.randint(100000000, 999999999)}"
            fblink = f"https://facebook.com/{fake.user_name()}"
            blood_type = random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            blood_donation = random.choice([0, 1])
            medical_condition = random.choice(["None", "Asthma", "Hypertension", ""])
            payment_option = random.choice(["GCash", "PayMaya", "Bank Transfer"])
            username = email.split('@')[0]
            password = "Password123!"  # Demo password for makeup members
            
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
            
            # Create 1-3 requirements for this member
            num_events = random.randint(1, 3)
            selected_events = random.sample(all_event_ids, min(num_events, len(all_event_ids)))
            
            for event_id in selected_events:
                event_type = "internal" if event_id in internal_event_ids else "external"
                req_id = f"REQ-{random.randint(10000, 99999)}-{inserted}-{event_id}"
                
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
                
                # Create evaluation for this requirement
                criteria_json, satisfaction_score = generate_satisfaction_criteria()
                q13 = str(satisfaction_score)
                q14 = str(satisfaction_score)
                comment = random.choice([
                    "Great event!", "Well organized", "Enjoyed participating",
                    "Very helpful", "Good coordination", "Would participate again"
                ])
                recommendations = random.choice([
                    "Keep up the good work", "Continue organizing similar events",
                    "More events like this would be great", "Well done!"
                ])
                
                cursor.execute("""
                    INSERT INTO evaluation (
                        requirementId, criteria, q13, q14, comment, recommendations, finalized
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    req_id, criteria_json, q13, q14, comment, recommendations, 1
                ))
            
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i + 1}/100 members added...")
                conn.commit()
        
        except sqlite3.IntegrityError:
            skipped += 1
            continue
        except Exception as e:
            print(f"  Error inserting member {i + 1}: {e}")
            skipped += 1
            continue
    
    conn.commit()
    
    # Verify results
    cursor.execute("SELECT COUNT(*) FROM membership WHERE active = 1 AND accepted = 1")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
    total_reqs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
    total_evals = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT m.id)
        FROM membership m
        INNER JOIN requirements r ON m.email = r.email
        WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
    """)
    analytics_ready = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 100 MAKEUP MEMBERS ADDED!")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  - Added {inserted} new members")
    if skipped > 0:
        print(f"  - Skipped {skipped} (duplicates)")
    print(f"  - Total active & accepted members: {total_members}")
    print(f"  - Total accepted requirements: {total_reqs}")
    print(f"  - Total finalized evaluations: {total_evals}")
    print(f"  - Members ready for analytics: {analytics_ready}")
    
    print("\nThese members will now appear in:")
    print("  ✓ Age Analytics (8 age groups: 18-25)")
    print("  ✓ Sex Analytics (Male/Female breakdown)")
    print("  ✓ Satisfaction Analytics")
    print("  ✓ Dashboard charts")

if __name__ == "__main__":
    add_100_makeup_members()

















