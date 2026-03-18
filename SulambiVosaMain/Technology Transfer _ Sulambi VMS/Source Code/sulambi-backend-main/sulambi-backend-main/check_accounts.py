#!/usr/bin/env python3
"""
Script to check registered accounts in the accounts table
"""

import sqlite3
import os

def check_accounts():
    """Check the accounts table for registered users"""
    
    # Database path
    db_path = os.path.join("app", "database", "database.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found at:", db_path)
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking registered accounts in the accounts table...")
        print("=" * 60)
        
        # Get total count of accounts
        cursor.execute("SELECT COUNT(*) FROM accounts")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Total registered accounts: {total_count}")
        
        if total_count == 0:
            print("⚠️  No accounts found in the database.")
            print("💡 UI should show: 'No registered users yet. Please add or wait for registrations.'")
        else:
            print(f"✅ {total_count} accounts found.")
            
            # Get table schema to understand columns
            cursor.execute("PRAGMA table_info(accounts)")
            columns = cursor.fetchall()
            
            print("\n📋 Table Schema:")
            print("-" * 50)
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, primary_key = col
                print(f"• {col_name} ({col_type})")
            
            # Get account details
            cursor.execute("SELECT * FROM accounts ORDER BY id DESC LIMIT 10")
            accounts = cursor.fetchall()
            
            print(f"\n📋 Recent Accounts (Last 10):")
            print("-" * 100)
            
            # Print header
            header = " | ".join([col[1] for col in columns])
            print(header)
            print("-" * 100)
            
            for account in accounts:
                row = " | ".join([str(val) if val is not None else "NULL" for val in account])
                print(row)
            
            if total_count > 10:
                print(f"\n... and {total_count - 10} more accounts")
            
            # Get account type breakdown if accountType column exists
            type_columns = [col[1] for col in columns if 'type' in col[1].lower() or 'role' in col[1].lower()]
            if type_columns:
                type_col = type_columns[0]
                cursor.execute(f"SELECT {type_col}, COUNT(*) FROM accounts GROUP BY {type_col}")
                type_breakdown = cursor.fetchall()
                
                print(f"\n👥 Account Type Breakdown ({type_col}):")
                print("-" * 40)
                for account_type, count in type_breakdown:
                    type_display = account_type or "NULL"
                    print(f"{type_display:<20}: {count}")
            
            # Get status breakdown if status column exists
            status_columns = [col[1] for col in columns if 'status' in col[1].lower()]
            if status_columns:
                status_col = status_columns[0]
                cursor.execute(f"SELECT {status_col}, COUNT(*) FROM accounts GROUP BY {status_col}")
                status_breakdown = cursor.fetchall()
                
                print(f"\n📈 Status Breakdown ({status_col}):")
                print("-" * 40)
                for status, count in status_breakdown:
                    status_display = status or "NULL"
                    print(f"{status_display:<20}: {count}")
        
        conn.close()
        print("\n✅ Database check completed successfully")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_accounts()
