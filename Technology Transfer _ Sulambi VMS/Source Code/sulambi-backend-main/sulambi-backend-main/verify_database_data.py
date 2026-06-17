#!/usr/bin/env python3
"""Verify that new data is correctly stored in the database"""

from dotenv import load_dotenv
import os
import psycopg2
from urllib.parse import urlparse

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def verify_data_storage():
    """Verify data is stored and retrievable"""
    
    try:
        result = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )
        cursor = conn.cursor()
        
        print("=" * 70)
        print("DATABASE DATA VERIFICATION REPORT")
        print("=" * 70)
        
        # Check all main tables
        tables_to_check = [
            ("accounts", "SELECT COUNT(*) FROM accounts"),
            ("membership", "SELECT COUNT(*) FROM membership"),
            ("internalEvents", "SELECT COUNT(*) FROM \"internalEvents\""),
            ("externalEvents", "SELECT COUNT(*) FROM \"externalEvents\""),
            ("evaluation", "SELECT COUNT(*) FROM evaluation"),
            ("satisfactionSurveys", "SELECT COUNT(*) FROM \"satisfactionSurveys\""),
        ]
        
        print("\n📊 TABLE RECORD COUNTS:")
        print("-" * 70)
        
        total_records = 0
        for table_name, query in tables_to_check:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                total_records += count
                status = "✅" if count > 0 else "⏳"
                print(f"{status} {table_name:25} -> {count:6} records")
            except Exception as e:
                print(f"⚠️  {table_name:25} -> Error: {str(e)[:30]}")
        
        print("-" * 70)
        print(f"📈 TOTAL RECORDS IN DATABASE: {total_records}")
        
        # Sample recent data
        print("\n📋 RECENT DATA SAMPLES:")
        print("-" * 70)
        
        # Recent members
        cursor.execute("""
            SELECT member_email, member_name, date_created 
            FROM membership 
            ORDER BY date_created DESC 
            LIMIT 3
        """)
        
        recent_members = cursor.fetchall()
        if recent_members:
            print("\n✅ Recent Members Added:")
            for email, name, created in recent_members:
                print(f"   • {name} ({email}) - {created}")
        else:
            print("\n⏳ No members added yet")
        
        # Recent events
        cursor.execute("""
            SELECT event_name, event_date 
            FROM \"internalEvents\" 
            ORDER BY event_date DESC 
            LIMIT 3
        """)
        
        recent_events = cursor.fetchall()
        if recent_events:
            print("\n✅ Recent Events Created:")
            for name, date in recent_events:
                print(f"   • {name} - {date}")
        else:
            print("\n⏳ No events created yet")
        
        # Data integrity check
        print("\n🔍 DATA INTEGRITY CHECK:")
        print("-" * 70)
        
        # Check for orphaned data
        cursor.execute("""
            SELECT COUNT(*) FROM membership 
            WHERE member_email IS NULL OR member_email = ''
        """)
        orphaned = cursor.fetchone()[0]
        if orphaned == 0:
            print("✅ No orphaned member records")
        else:
            print(f"⚠️  Found {orphaned} members with missing email")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ DATABASE VERIFICATION COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nMake sure:")
        print("1. Internet connection is active")
        print("2. DATABASE_URL in .env is correct")
        print("3. PostgreSQL server is accessible")

if __name__ == "__main__":
    verify_data_storage()
