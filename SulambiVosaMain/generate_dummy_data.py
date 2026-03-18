#!/usr/bin/env python3
"""
Script to generate 1000 dummy test data entries for Sulambi VMS
Generates realistic test data for membership, requirements, and events
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_PH')  # Using Philippines locale for realistic data

# Database path
DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

# Constants for realistic data
APPLYING_AS_OPTIONS = ["Regular Member", "Student Leader", "Community Member"]
WEEKDAYS_OPTIONS = ["1-2 hours", "2-4 hours", "4-6 hours", "6+ hours"]
WEEKENDS_OPTIONS = ["2-4 hours", "4-6 hours", "6-8 hours", "Full day"]
AREAS_OF_INTEREST = [
    "Community Service", "Education", "Healthcare", "Environmental",
    "Disaster Relief", "Youth Development", "Senior Care", "Animal Welfare"
]
CAMPUS_OPTIONS = ["Main Campus", "North Campus", "South Campus", "East Campus"]
COLLEGES = [
    "College of Engineering", "College of Arts and Sciences", "College of Business",
    "College of Education", "College of Medicine", "College of Nursing",
    "College of Law", "College of Architecture"
]
YEAR_LEVELS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate"]
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BLOOD_DONATION_OPTIONS = ["Yes", "No", "Willing to donate"]
PAYMENT_OPTIONS = ["Cash", "GCash", "PayMaya", "Bank Transfer"]
MEDICAL_CONDITIONS = ["None", "Hypertension", "Asthma", "Diabetes", "None", "None", "None"]

def generate_membership_data(count=1000):
    """Generate dummy membership data"""
    print(f"Generating {count} membership records...")
    
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
    
    inserted = 0
    for i in range(count):
        try:
            # Generate personal info
            fullname = fake.name()
            email = fake.unique.email()
            srcode = f"SR-{fake.random_int(min=1000, max=9999)}-{fake.random_int(min=1000, max=9999)}"
            age = fake.random_int(min=18, max=30)
            birthday = fake.date_of_birth(minimum_age=age, maximum_age=age).strftime("%Y-%m-%d")
            sex = random.choice(["Male", "Female"])
            
            # Generate address
            address = fake.address().replace('\n', ', ')
            
            # Generate contact
            contact_num = f"09{fake.random_int(min=100000000, max=999999999)}"
            fblink = f"https://facebook.com/{fake.user_name()}"
            
            # Generate membership-specific data
            applying_as = random.choice(APPLYING_AS_OPTIONS)
            volunterism_experience = random.choice([True, False])
            weekdays_time = random.choice(WEEKDAYS_OPTIONS)
            weekends_time = random.choice(WEEKENDS_OPTIONS)
            areas_of_interest = ", ".join(random.sample(AREAS_OF_INTEREST, random.randint(1, 3)))
            
            campus = random.choice(CAMPUS_OPTIONS)
            college_dept = random.choice(COLLEGES)
            yrlevel_program = random.choice(YEAR_LEVELS)
            
            blood_type = random.choice(BLOOD_TYPES)
            blood_donation = random.choice(BLOOD_DONATION_OPTIONS)
            medical_condition = random.choice(MEDICAL_CONDITIONS)
            payment_option = random.choice(PAYMENT_OPTIONS)
            
            # Generate credentials
            username = f"{fake.user_name()}{i}"
            password = fake.password(length=12)
            
            # Generate optional fields
            volunteer_exp_q1 = fake.text(max_nb_chars=200) if volunterism_experience else ""
            volunteer_exp_q2 = fake.text(max_nb_chars=200) if volunterism_experience else ""
            reason_q1 = fake.text(max_nb_chars=200)
            reason_q2 = fake.text(max_nb_chars=200)
            
            # Insert into database
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
                applying_as, volunterism_experience, weekdays_time, weekends_time,
                areas_of_interest, fullname, email, "N/A", srcode, age, birthday, sex,
                campus, college_dept, yrlevel_program, address, contact_num, fblink,
                blood_type, blood_donation, medical_condition, payment_option,
                username, password, True, None,
                volunteer_exp_q1, volunteer_exp_q2, "",
                reason_q1, reason_q2
            ))
            
            inserted += 1
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{count} records inserted...")
                conn.commit()
        
        except sqlite3.IntegrityError as e:
            # Skip duplicates
            continue
        except Exception as e:
            print(f"  Error inserting record {i + 1}: {e}")
            continue
    
    conn.commit()
    conn.close()
    print(f"✅ Successfully inserted {inserted} membership records!")

def generate_requirements_data(count=500):
    """Generate dummy requirements/volunteer participation data"""
    print(f"\nGenerating {count} requirements records...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if requirements table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='requirements'
    """)
    
    if not cursor.fetchone():
        print("❌ Requirements table does not exist!")
        conn.close()
        return
    
    # Get existing event IDs
    cursor.execute("SELECT id FROM externalEvents")
    external_event_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM internalEvents")
    internal_event_ids = [row[0] for row in cursor.fetchall()]
    
    if not external_event_ids and not internal_event_ids:
        print("⚠️  No events found. Please generate events first.")
        conn.close()
        return
    
    inserted = 0
    for i in range(count):
        try:
            # Choose event type and ID
            if external_event_ids and internal_event_ids:
                event_type = random.choice(["external", "internal"])
                event_id = random.choice(external_event_ids if event_type == "external" else internal_event_ids)
            elif external_event_ids:
                event_type = "external"
                event_id = random.choice(external_event_ids)
            else:
                event_type = "internal"
                event_id = random.choice(internal_event_ids)
            
            # Generate volunteer info
            fullname = fake.name()
            email = fake.unique.email()
            srcode = f"SR-{fake.random_int(min=1000, max=9999)}-{fake.random_int(min=1000, max=9999)}"
            age = fake.random_int(min=18, max=30)
            birthday = fake.date_of_birth(minimum_age=age, maximum_age=age).strftime("%Y-%m-%d")
            sex = random.choice(["Male", "Female"])
            campus = random.choice(CAMPUS_OPTIONS)
            college_dept = random.choice(COLLEGES)
            yrlevel_program = random.choice(YEAR_LEVELS)
            address = fake.address().replace('\n', ', ')
            contact_num = f"09{fake.random_int(min=100000000, max=999999999)}"
            fblink = f"https://facebook.com/{fake.user_name()}"
            
            # Generate requirement documents (file paths)
            req_id = f"REQ-{fake.random_int(min=10000, max=99999)}-{i}"
            med_cert = f"documents/med_cert_{req_id}.pdf"
            waiver = f"documents/waiver_{req_id}.pdf"
            
            # Random acceptance status
            accepted = random.choice([True, False, None])
            
            # Insert into database
            cursor.execute("""
                INSERT INTO requirements (
                    id, medCert, waiver, type, eventId, affiliation, fullname, email,
                    srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
                    address, contactNum, fblink, accepted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req_id, med_cert, waiver, event_type, event_id, "N/A",
                fullname, email, srcode, age, birthday, sex, campus, college_dept,
                yrlevel_program, address, contact_num, fblink, accepted
            ))
            
            inserted += 1
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{count} records inserted...")
                conn.commit()
        
        except sqlite3.IntegrityError:
            continue
        except Exception as e:
            print(f"  Error inserting record {i + 1}: {e}")
            continue
    
    conn.commit()
    conn.close()
    print(f"✅ Successfully inserted {inserted} requirements records!")

def generate_events_data(internal_count=50, external_count=50):
    """Generate dummy internal and external events"""
    print(f"\nGenerating {internal_count} internal and {external_count} external events...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Generate Internal Events
    if internal_count > 0:
        print(f"  Generating {internal_count} internal events...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='internalEvents'")
        
        if cursor.fetchone():
            inserted = 0
            for i in range(internal_count):
                try:
                    title = fake.catch_phrase() + " Event"
                    venue = fake.address().split('\n')[0]
                    
                    # Random dates in the future
                    start_date = fake.date_between(start_date='today', end_date='+365d')
                    duration_start = int(start_date.timestamp())
                    duration_end = duration_start + (random.randint(1, 7) * 24 * 3600)
                    
                    mode_of_delivery = random.choice(["Face-to-Face", "Online", "Hybrid"])
                    project_team = ", ".join([fake.name() for _ in range(random.randint(3, 5))])
                    partner = fake.company()
                    participant = f"{random.randint(20, 200)} participants"
                    male_total = str(random.randint(10, 100))
                    female_total = str(random.randint(10, 100))
                    
                    rationale = fake.text(max_nb_chars=500)
                    objectives = fake.text(max_nb_chars=500)
                    description = fake.text(max_nb_chars=800)
                    work_plan = "[]"
                    financial_requirement = "[]"
                    evaluation_mechanics_plan = "[]"
                    sustainability_plan = fake.text(max_nb_chars=300)
                    
                    status = random.choice(["editing", "submitted", "accepted", "rejected"])
                    to_public = random.choice([True, False])
                    
                    cursor.execute("""
                        INSERT INTO internalEvents (
                            title, durationStart, durationEnd, venue, modeOfDelivery,
                            projectTeam, partner, participant, maleTotal, femaleTotal,
                            rationale, objectives, description, workPlan, financialRequirement,
                            evaluationMechanicsPlan, sustainabilityPlan, createdBy, status,
                            toPublic, evaluationSendTime, signatoriesId, createdAt, feedback_id, eventProposalType
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        title, duration_start, duration_end, venue, mode_of_delivery,
                        project_team, partner, participant, male_total, female_total,
                        rationale, objectives, description, work_plan, financial_requirement,
                        evaluation_mechanics_plan, sustainability_plan, 1, status,
                        to_public, 0, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, "[]"
                    ))
                    
                    inserted += 1
                except Exception as e:
                    print(f"    Error inserting internal event {i + 1}: {e}")
                    continue
            
            conn.commit()
            print(f"  ✅ Inserted {inserted} internal events")
    
    # Generate External Events
    if external_count > 0:
        print(f"  Generating {external_count} external events...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='externalEvents'")
        
        if cursor.fetchone():
            inserted = 0
            for i in range(external_count):
                try:
                    extension_service_type = random.choice(["Training", "Consultation", "Community Service"])
                    title = fake.catch_phrase() + " Extension Service"
                    location = fake.address().split('\n')[0]
                    
                    start_date = fake.date_between(start_date='today', end_date='+365d')
                    duration_start = int(start_date.timestamp())
                    duration_end = duration_start + (random.randint(1, 14) * 24 * 3600)
                    
                    sdg = ", ".join([f"SDG {random.randint(1, 17)}" for _ in range(random.randint(1, 3))])
                    org_involved = fake.company()
                    program_involved = fake.bs()
                    project_leader = fake.name()
                    partners = ", ".join([fake.company() for _ in range(random.randint(1, 3))])
                    beneficiaries = f"{random.randint(50, 500)} beneficiaries"
                    total_cost = round(random.uniform(10000, 500000), 2)
                    source_of_fund = random.choice(["Internal Budget", "External Grant", "Donations", "Sponsors"])
                    
                    rationale = fake.text(max_nb_chars=500)
                    objectives = fake.text(max_nb_chars=500)
                    expected_output = fake.text(max_nb_chars=400)
                    description = fake.text(max_nb_chars=800)
                    financial_plan = "[]"
                    duties_of_partner = fake.text(max_nb_chars=300)
                    evaluation_mechanics_plan = "[]"
                    sustainability_plan = fake.text(max_nb_chars=300)
                    
                    status = random.choice(["editing", "submitted", "accepted", "rejected"])
                    to_public = random.choice([True, False])
                    
                    cursor.execute("""
                        INSERT INTO externalEvents (
                            extensionServiceType, title, location, durationStart, durationEnd,
                            sdg, orgInvolved, programInvolved, projectLeader, partners,
                            beneficiaries, totalCost, sourceOfFund, rationale, objectives,
                            expectedOutput, description, financialPlan, dutiesOfPartner,
                            evaluationMechanicsPlan, sustainabilityPlan, createdBy, status,
                            evaluationSendTime, toPublic, signatoriesId, createdAt, feedback_id, externalServiceType, eventProposalType
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        extension_service_type, title, location, duration_start, duration_end,
                        sdg, org_involved, program_involved, project_leader, partners,
                        beneficiaries, total_cost, source_of_fund, rationale, objectives,
                        expected_output, description, financial_plan, duties_of_partner,
                        evaluation_mechanics_plan, sustainability_plan, 1, status,
                        0, to_public, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, "[]", "[]"
                    ))
                    
                    inserted += 1
                except Exception as e:
                    print(f"    Error inserting external event {i + 1}: {e}")
                    continue
            
            conn.commit()
            print(f"  ✅ Inserted {inserted} external events")
    
    conn.close()

def main():
    """Main function to generate all dummy data"""
    print("=" * 60)
    print("SULAMBI VMS - DUMMY DATA GENERATOR")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Please make sure the database file exists.")
        return
    
    print(f"✓ Database found: {DB_PATH}\n")
    
    try:
        # Generate events first (needed for requirements)
        generate_events_data(internal_count=50, external_count=50)
        
        # Generate membership data
        generate_membership_data(count=1000)
        
        # Generate requirements data (depends on events)
        generate_requirements_data(count=500)
        
        print("\n" + "=" * 60)
        print("✅ DUMMY DATA GENERATION COMPLETE!")
        print("=" * 60)
        print("\nGenerated:")
        print("  - 50 Internal Events")
        print("  - 50 External Events")
        print("  - 1000 Membership Records")
        print("  - 500 Requirements/Volunteer Participation Records")
        
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 