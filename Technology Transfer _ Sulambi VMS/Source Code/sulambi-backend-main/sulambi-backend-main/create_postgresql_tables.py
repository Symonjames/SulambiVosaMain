#!/usr/bin/env python3
"""
Create PostgreSQL tables compatible with the SQLite schema
Run this BEFORE running migrate_sqlite_to_postgresql.py
"""

import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("Please set DATABASE_URL to your Render PostgreSQL connection string")
    sys.exit(1)

try:
    import psycopg2
    result = urlparse(DATABASE_URL)
    
    pg_conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432
    )
    pg_cursor = pg_conn.cursor()
    print("✓ Connected to PostgreSQL database")
except ImportError:
    print("❌ ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR connecting to PostgreSQL: {e}")
    sys.exit(1)

print("=" * 70)
print("CREATING POSTGRESQL TABLES")
print("=" * 70)

# Convert SQLite syntax to PostgreSQL
# SQLite: INTEGER PRIMARY KEY AUTOINCREMENT -> PostgreSQL: SERIAL PRIMARY KEY
# SQLite: STRING -> PostgreSQL: VARCHAR or TEXT
# SQLite: BOOLEAN -> PostgreSQL: BOOLEAN (same)

tables = {
    'accounts': """
        CREATE TABLE IF NOT EXISTS accounts(
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            accountType VARCHAR(255) NOT NULL,
            membershipId INTEGER,
            active BOOLEAN DEFAULT TRUE
        )
    """,
    
    'sessions': """
        CREATE TABLE IF NOT EXISTS sessions(
            id SERIAL PRIMARY KEY,
            token VARCHAR(255) UNIQUE,
            userid INTEGER NOT NULL,
            accountType VARCHAR(255) NOT NULL
        )
    """,
    
    'membership': """
        CREATE TABLE IF NOT EXISTS membership(
            id SERIAL PRIMARY KEY,
            applyingAs VARCHAR(255) NOT NULL,
            volunterismExperience BOOLEAN NOT NULL,
            weekdaysTimeDevotion VARCHAR(255) NOT NULL,
            weekendsTimeDevotion VARCHAR(255) NOT NULL,
            areasOfInterest TEXT NOT NULL,
            fullname VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            affiliation VARCHAR(255) DEFAULT 'N/A',
            srcode VARCHAR(255) NOT NULL,
            age INTEGER NOT NULL,
            birthday VARCHAR(255) NOT NULL,
            sex VARCHAR(255) NOT NULL,
            campus VARCHAR(255) NOT NULL,
            collegeDept VARCHAR(255) NOT NULL,
            yrlevelprogram VARCHAR(255) NOT NULL,
            address TEXT NOT NULL,
            contactNum VARCHAR(255) NOT NULL,
            fblink VARCHAR(255) NOT NULL,
            bloodType VARCHAR(255) NOT NULL,
            bloodDonation VARCHAR(255) NOT NULL,
            medicalCondition TEXT NOT NULL,
            paymentOption TEXT NOT NULL,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            accepted BOOLEAN,
            volunteerExpQ1 TEXT,
            volunteerExpQ2 TEXT,
            volunteerExpProof VARCHAR(255),
            reasonQ1 TEXT,
            reasonQ2 TEXT
        )
    """,
    
    'requirements': """
        CREATE TABLE IF NOT EXISTS requirements(
            id VARCHAR(255) PRIMARY KEY,
            medCert VARCHAR(255) NOT NULL,
            waiver VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL,
            eventId INTEGER NOT NULL,
            affiliation VARCHAR(255) DEFAULT 'N/A',
            curriculum VARCHAR(255),
            destination VARCHAR(255),
            firstAid VARCHAR(255),
            fees VARCHAR(255),
            personnelInCharge VARCHAR(255),
            personnelRole VARCHAR(255),
            fullname VARCHAR(255),
            email VARCHAR(255),
            srcode VARCHAR(255),
            age INTEGER,
            birthday VARCHAR(255),
            sex VARCHAR(255),
            campus VARCHAR(255),
            collegeDept VARCHAR(255),
            yrlevelprogram VARCHAR(255),
            address TEXT,
            contactNum VARCHAR(255),
            fblink VARCHAR(255),
            accepted BOOLEAN
        )
    """,
    
    'internalEvents': """
        CREATE TABLE IF NOT EXISTS internalEvents(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            durationStart BIGINT NOT NULL,
            durationEnd BIGINT NOT NULL,
            venue VARCHAR(255) NOT NULL,
            modeOfDelivery VARCHAR(255) NOT NULL,
            projectTeam TEXT NOT NULL,
            partner VARCHAR(255) NOT NULL,
            participant VARCHAR(255) NOT NULL,
            maleTotal INTEGER NOT NULL,
            femaleTotal INTEGER NOT NULL,
            rationale TEXT NOT NULL,
            objectives TEXT NOT NULL,
            description TEXT NOT NULL,
            workPlan TEXT NOT NULL,
            financialRequirement TEXT NOT NULL,
            evaluationMechanicsPlan TEXT NOT NULL,
            sustainabilityPlan TEXT NOT NULL,
            createdBy INTEGER NOT NULL,
            status VARCHAR(255) NOT NULL,
            toPublic BOOLEAN NOT NULL,
            evaluationSendTime BIGINT NOT NULL,
            feedback_id INTEGER,
            eventProposalType VARCHAR(255),
            signatoriesId INTEGER,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'externalEvents': """
        CREATE TABLE IF NOT EXISTS externalEvents(
            id SERIAL PRIMARY KEY,
            extensionServiceType VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            durationStart BIGINT NOT NULL,
            durationEnd BIGINT NOT NULL,
            sdg VARCHAR(255) NOT NULL,
            orgInvolved VARCHAR(255) NOT NULL,
            programInvolved VARCHAR(255) NOT NULL,
            projectLeader VARCHAR(255) NOT NULL,
            partners VARCHAR(255) NOT NULL,
            beneficiaries VARCHAR(255) NOT NULL,
            totalCost REAL NOT NULL,
            sourceOfFund VARCHAR(255) NOT NULL,
            rationale TEXT NOT NULL,
            objectives TEXT NOT NULL,
            expectedOutput TEXT NOT NULL,
            description TEXT NOT NULL,
            financialPlan TEXT NOT NULL,
            dutiesOfPartner TEXT NOT NULL,
            evaluationMechanicsPlan TEXT NOT NULL,
            sustainabilityPlan TEXT NOT NULL,
            createdBy INTEGER NOT NULL,
            status VARCHAR(255) NOT NULL,
            evaluationSendTime BIGINT NOT NULL,
            toPublic BOOLEAN DEFAULT FALSE,
            feedback_id INTEGER,
            externalServiceType VARCHAR(255),
            eventProposalType VARCHAR(255),
            signatoriesId INTEGER,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'externalReport': """
        CREATE TABLE IF NOT EXISTS externalReport(
            id SERIAL PRIMARY KEY,
            eventId INTEGER NOT NULL,
            narrative TEXT NOT NULL,
            photos TEXT NOT NULL,
            photoCaptions TEXT,
            signatoriesId INTEGER
        )
    """,
    
    'internalReport': """
        CREATE TABLE IF NOT EXISTS internalReport(
            id SERIAL PRIMARY KEY,
            eventId INTEGER NOT NULL,
            narrative TEXT NOT NULL,
            budgetUtilized INTEGER NOT NULL,
            budgetUtilizedSrc VARCHAR(255) NOT NULL,
            psAttribution INTEGER NOT NULL,
            psAttributionSrc VARCHAR(255) NOT NULL,
            photos TEXT NOT NULL,
            photoCaptions TEXT,
            signatoriesId INTEGER
        )
    """,
    
    'helpdesk': """
        CREATE TABLE IF NOT EXISTS helpdesk(
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            nameOfRequestee VARCHAR(255) NOT NULL,
            addressOfRequestee VARCHAR(255) NOT NULL,
            contactOfRequestee VARCHAR(255) NOT NULL,
            fblinkOfRequestee VARCHAR(255) NOT NULL,
            donationType INTEGER NOT NULL,
            nameOfMoneyRecipient VARCHAR(255) NOT NULL,
            addressOfRecipient VARCHAR(255) NOT NULL,
            contactOfRecipient VARCHAR(255) NOT NULL,
            gcashOrBankOfRecipient VARCHAR(255),
            reason VARCHAR(255) NOT NULL,
            bloodTypeOfRecipient VARCHAR(255),
            necessaryFiles TEXT NOT NULL,
            donationNeeded TEXT NOT NULL
        )
    """,
    
    'evaluation': """
        CREATE TABLE IF NOT EXISTS evaluation(
            id SERIAL PRIMARY KEY,
            criteria TEXT NOT NULL,
            q13 TEXT NOT NULL,
            q14 TEXT NOT NULL,
            comment TEXT NOT NULL,
            recommendations TEXT NOT NULL,
            requirementId VARCHAR(255) NOT NULL,
            finalized BOOLEAN DEFAULT FALSE
        )
    """,
    
    'eventSignatories': """
        CREATE TABLE IF NOT EXISTS eventSignatories(
            id SERIAL PRIMARY KEY,
            preparedBy VARCHAR(255) DEFAULT 'NAME',
            reviewedBy VARCHAR(255) DEFAULT 'NAME',
            recommendingApproval1 VARCHAR(255) DEFAULT 'NAME',
            recommendingApproval2 VARCHAR(255) DEFAULT 'NAME',
            approvedBy VARCHAR(255) DEFAULT 'NAME',
            preparedTitle VARCHAR(255) DEFAULT 'Asst. Director, GAD Advocacies/GAD Head Secretariat/Coordinator',
            reviewedTitle VARCHAR(255) DEFAULT 'Director, Extension Services/Head, Extension Services',
            approvedTitle VARCHAR(255) DEFAULT 'University President/Chancellor',
            recommendingSignatory1 VARCHAR(255) DEFAULT 'Vice President/Vice Chancellor for Research, Development and Extension Services',
            recommendingSignatory2 VARCHAR(255) DEFAULT 'Vice President/Vice Chancellor for Administration and Finance'
        )
    """,
    
    'feedback': """
        CREATE TABLE IF NOT EXISTS feedback(
            id SERIAL PRIMARY KEY,
            message TEXT NOT NULL,
            state VARCHAR(255)
        )
    """,
    
    'activity_month_assignments': """
        CREATE TABLE IF NOT EXISTS activity_month_assignments(
            id SERIAL PRIMARY KEY,
            eventId INTEGER NOT NULL,
            activity_name TEXT NOT NULL,
            month INTEGER NOT NULL
        )
    """,
    
    'satisfactionSurveys': """
        CREATE TABLE IF NOT EXISTS satisfactionSurveys(
            id SERIAL PRIMARY KEY,
            eventId INTEGER NOT NULL,
            eventType VARCHAR(255) NOT NULL,
            requirementId VARCHAR(255),
            respondentType VARCHAR(255) NOT NULL,
            respondentEmail VARCHAR(255) NOT NULL,
            respondentName VARCHAR(255),
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
            submittedAt BIGINT NOT NULL,
            finalized BOOLEAN DEFAULT FALSE
        )
    """,
    
    'dropoutRiskAssessment': """
        CREATE TABLE IF NOT EXISTS dropoutRiskAssessment(
            id SERIAL PRIMARY KEY,
            membershipId INTEGER NOT NULL,
            volunteerEmail VARCHAR(255) NOT NULL,
            volunteerName VARCHAR(255) NOT NULL,
            totalEventsAttended INTEGER DEFAULT 0,
            eventsLastSemester INTEGER DEFAULT 0,
            eventsLastMonth INTEGER DEFAULT 0,
            averageEventsPerSemester REAL DEFAULT 0,
            lastEventDate BIGINT,
            daysSinceLastEvent INTEGER DEFAULT 0,
            longestInactivityPeriod INTEGER DEFAULT 0,
            riskScore INTEGER DEFAULT 0,
            riskLevel VARCHAR(255) DEFAULT 'Low',
            riskFactors TEXT,
            engagementTrend VARCHAR(255) DEFAULT 'Stable',
            participationRate REAL DEFAULT 0,
            retentionProbability REAL DEFAULT 100,
            semester VARCHAR(255),
            calculatedAt BIGINT NOT NULL,
            isAtRisk BOOLEAN DEFAULT FALSE,
            interventionNeeded BOOLEAN DEFAULT FALSE,
            notes TEXT
        )
    """,
    
    'volunteerParticipationHistory': """
        CREATE TABLE IF NOT EXISTS volunteerParticipationHistory(
            id SERIAL PRIMARY KEY,
            volunteerEmail VARCHAR(255) NOT NULL,
            volunteerName VARCHAR(255) NOT NULL,
            membershipId INTEGER,
            semester VARCHAR(255) NOT NULL,
            semesterYear INTEGER NOT NULL,
            semesterNumber INTEGER NOT NULL,
            eventsJoined INTEGER DEFAULT 0,
            eventsAttended INTEGER DEFAULT 0,
            eventsDropped INTEGER DEFAULT 0,
            attendanceRate REAL DEFAULT 0,
            firstEventDate BIGINT,
            lastEventDate BIGINT,
            daysActiveInSemester INTEGER DEFAULT 0,
            participationConsistency VARCHAR(255) DEFAULT 'Regular',
            engagementLevel VARCHAR(255) DEFAULT 'Active',
            calculatedAt BIGINT NOT NULL,
            lastUpdated BIGINT NOT NULL,
            UNIQUE(volunteerEmail, semester)
        )
    """,
    
    'semester_satisfaction': """
        CREATE TABLE IF NOT EXISTS semester_satisfaction(
            id SERIAL PRIMARY KEY,
            semester VARCHAR(255) NOT NULL,
            semesterYear INTEGER NOT NULL,
            semesterNumber INTEGER NOT NULL,
            averageSatisfaction REAL NOT NULL,
            totalResponses INTEGER NOT NULL,
            volunteerSatisfaction REAL,
            beneficiarySatisfaction REAL,
            calculatedAt BIGINT NOT NULL,
            lastUpdated BIGINT NOT NULL
        )
    """
}

# Create tables
created_count = 0
for table_name, create_sql in tables.items():
    try:
        pg_cursor.execute(create_sql)
        pg_conn.commit()
        print(f"✓ Created table: {table_name}")
        created_count += 1
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠️  Table {table_name} already exists, skipping...")
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            pg_conn.rollback()

# Create indexes for volunteerParticipationHistory
try:
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_volunteer_email ON volunteerParticipationHistory(volunteerEmail)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_semester ON volunteerParticipationHistory(semester)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_event_date ON volunteerParticipationHistory(lastEventDate)")
    pg_conn.commit()
    print("✓ Created indexes for volunteerParticipationHistory")
except Exception as e:
    print(f"⚠️  Could not create indexes: {e}")
    pg_conn.rollback()

# Insert default accounts
try:
    pg_cursor.execute("""
        INSERT INTO accounts (username, password, accountType) 
        VALUES ('Admin', 'sulambi@2024', 'admin'),
               ('Sulambi-Officer', 'password@2024', 'officer')
        ON CONFLICT DO NOTHING
    """)
    pg_conn.commit()
    print("✓ Inserted default admin accounts (if they don't exist)")
except Exception as e:
    print(f"⚠️  Could not insert default accounts: {e}")
    pg_conn.rollback()

print("\n" + "=" * 70)
print(f"SUCCESS: Created {created_count}/{len(tables)} tables")
print("=" * 70)
print("\nNext steps:")
print("1. Run migrate_sqlite_to_postgresql.py to import your data")
print("2. Verify tables in Render PostgreSQL database")
print("\n✓ Connections closed")

pg_cursor.close()
pg_conn.close()

















