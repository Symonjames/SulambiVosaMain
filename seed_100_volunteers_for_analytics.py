#!/usr/bin/env python3
"""
Seed 100 dummy volunteers with realistic event attendance history
for Dropout Risk Assessment and volunteer analytics widgets
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
    """Get existing events or create multiple events across different time periods"""
    cursor = conn.cursor()
    
    # Get existing events
    cursor.execute("SELECT id, durationStart FROM internalEvents WHERE status = 'accepted' LIMIT 10")
    internal_events = cursor.fetchall()
    
    cursor.execute("SELECT id, durationStart FROM externalEvents WHERE status = 'accepted' LIMIT 10")
    external_events = cursor.fetchall()
    
    # If we have less than 6 events, create more events spread across 2024-2025
    if len(internal_events) + len(external_events) < 6:
        print("Creating events across different semesters...")
        now = int(datetime.now().timestamp() * 1000)

        # Use realistic titles instead of "Community Service Event ..."
        # User-facing, realistic titles (match the naming used in the UI)
        themes = [
            "Beach Cleaning",
            "Coastal Cleanup",
            "Tree Planting",
            "Mangrove Restoration",
            "Community Feeding Program",
            "Food Distribution Drive",
            "School Supply Donation",
            "Clothing Donation Drive",
            "Blood Donation Activity",
            "Medical Mission",
            "Environmental Awareness Campaign",
            "Clean-Up Drive",
            "Recycling Program",
            "Community Outreach Program",
            "Disaster Relief Operation",
        ]
        def pick_theme(year: int, sem: int, month: int) -> str:
            # Deterministic mapping for stable names across runs
            return themes[(year * 100 + sem * 10 + month) % len(themes)]
        
        # Create events for different semesters
        semesters = [
            (2024, 1, 1, 3),    # Jan-Mar 2024 (semester 1)
            (2024, 2, 7, 9),    # Jul-Sep 2024 (semester 2)
            (2025, 1, 1, 3),    # Jan-Mar 2025 (semester 1)
            (2025, 2, 7, 9),    # Jul-Sep 2025 (semester 2)
        ]
        
        for year, semester, start_month, end_month in semesters:
            for month in range(start_month, end_month + 1):
                day = random.randint(1, 28)
                event_start = int(datetime(year, month, day, 9, 0).timestamp() * 1000)
                event_end = event_start + (8 * 60 * 60 * 1000)  # 8 hours

                title = f"{pick_theme(year, semester, month)} ({year} S{semester} M{month})"
                
                cursor.execute("""
                    INSERT INTO internalEvents (
                        title, durationStart, durationEnd, venue, modeOfDelivery,
                        projectTeam, partner, participant, maleTotal, femaleTotal,
                        rationale, objectives, description, workPlan, financialRequirement,
                        evaluationMechanicsPlan, sustainabilityPlan, createdBy, status,
                        toPublic, evaluationSendTime, createdAt, eventProposalType
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    title, event_start, event_end, "Main Campus", "Face-to-Face",
                    "Volunteer Team", "Community Partners", "Students", "50", "50",
                    "Community service", "Help community", "Service event", "[]", "[]",
                    "[]", "[]", 1, "accepted", 1, event_start, event_start, "[]"
                ))
        
        conn.commit()
        print(f"✓ Created events across semesters")
        
        # Get all events again
        cursor.execute("SELECT id, durationStart FROM internalEvents WHERE status = 'accepted' ORDER BY durationStart")
        internal_events = cursor.fetchall()
        cursor.execute("SELECT id, durationStart FROM externalEvents WHERE status = 'accepted' ORDER BY durationStart")
        external_events = cursor.fetchall()
    
    internal_event_ids = [row[0] for row in internal_events]
    external_event_ids = [row[0] for row in external_events]
    
    return internal_event_ids, external_event_ids, internal_events, external_events

