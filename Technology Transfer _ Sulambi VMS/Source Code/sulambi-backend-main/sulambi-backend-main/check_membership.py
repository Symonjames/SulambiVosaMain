#!/usr/bin/env python3
"""
Script to check registered members in the membership table
"""

import sqlite3
import os
from datetime import datetime

def check_membership():
    """Check the membership table for registered members"""
    
    # Database path
    db_path = os.path.join("app", "database", "database.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found at:", db_path)
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking registered members in the membership table...")
        print("=" * 60)
        
        # Check if membership table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='membership'
        """)
        
        table_exists = cursor.fetchone()
        if not table_exists:
            print("❌ Membership table does not exist in the database")
            return
        
        # Get total count of members
        cursor.execute("SELECT COUNT(*) FROM membership")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Total registered members: {total_count}")
        
        if total_count == 0:
            print("⚠️  No members found in the database.")
            print("💡 UI should show: 'No registered members yet. Please add or wait for registrations.'")
        else:
            print(f"✅ {total_count} members found.")
            
            # Get table schema to understand columns
            cursor.execute("PRAGMA table_info(membership)")
            columns = cursor.fetchall()
            
            print("\n📋 Table Schema:")
            print("-" * 50)
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, primary_key = col
                print(f"• {col_name} ({col_type})")
            
            # Get member details
            cursor.execute("SELECT * FROM membership ORDER BY id DESC LIMIT 10")
            members = cursor.fetchall()
            
            print(f"\n📋 Recent Members (Last 10):")
            print("-" * 100)
            
            # Print header
            header = " | ".join([col[1] for col in columns])
            print(header)
            print("-" * 100)
            
            for member in members:
                row = " | ".join([str(val) if val is not None else "NULL" for val in member])
                print(row)
            
            if total_count > 10:
                print(f"\n... and {total_count - 10} more members")
            
            # Get status breakdown if status column exists
            status_columns = [col[1] for col in columns if 'status' in col[1].lower()]
            if status_columns:
                status_col = status_columns[0]
                cursor.execute(f"SELECT {status_col}, COUNT(*) FROM membership GROUP BY {status_col}")
                status_breakdown = cursor.fetchall()
                
                print(f"\n📈 Status Breakdown ({status_col}):")
                print("-" * 40)
                for status, count in status_breakdown:
                    status_display = status or "NULL"
                    print(f"{status_display:<20}: {count}")
            
            # Get account type breakdown if accountType column exists
            type_columns = [col[1] for col in columns if 'type' in col[1].lower() or 'role' in col[1].lower()]
            if type_columns:
                type_col = type_columns[0]
                cursor.execute(f"SELECT {type_col}, COUNT(*) FROM membership GROUP BY {type_col}")
                type_breakdown = cursor.fetchall()
                
                print(f"\n👥 Account Type Breakdown ({type_col}):")
                print("-" * 40)
                for account_type, count in type_breakdown:
                    type_display = account_type or "NULL"
                    print(f"{type_display:<20}: {count}")
        
        conn.close()
        print("\n✅ Database check completed successfully")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_membership()
