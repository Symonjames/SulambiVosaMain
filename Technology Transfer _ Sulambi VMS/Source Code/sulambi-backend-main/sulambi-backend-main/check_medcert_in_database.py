#!/usr/bin/env python3
"""
Check medical certificate values in the database for pending requirements
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)

try:
    import psycopg2
    result = urlparse(DATABASE_URL)
    
    print("=" * 70)
    print("CHECKING MEDICAL CERTIFICATE VALUES IN DATABASE")
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
    
    # Get all pending requirements with their medCert values
    # Check column names first
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'requirements' 
        AND table_schema = 'public'
        AND column_name IN ('eventId', 'eventid', 'medCert', 'medcert')
        ORDER BY column_name;
    """)
    columns = [row[0] for row in cursor.fetchall()]
    
    event_id_col = 'eventId' if 'eventId' in columns else 'eventid'
    medcert_col = 'medCert' if 'medCert' in columns else 'medcert'
    
    cursor.execute(f"""
        SELECT id, email, fullname, "{medcert_col}", waiver, "{event_id_col}", type
        FROM "requirements"
        WHERE accepted IS NULL
        ORDER BY id DESC
    """)
    
    pending_reqs = cursor.fetchall()
    
    print(f"Found {len(pending_reqs)} pending requirements:\n")
    print("=" * 70)
    
    empty_medcert = 0
    na_medcert = 0
    valid_medcert = 0
    
    for req in pending_reqs:
        req_id, email, fullname, medcert, waiver, event_id, req_type = req
        
        print(f"\nRequirement ID: {req_id}")
        print(f"  Email: {email}")
        print(f"  Full Name: {fullname}")
        print(f"  Event ID: {event_id}")
        print(f"  Type: {req_type}")
        print(f"  Medical Certificate: {medcert}")
        print(f"    - Type: {type(medcert).__name__}")
        print(f"    - Length: {len(medcert) if medcert else 0}")
        print(f"  Waiver: {waiver}")
        print(f"    - Type: {type(waiver).__name__}")
        print(f"    - Length: {len(waiver) if waiver else 0}")
        
        # Categorize medCert values
        if not medcert or medcert.strip() == "":
            empty_medcert += 1
            print(f"  ⚠️  Medical Certificate is EMPTY")
        elif medcert.strip().upper() == "N/A":
            na_medcert += 1
            print(f"  ⚠️  Medical Certificate is 'N/A'")
        else:
            valid_medcert += 1
            print(f"  ✅ Medical Certificate has value")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total pending requirements: {len(pending_reqs)}")
    print(f"  ✅ Valid medical certificates: {valid_medcert}")
    print(f"  ⚠️  Empty medical certificates: {empty_medcert}")
    print(f"  ⚠️  'N/A' medical certificates: {na_medcert}")
    
    # Check all requirements (not just pending)
    cursor.execute('SELECT COUNT(*) FROM "requirements" WHERE medCert IS NULL OR medCert = \'\' OR medCert = \'N/A\'')
    all_empty_medcert = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM "requirements" WHERE medCert IS NOT NULL AND medCert != \'\' AND medCert != \'N/A\'')
    all_valid_medcert = cursor.fetchone()[0]
    
    print("\n" + "=" * 70)
    print("ALL REQUIREMENTS (Not Just Pending)")
    print("=" * 70)
    print(f"  ✅ Valid medical certificates: {all_valid_medcert}")
    print(f"  ⚠️  Empty/NULL/N/A medical certificates: {all_empty_medcert}")
    
    # Check if medCert column allows NULL
    cursor.execute("""
        SELECT is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'requirements' 
        AND column_name = 'medCert'
        AND table_schema = 'public'
    """)
    medcert_info = cursor.fetchone()
    if medcert_info:
        is_nullable, default = medcert_info
        print(f"\n  medCert column info:")
        print(f"    - Nullable: {is_nullable}")
        print(f"    - Default: {default}")
    
    cursor.close()
    conn.close()
    print("\n✓ Connection closed")
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

