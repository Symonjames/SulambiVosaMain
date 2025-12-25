"""
Export Predictive Satisfaction Ratings to Excel (.xlsx) format
Collects volunteers' and beneficiaries' responses including 1-5 rating scores and written comments
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

EXCEL_OUTPUT = os.path.join("data", "satisfaction-ratings.xlsx")

def export_satisfaction_ratings_to_excel():
    """Export satisfaction ratings from database to Excel format"""
    print("=" * 70)
    print("EXPORTING PREDICTIVE SATISFACTION RATINGS TO EXCEL")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if satisfactionSurveys table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='satisfactionSurveys'
    """)
    
    if not cursor.fetchone():
        print("⚠️  satisfactionSurveys table does not exist. Creating it...")
        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS satisfactionSurveys(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                eventId INTEGER NOT NULL,
                eventType STRING NOT NULL,
                requirementId STRING,
                respondentType STRING NOT NULL,
                respondentEmail STRING NOT NULL,
                respondentName STRING,
                
                -- Satisfaction Ratings (1-5 scale)
                overallSatisfaction REAL NOT NULL,
                volunteerRating REAL,
                beneficiaryRating REAL,
                
                -- Detailed Ratings
                organizationRating REAL,
                communicationRating REAL,
                venueRating REAL,
                materialsRating REAL,
                supportRating REAL,
                
                -- Survey Questions
                q13 TEXT,
                q14 TEXT,
                comment TEXT,
                recommendations TEXT,
                
                -- Additional Feedback
                wouldRecommend BOOLEAN,
                areasForImprovement TEXT,
                positiveAspects TEXT,
                
                -- Metadata
                submittedAt INTEGER NOT NULL,
                finalized BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        print("✓ Table created")
    
    # Get all satisfaction survey data
    # First, try to get from satisfactionSurveys table
    cursor.execute("""
        SELECT 
            id,
            eventId,
            eventType,
            requirementId,
            respondentType,
            respondentEmail,
            respondentName,
            overallSatisfaction,
            volunteerRating,
            beneficiaryRating,
            organizationRating,
            communicationRating,
            venueRating,
            materialsRating,
            supportRating,
            q13,
            q14,
            comment,
            recommendations,
            wouldRecommend,
            areasForImprovement,
            positiveAspects,
            submittedAt,
            finalized
        FROM satisfactionSurveys
        ORDER BY submittedAt DESC
    """)
    
    surveys = cursor.fetchall()
    
    # If no data in satisfactionSurveys, get from evaluation table (existing data)
    if len(surveys) == 0:
        print("\n⚠️  No data in satisfactionSurveys table. Checking evaluation table...")
        cursor.execute("""
            SELECT 
                e.id,
                r.eventId,
                r.type as eventType,
                e.requirementId,
                CASE 
                    WHEN e.q13 IS NOT NULL AND e.q13 != '' THEN 'Volunteer'
                    WHEN e.q14 IS NOT NULL AND e.q14 != '' THEN 'Beneficiary'
                    ELSE 'Unknown'
                END as respondentType,
                r.email as respondentEmail,
                r.fullname as respondentName,
                CASE 
                    WHEN e.q13 IS NOT NULL AND e.q13 != '' THEN CAST(e.q13 AS REAL)
                    WHEN e.q14 IS NOT NULL AND e.q14 != '' THEN CAST(e.q14 AS REAL)
                    ELSE 0
                END as overallSatisfaction,
                CAST(e.q13 AS REAL) as volunteerRating,
                CAST(e.q14 AS REAL) as beneficiaryRating,
                0 as organizationRating,
                0 as communicationRating,
                0 as venueRating,
                0 as materialsRating,
                0 as supportRating,
                e.q13,
                e.q14,
                e.comment,
                e.recommendations,
                NULL as wouldRecommend,
                NULL as areasForImprovement,
                NULL as positiveAspects,
                strftime('%s', 'now') * 1000 as submittedAt,
                e.finalized
            FROM evaluation e
            INNER JOIN requirements r ON e.requirementId = r.id
            WHERE e.finalized = 1
            AND (e.q13 IS NOT NULL OR e.q14 IS NOT NULL OR e.comment IS NOT NULL)
            ORDER BY e.id DESC
        """)
        
        surveys = cursor.fetchall()
        print(f"✓ Found {len(surveys)} records in evaluation table")
    
    if len(surveys) == 0:
        print("\n❌ No satisfaction rating data found in database")
        print("   Data will be collected when volunteers/beneficiaries submit surveys")
        conn.close()
        return
    
    # Prepare data for Excel
    data_rows = []
    for survey in surveys:
        (id, eventId, eventType, requirementId, respondentType, respondentEmail, 
         respondentName, overallSatisfaction, volunteerRating, beneficiaryRating,
         organizationRating, communicationRating, venueRating, materialsRating, 
         supportRating, q13, q14, comment, recommendations, wouldRecommend,
         areasForImprovement, positiveAspects, submittedAt, finalized) = survey
        
        # Convert timestamp to readable date
        if submittedAt:
            try:
                submitted_date = datetime.fromtimestamp(submittedAt / 1000).strftime("%Y-%m-%d %H:%M:%S")
            except:
                submitted_date = str(submittedAt)
        else:
            submitted_date = ""
        
        # Get event title
        event_title = ""
        if eventId and eventType:
            try:
                event_table = "internalEvents" if eventType == "internal" else "externalEvents"
                cursor.execute(f"SELECT title FROM {event_table} WHERE id = ?", (eventId,))
                event_row = cursor.fetchone()
                if event_row:
                    event_title = event_row[0]
            except:
                pass
        
        data_rows.append({
            "ID": id,
            "Event ID": eventId or "",
            "Event Type": eventType or "",
            "Event Title": event_title,
            "Requirement ID": requirementId or "",
            "Respondent Type": respondentType or "",
            "Respondent Email": respondentEmail or "",
            "Respondent Name": respondentName or "",
            "Overall Satisfaction (1-5)": overallSatisfaction or 0,
            "Volunteer Rating (1-5)": volunteerRating or "",
            "Beneficiary Rating (1-5)": beneficiaryRating or "",
            "Organization Rating (1-5)": organizationRating or "",
            "Communication Rating (1-5)": communicationRating or "",
            "Venue Rating (1-5)": venueRating or "",
            "Materials Rating (1-5)": materialsRating or "",
            "Support Rating (1-5)": supportRating or "",
            "Q13 (Volunteer Score)": q13 or "",
            "Q14 (Beneficiary Score)": q14 or "",
            "Comment": comment or "",
            "Recommendations": recommendations or "",
            "Would Recommend": "Yes" if wouldRecommend else "No" if wouldRecommend is not None else "",
            "Areas for Improvement": areasForImprovement or "",
            "Positive Aspects": positiveAspects or "",
            "Submitted At": submitted_date,
            "Finalized": "Yes" if finalized else "No"
        })
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(EXCEL_OUTPUT), exist_ok=True)
    
    # Export to Excel
    try:
        df.to_excel(EXCEL_OUTPUT, index=False, engine='openpyxl')
        print(f"\n✓ Successfully exported {len(data_rows)} satisfaction ratings to:")
        print(f"  {EXCEL_OUTPUT}")
        print(f"\nColumns exported:")
        for col in df.columns:
            print(f"  - {col}")
    except Exception as e:
        print(f"\n❌ Error exporting to Excel: {e}")
        print("   Make sure openpyxl is installed: pip install openpyxl")
        conn.close()
        return
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("EXPORT SUMMARY")
    print("=" * 70)
    print(f"Total records: {len(data_rows)}")
    print(f"Volunteer responses: {len([r for r in data_rows if r['Respondent Type'] == 'Volunteer'])}")
    print(f"Beneficiary responses: {len([r for r in data_rows if r['Respondent Type'] == 'Beneficiary'])}")
    print(f"Excel file: {EXCEL_OUTPUT}")
    print("=" * 70)

if __name__ == "__main__":
    export_satisfaction_ratings_to_excel()

















