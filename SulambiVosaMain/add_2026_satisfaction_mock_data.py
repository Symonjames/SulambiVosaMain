#!/usr/bin/env python3
"""
Script to add mock satisfaction rating predictive analytics data for 2026
for both beneficiaries and volunteers
"""

import sqlite3
import os
import random
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Database path resolution
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(backend_dir, DB_PATH)

# Check for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
is_postgresql = DATABASE_URL and DATABASE_URL.startswith('postgresql://')


def get_db_connection():
    """Get database connection (SQLite or PostgreSQL)"""
    if is_postgresql:
        try:
            import psycopg2
            from urllib.parse import urlparse
            result = urlparse(DATABASE_URL)
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port or 5432
            )
            return conn
        except ImportError:
            print("Warning: psycopg2 not installed. Using SQLite...")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}. Using SQLite...")
    
    # SQLite fallback
    return sqlite3.connect(DB_PATH, timeout=30.0)


def ensure_satisfaction_table(cursor, conn):
    """Ensure satisfactionSurveys table exists"""
    if is_postgresql:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS satisfactionSurveys(
                id SERIAL PRIMARY KEY,
                "eventId" INTEGER NOT NULL,
                "eventType" VARCHAR(255) NOT NULL,
                "requirementId" VARCHAR(255),
                "respondentType" VARCHAR(255) NOT NULL,
                "respondentEmail" VARCHAR(255) NOT NULL,
                "respondentName" VARCHAR(255),
                "overallSatisfaction" REAL NOT NULL,
                "volunteerRating" REAL,
                "beneficiaryRating" REAL,
                "organizationRating" REAL,
                "communicationRating" REAL,
                "venueRating" REAL,
                "materialsRating" REAL,
                "supportRating" REAL,
                q13 TEXT,
                q14 TEXT,
                comment TEXT,
                recommendations TEXT,
                "wouldRecommend" BOOLEAN,
                "areasForImprovement" TEXT,
                "positiveAspects" TEXT,
                "submittedAt" BIGINT NOT NULL,
                finalized BOOLEAN DEFAULT FALSE
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS satisfactionSurveys(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                eventId INTEGER NOT NULL,
                eventType STRING NOT NULL,
                requirementId STRING,
                respondentType STRING NOT NULL,
                respondentEmail STRING NOT NULL,
                respondentName STRING,
                overallSatisfaction REAL NOT NULL,
                volunteerRating REAL,
                beneficiaryRating REAL,
                organizationRating REAL,
                communicationRating REAL,
                venueRating REAL,
                materialsRating REAL,
                supportRating REAL,
                q13 TEXT,
                q14 TEXT,
                comment TEXT,
                recommendations TEXT,
                wouldRecommend BOOLEAN,
                areasForImprovement TEXT,
                positiveAspects TEXT,
                submittedAt INTEGER NOT NULL,
                finalized BOOLEAN DEFAULT FALSE
            )
        """)
    conn.commit()


def get_2026_timestamps():
    """Generate timestamps for 2026 events"""
    # Generate timestamps for different months in 2026
    timestamps = []
    for month in range(1, 13):
        # Random day in month
        day = random.randint(1, 28)
        dt = datetime(2026, month, day, random.randint(8, 18), random.randint(0, 59))
        # Event duration: 2-6 hours
        start_ts = int(dt.timestamp() * 1000)
        end_dt = dt + timedelta(hours=random.randint(2, 6))
        end_ts = int(end_dt.timestamp() * 1000)
        timestamps.append((start_ts, end_ts))
    return timestamps


def get_or_create_2026_events(conn, cursor):
    """Get existing events or create mock 2026 events"""
    event_timestamps = get_2026_timestamps()
    events = []
    
    # Try to get existing accepted events first
    if is_postgresql:
        cursor.execute('SELECT id, title, \'internal\' as type FROM "internalEvents" WHERE status = \'accepted\' LIMIT 10')
        internal_events = cursor.fetchall()
        cursor.execute('SELECT id, title, \'external\' as type FROM "externalEvents" WHERE status = \'accepted\' LIMIT 10')
        external_events = cursor.fetchall()
    else:
        cursor.execute("SELECT id, title, 'internal' as type FROM internalEvents WHERE status = 'accepted' LIMIT 10")
        internal_events = cursor.fetchall()
        cursor.execute("SELECT id, title, 'external' as type FROM externalEvents WHERE status = 'accepted' LIMIT 10")
        external_events = cursor.fetchall()
    
    all_existing_events = internal_events + external_events
    
    if all_existing_events:
        # Use existing events but assign 2026 timestamps for mock data
        print(f"[OK] Found {len(all_existing_events)} existing events, will use them for 2026 mock data")
        return all_existing_events[:12], event_timestamps
    
    # Create mock events if none exist
    print("[WARNING] No existing events found. Creating mock 2026 events...")
    event_titles = [
        ("Community Health Outreach Program", "internal"),
        ("Educational Workshop Series", "internal"),
        ("Environmental Cleanup Drive", "external"),
        ("Youth Leadership Training", "internal"),
        ("Food Distribution Event", "external"),
        ("Digital Literacy Program", "internal"),
        ("Disaster Relief Operations", "external"),
        ("Skills Development Workshop", "internal"),
        ("Community Garden Initiative", "external"),
        ("Mental Health Awareness Campaign", "internal"),
        ("Clean Water Access Project", "external"),
        ("Livelihood Training Program", "internal")
    ]
    
    mock_events = []
    for idx, (title, event_type) in enumerate(event_titles):
        start_ts, end_ts = event_timestamps[idx % len(event_timestamps)]
        
        if event_type == "internal":
            if is_postgresql:
                cursor.execute('''
                    INSERT INTO "internalEvents" (title, status, partner, venue, "durationStart", "durationEnd", created, modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (title, "accepted", "Community Partner", "Various Locations", start_ts, end_ts, start_ts, start_ts))
            else:
                cursor.execute('''
                    INSERT INTO internalEvents (title, status, partner, venue, durationStart, durationEnd, created, modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title, "accepted", "Community Partner", "Various Locations", start_ts, end_ts, start_ts, start_ts))
                event_id = cursor.lastrowid
        else:
            if is_postgresql:
                cursor.execute('''
                    INSERT INTO "externalEvents" (title, status, "orgInvolved", location, "durationStart", "durationEnd", created, modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (title, "accepted", "Partner Organization", "Various Locations", start_ts, end_ts, start_ts, start_ts))
            else:
                cursor.execute('''
                    INSERT INTO externalEvents (title, status, orgInvolved, location, durationStart, durationEnd, created, modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title, "accepted", "Partner Organization", "Various Locations", start_ts, end_ts, start_ts, start_ts))
                event_id = cursor.lastrowid
        
        if is_postgresql:
            event_id = cursor.fetchone()[0]
        
        mock_events.append((event_id, title, event_type))
    
    conn.commit()
    return mock_events, event_timestamps


def generate_satisfaction_ratings():
    """Generate realistic satisfaction ratings (1-5 scale)"""
    # Most ratings are positive (3-5), with some variation
    ratings = {
        'overall': round(random.choices([3, 4, 4, 5, 5], weights=[1, 3, 4, 5, 4])[0] + random.uniform(-0.3, 0.3), 2),
        'organization': round(random.choices([3, 4, 4, 5, 5], weights=[1, 2, 4, 5, 4])[0] + random.uniform(-0.3, 0.3), 2),
        'communication': round(random.choices([3, 4, 4, 5, 5], weights=[1, 3, 4, 5, 4])[0] + random.uniform(-0.3, 0.3), 2),
        'venue': round(random.choices([3, 4, 4, 5, 5], weights=[1, 3, 4, 5, 3])[0] + random.uniform(-0.3, 0.3), 2),
        'materials': round(random.choices([3, 4, 4, 5, 5], weights=[1, 3, 4, 5, 4])[0] + random.uniform(-0.3, 0.3), 2),
        'support': round(random.choices([3, 4, 4, 5, 5], weights=[1, 3, 4, 5, 4])[0] + random.uniform(-0.3, 0.3), 2),
    }
    
    # Ensure ratings are within 1-5 range
    for key in ratings:
        ratings[key] = max(1.0, min(5.0, ratings[key]))
    
    return ratings


def generate_comments(respondent_type):
    """Generate realistic comments based on respondent type"""
    if respondent_type == "Volunteer":
        comments = [
            "Great event, well organized and meaningful",
            "Enjoyed working with the team and helping the community",
            "Very informative and well-structured activities",
            "Good communication throughout the event",
            "Would definitely volunteer again",
            "Excellent coordination and support",
            "Helpful for personal growth and community impact",
            "Well planned activities with clear objectives",
            "Good venue and facilities provided",
            "Professional and well-managed event"
        ]
    else:  # Beneficiary
        comments = [
            "Very helpful program, learned a lot",
            "Appreciate the support and assistance provided",
            "The event addressed our community needs well",
            "Clear communication and easy to follow",
            "Would recommend to others in need",
            "Grateful for the services provided",
            "Well organized and accessible",
            "The materials and resources were very useful",
            "Support staff was friendly and helpful",
            "Made a positive impact on our community"
        ]
    
    recommendations = [
        "Keep up the good work",
        "Continue organizing similar events",
        "More events like this would be great",
        "Consider expanding to more locations",
        "Well done!",
        "Excellent initiative",
        "Hope to see more programs like this",
        "Continue improving and expanding"
    ]
    
    return random.choice(comments), random.choice(recommendations)


def generate_email(name):
    """Generate a realistic email from name"""
    name_lower = name.lower().replace(" ", ".")
    domains = ["gmail.com", "yahoo.com", "outlook.com", "email.com", "student.batstate-u.edu.ph"]
    return f"{name_lower}@{random.choice(domains)}"


def add_2026_satisfaction_data():
    """Add mock satisfaction rating data for 2026"""
    print("=" * 70)
    print("ADDING 2026 SATISFACTION RATING PREDICTIVE ANALYTICS DATA")
    print("=" * 70)
    
    if not os.path.exists(DB_PATH) and not is_postgresql:
        print(f"[ERROR] Database not found at: {DB_PATH}")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure table exists
    ensure_satisfaction_table(cursor, conn)
    
    # Get or create events
    events, timestamps = get_or_create_2026_events(conn, cursor)
    
    if not events:
        print("[ERROR] No events available for creating satisfaction data")
        conn.close()
        return
    
    print(f"\n[OK] Using {len(events)} events for 2026 satisfaction data")
    print("\nGenerating satisfaction ratings for volunteers and beneficiaries...\n")
    
    # Generate satisfaction data
    volunteer_names = [
        "Maria Santos", "Juan Cruz", "Ana Reyes", "Carlos Mendoza", "Liza Garcia",
        "Mark Torres", "Sarah Lopez", "Michael Villanueva", "Jennifer Martinez", "Robert Tan",
        "Grace Lim", "David Ong", "Patricia Chan", "James Lee", "Catherine Yu",
        "Ryan Kim", "Michelle Wong", "Kevin Lim", "Rachel Tan", "Daniel Ng"
    ]
    
    beneficiary_names = [
        "Rosa Dela Cruz", "Pedro Bautista", "Elena Gonzales", "Manuel Ramos", "Carmen Flores",
        "Jose Fernandez", "Teresa Rivera", "Antonio Morales", "Maria Concepcion", "Francisco Estrada",
        "Dolores Vargas", "Ricardo Navarro", "Beatriz Herrera", "Rodrigo Alvarez", "Esperanza Guzman",
        "Emilio Castillo", "Amparo Del Rosario", "Hector Medina", "Lucia Salazar", "Gerardo Valdez"
    ]
    
    added_volunteers = 0
    added_beneficiaries = 0
    errors = 0
    
    # Generate satisfaction data for each event
    for event_id, event_title, event_type in events:
        # Add volunteer satisfaction data (3-5 volunteers per event)
        num_volunteers = random.randint(3, 5)
        for _ in range(num_volunteers):
            try:
                name = random.choice(volunteer_names)
                email = generate_email(name)
                ratings = generate_satisfaction_ratings()
                comment, recommendation = generate_comments("Volunteer")
                
                # Generate submission timestamp (within 2026)
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                submitted_dt = datetime(2026, month, day, random.randint(10, 20), random.randint(0, 59))
                submitted_at = int(submitted_dt.timestamp() * 1000)
                
                if is_postgresql:
                    cursor.execute('''
                        INSERT INTO satisfactionSurveys (
                            "eventId", "eventType", "requirementId", "respondentType",
                            "respondentEmail", "respondentName", "overallSatisfaction",
                            "volunteerRating", "beneficiaryRating", "organizationRating",
                            "communicationRating", "venueRating", "materialsRating",
                            "supportRating", q13, q14, comment, recommendations,
                            "wouldRecommend", "areasForImprovement", "positiveAspects",
                            "submittedAt", finalized
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        event_id, event_type, None, "Volunteer",
                        email, name, ratings['overall'],
                        ratings['overall'], None, ratings['organization'],
                        ratings['communication'], ratings['venue'], ratings['materials'],
                        ratings['support'], str(ratings['overall']), None, comment, recommendation,
                        True, "", comment,
                        submitted_at, True
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO satisfactionSurveys (
                            eventId, eventType, requirementId, respondentType,
                            respondentEmail, respondentName, overallSatisfaction,
                            volunteerRating, beneficiaryRating, organizationRating,
                            communicationRating, venueRating, materialsRating,
                            supportRating, q13, q14, comment, recommendations,
                            wouldRecommend, areasForImprovement, positiveAspects,
                            submittedAt, finalized
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event_id, event_type, None, "Volunteer",
                        email, name, ratings['overall'],
                        ratings['overall'], None, ratings['organization'],
                        ratings['communication'], ratings['venue'], ratings['materials'],
                        ratings['support'], str(ratings['overall']), None, comment, recommendation,
                        1, "", comment,
                        submitted_at, 1
                    ))
                
                added_volunteers += 1
                
            except Exception as e:
                print(f"  Error adding volunteer data: {e}")
                errors += 1
                continue
        
        # Add beneficiary satisfaction data (5-8 beneficiaries per event)
        num_beneficiaries = random.randint(5, 8)
        for _ in range(num_beneficiaries):
            try:
                name = random.choice(beneficiary_names)
                email = generate_email(name)
                ratings = generate_satisfaction_ratings()
                comment, recommendation = generate_comments("Beneficiary")
                
                # Generate submission timestamp (within 2026)
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                submitted_dt = datetime(2026, month, day, random.randint(10, 20), random.randint(0, 59))
                submitted_at = int(submitted_dt.timestamp() * 1000)
                
                if is_postgresql:
                    cursor.execute('''
                        INSERT INTO satisfactionSurveys (
                            "eventId", "eventType", "requirementId", "respondentType",
                            "respondentEmail", "respondentName", "overallSatisfaction",
                            "volunteerRating", "beneficiaryRating", "organizationRating",
                            "communicationRating", "venueRating", "materialsRating",
                            "supportRating", q13, q14, comment, recommendations,
                            "wouldRecommend", "areasForImprovement", "positiveAspects",
                            "submittedAt", finalized
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        event_id, event_type, None, "Beneficiary",
                        email, name, ratings['overall'],
                        None, ratings['overall'], ratings['organization'],
                        ratings['communication'], ratings['venue'], ratings['materials'],
                        ratings['support'], None, str(ratings['overall']), comment, recommendation,
                        True, "", comment,
                        submitted_at, True
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO satisfactionSurveys (
                            eventId, eventType, requirementId, respondentType,
                            respondentEmail, respondentName, overallSatisfaction,
                            volunteerRating, beneficiaryRating, organizationRating,
                            communicationRating, venueRating, materialsRating,
                            supportRating, q13, q14, comment, recommendations,
                            wouldRecommend, areasForImprovement, positiveAspects,
                            submittedAt, finalized
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event_id, event_type, None, "Beneficiary",
                        email, name, ratings['overall'],
                        None, ratings['overall'], ratings['organization'],
                        ratings['communication'], ratings['venue'], ratings['materials'],
                        ratings['support'], None, str(ratings['overall']), comment, recommendation,
                        1, "", comment,
                        submitted_at, 1
                    ))
                
                added_beneficiaries += 1
                
            except Exception as e:
                print(f"  Error adding beneficiary data: {e}")
                errors += 1
                continue
        
        if (added_volunteers + added_beneficiaries) % 20 == 0:
            conn.commit()
            print(f"  Progress: {added_volunteers} volunteers, {added_beneficiaries} beneficiaries...")
    
    conn.commit()
    
    # Verify results
    if is_postgresql:
        cursor.execute('SELECT COUNT(*) FROM satisfactionSurveys WHERE EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026')
        total_2026 = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM satisfactionSurveys WHERE "respondentType" = \'Volunteer\' AND EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026')
        volunteers_2026 = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM satisfactionSurveys WHERE "respondentType" = \'Beneficiary\' AND EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026')
        beneficiaries_2026 = cursor.fetchone()[0]
    else:
        cursor.execute('''
            SELECT COUNT(*) FROM satisfactionSurveys 
            WHERE CAST(strftime('%Y', datetime(submittedAt / 1000, 'unixepoch')) AS INTEGER) = 2026
        ''')
        total_2026 = cursor.fetchone()[0]
        cursor.execute('''
            SELECT COUNT(*) FROM satisfactionSurveys 
            WHERE respondentType = 'Volunteer' 
            AND CAST(strftime('%Y', datetime(submittedAt / 1000, 'unixepoch')) AS INTEGER) = 2026
        ''')
        volunteers_2026 = cursor.fetchone()[0]
        cursor.execute('''
            SELECT COUNT(*) FROM satisfactionSurveys 
            WHERE respondentType = 'Beneficiary' 
            AND CAST(strftime('%Y', datetime(submittedAt / 1000, 'unixepoch')) AS INTEGER) = 2026
        ''')
        beneficiaries_2026 = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("[SUCCESS] 2026 SATISFACTION RATING DATA ADDED!")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  - Added {added_volunteers} volunteer satisfaction ratings")
    print(f"  - Added {added_beneficiaries} beneficiary satisfaction ratings")
    print(f"  - Total 2026 satisfaction surveys: {total_2026}")
    print(f"  - Volunteers (2026): {volunteers_2026}")
    print(f"  - Beneficiaries (2026): {beneficiaries_2026}")
    if errors > 0:
        print(f"  - Errors: {errors}")
    
    print("\nThis data will appear in:")
    print("  - Predictive Satisfaction Ratings Analytics")
    print("  - Satisfaction Analytics by Year (2026)")
    print("  - Volunteer vs Beneficiary Satisfaction Breakdown")
    print("  - Satisfaction Trends Analysis")


if __name__ == "__main__":
    add_2026_satisfaction_data()

