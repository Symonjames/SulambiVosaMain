#!/usr/bin/env python3
"""Test the satisfaction analytics API to see what it returns"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

# Simulate the getSatisfactionAnalytics function
def test_satisfaction_analytics(year=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get evaluations with event dates
    query = """
        SELECT e.id, e.requirementId, e.criteria, e.finalized, e.q13, e.q14, e.comment, e.recommendations,
               r.eventId, r.type,
               CASE 
                   WHEN r.type = 'internal' THEN ei.durationStart
                   ELSE ee.durationStart
               END as eventDate
        FROM evaluation e
        INNER JOIN requirements r ON e.requirementId = r.id
        LEFT JOIN internalEvents ei ON r.eventId = ei.id AND r.type = 'internal'
        LEFT JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
        WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    """
    
    cursor.execute(query)
    evaluation_rows = cursor.fetchall()
    
    print(f"Total evaluations found: {len(evaluation_rows)}")
    
    satisfactionBySemester = {}
    issues = {}
    volunteerSatisfaction = []
    beneficiarySatisfaction = []
    
    for row in evaluation_rows:
        eval_id, req_id, criteria_str, finalized, q13, q14, comment, recommendations, event_id, event_type, event_date = row
        
        if not finalized or not criteria_str:
            continue
            
        try:
            # Parse criteria
            criteria = criteria_str
            if isinstance(criteria, str):
                try:
                    criteria = eval(criteria) if criteria.startswith('{') else json.loads(criteria)
                except:
                    criteria = {}
            
            # Extract semester from event date
            if event_date:
                evalDate = datetime.fromtimestamp(event_date / 1000)
            else:
                evalDate = datetime.now()
            semester = f"{evalDate.year}-{math.ceil(evalDate.month / 6)}"
            
            print(f"  Evaluation {eval_id}: semester={semester}, criteria keys={list(criteria.keys()) if isinstance(criteria, dict) else 'not dict'}")
            
            # Filter by year if specified
            if year and not semester.startswith(str(year)):
                continue
            
            if semester not in satisfactionBySemester:
                satisfactionBySemester[semester] = {
                    'volunteers': [],
                    'beneficiaries': [],
                    'overall': []
                }
            
            # Extract satisfaction scores
            satisfaction_score = 4.0
            if isinstance(criteria, dict):
                if 'overall' in criteria:
                    satisfaction_score = criteria['overall']
                elif 'satisfaction' in criteria:
                    satisfaction_score = criteria['satisfaction']
                elif 'rating' in criteria:
                    satisfaction_score = criteria['rating']
            
            satisfactionBySemester[semester]['volunteers'].append(satisfaction_score)
            volunteerSatisfaction.append(satisfaction_score)
            satisfactionBySemester[semester]['overall'].append(satisfaction_score)
            
        except Exception as e:
            print(f"  Error processing evaluation {eval_id}: {e}")
            continue
    
    # Calculate semester averages
    satisfactionData = []
    for semester, data in satisfactionBySemester.items():
        if data['overall']:
            overall_avg = sum(data['overall']) / len(data['overall'])
            volunteer_avg = sum(data['volunteers']) / len(data['volunteers']) if data['volunteers'] else overall_avg
            
            satisfactionData.append({
                'semester': semester,
                'score': round(overall_avg, 1),
                'volunteers': round(volunteer_avg, 1),
                'beneficiaries': round(volunteer_avg, 1)  # Using volunteer as fallback
            })
    
    satisfactionData.sort(key=lambda x: x['semester'])
    
    print(f"\nResults for year={year}:")
    print(f"  Semesters found: {list(satisfactionBySemester.keys())}")
    print(f"  Satisfaction data: {json.dumps(satisfactionData, indent=2)}")
    
    conn.close()
    return satisfactionData

import math
test_satisfaction_analytics(year="2025")

















