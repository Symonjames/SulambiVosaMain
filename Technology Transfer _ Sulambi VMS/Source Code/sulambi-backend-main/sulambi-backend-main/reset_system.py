"""
SULAMBI VMS - System Reset Script
==================================
This script will COMPLETELY RESET your Sulambi VMS system to factory defaults.

WARNING: This will DELETE ALL DATA including:
- All user accounts (except default Admin and Officer accounts)
- All membership applications
- All events (internal and external)
- All reports
- All evaluations
- All uploaded files
- All sessions

Use this ONLY if you want to start completely fresh!
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
import sqlite3

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
UPLOADS_DIR = "uploads"

def confirm_reset():
    """Ask user for confirmation before proceeding"""
    print("\n" + "="*70)
    print("⚠️  WARNING: SYSTEM RESET ⚠️")
    print("="*70)
    print("\nThis will permanently delete ALL data including:")
    print("  ✗ All membership applications")
    print("  ✗ All volunteer accounts")
    print("  ✗ All events and reports")
    print("  ✗ All evaluations and feedback")
    print("  ✗ All uploaded files (photos, documents, etc.)")
    print("\nOnly these default accounts will remain:")
    print("  ✓ Admin (username: Admin, password: sulambi@2024)")
    print("  ✓ Officer (username: Sulambi-Officer, password: password@2024)")
    print("\n" + "="*70)
    
    response = input("\nAre you ABSOLUTELY sure you want to continue? (type 'YES' to confirm): ")
    return response == "YES"

def backup_database():
    """Create a backup of the current database before deletion"""
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + ".backup"
        counter = 1
        while os.path.exists(backup_path):
            backup_path = f"{DB_PATH}.backup{counter}"
            counter += 1
        
        print(f"\n📦 Creating backup at: {backup_path}")
        shutil.copy2(DB_PATH, backup_path)
        print("✓ Backup created successfully")
        return backup_path
    return None

def delete_database():
    """Delete the existing database file"""
    if os.path.exists(DB_PATH):
        print(f"\n🗑️  Deleting database: {DB_PATH}")
        os.remove(DB_PATH)
        print("✓ Database deleted")
        
        # Also delete WAL and SHM files if they exist
        wal_file = DB_PATH + "-wal"
        shm_file = DB_PATH + "-shm"
        
        if os.path.exists(wal_file):
            os.remove(wal_file)
            print("✓ WAL file deleted")
        
        if os.path.exists(shm_file):
            os.remove(shm_file)
            print("✓ SHM file deleted")
    else:
        print(f"\n⚠️  Database file not found at: {DB_PATH}")

def clear_uploads():
    """Clear all uploaded files except README.md"""
    if os.path.exists(UPLOADS_DIR):
        print(f"\n🗑️  Clearing uploads directory: {UPLOADS_DIR}")
        
        files_deleted = 0
        for item in os.listdir(UPLOADS_DIR):
            item_path = os.path.join(UPLOADS_DIR, item)
            
            # Skip README.md
            if item == "README.md":
                continue
            
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    files_deleted += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    files_deleted += 1
            except Exception as e:
                print(f"  ⚠️  Error deleting {item}: {e}")
        
        print(f"✓ Deleted {files_deleted} file(s)/folder(s)")
    else:
        print(f"\n⚠️  Uploads directory not found: {UPLOADS_DIR}")

def reinitialize_database():
    """Reinitialize the database with fresh tables and default accounts"""
    print("\n🔧 Reinitializing database...")
    
    # Import the table initializer to recreate tables
    try:
        from app.database import tableInitializer
        print("✓ Database reinitialized with default accounts")
    except Exception as e:
        print(f"⚠️  Error reinitializing database: {e}")
        print("You may need to start the server to initialize the database.")

def main():
    print("\n" + "="*70)
    print("SULAMBI VMS - SYSTEM RESET TOOL")
    print("="*70)
    
    # Confirm with user
    if not confirm_reset():
        print("\n❌ Reset cancelled. No changes were made.")
        return
    
    print("\n" + "="*70)
    print("Starting reset process...")
    print("="*70)
    
    # Step 1: Backup database
    backup_path = backup_database()
    
    # Step 2: Delete database
    delete_database()
    
    # Step 3: Clear uploads
    clear_uploads()
    
    # Step 4: Reinitialize database
    reinitialize_database()
    
    # Success message
    print("\n" + "="*70)
    print("✅ RESET COMPLETE!")
    print("="*70)
    print("\nYour Sulambi VMS has been reset to factory defaults.")
    print("\n📝 Default Login Credentials:")
    print("   Admin Account:")
    print("   - Username: Admin")
    print("   - Password: sulambi@2024")
    print("\n   Officer Account:")
    print("   - Username: Sulambi-Officer")
    print("   - Password: password@2024")
    
    if backup_path:
        print(f"\n💾 Backup saved at: {backup_path}")
        print("   (You can restore from this backup if needed)")
    
    print("\n🚀 You can now start the server with fresh data!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
















































