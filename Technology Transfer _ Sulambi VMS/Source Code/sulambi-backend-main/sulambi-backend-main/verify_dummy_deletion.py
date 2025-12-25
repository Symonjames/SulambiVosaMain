"""
Script to verify dummy data deletion
Run this to check if dummy users and their data still exist
"""
from app.database import connection

def verify_dummy_deletion():
    conn, cursor = connection.cursorInstance()
    
    print("=" * 60)
    print("VERIFYING DUMMY DATA DELETION")
    print("=" * 60)
    
    # 1. Check for dummy members
    print("\n1. Checking for dummy members...")
    cursor.execute("""
        SELECT COUNT(*) FROM membership 
        WHERE LOWER(email) LIKE 'dummy%@%' 
           OR LOWER(email) LIKE 'test%@%'
           OR LOWER(email) LIKE 'demo%@%'
           OR LOWER(email) LIKE 'fake%@%'
           OR (LOWER(email) LIKE 'example%@%' AND LOWER(email) NOT LIKE '%batstate%')
           OR LOWER(fullname) = 'dummy'
           OR LOWER(fullname) = 'test'
           OR LOWER(fullname) = 'demo'
           OR LOWER(fullname) = 'fake'
           OR LOWER(fullname) LIKE 'dummy %'
           OR LOWER(fullname) LIKE 'test %'
           OR LOWER(fullname) LIKE 'demo %'
           OR LOWER(fullname) LIKE 'fake %'
    """)
    dummy_member_count = cursor.fetchone()[0]
    print(f"   Dummy members found: {dummy_member_count}")
    
    if dummy_member_count > 0:
        print("\n   Sample dummy members:")
        cursor.execute("""
            SELECT id, email, fullname FROM membership 
            WHERE LOWER(email) LIKE 'dummy%@%' 
               OR LOWER(email) LIKE 'test%@%'
               OR LOWER(email) LIKE 'demo%@%'
               OR LOWER(email) LIKE 'fake%@%'
               OR (LOWER(email) LIKE 'example%@%' AND LOWER(email) NOT LIKE '%batstate%')
               OR LOWER(fullname) = 'dummy'
               OR LOWER(fullname) = 'test'
               OR LOWER(fullname) = 'demo'
               OR LOWER(fullname) = 'fake'
               OR LOWER(fullname) LIKE 'dummy %'
               OR LOWER(fullname) LIKE 'test %'
               OR LOWER(fullname) LIKE 'demo %'
               OR LOWER(fullname) LIKE 'fake %'
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"      ID: {row[0]}, Email: {row[1]}, Name: {row[2]}")
    
    # 2. Check for requirements from dummy emails
    print("\n2. Checking for requirements from dummy users...")
    cursor.execute("""
        SELECT COUNT(*) FROM requirements 
        WHERE LOWER(email) LIKE 'dummy%@%' 
           OR LOWER(email) LIKE 'test%@%'
           OR LOWER(email) LIKE 'demo%@%'
           OR LOWER(email) LIKE 'fake%@%'
           OR (LOWER(email) LIKE 'example%@%' AND LOWER(email) NOT LIKE '%batstate%')
    """)
    dummy_requirements_count = cursor.fetchone()[0]
    print(f"   Dummy requirements found: {dummy_requirements_count}")
    
    # 3. Check for evaluations linked to dummy requirements
    print("\n3. Checking for evaluations from dummy users...")
    cursor.execute("""
        SELECT COUNT(*) FROM evaluation e
        JOIN requirements r ON e.requirementId = r.id
        WHERE LOWER(r.email) LIKE 'dummy%@%' 
           OR LOWER(r.email) LIKE 'test%@%'
           OR LOWER(r.email) LIKE 'demo%@%'
           OR LOWER(r.email) LIKE 'fake%@%'
           OR (LOWER(r.email) LIKE 'example%@%' AND LOWER(r.email) NOT LIKE '%batstate%')
    """)
    dummy_evaluations_count = cursor.fetchone()[0]
    print(f"   Dummy evaluations found: {dummy_evaluations_count}")
    
    # 4. Check for accounts linked to dummy members
    print("\n4. Checking for accounts linked to dummy members...")
    cursor.execute("""
        SELECT COUNT(*) FROM accounts a
        JOIN membership m ON a.membershipId = m.id
        WHERE LOWER(m.email) LIKE 'dummy%@%' 
           OR LOWER(m.email) LIKE 'test%@%'
           OR LOWER(m.email) LIKE 'demo%@%'
           OR LOWER(m.email) LIKE 'fake%@%'
           OR (LOWER(m.email) LIKE 'example%@%' AND LOWER(m.email) NOT LIKE '%batstate%')
           OR LOWER(m.fullname) = 'dummy'
           OR LOWER(m.fullname) = 'test'
           OR LOWER(m.fullname) = 'demo'
           OR LOWER(m.fullname) = 'fake'
           OR LOWER(m.fullname) LIKE 'dummy %'
           OR LOWER(m.fullname) LIKE 'test %'
           OR LOWER(m.fullname) LIKE 'demo %'
           OR LOWER(m.fullname) LIKE 'fake %'
    """)
    dummy_accounts_count = cursor.fetchone()[0]
    print(f"   Dummy accounts found: {dummy_accounts_count}")
    
    # 5. Check for sessions from dummy accounts
    print("\n5. Checking for sessions from dummy accounts...")
    cursor.execute("""
        SELECT COUNT(*) FROM sessions s
        JOIN accounts a ON s.userid = a.id
        JOIN membership m ON a.membershipId = m.id
        WHERE LOWER(m.email) LIKE 'dummy%@%' 
           OR LOWER(m.email) LIKE 'test%@%'
           OR LOWER(m.email) LIKE 'demo%@%'
           OR LOWER(m.email) LIKE 'fake%@%'
           OR (LOWER(m.email) LIKE 'example%@%' AND LOWER(m.email) NOT LIKE '%batstate%')
           OR LOWER(m.fullname) = 'dummy'
           OR LOWER(m.fullname) = 'test'
           OR LOWER(m.fullname) = 'demo'
           OR LOWER(m.fullname) = 'fake'
           OR LOWER(m.fullname) LIKE 'dummy %'
           OR LOWER(m.fullname) LIKE 'test %'
           OR LOWER(m.fullname) LIKE 'demo %'
           OR LOWER(m.fullname) LIKE 'fake %'
    """)
    dummy_sessions_count = cursor.fetchone()[0]
    print(f"   Dummy sessions found: {dummy_sessions_count}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_dummy_data = (
        dummy_member_count + 
        dummy_requirements_count + 
        dummy_evaluations_count + 
        dummy_accounts_count + 
        dummy_sessions_count
    )
    print(f"Total dummy records found: {total_dummy_data}")
    
    if total_dummy_data == 0:
        print("✅ All dummy data has been successfully deleted!")
    else:
        print("❌ Dummy data still exists. Run the deletion function again.")
        print("\nTo delete, call: POST /api/analytics/dev/delete-dummy-volunteers")
    
    conn.close()
    return {
        'dummy_members': dummy_member_count,
        'dummy_requirements': dummy_requirements_count,
        'dummy_evaluations': dummy_evaluations_count,
        'dummy_accounts': dummy_accounts_count,
        'dummy_sessions': dummy_sessions_count,
        'total': total_dummy_data
    }

if __name__ == "__main__":
    verify_dummy_deletion()

