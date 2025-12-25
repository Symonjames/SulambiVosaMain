#!/usr/bin/env python3
"""
Script to add evaluations with satisfaction data for predictive satisfaction analytics
This creates evaluations for existing requirements so satisfaction analytics will show data
"""

import sqlite3
import os
import random
import json
from datetime import datetime, timedelta

# Database path
# Try to get DB_PATH from environment (backend's .env), otherwise use default
from dotenv import load_dotenv
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    # If relative path, make it relative to backend directory
    DB_PATH = os.path.join(backend_dir, DB_PATH)

def generate_satisfaction_criteria():
    """Generate realistic satisfaction criteria data"""
    # Generate satisfaction score (1-5 scale, weighted towards positive)
    satisfaction_scores = [4, 4, 4, 5, 5, 3, 4, 5, 4, 4, 3, 5, 4, 4, 5, 3, 4, 4, 5, 4]  # Mostly 4-5, some 3s
    overall_satisfaction = random.choice(satisfaction_scores)
    
    # Generate detailed ratings
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
    
    # Generate comments (optional, some have comments)
    comments = [
        "",
        "",
        "",
        "Great event, well organized",
        "Enjoyed participating",
        "Very informative and helpful",
        "Good communication throughout",
        "Would participate again",
        "Excellent coordination",
        "Helpful for community",
        "Well planned activities",
        "Good venue and facilities"
    ]
    
    comment = random.choice(comments)
    
    # Build criteria dictionary
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

def add_satisfaction_evaluations():
    """Add evaluations with satisfaction data for existing requirements"""
    print("=" * 60)
    print("ADDING SATISFACTION EVALUATIONS FOR ANALYTICS")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if evaluation table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='evaluation'
    """)
    
    if not cursor.fetchone():
        print("❌ Evaluation table does not exist!")
        conn.close()
        return
    
    # Get all accepted requirements without evaluations
    print("Finding requirements without evaluations...")
    cursor.execute("""
        SELECT r.id, r.eventId, r.type, r.email
        FROM requirements r
        WHERE r.accepted = 1
        AND NOT EXISTS (
            SELECT 1 FROM evaluation e 
            WHERE e.requirementId = r.id AND e.finalized = 1
        )
        LIMIT 200
    """)
    
    requirements = cursor.fetchall()
    
    if not requirements:
        print("✓ All requirements already have evaluations!")
        conn.close()
        return
    
    print(f"Found {len(requirements)} requirements without evaluations\n")
    print("Adding evaluations with satisfaction data...\n")
    
    added = 0
    errors = 0
    
    # Get current year for semester calculation
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Generate evaluations for different semesters (spread across 2024 and 2025)
    semesters = [
        (2024, 1), (2024, 2),  # 2024-1, 2024-2
        (2025, 1), (2025, 2)   # 2025-1, 2025-2
    ]
    
    for req_id, event_id, event_type, email in requirements:
        try:
            # Generate satisfaction criteria
            criteria_json, satisfaction_score = generate_satisfaction_criteria()
            
            # Note: Evaluation table doesn't have createdAt, so we'll use event date for semester calculation
            
            # Generate q13 and q14 (satisfaction components)
            q13 = str(satisfaction_score)
            q14 = str(satisfaction_score)
            
            # Generate comments and recommendations
            comments = [
                "Great event!",
                "Well organized and informative",
                "Enjoyed the experience",
                "Very helpful for the community",
                "Good coordination and communication",
                "Would participate again",
                "Excellent planning",
                "Helpful and meaningful activity"
            ]
            
            comment = random.choice(comments)
            recommendations = random.choice([
                "Keep up the good work",
                "Continue organizing similar events",
                "More events like this would be great",
                "Well done!",
                "Excellent initiative"
            ])
            
            # Insert evaluation (no createdAt column in table)
            cursor.execute("""
                INSERT INTO evaluation (
                    requirementId, criteria, q13, q14, comment, recommendations, finalized
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                req_id,
                criteria_json,
                q13,
                q14,
                comment,
                recommendations,  # Non-empty recommendations to count as attended
                1  # finalized = 1
            ))
            
            added += 1
            if added % 50 == 0:
                print(f"  Progress: {added}/{len(requirements)} evaluations added...")
                conn.commit()
        
        except sqlite3.IntegrityError as e:
            # Skip duplicates
            errors += 1
            continue
        except Exception as e:
            print(f"  Error adding evaluation for requirement {req_id}: {e}")
            errors += 1
            continue
    
    conn.commit()
    
    # Verify the results
    cursor.execute("""
        SELECT COUNT(*) FROM evaluation 
        WHERE finalized = 1 AND criteria IS NOT NULL AND criteria != ''
    """)
    total_evaluations = cursor.fetchone()[0]
    
    # Check evaluations by semester using event dates
    cursor.execute("""
        SELECT 
            CASE 
                WHEN CAST(strftime('%m', datetime(ei.durationStart/1000, 'unixepoch')) AS INTEGER) <= 6 THEN 
                    strftime('%Y', datetime(ei.durationStart/1000, 'unixepoch')) || '-1'
                ELSE 
                    strftime('%Y', datetime(ei.durationStart/1000, 'unixepoch')) || '-2'
            END as semester,
            COUNT(*) as count
        FROM evaluation e
        INNER JOIN requirements r ON e.requirementId = r.id
        INNER JOIN internalEvents ei ON r.eventId = ei.id AND r.type = 'internal'
        WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
        GROUP BY semester
        
        UNION ALL
        
        SELECT 
            CASE 
                WHEN CAST(strftime('%m', datetime(ee.durationStart/1000, 'unixepoch')) AS INTEGER) <= 6 THEN 
                    strftime('%Y', datetime(ee.durationStart/1000, 'unixepoch')) || '-1'
                ELSE 
                    strftime('%Y', datetime(ee.durationStart/1000, 'unixepoch')) || '-2'
            END as semester,
            COUNT(*) as count
        FROM evaluation e
        INNER JOIN requirements r ON e.requirementId = r.id
        INNER JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
        WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
        GROUP BY semester
        
        ORDER BY semester
    """)
    
    semester_counts = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ SATISFACTION EVALUATIONS ADDED!")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  - Added {added} evaluations with satisfaction data")
    if errors > 0:
        print(f"  - Errors: {errors}")
    print(f"  - Total finalized evaluations: {total_evaluations}")
    
    if semester_counts:
        print(f"\nEvaluations by semester:")
        for semester, count in semester_counts:
            print(f"  - {semester}: {count} evaluations")
    
    print("\nThese evaluations will now appear in:")
    print("  ✓ Predictive Satisfaction Ratings")
    print("  ✓ Satisfaction Analytics by Semester")
    print("  ✓ Volunteer and Beneficiary Satisfaction Breakdown")

if __name__ == "__main__":
    add_satisfaction_evaluations()

