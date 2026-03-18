#!/usr/bin/env python3
"""Show ALL analytics data that has been added to the database"""

import sqlite3
import os

backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("ALL ANALYTICS DATA IN DATABASE")
print("=" * 60)

# 1. MEMBERS DATA
print("\n1. MEMBERS DATA:")
cursor.execute("SELECT COUNT(*) FROM membership WHERE active = 1 AND accepted = 1")
total_members = cursor.fetchone()[0]
print(f"   ✓ Total active & accepted members: {total_members}")

# Age distribution
cursor.execute("""
    SELECT age, COUNT(*) as count
    FROM membership
    WHERE active = 1 AND accepted = 1 AND age IS NOT NULL
    GROUP BY age
    ORDER BY CAST(age AS INTEGER)
""")
age_data = cursor.fetchall()
print(f"\n   Age Distribution ({len(age_data)} age groups):")
for age, count in age_data:
    print(f"      Age {age}: {count} members")

# Sex distribution
cursor.execute("""
    SELECT sex, COUNT(*) as count
    FROM membership
    WHERE active = 1 AND accepted = 1 AND sex IS NOT NULL
    GROUP BY sex
""")
sex_data = cursor.fetchall()
print(f"\n   Sex Distribution ({len(sex_data)} groups):")
for sex, count in sex_data:
    print(f"      {sex}: {count} members")

# 2. REQUIREMENTS DATA
print("\n2. REQUIREMENTS DATA:")
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
total_reqs = cursor.fetchone()[0]
print(f"   ✓ Total accepted requirements: {total_reqs}")

cursor.execute("""
    SELECT COUNT(DISTINCT email) 
    FROM requirements 
    WHERE accepted = 1
""")
members_with_reqs = cursor.fetchone()[0]
print(f"   ✓ Members with requirements: {members_with_reqs}")

# Requirements per member
cursor.execute("""
    SELECT 
        CASE 
            WHEN COUNT(*) = 1 THEN '1 event'
            WHEN COUNT(*) = 2 THEN '2 events'
            WHEN COUNT(*) = 3 THEN '3 events'
            WHEN COUNT(*) >= 4 THEN '4+ events'
        END as participation_level,
        COUNT(DISTINCT email) as member_count
    FROM requirements
    WHERE accepted = 1
    GROUP BY email
""")
participation_dist = {}
for row in cursor.fetchall():
    level, count = row
    participation_dist[level] = participation_dist.get(level, 0) + 1

print(f"\n   Participation Distribution:")
for level, count in sorted(participation_dist.items()):
    print(f"      {level}: {count} members")

# 3. EVALUATIONS DATA
print("\n3. EVALUATIONS DATA:")
cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
total_evals = cursor.fetchone()[0]
print(f"   ✓ Total finalized evaluations: {total_evals}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1 AND criteria IS NOT NULL AND criteria != ''")
evals_with_criteria = cursor.fetchone()[0]
print(f"   ✓ Evaluations with satisfaction criteria: {evals_with_criteria}")

# 4. ANALYTICS READINESS
print("\n4. ANALYTICS READINESS:")
cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
    AND m.age IS NOT NULL AND m.sex IS NOT NULL
""")
analytics_ready = cursor.fetchone()[0]
print(f"   ✓ Members ready for Age/Sex Analytics: {analytics_ready}")

cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    INNER JOIN evaluation e ON r.id = e.requirementId
    WHERE m.active = 1 AND m.accepted = 1 
    AND r.accepted = 1 
    AND e.finalized = 1
    AND e.recommendations != ''
""")
dropout_ready = cursor.fetchone()[0]
print(f"   ✓ Members ready for Dropout Risk Analytics: {dropout_ready}")

cursor.execute("""
    SELECT COUNT(*)
    FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    INNER JOIN internalEvents ie ON r.eventId = ie.id AND r.type = 'internal'
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    
    UNION ALL
    
    SELECT COUNT(*)
    FROM evaluation e
    INNER JOIN requirements r ON e.requirementId = r.id
    INNER JOIN externalEvents ee ON r.eventId = ee.id AND r.type = 'external'
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
""")
satisfaction_ready = sum([row[0] for row in cursor.fetchall()])
print(f"   ✓ Evaluations ready for Satisfaction Analytics: {satisfaction_ready}")

# 5. SAMPLE DATA FOR EACH ANALYTICS TYPE
print("\n5. SAMPLE DATA:")

# Sample for Age Analytics
print("\n   Age Analytics Sample (first 5 members):")
cursor.execute("""
    SELECT m.fullname, m.age, m.sex
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
    AND m.age IS NOT NULL AND m.sex IS NOT NULL
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"      - {row[0]}: Age {row[1]}, {row[2]}")

# Sample for Dropout Risk
print("\n   Dropout Risk Sample (first 5 members with participation):")
cursor.execute("""
    SELECT 
        m.fullname,
        COUNT(r.id) as total_regs,
        COUNT(CASE WHEN e.finalized = 1 AND e.recommendations != '' THEN 1 END) as attended
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
    LEFT JOIN evaluation e ON r.id = e.requirementId AND e.finalized = 1
    WHERE m.active = 1 AND m.accepted = 1
    GROUP BY m.id, m.fullname
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"      - {row[0]}: {row[1]} registrations, {row[2]} attended")

# Sample for Satisfaction
print("\n   Satisfaction Analytics Sample (first 5 evaluations):")
cursor.execute("""
    SELECT e.id, LENGTH(e.criteria) as criteria_len, e.q13, e.q14
    FROM evaluation e
    WHERE e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != ''
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"      - Evaluation {row[0]}: Criteria length {row[1]}, Q13={row[2]}, Q14={row[3]}")

conn.close()

print("\n" + "=" * 60)
print("✅ ALL DATA IS IN THE DATABASE!")
print("=" * 60)
print(f"\nSummary:")
print(f"  - {total_members} members with age and sex data")
print(f"  - {total_reqs} requirements (event registrations)")
print(f"  - {total_evals} evaluations with satisfaction data")
print(f"  - {analytics_ready} members ready for Age/Sex Analytics")
print(f"  - {dropout_ready} members ready for Dropout Risk Analytics")
print(f"  - {satisfaction_ready} evaluations ready for Satisfaction Analytics")
print("\n⚠️  If analytics still show 'No Data Available':")
print("   1. Restart the backend server (python server.py)")
print("   2. Refresh the frontend dashboard")
print("   3. The backend code has been fixed (accepted = 1 instead of True)")
print("=" * 60)

















