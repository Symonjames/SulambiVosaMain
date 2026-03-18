#!/usr/bin/env python3
"""
Script to verify that the 50 people are in the database and will appear in analytics
"""

import sqlite3
import os

# Database path
DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")

def verify_analytics_data():
    """Verify that members are set up correctly for analytics"""
    print("=" * 60)
    print("VERIFYING ANALYTICS DATA")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check total members
    cursor.execute("SELECT COUNT(*) FROM membership")
    total_members = cursor.fetchone()[0]
    print(f"\n1. Total members in database: {total_members}")
    
    # Check accepted and active members
    cursor.execute("""
        SELECT COUNT(*) FROM membership 
        WHERE accepted = 1 AND active = 1
    """)
    accepted_active = cursor.fetchone()[0]
    print(f"2. Accepted and active members: {accepted_active}")
    
    # Check members with requirements
    cursor.execute("""
        SELECT COUNT(DISTINCT m.email)
        FROM membership m
        INNER JOIN requirements r ON m.email = r.email
        WHERE m.accepted = 1 AND m.active = 1 AND r.accepted = 1
    """)
    members_with_reqs = cursor.fetchone()[0]
    print(f"3. Members with accepted requirements: {members_with_reqs}")
    
    # Check requirements count
    cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
    total_reqs = cursor.fetchone()[0]
    print(f"4. Total accepted requirements: {total_reqs}")
    
    # Check age and sex data
    cursor.execute("""
        SELECT COUNT(*) FROM membership 
        WHERE accepted = 1 AND active = 1 
        AND age IS NOT NULL AND age != ''
        AND sex IS NOT NULL AND sex != ''
    """)
    members_with_demographics = cursor.fetchone()[0]
    print(f"5. Members with age and sex data: {members_with_demographics}")
    
    # Sample data that should appear in analytics
    print("\n" + "=" * 60)
    print("SAMPLE DATA (First 10 members that should appear in analytics):")
    print("=" * 60)
    
    cursor.execute("""
        SELECT m.fullname, m.email, m.age, m.sex, m.accepted, m.active,
               COUNT(r.id) as req_count
        FROM membership m
        LEFT JOIN requirements r ON m.email = r.email AND r.accepted = 1
        WHERE m.accepted = 1 AND m.active = 1
        GROUP BY m.id
        HAVING req_count > 0
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    if samples:
        for i, (name, email, age, sex, accepted, active, req_count) in enumerate(samples, 1):
            print(f"\n{i}. {name}")
            print(f"   Email: {email}")
            print(f"   Age: {age}, Sex: {sex}")
            print(f"   Accepted: {accepted}, Active: {active}")
            print(f"   Requirements: {req_count}")
    else:
        print("❌ No members found that match analytics criteria!")
    
    # Check what the analytics API would return
    print("\n" + "=" * 60)
    print("WHAT ANALYTICS API WOULD RETURN:")
    print("=" * 60)
    
    cursor.execute("""
        SELECT m.age, m.sex
        FROM membership m
        INNER JOIN requirements r ON m.email = r.email
        WHERE m.accepted = 1 AND m.active = 1 
        AND r.accepted = 1
        AND m.age IS NOT NULL AND m.age != ''
        AND m.sex IS NOT NULL AND m.sex != ''
    """)
    
    analytics_data = cursor.fetchall()
    print(f"\nTotal records for analytics: {len(analytics_data)}")
    
    if analytics_data:
        # Count by age
        age_counts = {}
        sex_counts = {}
        for age, sex in analytics_data:
            age_str = str(int(age)) if age else None
            if age_str:
                age_counts[age_str] = age_counts.get(age_str, 0) + 1
            if sex:
                sex_normalized = sex.strip().title()
                sex_counts[sex_normalized] = sex_counts.get(sex_normalized, 0) + 1
        
        print("\nAge Groups:")
        for age in sorted(age_counts.keys(), key=int):
            print(f"  Age {age}: {age_counts[age]}")
        
        print("\nSex Groups:")
        for sex in sorted(sex_counts.keys()):
            print(f"  {sex}: {sex_counts[sex]}")
    else:
        print("❌ No data would be returned by analytics API!")
        print("\nPossible issues:")
        print("  - Members don't have accepted=1 and active=1")
        print("  - Members don't have requirements with accepted=1")
        print("  - Members don't have age or sex data")
    
    conn.close()
    
    print("\n" + "=" * 60)
    if members_with_reqs > 0:
        print(f"✅ {members_with_reqs} members should appear in analytics")
    else:
        print("❌ No members will appear in analytics!")
        print("\nTo fix:")
        print("  1. Make sure members have accepted=1 and active=1")
        print("  2. Make sure members have requirements with accepted=1")
        print("  3. Run: python add_100_people.py")
    print("=" * 60)

if __name__ == "__main__":
    verify_analytics_data()

















