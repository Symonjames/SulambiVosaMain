#!/usr/bin/env python3
"""
Script to verify 2026 satisfaction rating data
"""

import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

# Database path resolution
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(backend_dir, DB_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
is_postgresql = DATABASE_URL and DATABASE_URL.startswith('postgresql://')


def verify_2026_data():
    """Verify 2026 satisfaction data"""
    print("=" * 70)
    print("VERIFYING 2026 SATISFACTION RATING DATA")
    print("=" * 70)
    
    if not os.path.exists(DB_PATH) and not is_postgresql:
        print(f"[ERROR] Database not found at: {DB_PATH}")
        return
    
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
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return
    else:
        conn = sqlite3.connect(DB_PATH)
    
    cursor = conn.cursor()
    
    # Get total 2026 satisfaction surveys
    if is_postgresql:
        cursor.execute('''
            SELECT COUNT(*) FROM satisfactionSurveys 
            WHERE EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026
        ''')
        total_2026 = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM satisfactionSurveys 
            WHERE "respondentType" = 'Volunteer' 
            AND EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026
        ''')
        volunteers_2026 = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM satisfactionSurveys 
            WHERE "respondentType" = 'Beneficiary' 
            AND EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026
        ''')
        beneficiaries_2026 = cursor.fetchone()[0]
        
        # Get average ratings
        cursor.execute('''
            SELECT 
                AVG("overallSatisfaction") as avg_overall,
                AVG("organizationRating") as avg_org,
                AVG("communicationRating") as avg_comm,
                AVG("venueRating") as avg_venue,
                AVG("materialsRating") as avg_materials,
                AVG("supportRating") as avg_support
            FROM satisfactionSurveys 
            WHERE EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026
        ''')
        avg_ratings = cursor.fetchone()
        
        # Get sample data
        cursor.execute('''
            SELECT "respondentType", "respondentName", "overallSatisfaction", 
                   TO_TIMESTAMP("submittedAt" / 1000) as submitted_date
            FROM satisfactionSurveys 
            WHERE EXTRACT(YEAR FROM TO_TIMESTAMP("submittedAt" / 1000)) = 2026
            ORDER BY "submittedAt" DESC
            LIMIT 10
        ''')
        samples = cursor.fetchall()
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
        
        # Get average ratings
        cursor.execute('''
            SELECT 
                AVG(overallSatisfaction) as avg_overall,
                AVG(organizationRating) as avg_org,
                AVG(communicationRating) as avg_comm,
                AVG(venueRating) as avg_venue,
                AVG(materialsRating) as avg_materials,
                AVG(supportRating) as avg_support
            FROM satisfactionSurveys 
            WHERE CAST(strftime('%Y', datetime(submittedAt / 1000, 'unixepoch')) AS INTEGER) = 2026
        ''')
        avg_ratings = cursor.fetchone()
        
        # Get sample data
        cursor.execute('''
            SELECT respondentType, respondentName, overallSatisfaction, 
                   datetime(submittedAt / 1000, 'unixepoch') as submitted_date
            FROM satisfactionSurveys 
            WHERE CAST(strftime('%Y', datetime(submittedAt / 1000, 'unixepoch')) AS INTEGER) = 2026
            ORDER BY submittedAt DESC
            LIMIT 10
        ''')
        samples = cursor.fetchall()
    
    print(f"\n2026 Satisfaction Data Summary:")
    print(f"  - Total 2026 satisfaction surveys: {total_2026}")
    print(f"  - Volunteer satisfaction ratings: {volunteers_2026}")
    print(f"  - Beneficiary satisfaction ratings: {beneficiaries_2026}")
    
    if avg_ratings and avg_ratings[0]:
        print(f"\nAverage Ratings (2026):")
        print(f"  - Overall Satisfaction: {avg_ratings[0]:.2f}")
        print(f"  - Organization: {avg_ratings[1]:.2f}")
        print(f"  - Communication: {avg_ratings[2]:.2f}")
        print(f"  - Venue: {avg_ratings[3]:.2f}")
        print(f"  - Materials: {avg_ratings[4]:.2f}")
        print(f"  - Support: {avg_ratings[5]:.2f}")
    
    if samples:
        print(f"\nSample Recent Entries (last 10):")
        for sample in samples:
            respondent_type, name, rating, date = sample
            print(f"  - {respondent_type}: {name} - Rating: {rating:.2f} - Date: {date}")
    
    conn.close()
    print("\n" + "=" * 70)


if __name__ == "__main__":
    verify_2026_data()

