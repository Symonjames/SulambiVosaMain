#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix timestamp columns in PostgreSQL to use BIGINT instead of INTEGER
Run this BEFORE running the migration script if you get "integer out of range" errors
"""

import os
import sys
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
    
    db_name = result.path[1:] if result.path.startswith('/') else result.path
    db_user = result.username
    db_password = result.password
    db_host = result.hostname
    db_port = result.port or 5432
    
    print("=" * 70)
    print("FIXING TIMESTAMP COLUMNS IN POSTGRESQL")
    print("=" * 70)
    print(f"Connecting to: {db_host}:{db_port}/{db_name}")
    
    pg_conn = psycopg2.connect(
        database=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        connect_timeout=10
    )
    pg_cursor = pg_conn.cursor()
    print("✓ Connected to PostgreSQL database\n")
    
    # Columns that need to be changed from INTEGER to BIGINT
    tables_to_fix = {
        'internalEvents': ['durationStart', 'durationEnd', 'evaluationSendTime'],
        'externalEvents': ['durationStart', 'durationEnd', 'evaluationSendTime']
    }
    
    for table_name, columns in tables_to_fix.items():
        print(f"Fixing table: {table_name}")
        
        # Check if table exists
        pg_cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, (table_name,))
        table_exists = pg_cursor.fetchone()[0]
        
        if not table_exists:
            print(f"  ⚠️  Table '{table_name}' does not exist, skipping...\n")
            continue
        
        for column_name in columns:
            try:
                # Check current column type
                pg_cursor.execute("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s
                """, (table_name, column_name))
                result = pg_cursor.fetchone()
                
                if not result:
                    print(f"  ⚠️  Column '{column_name}' does not exist, skipping...")
                    continue
                
                current_type = result[0]
                
                if current_type.upper() == 'BIGINT':
                    print(f"  ✓ Column '{column_name}' is already BIGINT")
                elif current_type.upper() == 'INTEGER':
                    print(f"  → Converting '{column_name}' from INTEGER to BIGINT...")
                    pg_cursor.execute(f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" TYPE BIGINT USING "{column_name}"::BIGINT')
                    pg_conn.commit()
                    print(f"  ✓ Successfully converted '{column_name}' to BIGINT")
                else:
                    print(f"  ⚠️  Column '{column_name}' is {current_type}, not INTEGER. Skipping...")
                    
            except Exception as e:
                print(f"  ❌ Error fixing column '{column_name}': {e}")
                pg_conn.rollback()
        
        print()
    
    print("=" * 70)
    print("DONE")
    print("=" * 70)
    print("\nYou can now run the migration script.")
    
    pg_cursor.close()
    pg_conn.close()
    
except ImportError:
    print("❌ ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

