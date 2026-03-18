#!/usr/bin/env python3
"""
View the Render PostgreSQL database contents
Run this locally with DATABASE_URL set to your Render database connection string
"""

import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("\nTo get your DATABASE_URL:")
    print("1. Go to Render Dashboard → sulambi-database")
    print("2. Click on 'Connection Info' tab")
    print("3. Copy the 'External Database URL' (NOT Internal - that only works inside Render)")
    print("   The External URL should have a hostname like: dpg-xxxxx-a.render.com")
    print("\nThen set it as:")
    print("  Windows PowerShell: $env:DATABASE_URL = 'your-connection-string'")
    print("  Or create a .env file with: DATABASE_URL=your-connection-string")
    sys.exit(1)

try:
    import psycopg2
    result = urlparse(DATABASE_URL)
    
    # Check if using Internal URL (won't work from local machine)
    if result.hostname and result.hostname.endswith('-a') and '.render.com' not in result.hostname:
        print("⚠️  WARNING: You're using an Internal Database URL!")
        print("   Internal URLs (ending with '-a') only work inside Render's network.")
        print("\n   To connect from your local machine:")
        print("   1. Go to Render Dashboard → sulambi-database")
        print("   2. Click 'Connection Info' tab")
        print("   3. Copy the 'External Database URL' (hostname ends with .render.com)")
        print("   4. Update your DATABASE_URL environment variable")
        print("\n   The External URL looks like:")
        print("   postgresql://user:pass@dpg-xxxxx-a.render.com:5432/dbname")
        sys.exit(1)
    
    print("=" * 70)
    print("CONNECTING TO RENDER POSTGRESQL DATABASE")
    print("=" * 70)
    print(f"Host: {result.hostname}")
    print(f"Database: {result.path[1:]}")
    print(f"User: {result.username}")
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
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables:\n")
    
    # Show data for each table
    is_postgresql = DATABASE_URL and DATABASE_URL.startswith('postgresql://')
    
    for table in tables:
        table_name = table[0]
        # Quote table name for PostgreSQL to preserve case (PostgreSQL converts unquoted to lowercase)
        quoted_table = f'"{table_name}"' if is_postgresql else table_name
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {quoted_table}")
            count = cursor.fetchone()[0]
            print(f"📊 {table_name}: {count} rows")
        except Exception as e:
            print(f"📊 {table_name}: Error - {str(e)[:60]}")
            try:
                conn.rollback()
            except:
                pass
            continue
        
        # Show first few rows if table has data
        if count > 0 and count <= 10:
            cursor.execute(f"SELECT * FROM {quoted_table} LIMIT 5")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            columns = [col[0] for col in cursor.fetchall()]
            
            print(f"   Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
            
            if rows:
                print(f"   Sample data (first row):")
                print(f"   {dict(zip(columns, rows[0]))}")
        print()
    
    # Summary statistics
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    # Check key tables
    key_tables = ['accounts', 'membership', 'requirements', 'evaluation', 'internalEvents', 'externalEvents']
    for table in key_tables:
        try:
            # Quote table name for PostgreSQL to preserve case
            quoted_table = f'"{table}"' if DATABASE_URL and DATABASE_URL.startswith('postgresql://') else table
            cursor.execute(f"SELECT COUNT(*) FROM {quoted_table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
        except Exception as e:
            print(f"  {table}: table does not exist or error - {str(e)[:50]}")
    
    cursor.close()
    conn.close()
    print("\n✓ Connection closed")
    
except ImportError:
    print("❌ ERROR: psycopg2 not installed")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)
except psycopg2.OperationalError as e:
    error_msg = str(e)
    if "could not translate host name" in error_msg or "Name or service not known" in error_msg:
        print(f"❌ ERROR: Cannot resolve hostname '{result.hostname}'")
        print("\n   This usually means you're using the Internal Database URL.")
        print("   Internal URLs only work from within Render's network.")
        print("\n   Solution:")
        print("   1. Go to Render Dashboard → sulambi-database")
        print("   2. Click 'Connection Info' tab")
        print("   3. Copy the 'External Database URL' (has .render.com in hostname)")
        print("   4. Update your DATABASE_URL:")
        print("      PowerShell: $env:DATABASE_URL = 'postgresql://...'")
        print("      Or update .env file with the External URL")
    else:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

