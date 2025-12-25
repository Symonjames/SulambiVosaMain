import os
import sys
sys.path.append('.')

# Set environment variable
os.environ['DB_PATH'] = 'app/database/database.db'

print("Testing database connection...")
try:
    from app.database.connection import cursorInstance
    conn, cursor = cursorInstance()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [table[0] for table in tables])
    
    # Check if evaluation table has data
    cursor.execute("SELECT COUNT(*) FROM evaluation;")
    eval_count = cursor.fetchone()[0]
    print(f"Evaluation table has {eval_count} records")
    
    # Check if requirements table has data
    cursor.execute("SELECT COUNT(*) FROM requirements;")
    req_count = cursor.fetchone()[0]
    print(f"Requirements table has {req_count} records")
    
    conn.close()
    print("Database connection successful")
except Exception as e:
    print(f"Database error: {e}")
    import traceback
    traceback.print_exc()

































































