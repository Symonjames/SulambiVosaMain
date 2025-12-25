#!/usr/bin/env python3
"""
Script to check if new volunteer data is being recorded properly
"""

import sqlite3
import os

def check_volunteer_data():
    # Get the database path
    db_path = "app/database/database.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("CURRENT VOLUNTEER DATA CHECK")
        print("=" * 80)
        
        # Check all requirements (volunteer participations)
        print("\n👥 ALL VOLUNTEER REQUIREMENTS:")
        print("-" * 50)
        req_query = """
        SELECT 
            r.id,
            r.eventId,
            r.type,
            r.fullname,
            r.email,
            r.age,
            r.sex,
            r.accepted,
            CASE 
                WHEN r.type = 'external' THEN e.title
                WHEN r.type = 'internal' THEN i.title
            END as eventTitle
        FROM requirements r
        LEFT JOIN externalEvents e ON r.eventId = e.id AND r.type = 'external'
        LEFT JOIN internalEvents i ON r.eventId = i.id AND r.type = 'internal'
        ORDER BY r.id DESC
        """
        
        cursor.execute(req_query)
        requirements = cursor.fetchall()
        
        if len(requirements) == 0:
            print("No volunteer requirements found.")
        else:
            print(f"Found {len(requirements)} volunteer requirement(s):")
            for req in requirements:
                req_id, event_id, event_type, name, email, age, sex, accepted, event_title = req
                status = "ACCEPTED" if accepted else "PENDING"
                print(f"   - {name} (Age: {age}, Sex: {sex})")
                print(f"     Email: {email}")
                print(f"     Event: {event_title} (ID: {event_id}, {event_type.upper()})")
                print(f"     Status: {status}")
                print(f"     Requirement ID: {req_id}")
                print()
        
        # Check current events
        print("\n📅 CURRENT EVENTS:")
        print("-" * 50)
        
        # External Events
        cursor.execute("SELECT id, title, status FROM externalEvents")
        external_events = cursor.fetchall()
        
        if len(external_events) == 0:
            print("No external events found.")
        else:
            print("External Events:")
            for event in external_events:
                event_id, title, status = event
                print(f"   - ID: {event_id} | {title} | Status: {status}")
        
        # Internal Events
        cursor.execute("SELECT id, title, status FROM internalEvents")
        internal_events = cursor.fetchall()
        
        if len(internal_events) == 0:
            print("No internal events found.")
        else:
            print("Internal Events:")
            for event in internal_events:
                event_id, title, status = event
                print(f"   - ID: {event_id} | {title} | Status: {status}")
        
        # Check analytics data specifically
        print("\n📊 ANALYTICS DATA:")
        print("-" * 50)
        
        # Age groups
        age_query = """
        SELECT age, COUNT(*) as count
        FROM requirements 
        WHERE accepted = 1
        GROUP BY age
        ORDER BY age
        """
        
        cursor.execute(age_query)
        age_groups = cursor.fetchall()
        
        if len(age_groups) == 0:
            print("No age group data found (no accepted requirements).")
        else:
            print("Age Groups:")
            for age, count in age_groups:
                print(f"   - Age {age}: {count} volunteer(s)")
        
        # Sex groups
        sex_query = """
        SELECT sex, COUNT(*) as count
        FROM requirements 
        WHERE accepted = 1
        GROUP BY sex
        ORDER BY sex
        """
        
        cursor.execute(sex_query)
        sex_groups = cursor.fetchall()
        
        if len(sex_groups) == 0:
            print("No sex group data found (no accepted requirements).")
        else:
            print("Sex Groups:")
            for sex, count in sex_groups:
                print(f"   - {sex}: {count} volunteer(s)")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_volunteer_data()
