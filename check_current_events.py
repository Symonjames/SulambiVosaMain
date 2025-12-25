#!/usr/bin/env python3
"""
Script to check current events in the system
"""

import sqlite3
import os

def check_current_events():
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
        print("CURRENT EVENTS IN SYSTEM")
        print("=" * 80)
        
        # Check External Events
        print("\n📅 EXTERNAL EVENTS:")
        print("-" * 50)
        external_query = """
        SELECT 
            id,
            title,
            status,
            orgInvolved,
            location,
            durationStart,
            durationEnd
        FROM externalEvents 
        ORDER BY id
        """
        
        cursor.execute(external_query)
        external_events = cursor.fetchall()
        
        if len(external_events) == 0:
            print("No external events found.")
        else:
            for event in external_events:
                event_id, title, status, org, location, start, end = event
                print(f"ID: {event_id} | {title}")
                print(f"     Status: {status} | Org: {org}")
                print(f"     Location: {location}")
                print(f"     Duration: {start} to {end}")
                print()
        
        # Check Internal Events
        print("\n📅 INTERNAL EVENTS:")
        print("-" * 50)
        internal_query = """
        SELECT 
            id,
            title,
            status,
            partner,
            venue,
            durationStart,
            durationEnd
        FROM internalEvents 
        ORDER BY id
        """
        
        cursor.execute(internal_query)
        internal_events = cursor.fetchall()
        
        if len(internal_events) == 0:
            print("No internal events found.")
        else:
            for event in internal_events:
                event_id, title, status, partner, venue, start, end = event
                print(f"ID: {event_id} | {title}")
                print(f"     Status: {status} | Partner: {partner}")
                print(f"     Venue: {venue}")
                print(f"     Duration: {start} to {end}")
                print()
        
        # Check Requirements (Event Participations)
        print("\n👥 EVENT PARTICIPATIONS (Requirements):")
        print("-" * 50)
        req_query = """
        SELECT 
            r.id,
            r.eventId,
            r.type,
            r.fullname,
            r.age,
            r.accepted,
            e.title as eventTitle
        FROM requirements r
        LEFT JOIN externalEvents e ON r.eventId = e.id AND r.type = 'external'
        LEFT JOIN internalEvents i ON r.eventId = i.id AND r.type = 'internal'
        ORDER BY r.eventId, r.type
        """
        
        cursor.execute(req_query)
        requirements = cursor.fetchall()
        
        if len(requirements) == 0:
            print("No event participations found.")
        else:
            for req in requirements:
                req_id, event_id, event_type, name, age, accepted, event_title = req
                status = "ACCEPTED" if accepted else "PENDING"
                print(f"Requirement ID: {req_id}")
                print(f"     Event ID: {event_id} ({event_type.upper()})")
                print(f"     Event Title: {event_title}")
                print(f"     Volunteer: {name} (Age: {age})")
                print(f"     Status: {status}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_current_events()
