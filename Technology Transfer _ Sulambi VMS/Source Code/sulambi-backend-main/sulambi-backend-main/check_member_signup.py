#!/usr/bin/env python3
"""
Check if member signup credentials are saved in the database
Shows all membership records, especially pending ones
"""

import os
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("\nTo get your DATABASE_URL:")
    print("1. Go to Render Dashboard → sulambi-database")
    print("2. Click 'Connection Info' tab")
    print("3. Copy the 'External Database URL'")
    sys.exit(1)

try:
    import psycopg2
    result = urlparse(DATABASE_URL)
    
    print("=" * 70)
    print("CHECKING MEMBER SIGNUP IN DATABASE")
    print("=" * 70)
    print(f"Host: {result.hostname}")
    print(f"Database: {result.path[1:]}")
    print("=" * 70)
    
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432,
        connect_timeout=10
    )
    cursor = conn.cursor()
    print("✓ Connected successfully!\n")
    
    is_postgresql = DATABASE_URL.startswith('postgresql://')
    membership_table = '"membership"' if is_postgresql else 'membership'
    
    # Check if membership table exists
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {membership_table}")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total membership records: {total_count}\n")
    except Exception as e:
        print(f"❌ ERROR: Cannot access membership table: {e}")
        print("   Make sure the table exists in the database.")
        sys.exit(1)
    
    # Get all membership records with key information
    print("=" * 70)
    print("ALL MEMBERSHIP RECORDS")
    print("=" * 70)
    
    # Use lowercase column names for PostgreSQL (unquoted columns are lowercase)
    if is_postgresql:
        query = f"""
            SELECT id, fullname, email, username, srcode, 
                   accepted, active, collegedept, campus
            FROM {membership_table}
            ORDER BY id DESC
            LIMIT 50
        """
    else:
        query = f"""
            SELECT id, fullname, email, username, srcode, 
                   accepted, active, collegeDept, campus
            FROM {membership_table}
            ORDER BY id DESC
            LIMIT 50
        """
    
    cursor.execute(query)
    members = cursor.fetchall()
    
    if not members:
        print("⚠️  No membership records found in database!")
        print("   This could mean:")
        print("   1. No members have signed up yet")
        print("   2. The table is empty")
        print("   3. There's a database connection issue")
    else:
        print(f"Showing {len(members)} most recent members:\n")
        print(f"{'ID':<5} {'Full Name':<30} {'Email':<35} {'Status':<15} {'Active':<8}")
        print("-" * 100)
        
        pending_count = 0
        approved_count = 0
        rejected_count = 0
        
        for member in members:
            member_id, fullname, email, username, srcode, accepted, active, college_dept, campus = member
            
            # Determine status
            if accepted is None:
                status = "⏳ PENDING"
                pending_count += 1
            elif accepted == True or accepted == 1:
                status = "✅ APPROVED"
                approved_count += 1
            elif accepted == False or accepted == 0:
                status = "❌ REJECTED"
                rejected_count += 1
            else:
                status = "❓ UNKNOWN"
            
            active_str = "Yes" if (active == True or active == 1) else "No"
            
            print(f"{member_id:<5} {str(fullname or 'N/A')[:28]:<30} {str(email or 'N/A')[:33]:<35} {status:<15} {active_str:<8}")
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"⏳ Pending (accepted = NULL): {pending_count}")
        print(f"✅ Approved (accepted = True/1): {approved_count}")
        print(f"❌ Rejected (accepted = False/0): {rejected_count}")
        print(f"📊 Total records: {len(members)}")
    
    # Check specific member by username or email
    print("\n" + "=" * 70)
    print("QUICK SEARCH")
    print("=" * 70)
    print("To search for a specific member, you can modify this script or run SQL:")
    print(f"  SELECT * FROM {membership_table} WHERE email = 'your-email@example.com';")
    print(f"  SELECT * FROM {membership_table} WHERE username = 'your-username';")
    
    # Show pending members specifically
    print("\n" + "=" * 70)
    print("PENDING MEMBERSHIP APPLICATIONS (Need Approval)")
    print("=" * 70)
    
    # Use lowercase column names for PostgreSQL
    # Note: created_at may not exist in all databases, so we'll exclude it or handle it
    if is_postgresql:
        pending_query = f"""
            SELECT id, fullname, email, username, srcode, collegedept, campus
            FROM {membership_table}
            WHERE accepted IS NULL
            ORDER BY id DESC
        """
    else:
        pending_query = f"""
            SELECT id, fullname, email, username, srcode, collegeDept, campus
            FROM {membership_table}
            WHERE accepted IS NULL
            ORDER BY id DESC
        """
    
    try:
        cursor.execute(pending_query)
        pending_members = cursor.fetchall()
        
        if pending_members:
            print(f"Found {len(pending_members)} pending applications:\n")
            for member in pending_members:
                # Handle different number of columns (with or without created_at)
                member_id = member[0]
                fullname = member[1]
                email = member[2]
                username = member[3]
                srcode = member[4]
                college_dept = member[5]
                campus = member[6]
                
                print(f"  ID: {member_id}")
                print(f"  Name: {fullname}")
                print(f"  Email: {email}")
                print(f"  Username: {username}")
                print(f"  SR Code: {srcode}")
                print(f"  College/Dept: {college_dept}")
                print(f"  Campus: {campus}")
                print()
        else:
            print("No pending applications found.")
    except Exception as e:
        print(f"⚠️  Could not query pending members: {e}")
    
    cursor.close()
    conn.close()
    print("=" * 70)
    print("✓ Connection closed")
    print("=" * 70)
    
except ImportError:
    print("❌ ERROR: psycopg2 not installed")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

