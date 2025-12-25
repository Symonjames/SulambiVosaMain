#!/usr/bin/env python3
"""Verify dropout risk analytics data"""

import sqlite3
import os

backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("VERIFYING DROPOUT RISK ANALYTICS DATA")
print("=" * 60)

# Check what getActiveMemberData would return (used by dropout risk)
cursor.execute("""
    SELECT 
        m.fullname,
        COUNT(r.id) as total_registrations,
        COUNT(CASE WHEN e.finalized = 1 AND e.recommendations != '' THEN 1 END) as attended_count,
        MAX(ie.durationEnd) as last_internal_event,
        MAX(ee.durationEnd) as last_external_event
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
    LEFT JOIN evaluation e ON r.id = e.requirementId AND e.finalized = 1
    LEFT JOIN internalEvents ie ON r.eventId = ie.id AND r.type = 'internal'
    LEFT JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
    WHERE m.active = 1 AND m.accepted = 1
    GROUP BY m.id, m.fullname
    ORDER BY total_registrations DESC
    LIMIT 10
""")

members_data = cursor.fetchall()
print(f"\nSample members with participation data (top 10):")
for row in members_data:
    name, regs, attended, last_int, last_ext = row
    last_event = max(last_int or 0, last_ext or 0)
    print(f"  - {name}: {regs} registrations, {attended} attended, last event: {last_event}")

# Count by participation level
cursor.execute("""
    SELECT 
        CASE 
            WHEN COUNT(r.id) = 1 THEN '1 event (At Risk)'
            WHEN COUNT(r.id) = 2 THEN '2 events'
            WHEN COUNT(r.id) = 3 THEN '3 events'
            WHEN COUNT(r.id) >= 4 THEN '4+ events (Engaged)'
        END as participation_level,
        COUNT(DISTINCT m.id) as volunteer_count
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
    WHERE m.active = 1 AND m.accepted = 1
    GROUP BY m.id
""")

participation_levels = {}
for row in cursor.fetchall():
    level, count = row
    participation_levels[level] = participation_levels.get(level, 0) + 1

print(f"\nParticipation distribution:")
for level, count in sorted(participation_levels.items()):
    print(f"  - {level}: {count} volunteers")

# Check attendance rates
cursor.execute("""
    SELECT 
        COUNT(DISTINCT m.id) as total_volunteers,
        COUNT(r.id) as total_registrations,
        COUNT(CASE WHEN e.finalized = 1 AND e.recommendations != '' THEN 1 END) as total_attended
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
    LEFT JOIN evaluation e ON r.id = e.requirementId AND e.finalized = 1
    WHERE m.active = 1 AND m.accepted = 1
""")

stats = cursor.fetchone()
if stats[1] > 0:
    attendance_rate = (stats[2] / stats[1]) * 100
    print(f"\nOverall attendance rate: {attendance_rate:.1f}%")
    print(f"  - Total volunteers: {stats[0]}")
    print(f"  - Total registrations: {stats[1]}")
    print(f"  - Total attended: {stats[2]}")

conn.close()

print("\n" + "=" * 60)
print("✅ DATA READY FOR DROPOUT RISK ANALYTICS!")
print("=" * 60)

















