"""
Check where age/sex analytics data is coming from
"""
from app.database import connection

def check_analytics_source():
    conn, cursor = connection.cursorInstance()
    
    print("=" * 60)
    print("CHECKING ANALYTICS DATA SOURCE")
    print("=" * 60)
    
    # Check membership table - real members
    print("\n1. Real Members (from membership table):")
    cursor.execute("""
        SELECT id, email, fullname, age, sex, accepted, active 
        FROM membership 
        WHERE accepted = 1 AND active = 1
    """)
    real_members = cursor.fetchall()
    print(f"   Found {len(real_members)} accepted and active members:")
    for row in real_members:
        print(f"      ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Age: {row[3]}, Sex: {row[4]}")
    
    # Check requirements table - old data that might have age/sex
    print("\n2. Requirements table (old volunteer registrations):")
    cursor.execute("""
        SELECT COUNT(*) FROM requirements 
        WHERE accepted = 1 AND (age IS NOT NULL OR sex IS NOT NULL)
    """)
    req_with_age_sex = cursor.fetchone()[0]
    print(f"   Requirements with age/sex data: {req_with_age_sex}")
    
    if req_with_age_sex > 0:
        print("\n   Sample requirements with age/sex:")
        cursor.execute("""
            SELECT id, email, fullname, age, sex, accepted 
            FROM requirements 
            WHERE accepted = 1 AND (age IS NOT NULL OR sex IS NOT NULL)
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"      ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Age: {row[3]}, Sex: {row[4]}")
        
        # Check if these emails belong to real members
        print("\n   Checking if requirement emails match real members...")
        cursor.execute("""
            SELECT DISTINCT r.email, r.age, r.sex 
            FROM requirements r
            WHERE r.accepted = 1 
              AND (r.age IS NOT NULL OR r.sex IS NOT NULL)
              AND r.email NOT IN (
                  SELECT email FROM membership WHERE accepted = 1 AND active = 1
              )
        """)
        orphaned_reqs = cursor.fetchall()
        print(f"   Requirements with age/sex that DON'T belong to real members: {len(orphaned_reqs)}")
        if len(orphaned_reqs) > 0:
            print("   These are likely old dummy data:")
            for row in orphaned_reqs[:10]:
                print(f"      Email: {row[0]}, Age: {row[1]}, Sex: {row[2]}")
    
    # Check what the analytics API would return
    print("\n3. What getAnalytics() would return:")
    cursor.execute("""
        SELECT m.age, m.sex 
        FROM membership m
        WHERE m.accepted = 1 AND m.active = 1
        AND EXISTS (
            SELECT 1 FROM requirements r 
            WHERE r.email = m.email AND r.accepted = 1
        )
    """)
    analytics_data = cursor.fetchall()
    print(f"   Members counted in analytics: {len(analytics_data)}")
    age_counts = {}
    sex_counts = {}
    for row in analytics_data:
        age = row[0]
        sex = row[1]
        if age:
            age_counts[age] = age_counts.get(age, 0) + 1
        if sex:
            sex_normalized = sex.strip().title() if sex else ""
            if sex_normalized:
                sex_counts[sex_normalized] = sex_counts.get(sex_normalized, 0) + 1
    
    print(f"\n   Age distribution: {age_counts}")
    print(f"   Sex distribution: {sex_counts}")
    
    conn.close()
    
    return {
        'real_members': len(real_members),
        'requirements_with_data': req_with_age_sex,
        'orphaned_requirements': len(orphaned_reqs) if 'orphaned_reqs' in locals() else 0,
        'analytics_age': age_counts,
        'analytics_sex': sex_counts
    }

if __name__ == "__main__":
    check_analytics_source()





