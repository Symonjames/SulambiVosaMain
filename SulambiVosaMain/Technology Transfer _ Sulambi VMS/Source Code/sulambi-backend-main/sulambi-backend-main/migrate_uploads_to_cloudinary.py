#!/usr/bin/env python3
"""
Migrate local uploads to Cloudinary
This script:
1. Uploads all files from the uploads folder to Cloudinary
2. Updates database references from local paths to Cloudinary URLs
3. Creates a mapping file for rollback if needed
4. Preserves all existing references
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from datetime import datetime

# Import database connection utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))
from app.database.connection import cursorInstance, convert_placeholders, quote_identifier

# Load environment variables
load_dotenv()

# Uploads folder path
UPLOADS_DIR = os.path.join("uploads")

# Mapping file for rollback
MAPPING_FILE = "cloudinary_migration_mapping.json"

def configure_cloudinary():
    """Configure Cloudinary with environment variables"""
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )
    
    # Verify configuration
    if not all([os.getenv("CLOUDINARY_CLOUD_NAME"), 
                os.getenv("CLOUDINARY_API_KEY"), 
                os.getenv("CLOUDINARY_API_SECRET")]):
        raise Exception(
            "Cloudinary configuration missing! Please set:\n"
            "- CLOUDINARY_CLOUD_NAME\n"
            "- CLOUDINARY_API_KEY\n"
            "- CLOUDINARY_API_SECRET"
        )
    
    print("[OK] Cloudinary configured successfully")

def upload_file_to_cloudinary(file_path, folder="uploads"):
    """
    Upload a file to Cloudinary
    Returns the Cloudinary URL
    """
    try:
        with open(file_path, 'rb') as f:
            result = cloudinary.uploader.upload(
                f,
                folder=folder,
                resource_type="auto",  # Auto-detect type (image, pdf, etc.)
                overwrite=False,
                use_filename=True,
                unique_filename=True
            )
        
        cloudinary_url = result.get('secure_url') or result.get('url')
        if not cloudinary_url:
            raise Exception("Cloudinary upload succeeded but no URL was returned")
        
        return cloudinary_url
    except Exception as e:
        print(f"  [ERROR] Error uploading {file_path}: {e}")
        raise

def find_database_references(cursor, conn, filename, is_postgresql=False):
    """
    Find all database references to a filename
    Returns list of (table, column, row_id, current_value) tuples
    """
    references = []
    
    # Clean filename for searching (handle both with and without uploads/ prefix)
    search_patterns = [
        filename,
        f"uploads/{filename}",
        f"uploads\\{filename}",
        filename.replace("/", "\\"),
        filename.replace("\\", "/")
    ]
    
    # Tables and columns that store file paths
    file_path_tables = {
        'requirements': ['medCert', 'waiver', 'curriculum', 'destination', 'firstAid', 'fees'],
        'internalReport': ['photos'],
        'externalReport': ['photos']
    }
    
    for table_name, columns in file_path_tables.items():
        quoted_table = quote_identifier(table_name)
        
        # Get column list once (with proper error handling)
        existing_columns = []
        try:
            if is_postgresql:
                # PostgreSQL: check table exists and get columns
                # Handle case sensitivity - PostgreSQL stores unquoted names in lowercase
                # Use convert_placeholders to convert ? to %s for PostgreSQL
                query = """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE LOWER(table_name) = LOWER(%s)
                    ORDER BY column_name
                """
                cursor.execute(query, (table_name,))
                existing_columns = [row[0] for row in cursor.fetchall()]
            else:
                # SQLite: use PRAGMA
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = [col[1] for col in cursor.fetchall()]
        except Exception as e:
            # Rollback transaction on error (PostgreSQL) and continue
            if is_postgresql:
                try:
                    conn.rollback()
                except:
                    pass
            print(f"    [WARNING] Error checking table {table_name}: {e}")
            # Skip this table, continue with next
            continue
        
        # Process each column
        for column in columns:
            # Check if column exists (case-insensitive for PostgreSQL)
            column_exists = False
            actual_column_name = column
            if is_postgresql:
                # PostgreSQL columns might be case-sensitive
                for col in existing_columns:
                    if col.lower() == column.lower():
                        column_exists = True
                        actual_column_name = col  # Use actual case
                        break
            else:
                column_exists = column in existing_columns
            
            if not column_exists:
                continue
            
            quoted_column = quote_identifier(actual_column_name) if is_postgresql else actual_column_name
            
            # Search for filename in column
            try:
                for pattern in search_patterns:
                    if is_postgresql:
                        query = f"SELECT id, {quoted_column} FROM {quoted_table} WHERE {quoted_column}::text LIKE %s"
                        cursor.execute(query, (f"%{pattern}%",))
                    else:
                        query = f"SELECT id, {actual_column_name} FROM {table_name} WHERE {actual_column_name} LIKE ?"
                        cursor.execute(query, (f"%{pattern}%",))
                    
                    rows = cursor.fetchall()
                    
                    for row_id, value in rows:
                        if value and pattern in str(value):
                            # Avoid duplicates
                            ref_key = (table_name, actual_column_name, row_id)
                            if not any(r[:3] == ref_key for r in references):
                                references.append((table_name, actual_column_name, row_id, value))
            except Exception as e:
                # Rollback on error and continue
                if is_postgresql:
                    try:
                        conn.rollback()
                    except:
                        pass
                print(f"    [WARNING] Error searching {table_name}.{actual_column_name}: {e}")
                continue
    
    return references

def update_references_in_db(cursor, conn, old_path, new_url, mapping_file, is_postgresql=False):
    """
    Update all database references from old_path to new_url
    Handles both single values and JSON arrays
    """
    updated_count = 0
    
    # Find all references (pass conn for rollback handling)
    filename = old_path.replace("uploads/", "").replace("uploads\\", "")
    references = find_database_references(cursor, conn, filename, is_postgresql)
    
    if not references:
        print(f"  [INFO] No database references found for {filename} (may be UI-only or unused file)")
        return updated_count
    
    for table, column, row_id, current_value in references:
        try:
            new_value = None
            
            # Check if value is a JSON array (for photos columns)
            if column == 'photos' and (current_value.startswith('[') or current_value.startswith('"')):
                try:
                    photos_array = json.loads(current_value) if isinstance(current_value, str) else current_value
                    if isinstance(photos_array, list):
                        # Replace matching paths in array
                        updated_array = []
                        for photo in photos_array:
                            if old_path in str(photo) or filename in str(photo):
                                updated_array.append(new_url)
                            else:
                                updated_array.append(photo)
                        new_value = json.dumps(updated_array)
                    else:
                        # Single value in JSON format
                        new_value = new_url if (old_path in str(current_value) or filename in str(current_value)) else current_value
                except:
                    # Not valid JSON, treat as string
                    new_value = new_url if (old_path in str(current_value) or filename in str(current_value)) else current_value
            else:
                # Single value replacement
                if old_path in str(current_value) or filename in str(current_value):
                    new_value = str(current_value).replace(old_path, new_url)
                    new_value = new_value.replace(f"uploads/{filename}", new_url)
                    new_value = new_value.replace(f"uploads\\{filename}", new_url)
                else:
                    continue
            
            if new_value and new_value != current_value:
                # Update database
                quoted_table = quote_identifier(table)
                quoted_column = quote_identifier(column) if is_postgresql else column
                
                # Update database with proper error handling
                try:
                    if is_postgresql:
                        query = f"UPDATE {quoted_table} SET {quoted_column} = %s WHERE id = %s"
                        cursor.execute(query, (new_value, row_id))
                    else:
                        query = f"UPDATE {table} SET {column} = ? WHERE id = ?"
                        cursor.execute(query, (new_value, row_id))
                except Exception as e:
                    # Rollback on error (PostgreSQL)
                    if is_postgresql:
                        try:
                            conn.rollback()
                        except:
                            pass
                    print(f"    [ERROR] Error updating {table}.{column} (id: {row_id}): {e}")
                    continue
                
                # Save to mapping file
                mapping_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'table': table,
                    'column': column,
                    'row_id': row_id,
                    'old_value': current_value,
                    'new_value': new_value,
                    'file': filename
                }
                
                with open(mapping_file, 'a') as f:
                    f.write(json.dumps(mapping_entry) + '\n')
                
                updated_count += 1
                print(f"    ✓ Updated {table}.{column} (id: {row_id})")
        
        except Exception as e:
            print(f"    ❌ Error updating {table}.{column} (id: {row_id}): {e}")
            continue
    
    return updated_count

def migrate_uploads_to_cloudinary():
    """
    Main migration function
    """
    print("=" * 60)
    print("MIGRATING UPLOADS TO CLOUDINARY")
    print("=" * 60)
    print()
    
    # Configure Cloudinary
    try:
        configure_cloudinary()
    except Exception as e:
        print(f"[ERROR] {e}")
        return
    
    # Check if uploads folder exists
    if not os.path.exists(UPLOADS_DIR):
        print(f"[ERROR] Uploads folder not found: {UPLOADS_DIR}")
        return
    
    # Initialize mapping file
    if os.path.exists(MAPPING_FILE):
        os.remove(MAPPING_FILE)
    with open(MAPPING_FILE, 'w') as f:
        f.write('')  # Create empty file
    
    # Connect to database (supports both SQLite and PostgreSQL)
    try:
        conn, cursor = cursorInstance()
        from app.database.connection import DATABASE_URL
        is_postgresql = DATABASE_URL and DATABASE_URL.startswith('postgresql://')
        print(f"[OK] Connected to {'PostgreSQL' if is_postgresql else 'SQLite'} database")
    except Exception as e:
        print(f"[ERROR] Error connecting to database: {e}")
        return
    
    # Get all files from uploads folder
    upload_files = []
    for root, dirs, files in os.walk(UPLOADS_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            # Get relative path from uploads folder
            rel_path = os.path.relpath(file_path, UPLOADS_DIR).replace("\\", "/")
            upload_files.append((rel_path, file_path))
    
    if not upload_files:
        print("[WARNING] No files found in uploads folder")
        conn.close()
        return
    
    print(f"Found {len(upload_files)} file(s) to migrate\n")
    
    uploaded_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    # Process each file
    for i, (rel_path, file_path) in enumerate(upload_files, 1):
        print(f"[{i}/{len(upload_files)}] Processing: {rel_path}")
        
        try:
            # Check if file already exists in database as Cloudinary URL
            filename = rel_path
            references = find_database_references(cursor, conn, filename, is_postgresql)
            
            # Check if already migrated (check if any reference is already a Cloudinary URL)
            already_cloudinary = False
            for table, column, row_id, value in references:
                if value and 'res.cloudinary.com' in str(value):
                    already_cloudinary = True
                    break
            
            if already_cloudinary:
                print(f"  [SKIP] Already using Cloudinary URL, skipping")
                skipped_count += 1
                continue
            
            # Upload to Cloudinary
            print(f"  [UPLOAD] Uploading to Cloudinary...")
            cloudinary_url = upload_file_to_cloudinary(file_path, folder="uploads")
            print(f"  [OK] Uploaded: {cloudinary_url[:60]}...")
            uploaded_count += 1
            
            # Update database references
            print(f"  [UPDATE] Updating database references...")
            local_path = f"uploads/{rel_path}"
            updated = update_references_in_db(cursor, conn, local_path, cloudinary_url, MAPPING_FILE, is_postgresql)
            updated_count += updated
            
            if updated > 0:
                # Commit changes after each successful update
                try:
                    conn.commit()
                    print(f"  [OK] Updated {updated} database reference(s)")
                except Exception as e:
                    print(f"  [ERROR] Error committing changes: {e}")
                    try:
                        conn.rollback()
                    except:
                        pass
            else:
                # Save UI-only file to mapping file for frontend update script
                mapping_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'table': None,
                    'column': None,
                    'row_id': None,
                    'old_value': local_path,
                    'new_value': cloudinary_url,
                    'file': rel_path,
                    'type': 'ui-only'  # Mark as UI-only file
                }
                
                with open(MAPPING_FILE, 'a') as f:
                    f.write(json.dumps(mapping_entry) + '\n')
                
                print(f"  [INFO] File uploaded but no database references found (may be UI-only or unused file)")
                print(f"  [INFO] Saved to mapping file for frontend update script")
        
        except Exception as e:
            print(f"  [ERROR] Error processing {rel_path}: {e}")
            error_count += 1
            continue
        
        print()
    
    # Summary
    print("=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"[OK] Files uploaded to Cloudinary: {uploaded_count}")
    print(f"[UPDATE] Database references updated: {updated_count}")
    print(f"[SKIP] Files skipped (already migrated): {skipped_count}")
    print(f"[INFO] UI-only/unused files (no DB refs): {uploaded_count - updated_count}")
    print(f"[ERROR] Errors: {error_count}")
    print(f"[INFO] Mapping file saved: {MAPPING_FILE}")
    print()
    
    if uploaded_count > 0:
        print("[WARNING] IMPORTANT:")
        print("1. Review the database to ensure all references are updated correctly")
        print("2. Test the application to verify images appear correctly")
        print("3. UI-only files were uploaded but may not have database references (this is normal)")
        print("4. The mapping file contains all changes for potential rollback")
        print("5. Local files in uploads/ folder can be deleted after verification")
        print()
    
    conn.close()

if __name__ == "__main__":
    migrate_uploads_to_cloudinary()
