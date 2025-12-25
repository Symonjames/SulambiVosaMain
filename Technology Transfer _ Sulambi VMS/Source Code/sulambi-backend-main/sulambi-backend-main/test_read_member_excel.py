"""
Test script to read and display member-app.xlsx file
"""

import os
import pandas as pd
import sys

# Get the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(SCRIPT_DIR, "data", "member-app.xlsx")

print("=" * 70)
print("TESTING MEMBER-APP.XLSX FILE READ")
print("=" * 70)

# Check if file exists
if not os.path.exists(EXCEL_FILE):
    print(f"[ERROR] File not found: {EXCEL_FILE}")
    print(f"\nLooking for alternative locations...")
    
    # Try alternative paths
    alt_paths = [
        os.path.join(SCRIPT_DIR, "member-app.xlsx"),
        os.path.join(SCRIPT_DIR, "data", "member_app.xlsx"),
        os.path.join(SCRIPT_DIR, "data", "member- app.xlsx"),
    ]
    
    for alt_path in alt_paths:
        if os.path.exists(alt_path):
            print(f"[OK] Found at: {alt_path}")
            EXCEL_FILE = alt_path
            break
    else:
        print("[ERROR] File not found in any location")
        sys.exit(1)

print(f"\n[OK] File found: {EXCEL_FILE}")
print(f"  File size: {os.path.getsize(EXCEL_FILE):,} bytes")

# Try to read the file
try:
    print(f"\nReading Excel file...")
    df = pd.read_excel(EXCEL_FILE)
    
    print(f"[OK] Successfully read Excel file!")
    print(f"\nFile Information:")
    print(f"  - Total rows: {len(df)}")
    print(f"  - Total columns: {len(df.columns)}")
    
    print(f"\nColumn Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # Check for key columns needed for membership
    key_columns = [
        "Name (Last Name, First Name, Middle Initial)",
        "Email Address",
        "Gsuite Email",
        "Sr-Code",
        "Age",
        "Sex",
        "Campus",
        "College/Department"
    ]
    
    print(f"\nChecking for key columns:")
    missing_columns = []
    for col in key_columns:
        if col in df.columns:
            print(f"  [OK] {col}")
        else:
            print(f"  [MISSING] {col} - MISSING")
            missing_columns.append(col)
    
    if missing_columns:
        print(f"\n⚠️  Warning: {len(missing_columns)} key columns are missing!")
    
    # Show first few rows
    print(f"\nFirst 3 rows preview:")
    print(df.head(3).to_string())
    
    # Show summary statistics
    print(f"\nSummary Statistics:")
    print(f"  - Non-null name entries: {df['Name (Last Name, First Name, Middle Initial)'].notna().sum()}")
    print(f"  - Non-null email entries: {df['Email Address'].notna().sum() if 'Email Address' in df.columns else 0}")
    print(f"  - Non-null age entries: {df['Age'].notna().sum() if 'Age' in df.columns else 0}")
    
    print(f"\n[OK] Excel file is readable and contains data!")
    
except ImportError as e:
    print(f"[ERROR] Missing required library: {e}")
    print(f"   Install with: pip install pandas openpyxl")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Error reading Excel file: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    print(f"\n   Full error details:")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

