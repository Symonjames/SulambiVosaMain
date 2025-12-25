"""
Populate volunteerParticipationHistory table from requirements and evaluations
This creates semester-by-semester participation records for each volunteer
"""

import sqlite3
import os
import math
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

def populate_volunteer_participation_history():
    """Populate volunteer participation history from requirements and evaluations"""
    print("=" * 70)
    print("POPULATING VOLUNTEER PARTICIPATION HISTORY")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    print("\n1. Creating volunteerParticipationHistory table if needed...")
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS volunteerParticipationHistory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteerEmail STRING NOT NULL,
        volunteerName STRING NOT NULL,
        membershipId INTEGER,
        
        -- Semester Information
        semester STRING NOT NULL,
        semesterYear INTEGER NOT NULL,
        semesterNumber INTEGER NOT NULL,
        
        -- Participation Metrics
        eventsJoined INTEGER DEFAULT 0,
        eventsAttended INTEGER DEFAULT 0,
        eventsDropped INTEGER DEFAULT 0,
        attendanceRate REAL DEFAULT 0,
        
        -- Event Details
        firstEventDate INTEGER,
        lastEventDate INTEGER,
        daysActiveInSemester INTEGER DEFAULT 0,
        
        -- Consistency Metrics
        participationConsistency STRING DEFAULT 'Regular',
        engagementLevel STRING DEFAULT 'Active',
        
        -- Timestamps
        calculatedAt INTEGER NOT NULL,
        lastUpdated INTEGER NOT NULL,
        
        -- Indexes for faster queries
        UNIQUE(volunteerEmail, semester)
      )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_volunteer_email ON volunteerParticipationHistory(volunteerEmail)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_semester ON volunteerParticipationHistory(semester)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_event_date ON volunteerParticipationHistory(lastEventDate)")
    conn.commit()
    print("   ✓ Table created/verified")
    
    # Clear existing history (optional - comment out if you want to keep existing)
    print("\n2. Clearing existing participation history...")
    cursor.execute("DELETE FROM volunteerParticipationHistory")
    conn.commit()
    print("   ✓ Cleared existing history")
    
    # Get all events with their dates
    print("\n3. Getting events and grouping by semester...")
    cursor.execute("""
        SELECT id, title, durationStart, durationEnd, 'internal' as type
        FROM internalEvents
        WHERE status IN ('accepted', 'completed')
        UNION ALL
        SELECT id, title, durationStart, durationEnd, 'external' as type
        FROM externalEvents
        WHERE status IN ('accepted', 'completed')
        ORDER BY durationStart
    """)
    all_events = cursor.fetchall()
    
    if not all_events:
        print("   ❌ No events found")
        conn.close()
        return
    
    # Group events by semester
    semester_events = {}
    for event_id, event_title, event_start, event_end, event_type in all_events:
        if event_start:
            event_date = datetime.fromtimestamp(event_start / 1000)
            semester_year = event_date.year
            semester_num = math.ceil(event_date.month / 6)  # 1 for Jan-Jun, 2 for Jul-Dec
            semester_key = f"{semester_year}-{semester_num}"
            
            if semester_key not in semester_events:
                semester_events[semester_key] = []
            semester_events[semester_key].append((event_id, event_type, event_start, event_end))
    
    print(f"   ✓ Found {len(semester_events)} semesters: {list(semester_events.keys())}")
    
    # Process each semester
    print("\n4. Processing participation data by semester...")
    total_records = 0
    
    for semester, events in sorted(semester_events.items()):
        semester_year, semester_num = semester.split('-')
        semester_year_int = int(semester_year)
        semester_num_int = int(semester_num)
        
        event_ids_internal = [e[0] for e in events if e[1] == 'internal']
        event_ids_external = [e[0] for e in events if e[1] == 'external']
        
        # Get all volunteers who joined events in this semester
        if event_ids_internal and event_ids_external:
            placeholders_int = ','.join(['?' for _ in event_ids_internal])
            placeholders_ext = ','.join(['?' for _ in event_ids_external])
            cursor.execute(f"""
                SELECT DISTINCT r.email, r.fullname, m.id as membershipId
                FROM requirements r
                LEFT JOIN membership m ON r.email = m.email
                WHERE r.accepted = 1
                AND ((r.type = 'internal' AND r.eventId IN ({placeholders_int}))
                     OR (r.type = 'external' AND r.eventId IN ({placeholders_ext})))
            """, event_ids_internal + event_ids_external)
        elif event_ids_internal:
            placeholders = ','.join(['?' for _ in event_ids_internal])
            cursor.execute(f"""
                SELECT DISTINCT r.email, r.fullname, m.id as membershipId
                FROM requirements r
                LEFT JOIN membership m ON r.email = m.email
                WHERE r.accepted = 1
                AND r.type = 'internal' AND r.eventId IN ({placeholders})
            """, event_ids_internal)
        elif event_ids_external:
            placeholders = ','.join(['?' for _ in event_ids_external])
            cursor.execute(f"""
                SELECT DISTINCT r.email, r.fullname, m.id as membershipId
                FROM requirements r
                LEFT JOIN membership m ON r.email = m.email
                WHERE r.accepted = 1
                AND r.type = 'external' AND r.eventId IN ({placeholders})
            """, event_ids_external)
        else:
            continue
        
        volunteers = cursor.fetchall()
        
        for email, fullname, membership_id in volunteers:
            if not email or not fullname:
                continue
            
            # Count events joined
            if event_ids_internal and event_ids_external:
                placeholders_int = ','.join(['?' for _ in event_ids_internal])
                placeholders_ext = ','.join(['?' for _ in event_ids_external])
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT r.id) as joined_count,
                           COUNT(DISTINCT CASE WHEN e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != '' THEN r.id END) as attended_count,
                           MIN(CASE 
                               WHEN r.type = 'internal' THEN ei.durationStart
                               ELSE ee.durationStart
                           END) as first_event_date,
                           MAX(CASE 
                               WHEN r.type = 'internal' THEN ei.durationEnd
                               ELSE ee.durationEnd
                           END) as last_event_date
                    FROM requirements r
                    LEFT JOIN evaluation e ON r.id = e.requirementId
                    LEFT JOIN internalEvents ei ON r.eventId = ei.id AND r.type = 'internal'
                    LEFT JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
                    WHERE r.accepted = 1 AND r.email = ?
                    AND ((r.type = 'internal' AND r.eventId IN ({placeholders_int}))
                         OR (r.type = 'external' AND r.eventId IN ({placeholders_ext})))
                """, [email] + event_ids_internal + event_ids_external)
            elif event_ids_internal:
                placeholders = ','.join(['?' for _ in event_ids_internal])
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT r.id) as joined_count,
                           COUNT(DISTINCT CASE WHEN e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != '' THEN r.id END) as attended_count,
                           MIN(ei.durationStart) as first_event_date,
                           MAX(ei.durationEnd) as last_event_date
                    FROM requirements r
                    LEFT JOIN evaluation e ON r.id = e.requirementId
                    LEFT JOIN internalEvents ei ON r.eventId = ei.id
                    WHERE r.accepted = 1 AND r.email = ?
                    AND r.type = 'internal' AND r.eventId IN ({placeholders})
                """, [email] + event_ids_internal)
            elif event_ids_external:
                placeholders = ','.join(['?' for _ in event_ids_external])
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT r.id) as joined_count,
                           COUNT(DISTINCT CASE WHEN e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != '' THEN r.id END) as attended_count,
                           MIN(ee.durationStart) as first_event_date,
                           MAX(ee.durationEnd) as last_event_date
                    FROM requirements r
                    LEFT JOIN evaluation e ON r.id = e.requirementId
                    LEFT JOIN externalEvents ee ON r.eventId = ee.id
                    WHERE r.accepted = 1 AND r.email = ?
                    AND r.type = 'external' AND r.eventId IN ({placeholders})
                """, [email] + event_ids_external)
            
            row = cursor.fetchone()
            if not row:
                continue
            
            events_joined, events_attended, first_event_date, last_event_date = row
            events_dropped = events_joined - events_attended
            attendance_rate = (events_attended / events_joined * 100) if events_joined > 0 else 0
            
            # Calculate days active in semester
            days_active = 0
            if first_event_date and last_event_date:
                first_date = datetime.fromtimestamp(first_event_date / 1000)
                last_date = datetime.fromtimestamp(last_event_date / 1000)
                days_active = (last_date - first_date).days + 1
            
            # Determine participation consistency
            if events_attended == 0:
                participation_consistency = "No Participation"
                engagement_level = "Inactive"
            elif attendance_rate >= 80:
                participation_consistency = "Regular"
                engagement_level = "Active"
            elif attendance_rate >= 50:
                participation_consistency = "Irregular"
                engagement_level = "Moderate"
            else:
                participation_consistency = "Low"
                engagement_level = "At Risk"
            
            # Insert or update record
            current_time = int(datetime.now().timestamp() * 1000)
            
            cursor.execute("""
                INSERT OR REPLACE INTO volunteerParticipationHistory (
                    volunteerEmail, volunteerName, membershipId,
                    semester, semesterYear, semesterNumber,
                    eventsJoined, eventsAttended, eventsDropped, attendanceRate,
                    firstEventDate, lastEventDate, daysActiveInSemester,
                    participationConsistency, engagementLevel,
                    calculatedAt, lastUpdated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email, fullname, membership_id,
                semester, semester_year_int, semester_num_int,
                events_joined, events_attended, events_dropped, round(attendance_rate, 2),
                first_event_date, last_event_date, days_active,
                participation_consistency, engagement_level,
                current_time, current_time
            ))
            
            total_records += 1
        
        print(f"   ✓ Processed {len(volunteers)} volunteers for {semester}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("PARTICIPATION HISTORY POPULATED")
    print("=" * 70)
    print(f"✓ Total records created: {total_records}")
    print(f"✓ Semesters processed: {len(semester_events)}")
    print("\n✓ Data is now ready for Dropout Risk Assessment analytics!")
    print("=" * 70)

if __name__ == "__main__":
    populate_volunteer_participation_history()

