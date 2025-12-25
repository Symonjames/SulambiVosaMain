"""
Diagnostic script to check if member-app.xlsx can be read
"""

import os
import sys

print("=" * 70)
print("EXCEL FILE DIAGNOSTIC TOOL")
print("=" * 70)

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

print(f"\n1. Checking script location: {SCRIPT_DIR}")
print(f"2. Checking data directory: {DATA_DIR}")

# Check if data directory exists
if not os.path.exists(DATA_DIR):
    print(f"❌ Data directory does not exist: {DATA_DIR}")
    sys.exit(1)
else:
    print(f"✓ Data directory exists")

# List all files in data directory
print(f"\n3. Files in data directory:")
files_in_data = os.listdir(DATA_DIR)
for file in files_in_data:
    file_path = os.path.join(DATA_DIR, file)
    file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
    print(f"   - {file} ({file_size:,} bytes)")

# Check for Excel files with different names (including with spaces)
possible_names = [
    "member-app.xlsx",
    "member- app.xlsx",  # With space
    "member app.xlsx",   # With space, no dash
    "members-app.xlsx", 
    "member_app.xlsx",
    "members_app.xlsx"
]

print(f"\n4. Checking for Excel files:")
excel_file_found = None
for name in possible_names:
    file_path = os.path.join(DATA_DIR, name)
    if os.path.exists(file_path):
        print(f"   ✓ Found: {name}")
        excel_file_found = file_path
    else:
        print(f"   ✗ Not found: {name}")

if not excel_file_found:
    print(f"\n❌ No Excel file found with any of the expected names!")
    print(f"   Please ensure the file exists in: {DATA_DIR}")
    sys.exit(1)

# Try to read the Excel file
print(f"\n5. Attempting to read Excel file: {excel_file_found}")

try:
    import pandas as pd
    print(f"   ✓ pandas library is installed")
except ImportError:
    print(f"   ❌ pandas library is NOT installed")
    print(f"   Install it with: pip install pandas openpyxl")
    sys.exit(1)

try:
    import openpyxl
    print(f"   ✓ openpyxl library is installed")
except ImportError:
    print(f"   ⚠️  openpyxl library is NOT installed (may cause issues)")
    print(f"   Install it with: pip install openpyxl")

try:
    print(f"   Reading Excel file...")
    df = pd.read_excel(excel_file_found)
    print(f"   ✓ Successfully read Excel file!")
    print(f"   - Total rows: {len(df)}")
    print(f"   - Total columns: {len(df.columns)}")
    print(f"\n6. Column names in Excel file:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    print(f"\n7. First few rows preview:")
    print(df.head(3).to_string())
    
    print(f"\n✓ Excel file is readable and contains data!")
    
except Exception as e:
    print(f"   ❌ Error reading Excel file: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    print(f"\n   Full error details:")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)

