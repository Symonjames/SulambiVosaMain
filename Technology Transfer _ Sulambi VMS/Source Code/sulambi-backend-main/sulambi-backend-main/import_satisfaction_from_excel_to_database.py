"""
Import satisfaction ratings from Excel file into the database
This will make the data appear in the Predictive Satisfaction Ratings analytics
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

EXCEL_FILE = os.path.join("data", "satisfaction-ratings.xlsx")

def import_satisfaction_to_database():
    """Import satisfaction ratings from Excel to database"""
    print("=" * 70)
    print("IMPORTING SATISFACTION RATINGS FROM EXCEL TO DATABASE")
    print("=" * 70)
    
    # Read Excel file
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Excel file not found: {EXCEL_FILE}")
        return
    
    print(f"\nReading Excel file: {EXCEL_FILE}")
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"✓ Found {len(df)} records in Excel file")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure satisfactionSurveys table exists
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
    
    # Clear existing data (optional - comment out if you want to keep existing)
    cursor.execute("DELETE FROM satisfactionSurveys")
    conn.commit()
    print("✓ Cleared existing satisfaction surveys")
    
    inserted = 0
    skipped = 0
    
    print(f"\nImporting {len(df)} records...")
    
    for index, row in df.iterrows():
        try:
            # Extract data from Excel row
            event_id = int(row.get("Event ID", 0)) if pd.notna(row.get("Event ID")) else 0
            event_type = str(row.get("Event Type", "internal")).strip()
            req_id = str(row.get("Requirement ID", "")).strip() if pd.notna(row.get("Requirement ID")) else f"REQ-{random.randint(10000, 99999)}"
            respondent_type = str(row.get("Respondent Type", "")).strip()
            email = str(row.get("Respondent Email", "")).strip()
            name = str(row.get("Respondent Name", "")).strip()
            
            if not email or not name or not event_id:
                skipped += 1
                continue
            
            # Ratings
            overall = float(row.get("Overall Satisfaction (1-5)", 0)) if pd.notna(row.get("Overall Satisfaction (1-5)")) else 0
            volunteer_rating = float(row.get("Volunteer Rating (1-5)", 0)) if pd.notna(row.get("Volunteer Rating (1-5)")) and str(row.get("Volunteer Rating (1-5)")) != "" else None
            beneficiary_rating = float(row.get("Beneficiary Rating (1-5)", 0)) if pd.notna(row.get("Beneficiary Rating (1-5)")) and str(row.get("Beneficiary Rating (1-5)")) != "" else None
            organization = float(row.get("Organization Rating (1-5)", 0)) if pd.notna(row.get("Organization Rating (1-5)")) else 0
            communication = float(row.get("Communication Rating (1-5)", 0)) if pd.notna(row.get("Communication Rating (1-5)")) else 0
            venue = float(row.get("Venue Rating (1-5)", 0)) if pd.notna(row.get("Venue Rating (1-5)")) else 0
            materials = float(row.get("Materials Rating (1-5)", 0)) if pd.notna(row.get("Materials Rating (1-5)")) else 0
            support = float(row.get("Support Rating (1-5)", 0)) if pd.notna(row.get("Support Rating (1-5)")) else 0
            
            # Text fields
            q13 = str(row.get("Q13 (Volunteer Score)", "")).strip() if pd.notna(row.get("Q13 (Volunteer Score)")) and str(row.get("Q13 (Volunteer Score)")) != "" else None
            q14 = str(row.get("Q14 (Beneficiary Score)", "")).strip() if pd.notna(row.get("Q14 (Beneficiary Score)")) and str(row.get("Q14 (Beneficiary Score)")) != "" else None
            comment = str(row.get("Comment", "")).strip() if pd.notna(row.get("Comment")) else ""
            recommendations = str(row.get("Recommendations", "")).strip() if pd.notna(row.get("Recommendations")) else ""
            
            # Would recommend
            would_recommend_str = str(row.get("Would Recommend", "")).strip()
            would_recommend = True if would_recommend_str.lower() == "yes" else (False if would_recommend_str.lower() == "no" else None)
            
            areas_improvement = str(row.get("Areas for Improvement", "")).strip() if pd.notna(row.get("Areas for Improvement")) and str(row.get("Areas for Improvement")) != "" else None
            positive_aspects = str(row.get("Positive Aspects", "")).strip() if pd.notna(row.get("Positive Aspects")) and str(row.get("Positive Aspects")) != "" else None
            
            # Submitted date
            submitted_str = str(row.get("Submitted At", ""))
            if pd.notna(row.get("Submitted At")) and submitted_str:
                try:
                    submitted_date = datetime.strptime(submitted_str, "%Y-%m-%d %H:%M:%S")
                    submitted_at = int(submitted_date.timestamp() * 1000)
                except:
                    submitted_at = int(datetime.now().timestamp() * 1000)
            else:
                submitted_at = int(datetime.now().timestamp() * 1000)
            
            finalized = True if str(row.get("Finalized", "")).strip().lower() == "yes" else False
            
            # Insert into database
            cursor.execute("""
                INSERT INTO satisfactionSurveys (
                    eventId, eventType, requirementId, respondentType, respondentEmail, respondentName,
                    overallSatisfaction, volunteerRating, beneficiaryRating,
                    organizationRating, communicationRating, venueRating, materialsRating, supportRating,
                    q13, q14, comment, recommendations,
                    wouldRecommend, areasForImprovement, positiveAspects,
                    submittedAt, finalized
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, event_type, req_id, respondent_type, email, name,
                overall, volunteer_rating, beneficiary_rating,
                organization, communication, venue, materials, support,
                q13, q14, comment, recommendations,
                would_recommend, areas_improvement, positive_aspects,
                submitted_at, finalized
            ))
            
            inserted += 1
            
            if inserted % 10 == 0:
                conn.commit()
                print(f"   Processed {inserted} records...")
        
        except Exception as e:
            print(f"   ❌ Error processing row {index}: {e}")
            skipped += 1
            continue
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"✓ Successfully imported: {inserted} satisfaction surveys")
    print(f"⚠ Skipped: {skipped} records")
    print(f"Total in database: {inserted}")
    print("=" * 70)
    print("\n✓ Data is now in the database and will appear in Predictive Satisfaction Ratings analytics!")
    print("=" * 70)
    
    return inserted

if __name__ == "__main__":
    import random
    import_satisfaction_to_database()

















