#!/usr/bin/env python3
"""
Check if medCert is actually being saved in the database for pending requirements
"""

import os
import sys
import json
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    sys.exit(1)

try:
    import psycopg2
    from urllib.parse import urlparse
    
    result = urlparse(DATABASE_URL)
    
    print("=" * 70)
    print("CHECKING MEDCERT IN DATABASE")
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
    
    # Get pending requirements (accepted IS NULL)
    # Note: PostgreSQL stores unquoted column names in lowercase
    print("\n📋 Checking pending requirements (accepted IS NULL)...")
    cursor.execute("""
        SELECT id, medcert, waiver, email, fullname, eventid, type
        FROM requirements
        WHERE accepted IS NULL
        ORDER BY id DESC
        LIMIT 20
    """)
    
    pending_reqs = cursor.fetchall()
    print(f"Found {len(pending_reqs)} pending requirements\n")
    
    medcert_stats = {
        "has_medcert": 0,
        "no_medcert": 0,
        "has_waiver": 0,
        "no_waiver": 0,
        "both_present": 0,
        "neither_present": 0
    }
    
    print("=" * 70)
    print("DETAILED ANALYSIS")
    print("=" * 70)
    
    for req in pending_reqs:
        req_id, medcert, waiver, email, fullname, eventid, req_type = req
        
        has_medcert = medcert and str(medcert).strip() and str(medcert).strip() != ""
        has_waiver = waiver and str(waiver).strip() and str(waiver).strip() != ""
        
        if has_medcert:
            medcert_stats["has_medcert"] += 1
        else:
            medcert_stats["no_medcert"] += 1
            
        if has_waiver:
            medcert_stats["has_waiver"] += 1
        else:
            medcert_stats["no_waiver"] += 1
            
        if has_medcert and has_waiver:
            medcert_stats["both_present"] += 1
        elif not has_medcert and not has_waiver:
            medcert_stats["neither_present"] += 1
        
        print(f"\n📄 Requirement ID: {req_id}")
        print(f"   Email: {email}")
        print(f"   Name: {fullname}")
        print(f"   Event ID: {eventid} ({req_type})")
        print(f"   medCert: {'✅ PRESENT' if has_medcert else '❌ MISSING/EMPTY'}")
        if has_medcert:
            medcert_str = str(medcert)
            print(f"      URL: {medcert_str[:80]}..." if len(medcert_str) > 80 else f"      URL: {medcert_str}")
        print(f"   waiver: {'✅ PRESENT' if has_waiver else '❌ MISSING/EMPTY'}")
        if has_waiver:
            waiver_str = str(waiver)
            print(f"      URL: {waiver_str[:80]}..." if len(waiver_str) > 80 else f"      URL: {waiver_str}")
    
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total pending requirements checked: {len(pending_reqs)}")
    print(f"  ✅ Has medCert: {medcert_stats['has_medcert']}")
    print(f"  ❌ Missing medCert: {medcert_stats['no_medcert']}")
    print(f"  ✅ Has waiver: {medcert_stats['has_waiver']}")
    print(f"  ❌ Missing waiver: {medcert_stats['no_waiver']}")
    print(f"  ✅ Both present: {medcert_stats['both_present']}")
    print(f"  ❌ Neither present: {medcert_stats['neither_present']}")
    
    # Check all requirements (not just pending)
    print("\n" + "=" * 70)
    print("CHECKING ALL REQUIREMENTS")
    print("=" * 70)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(medcert) FILTER (WHERE medcert IS NOT NULL AND medcert != '') as has_medcert,
            COUNT(waiver) FILTER (WHERE waiver IS NOT NULL AND waiver != '') as has_waiver,
            COUNT(*) FILTER (WHERE medcert IS NOT NULL AND medcert != '' AND waiver IS NOT NULL AND waiver != '') as both_present
        FROM requirements
    """)
    
    stats = cursor.fetchone()
    total, has_medcert_all, has_waiver_all, both_present_all = stats
    
    print(f"Total requirements: {total}")
    print(f"  Has medCert: {has_medcert_all} ({has_medcert_all/total*100:.1f}%)")
    print(f"  Has waiver: {has_waiver_all} ({has_waiver_all/total*100:.1f}%)")
    print(f"  Both present: {both_present_all} ({both_present_all/total*100:.1f}%)")
    print(f"  Missing medCert: {total - has_medcert_all} ({(total - has_medcert_all)/total*100:.1f}%)")
    print(f"  Missing waiver: {total - has_waiver_all} ({(total - has_waiver_all)/total*100:.1f}%)")
    
    # Check recent requirements (last 10)
    print("\n" + "=" * 70)
    print("RECENT REQUIREMENTS (Last 10)")
    print("=" * 70)
    
    cursor.execute("""
        SELECT id, medcert, waiver, email, fullname, accepted
        FROM requirements
        ORDER BY id DESC
        LIMIT 10
    """)
    
    recent = cursor.fetchall()
    for req in recent:
        req_id, medcert, waiver, email, fullname, accepted = req
        has_medcert = medcert and str(medcert).strip() and str(medcert).strip() != ""
        has_waiver = waiver and str(waiver).strip() and str(waiver).strip() != ""
        
        status = "✅" if accepted == 1 else "⏳" if accepted is None else "❌"
        print(f"{status} {req_id[:20]}... | medCert: {'✅' if has_medcert else '❌'} | waiver: {'✅' if has_waiver else '❌'} | {email}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ CHECK COMPLETE")
    print("=" * 70)
    
except ImportError:
    print("❌ ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

