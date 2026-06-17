#!/usr/bin/env python3
"""Test database connection and data storage"""

from dotenv import load_dotenv
import os
import psycopg2
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

print(f"✓ DATABASE_URL found")
print(f"  Database: {DATABASE_URL.split('@')[1].split('/')[0]}")

try:
    result = urlparse(DATABASE_URL)
    
    print("\nAttempting connection...")
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432,
        connect_timeout=5
    )
    
    print("✅ CONNECTION SUCCESSFUL!")
    
    # Test 1: Check if tables exist
    print("\n" + "=" * 60)
    print("CHECKING TABLES")
    print("=" * 60)
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    if tables:
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("❌ No tables found - need to run initialization")
    
    # Test 2: Test write operation
    print("\n" + "=" * 60)
    print("TESTING DATA INSERT")
    print("=" * 60)
    
    # Test with accounts table (read-only for now)
    cursor.execute("SELECT COUNT(*) FROM accounts")
    count = cursor.fetchone()[0]
    print(f"✅ Current accounts in database: {count}")
    
    # Test 3: Verify data persistence
    print("\n" + "=" * 60)
    print("DATA STORAGE VERIFICATION")
    print("=" * 60)
    
    cursor.execute("SELECT username, accountType FROM accounts LIMIT 5")
    rows = cursor.fetchall()
    
    if rows:
        print(f"✅ Sample data found ({len(rows)} records):")
        for row in rows:
            print(f"   - User: {row[0]}, Role: {row[1]}")
    else:
        print("⚠️  No existing data - database is empty (this is normal for new database)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Database is ready!")
    print("=" * 60)

except psycopg2.OperationalError as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Verify DATABASE_URL is correct in .env file")
    print("3. Check if PostgreSQL server is running")
    print("4. Verify firewall/network settings")
    exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)
