#!/usr/bin/env python3
"""
Script to check registered members in the database
"""

import sqlite3
import os
from datetime import datetime

def check_members():
    """Check the members table for registered members"""
    
    # Database path
    db_path = os.path.join("app", "database", "database.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found at:", db_path)
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking registered members in the database...")
        print("=" * 50)
        
        # Check if members table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='members'
        """)
        
        table_exists = cursor.fetchone()
        if not table_exists:
            print("❌ Members table does not exist in the database")
            return
        
        # Get total count of members
        cursor.execute("SELECT COUNT(*) FROM members")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Total registered members: {total_count}")
        
        if total_count == 0:
            print("⚠️  No members found in the database.")
            print("💡 UI should show: 'No registered members yet. Please add or wait for registrations.'")
        else:
            print(f"✅ {total_count} members found.")
            
            # Get member details
            cursor.execute("""
                SELECT id, firstName, lastName, email, accountType, status, createdAt
                FROM members 
                ORDER BY createdAt DESC
                LIMIT 10
            """)
            
            members = cursor.fetchall()
            
            print("\n📋 Recent Members (Last 10):")
            print("-" * 80)
            print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Type':<10} {'Status':<10} {'Created':<15}")
            print("-" * 80)
            
            for member in members:
                member_id, first_name, last_name, email, account_type, status, created_at = member
                full_name = f"{first_name} {last_name}" if first_name and last_name else "N/A"
                email_display = email[:27] + "..." if email and len(email) > 30 else email or "N/A"
                created_display = created_at[:10] if created_at else "N/A"
                
                print(f"{member_id:<5} {full_name:<25} {email_display:<30} {account_type or 'N/A':<10} {status or 'N/A':<10} {created_display:<15}")
            
            if total_count > 10:
                print(f"\n... and {total_count - 10} more members")
            
            # Get status breakdown
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM members 
                GROUP BY status
            """)
            
            status_breakdown = cursor.fetchall()
            
            print("\n📈 Status Breakdown:")
            print("-" * 30)
            for status, count in status_breakdown:
                status_display = status or "NULL"
                print(f"{status_display:<15}: {count}")
            
            # Get account type breakdown
            cursor.execute("""
                SELECT accountType, COUNT(*) 
                FROM members 
                GROUP BY accountType
            """)
            
            type_breakdown = cursor.fetchall()
            
            print("\n👥 Account Type Breakdown:")
            print("-" * 30)
            for account_type, count in type_breakdown:
                type_display = account_type or "NULL"
                print(f"{type_display:<15}: {count}")
        
        conn.close()
        print("\n✅ Database check completed successfully")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_members()
