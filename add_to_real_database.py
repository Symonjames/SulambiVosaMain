#!/usr/bin/env python3
"""
Add members, requirements, and evaluations to the REAL database
Uses the same connection method as the backend
"""

import os
import sys

# Add backend directory to path
backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
sys.path.insert(0, backend_dir)

# Load environment variables (same as backend)
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

# Use backend's connection method
from app.database.connection import cursorInstance

print("=" * 60)
print("ADDING DATA TO REAL BACKEND DATABASE")
print("=" * 60)

# Get connection using backend's method
conn, cursor = cursorInstance()

# Check current data
cursor.execute("SELECT COUNT(*) FROM membership")
current_members = cursor.fetchone()[0]
print(f"Current members: {current_members}")

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
current_reqs = cursor.fetchone()[0]
print(f"Current accepted requirements: {current_reqs}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
current_evals = cursor.fetchone()[0]
print(f"Current finalized evaluations: {current_evals}")

# Import the add functions
import importlib.util

# Load and run add_requirements_to_members with backend connection
print("\n" + "=" * 60)
print("Adding requirements...")
print("=" * 60)

# Read the script and modify it to use our connection
with open('add_requirements_to_members.py', 'r') as f:
    req_script = f.read()

# Execute with modified connection
exec_globals = {
    '__name__': '__main__',
    'conn': conn,
    'cursor': cursor,
    'os': os,
    'random': __import__('random'),
    'sqlite3': __import__('sqlite3')
}

# Replace DB connection in script
req_script_modified = req_script.replace(
    'conn = sqlite3.connect(DB_PATH)',
    '# conn = sqlite3.connect(DB_PATH)  # Using provided connection'
).replace(
    'cursor = conn.cursor()',
    '# cursor = conn.cursor()  # Using provided cursor'
)

# Actually, let's just run the existing scripts but modify their DB_PATH
# First, let's check what DB_PATH the backend is using
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(backend_dir, DB_PATH)

print(f"Backend database path: {DB_PATH}")
print(f"Database exists: {os.path.exists(DB_PATH)}")

conn.close()

# Now run the scripts with the correct DB_PATH
print("\nRunning add_requirements_to_members.py with correct DB path...")
os.environ['DB_PATH'] = DB_PATH

# Modify the scripts to use environment variable
import subprocess

# Create modified versions that use DB_PATH from env
with open('add_requirements_to_members.py', 'r') as f:
    req_content = f.read()

# Replace hardcoded path with env variable
req_content = req_content.replace(
    'DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")',
    'DB_PATH = os.getenv("DB_PATH") or os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")'
)

with open('add_requirements_to_members_real.py', 'w') as f:
    f.write(req_content)

with open('add_satisfaction_evaluations.py', 'r') as f:
    eval_content = f.read()

eval_content = eval_content.replace(
    'DB_PATH = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")',
    'DB_PATH = os.getenv("DB_PATH") or os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main", "app", "database", "database.db")'
)

with open('add_satisfaction_evaluations_real.py', 'w') as f:
    f.write(eval_content)

# Run the scripts
print("\n1. Adding requirements...")
result1 = subprocess.run([sys.executable, 'add_requirements_to_members_real.py'], 
                        env={**os.environ, 'DB_PATH': DB_PATH}, 
                        capture_output=True, text=True)
print(result1.stdout)
if result1.stderr:
    print("Errors:", result1.stderr)

print("\n2. Adding evaluations...")
result2 = subprocess.run([sys.executable, 'add_satisfaction_evaluations_real.py'],
                        env={**os.environ, 'DB_PATH': DB_PATH},
                        capture_output=True, text=True)
print(result2.stdout)
if result2.stderr:
    print("Errors:", result2.stderr)

# Cleanup
os.remove('add_requirements_to_members_real.py')
os.remove('add_satisfaction_evaluations_real.py')

# Final verification
print("\n" + "=" * 60)
print("FINAL VERIFICATION")
print("=" * 60)

conn, cursor = cursorInstance()

cursor.execute("SELECT COUNT(*) FROM membership WHERE active = 1 AND accepted = 1")
members = cursor.fetchone()[0]
print(f"Active & accepted members: {members}")

cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
reqs = cursor.fetchone()[0]
print(f"Accepted requirements: {reqs}")

cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
evals = cursor.fetchone()[0]
print(f"Finalized evaluations: {evals}")

cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
""")
analytics_ready = cursor.fetchone()[0]
print(f"Members ready for analytics: {analytics_ready}")

conn.close()

print("\n" + "=" * 60)
if analytics_ready > 0:
    print("✅ DATA SUCCESSFULLY ADDED TO REAL DATABASE!")
else:
    print("❌ DATA NOT READY - Check errors above")
print("=" * 60)

















