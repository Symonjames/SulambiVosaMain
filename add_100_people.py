#!/usr/bin/env python3
"""
Script to add exactly 100 realistic people to the Sulambi VMS database
These will look like manually added members with realistic Filipino names and data
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_PH')  # Using Philippines locale for realistic data

# Database path
DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

# Realistic Filipino first and last names
FILIPINO_FIRST_NAMES = [
    "Maria", "Jose", "Juan", "Ana", "Carlos", "Rosa", "Antonio", "Carmen",
    "Francisco", "Josefa", "Manuel", "Patricia", "Ricardo", "Lourdes",
    "Fernando", "Teresa", "Roberto", "Cristina", "Miguel", "Angelica",
    "Ramon", "Grace", "Eduardo", "Maricel", "Alberto", "Jennifer",
    "Rodrigo", "Michelle", "Enrique", "Karen", "Alfredo", "Diana",
    "Rafael", "Sharon", "Vicente", "Melissa", "Jorge", "Catherine",
    "Armando", "Stephanie", "Felipe", "Nicole", "Arturo", "Rachel",
    "Sergio", "Angela", "Hector", "Monica", "Raul", "Vanessa"
]

FILIPINO_LAST_NAMES = [
    "Santos", "Reyes", "Cruz", "Bautista", "Ocampo", "Garcia", "Mendoza",
    "Torres", "Fernandez", "Villanueva", "Ramos", "Gonzales", "Delos Santos",
    "Lopez", "Martinez", "Aquino", "Castillo", "Rivera", "Dela Cruz",
    "Morales", "Perez", "Sanchez", "Gutierrez", "Dela Rosa", "Vargas",
    "Romero", "Salazar", "Mercado", "Navarro", "Valdez", "Castro",
    "Ortega", "Jimenez", "Pascual", "Marquez", "Medina", "Herrera",
    "Santiago", "Alvarez", "Moreno", "Vega", "Silva", "Flores", "Ramos",
    "Diaz", "Espinoza", "Chavez", "Mendoza", "Guerrero", "Rojas"
]

# Constants for realistic data
APPLYING_AS_OPTIONS = ["New membership", "Renewal of Membership", "Alumni Membership"]
WEEKDAYS_OPTIONS = ["1-4 hours", "5-8 hours", "8 hours or more", "other"]
WEEKENDS_OPTIONS = ["1-4 hours", "5-8 hours", "8 hours or more", "other"]
AREAS_OF_INTEREST = [
    "Education and Literacy (Peace education, Human rights, Legal counseling/advice, IT literacy, Labor and Employment / Workers' education, Socio-cultural, history and heritage - related activities, Arts, IEC Materials Development, Urban Planning, Rural Development)",
    "Health and Wellness (Food and nutrition, Health and sanitation, Maternal and child-care, Guidance counseling)",
    "Environment and Disaster Mitigation (Cleanup drives, Tree-planting, Clean and green activities, Solid Waste Management)",
    "Livelihood (Agriculture, Technical-vocational / skills training, Nursery and vegetable garden establishment, Business / Financial Planning, Small construction works, Engineering design consultancy)",
    "Outreach (Medical mission, Dental mission, Optical mission, Blood donation, Visit to orphanages, Visit to prison camps, Visit to rehabilitation center, Relief operation, Gift-giving activity, Sports and Recreation)",
    "Gender and Development (GAD)"
]
CAMPUS_OPTIONS = ["Main Campus", "Alangilan Campus", "Pablo Borbon Campus", "Lipa Campus", "Rosario Campus", "Lobo Campus", "Balayan Campus", "Lemery Campus"]
COLLEGES = [
    "College of Engineering", "College of Arts and Sciences", "College of Business Administration",
    "College of Education", "College of Medicine", "College of Nursing",
    "College of Law", "College of Architecture and Fine Arts", "College of Industrial Technology"
]
PROGRAMS = [
    "BS Computer Science", "BS Information Technology", "BS Civil Engineering",
    "BS Mechanical Engineering", "BS Electrical Engineering", "BS Accountancy",
    "BS Business Administration", "BS Education", "BS Nursing", "BS Medicine",
    "BS Architecture", "BS Psychology", "BS Biology", "BS Chemistry"
]
YEAR_LEVELS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year", "Graduate"]
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BLOOD_DONATION_OPTIONS = ["0", "1", "2", "3"]  # 0=eligible, 1=willing, 2=willing but unsure, 3=not willing
PAYMENT_OPTIONS = [
    "One-time payment of Php 50.00 for the whole semester",
    "One-time payment of Php 100.00 for the whole academic year (2 semesters)"
]

def generate_realistic_name():
    """Generate a realistic Filipino name"""
    first_name = random.choice(FILIPINO_FIRST_NAMES)
    last_name = random.choice(FILIPINO_LAST_NAMES)
    middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{last_name}, {first_name} {middle_initial}."

def generate_srcode():
    """Generate a realistic SR code"""
    return f"SR-{random.randint(20, 25)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generate_email(fullname, srcode):
    """Generate a realistic GSuite email"""
    # Extract first name and last name
    parts = fullname.split(',')
    if len(parts) >= 2:
        last_name = parts[0].strip()
        first_name = parts[1].split()[0].strip() if parts[1].strip() else "student"
        username = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}"
    else:
        username = f"student{random.randint(100, 999)}"
    
    # Add numbers to make it unique
    username = f"{username}{random.randint(10, 99)}"
    return f"{username}@g.batstate-u.edu.ph"

def generate_philippine_address():
    """Generate a realistic Philippine address"""
    cities = ["Batangas City", "Lipa City", "Tanauan City", "Calamba City", "San Pablo City", 
              "Sta. Rosa City", "Bauan", "Lemery", "Balayan", "Nasugbu", "Taal", "Alitagtag"]
    barangays = ["Barangay 1", "Barangay 2", "Barangay 3", "Poblacion", "San Jose", "San Isidro",
                 "San Antonio", "San Miguel", "Sta. Cruz", "Sta. Maria", "Sta. Ana", "Sta. Rita"]
    streets = ["Rizal Street", "Aguinaldo Street", "Bonifacio Street", "Mabini Street", 
               "Luna Street", "Del Pilar Street", "Burgos Street", "Gomez Street"]
    
    street_num = random.randint(1, 999)
    street = random.choice(streets)
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

def add_100_people(count=50):
    """Add realistic people to the database (default: 50)"""
    print("=" * 60)
    print(f"ADDING {count} REALISTIC PEOPLE TO SULAMBI VMS")
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
    
    # Get or create events
    print("Checking for events...")
    internal_event_ids, external_event_ids = get_or_create_events(conn)
    all_event_ids = internal_event_ids + external_event_ids
    
    if not all_event_ids:
        print("⚠️  Warning: No events available. Members will be added but won't appear in analytics until they register for events.")
    else:
        print(f"✓ Found {len(all_event_ids)} events for volunteer registrations\n")
    
    print(f"Generating {count} realistic membership records...\n")
    
    inserted = 0
    skipped = 0
    
    for i in range(count):
        try:
            # Generate realistic personal info
            fullname = generate_realistic_name()
            srcode = generate_srcode()
            email = generate_email(fullname, srcode)
            age = random.randint(18, 25)
            
            # Generate birthday based on age
            birth_year = datetime.now().year - age
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birthday = f"{random.choice(['January', 'February', 'March', 'April', 'May', 'June', 
                                         'July', 'August', 'September', 'October', 'November', 'December'])} {birth_day}, {birth_year}"
            
            sex = random.choice(["Male", "Female"])  # Capitalized for analytics compatibility
            
            # Generate address
            address = generate_philippine_address()
            
            # Generate contact
            contact_num = f"09{random.randint(10, 19)}{random.randint(1000000, 9999999)}"
            fblink = f"https://facebook.com/{fullname.split(',')[1].split()[0].lower()}.{fullname.split(',')[0].lower().replace(' ', '')}"
            
            # Generate membership-specific data
            applying_as = random.choice(APPLYING_AS_OPTIONS)
            volunterism_experience = random.choice([True, False])
            
            # Time devotion - make it realistic
            if volunterism_experience:
                weekdays_time = random.choice(["1-4 hours", "5-8 hours"])
                weekends_time = random.choice(["5-8 hours", "8 hours or more"])
            else:
                weekdays_time = random.choice(["1-4 hours", "other"])
                weekends_time = random.choice(["1-4 hours", "5-8 hours"])
            
            # Areas of interest - select 1-3 areas
            selected_areas = random.sample(AREAS_OF_INTEREST, random.randint(1, 3))
            areas_of_interest = ", ".join(selected_areas)
            
            campus = random.choice(CAMPUS_OPTIONS)
            college_dept = random.choice(COLLEGES)
            program = random.choice(PROGRAMS)
            year_level = random.choice(YEAR_LEVELS)
            yrlevel_program = f"{year_level} - {program}"
            
            blood_type = random.choice(BLOOD_TYPES)
            blood_donation = random.choice(BLOOD_DONATION_OPTIONS)
            medical_condition = "None"  # Most students don't have medical conditions
            payment_option = random.choice(PAYMENT_OPTIONS)
            
            # Generate unique username
            username = f"{fullname.split(',')[1].split()[0].lower()}{fullname.split(',')[0].lower().replace(' ', '')}{random.randint(100, 999)}"
            password = "Password123!"  # Default password for all test accounts
            
            # Generate optional fields
            if volunterism_experience:
                volunteer_exp_q1 = f"Participated in {random.choice(['community outreach', 'tree planting', 'blood donation', 'tutoring program', 'medical mission'])} organized by Sulambi VOSA last academic year."
                volunteer_exp_q2 = f"Volunteered in {random.choice(['local barangay cleanup', 'church activities', 'youth organization', 'NGO programs', 'school events'])} outside the university."
                volunteer_exp_proof = ""
            else:
                volunteer_exp_q1 = ""
                volunteer_exp_q2 = ""
                volunteer_exp_proof = ""
            
            reason_q1 = f"I want to become a member because I believe in giving back to the community and making a positive impact in the lives of others."
            reason_q2 = f"I can contribute my {random.choice(['time', 'skills', 'knowledge', 'enthusiasm', 'dedication'])} to help the organization achieve its goals and serve the community better."
            
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
                username, password, 1, 1,  # Set active=1 and accepted=1 (approved) so they appear in the system
                volunteer_exp_q1, volunteer_exp_q2, volunteer_exp_proof,
                reason_q1, reason_q2
            ))
            
            inserted += 1
            
            # Create requirement (volunteer registration) for this member so they appear in analytics
            if all_event_ids:
                try:
                    # Randomly assign member to 1-3 events
                    num_events = random.randint(1, 3)
                    selected_events = random.sample(all_event_ids, min(num_events, len(all_event_ids)))
                    
                    for event_id in selected_events:
                        # Determine if it's internal or external
                        event_type = "internal" if event_id in internal_event_ids else "external"
                        
                        # Generate requirement ID
                        req_id = f"REQ-{random.randint(10000, 99999)}-{i}-{event_id}"
                        
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
                except Exception as e:
                    # If requirement creation fails, continue anyway
                    pass
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{count} records inserted...")
                conn.commit()
        
        except sqlite3.IntegrityError as e:
            # Skip duplicates (username, email, or srcode already exists)
            skipped += 1
            continue
        except Exception as e:
            print(f"  Error inserting record {i + 1}: {e}")
            skipped += 1
            continue
    
    conn.commit()
    
    # Count how many members now have requirements (will appear in analytics)
    cursor.execute("""
        SELECT COUNT(DISTINCT m.email)
        FROM membership m
        INNER JOIN requirements r ON m.email = r.email
        WHERE m.accepted = 1 AND m.active = 1 AND r.accepted = 1
    """)
    members_in_analytics = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ SUCCESSFULLY ADDED {inserted} PEOPLE TO THE DATABASE!")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} records (duplicates or errors)")
    print("=" * 60)
    print("\nAll members have been set to:")
    print("  - Active: True")
    print("  - Accepted: True (Approved)")
    print("  - Default Password: Password123!")
    print(f"  - {members_in_analytics} members have volunteer registrations (will appear in analytics)")
    print("\nThese members will now appear in:")
    print("  ✓ System database")
    print("  ✓ Predictive Analytics (Sex and Age breakdown)")
    print("  ✓ Dashboard charts")

if __name__ == "__main__":
    add_100_people(50)  # Add 50 people by default

