#!/usr/bin/env python3
"""
Script to check reports in the database
"""

import sqlite3
import os

def check_reports():
    """Check the reports tables for data"""
    
    # Database path
    db_path = os.path.join("app", "database", "database.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found at:", db_path)
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking reports in the database...")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📋 Available tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check for report-related tables
        report_tables = [t[0] for t in tables if 'report' in t[0].lower()]
        
        if not report_tables:
            print("\n❌ No report tables found!")
            print("💡 The Latest News section needs reports with photos to display content.")
            return
        
        print(f"\n📊 Found report tables: {report_tables}")
        
        # Check each report table
        for table_name in report_tables:
            print(f"\n--- {table_name.upper()} ---")
            
            # Get count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Total records: {count}")
            
            if count > 0:
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                print(f"Columns: {columns}")
                for i, row in enumerate(rows):
                    print(f"Record {i+1}: {dict(zip(columns, row))}")
        
        conn.close()
        print("\n✅ Database check completed successfully")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_reports()













