def generate_satisfaction_criteria():
    """Generate realistic satisfaction criteria"""
    satisfaction_scores = [4, 4, 4, 5, 5, 3, 4, 5, 4, 4, 3, 5, 4, 4, 5, 3, 4, 4, 5, 4]
    overall_satisfaction = random.choice(satisfaction_scores)
    
    ratings = {
        'excellent': 0, 'very_satisfactory': 0, 'satisfactory': 0, 'fair': 0, 'poor': 0
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
    
    comments = ["", "", "", "Great event!", "Well organized", "Enjoyed participating", "Very helpful"]
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

def seed_100_volunteers():
    """Seed 100 volunteers with realistic participation history"""
    print("=" * 60)
    print("SEEDING 100 VOLUNTEERS FOR ANALYTICS")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get or create events
    internal_event_ids, external_event_ids, internal_events, external_events = get_or_create_events(conn)
    all_event_ids = internal_event_ids + external_event_ids
    all_events = internal_events + external_events
    
    if not all_event_ids:
        print("❌ No events available!")
        conn.close()
        return
    
    print(f"✓ Found {len(all_event_ids)} events\n")
    
    # Add 100 volunteers with varying participation patterns
    print("Adding 100 volunteers with event attendance history...\n")
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
            password = "Password123!"
            
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
                username, password, 1, 1,
                "Yes", "Community service", "None",
                "To help", "Community"
            ))
            
            inserted += 1
            
            # Create participation history: 1-5 events per volunteer, spread across time
            # Some volunteers are highly engaged (4-5 events), some are at risk (1-2 events)
            num_events = random.choices(
                [1, 2, 3, 4, 5],
                weights=[15, 20, 30, 25, 10]  # More volunteers with 2-3 events
            )[0]
            
            # Select events spread across different time periods
            selected_events = random.sample(all_events, min(num_events, len(all_events)))
            
            # Sort by event date to create a timeline
            selected_events.sort(key=lambda x: x[1])
            
            for event_id, event_start in selected_events:
                event_type = "internal" if event_id in internal_event_ids else "external"
                req_id = f"REQ-{random.randint(10000, 99999)}-{inserted}-{event_id}"
                
                # Note: requirements table doesn't have createdAt column
                # Participation timeline will be based on event dates
                
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
                
                # Create evaluation for most requirements (80% attendance rate)
                if random.random() < 0.8:  # 80% attendance
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
                    
                    # Note: evaluation table doesn't have createdAt column
                    cursor.execute("""
                        INSERT INTO evaluation (
                            requirementId, criteria, q13, q14, comment, recommendations, finalized
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        req_id, criteria_json, q13, q14, comment, recommendations, 1
                    ))
            
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i + 1}/100 volunteers added...")
                conn.commit()
        
        except sqlite3.IntegrityError:
            skipped += 1
            continue
        except Exception as e:
            print(f"  Error inserting volunteer {i + 1}: {e}")
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
    
    # Check participation distribution
    cursor.execute("""
        SELECT COUNT(DISTINCT m.id) as volunteer_count,
               COUNT(r.id) as total_registrations,
               COUNT(e.id) as total_attendances,
               AVG(reg_count.regs) as avg_events_per_volunteer
        FROM membership m
        INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
        LEFT JOIN evaluation e ON r.id = e.requirementId AND e.finalized = 1
        LEFT JOIN (
            SELECT email, COUNT(*) as regs
            FROM requirements
            WHERE accepted = 1
            GROUP BY email
        ) reg_count ON m.email = reg_count.email
        WHERE m.active = 1 AND m.accepted = 1
    """)
    stats = cursor.fetchone()
    
    # Check volunteers by participation count
    cursor.execute("""
        SELECT 
            CASE 
                WHEN reg_count.regs = 1 THEN '1 event'
                WHEN reg_count.regs = 2 THEN '2 events'
                WHEN reg_count.regs = 3 THEN '3 events'
                WHEN reg_count.regs >= 4 THEN '4+ events'
            END as participation_level,
            COUNT(*) as count
        FROM membership m
        INNER JOIN (
            SELECT email, COUNT(*) as regs
            FROM requirements
            WHERE accepted = 1
            GROUP BY email
        ) reg_count ON m.email = reg_count.email
        WHERE m.active = 1 AND m.accepted = 1
        GROUP BY participation_level
    """)
    participation_dist = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 100 VOLUNTEERS SEEDED!")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  - Added {inserted} new volunteers")
    if skipped > 0:
        print(f"  - Skipped {skipped} (duplicates)")
    print(f"  - Total active & accepted members: {total_members}")
    print(f"  - Total accepted requirements: {total_reqs}")
    print(f"  - Total finalized evaluations: {total_evals}")
    print(f"  - Average events per volunteer: {stats[3]:.1f}" if stats[3] else "  - Average events per volunteer: N/A")
    
    if participation_dist:
        print(f"\nParticipation distribution:")
        for level, count in participation_dist:
            print(f"  - {level}: {count} volunteers")
    
    print("\nThese volunteers will now appear in:")
    print("  ✓ Dropout Risk Assessment (with varying participation levels)")
    print("  ✓ Volunteer Analytics (age and sex breakdown)")
    print("  ✓ Satisfaction Analytics")
    print("  ✓ Dashboard charts with real numbers")

if __name__ == "__main__":
    seed_100_volunteers()

