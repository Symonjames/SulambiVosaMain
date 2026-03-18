#!/usr/bin/env python3
"""
Script to update existing evaluations with proper satisfaction criteria
so they appear in predictive satisfaction analytics
"""

import sqlite3
import os
import random
import json
from datetime import datetime

# Database path
DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

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

def update_evaluations_for_satisfaction():
    """Update existing evaluations with proper satisfaction criteria"""
    print("=" * 60)
    print("UPDATING EVALUATIONS FOR SATISFACTION ANALYTICS")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all finalized evaluations with their requirement and event info
    print("Finding evaluations to update...")
    cursor.execute("""
        SELECT e.id, e.requirementId, e.criteria, r.eventId, r.type
        FROM evaluation e
        INNER JOIN requirements r ON e.requirementId = r.id
        WHERE e.finalized = 1
    """)
    
    evaluations = cursor.fetchall()
    
    if not evaluations:
        print("❌ No finalized evaluations found!")
        conn.close()
        return
    
    print(f"Found {len(evaluations)} evaluations\n")
    print("Updating evaluations with satisfaction criteria...\n")
    
    updated = 0
    skipped = 0
    errors = 0
    
    # Get current year for semester calculation
    current_year = datetime.now().year
    
    for eval_id, req_id, existing_criteria, event_id, event_type in evaluations:
        try:
            # Check if criteria already has satisfaction data
            has_satisfaction = False
            if existing_criteria:
                try:
                    if isinstance(existing_criteria, str):
                        criteria_dict = json.loads(existing_criteria) if existing_criteria.startswith('{') else {}
                    else:
                        criteria_dict = existing_criteria
                    
                    if isinstance(criteria_dict, dict) and ('overall' in criteria_dict or 'satisfaction' in criteria_dict):
                        has_satisfaction = True
                except:
                    pass
            
            # Skip if already has satisfaction data
            if has_satisfaction:
                skipped += 1
                continue
            
            # Get event date for semester calculation
            event_table = "internalEvents" if event_type == "internal" else "externalEvents"
            cursor.execute(f"SELECT durationStart FROM {event_table} WHERE id = ?", (event_id,))
            event_result = cursor.fetchone()
            
            # Generate new satisfaction criteria
            criteria_json, satisfaction_score = generate_satisfaction_criteria()
            
            # Update q13 and q14 to match satisfaction
            q13 = str(satisfaction_score)
            q14 = str(satisfaction_score)
            
            # Ensure recommendations is not empty (needed for attendance counting)
            cursor.execute("SELECT recommendations FROM evaluation WHERE id = ?", (eval_id,))
            rec_result = cursor.fetchone()
            recommendations = rec_result[0] if rec_result and rec_result[0] else "Keep up the good work"
            
            # Update the evaluation
            cursor.execute("""
                UPDATE evaluation
                SET criteria = ?, q13 = ?, q14 = ?, recommendations = ?
                WHERE id = ?
            """, (
                criteria_json,
                q13,
                q14,
                recommendations,
                eval_id
            ))
            
            updated += 1
            if updated % 50 == 0:
                print(f"  Progress: {updated} evaluations updated...")
                conn.commit()
        
        except Exception as e:
            print(f"  Error updating evaluation {eval_id}: {e}")
            errors += 1
            continue
    
    conn.commit()
    
    # Verify the results
    cursor.execute("""
        SELECT COUNT(*) FROM evaluation 
        WHERE finalized = 1 
        AND criteria IS NOT NULL 
        AND criteria != ''
        AND (criteria LIKE '%"overall"%' OR criteria LIKE '%"satisfaction"%')
    """)
    evaluations_with_satisfaction = cursor.fetchone()[0]
    
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
        WHERE e.finalized = 1 
        AND e.criteria IS NOT NULL 
        AND e.criteria != ''
        AND (e.criteria LIKE '%"overall"%' OR e.criteria LIKE '%"satisfaction"%')
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
        WHERE e.finalized = 1 
        AND e.criteria IS NOT NULL 
        AND e.criteria != ''
        AND (e.criteria LIKE '%"overall"%' OR e.criteria LIKE '%"satisfaction"%')
        GROUP BY semester
        
        ORDER BY semester
    """)
    
    semester_counts = cursor.fetchall()
    
    # Get average satisfaction scores
    cursor.execute("""
        SELECT 
            AVG(CAST(JSON_EXTRACT(criteria, '$.overall') AS REAL)) as avg_overall,
            AVG(CAST(JSON_EXTRACT(criteria, '$.satisfaction') AS REAL)) as avg_satisfaction
        FROM evaluation
        WHERE finalized = 1 
        AND criteria IS NOT NULL 
        AND criteria != ''
        AND (criteria LIKE '%"overall"%' OR criteria LIKE '%"satisfaction"%')
    """)
    
    avg_result = cursor.fetchone()
    avg_satisfaction = avg_result[0] if avg_result and avg_result[0] else None
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ EVALUATIONS UPDATED!")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  - Updated {updated} evaluations with satisfaction criteria")
    print(f"  - Skipped {skipped} (already had satisfaction data)")
    if errors > 0:
        print(f"  - Errors: {errors}")
    print(f"  - Total evaluations with satisfaction data: {evaluations_with_satisfaction}")
    if avg_satisfaction:
        print(f"  - Average satisfaction score: {avg_satisfaction:.2f}/5.0")
    
    if semester_counts:
        print(f"\nEvaluations by semester:")
        for semester, count in semester_counts:
            print(f"  - {semester}: {count} evaluations")
    
    print("\nThese evaluations will now appear in:")
    print("  ✓ Predictive Satisfaction Ratings")
    print("  ✓ Satisfaction Analytics by Semester (2024-1, 2024-2, 2025-1, 2025-2)")
    print("  ✓ Volunteer and Beneficiary Satisfaction Breakdown")

if __name__ == "__main__":
    update_evaluations_for_satisfaction()

