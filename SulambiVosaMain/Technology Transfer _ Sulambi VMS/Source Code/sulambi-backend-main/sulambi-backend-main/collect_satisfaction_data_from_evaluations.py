"""
Collect satisfaction rating data from existing evaluations and populate satisfactionSurveys table
This migrates existing evaluation data to the satisfactionSurveys format
"""

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

def collect_satisfaction_data():
    """Collect satisfaction data from evaluations table and populate satisfactionSurveys"""
    print("=" * 70)
    print("COLLECTING SATISFACTION RATINGS FROM EVALUATIONS")
    print("=" * 70)
    
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
    
    # Get all evaluations with their requirement and event info
    cursor.execute("""
        SELECT 
            e.id,
            e.requirementId,
            e.criteria,
            e.q13,
            e.q14,
            e.comment,
            e.recommendations,
            e.finalized,
            r.eventId,
            r.type as eventType,
            r.email,
            r.fullname,
            CASE 
                WHEN r.type = 'internal' THEN ei.durationStart
                ELSE ee.durationStart
            END as eventDate
        FROM evaluation e
        INNER JOIN requirements r ON e.requirementId = r.id
        LEFT JOIN internalEvents ei ON r.eventId = ei.id AND r.type = 'internal'
        LEFT JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
        WHERE e.finalized = 1
        AND (e.q13 IS NOT NULL OR e.q14 IS NOT NULL OR e.comment IS NOT NULL)
    """)
    
    evaluations = cursor.fetchall()
    print(f"\nFound {len(evaluations)} evaluations with data")
    
    if len(evaluations) == 0:
        print("No evaluation data found to migrate")
        conn.close()
        return
    
    inserted = 0
    skipped = 0
    
    for eval_row in evaluations:
        (eval_id, req_id, criteria_str, q13, q14, comment, recommendations, 
         finalized, event_id, event_type, email, fullname, event_date) = eval_row
        
        # Check if already exists
        cursor.execute("""
            SELECT id FROM satisfactionSurveys 
            WHERE requirementId = ? AND respondentEmail = ?
        """, (req_id, email))
        
        if cursor.fetchone():
            skipped += 1
            continue
        
        # Parse criteria to extract ratings
        import json
        criteria = {}
        if criteria_str:
            try:
                if isinstance(criteria_str, str):
                    criteria = eval(criteria_str) if criteria_str.startswith('{') else json.loads(criteria_str)
                else:
                    criteria = criteria_str
            except:
                criteria = {}
        
        # Extract ratings from criteria
        overall_satisfaction = 0
        organization_rating = 0
        communication_rating = 0
        venue_rating = 0
        materials_rating = 0
        support_rating = 0
        
        # Map criteria to ratings (1-5 scale)
        rating_map = {
            "Excellent": 5,
            "Very Satisfactory": 4,
            "Satisfactory": 3,
            "Fair": 2,
            "Poor": 1
        }
        
        if isinstance(criteria, dict):
            overall_satisfaction = rating_map.get(criteria.get('overall', ''), 0)
            organization_rating = rating_map.get(criteria.get('appropriateness', ''), 0)
            communication_rating = rating_map.get(criteria.get('expectations', ''), 0)
            materials_rating = rating_map.get(criteria.get('materials', ''), 0)
            support_rating = rating_map.get(criteria.get('session', ''), 0)
        
        # Use q13/q14 as overall if criteria doesn't have it
        if overall_satisfaction == 0:
            if q13:
                try:
                    overall_satisfaction = float(q13)
                except:
                    pass
            elif q14:
                try:
                    overall_satisfaction = float(q14)
                except:
                    pass
        
        # Determine respondent type
        respondent_type = "Volunteer"
        if q14 and not q13:
            respondent_type = "Beneficiary"
        elif q13 and q14:
            respondent_type = "Both"  # Has both ratings
        
        # Convert q13 and q14 to numbers
        volunteer_rating = None
        beneficiary_rating = None
        
        if q13:
            try:
                volunteer_rating = float(q13)
            except:
                pass
        
        if q14:
            try:
                beneficiary_rating = float(q14)
            except:
                pass
        
        # Use event date or current time for submittedAt
        if event_date:
            submitted_at = int(event_date)
        else:
            submitted_at = int(datetime.now().timestamp() * 1000)
        
        # Insert into satisfactionSurveys
        try:
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
                event_id, event_type, req_id, respondent_type, email, fullname,
                overall_satisfaction, volunteer_rating, beneficiary_rating,
                organization_rating, communication_rating, venue_rating, materials_rating, support_rating,
                q13, q14, comment, recommendations,
                None, None, comment,  # Use comment as positiveAspects for now
                submitted_at, finalized
            ))
            inserted += 1
        except Exception as e:
            print(f"Error inserting evaluation {eval_id}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)
    print(f"✓ Inserted: {inserted} satisfaction surveys")
    print(f"⚠ Skipped (already exists): {skipped}")
    print(f"Total processed: {len(evaluations)}")
    print("=" * 70)
    
    return inserted

if __name__ == "__main__":
    collect_satisfaction_data()

















