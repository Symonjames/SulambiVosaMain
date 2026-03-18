
import sqlite3
import os

print("Current directory:", os.getcwd())
print("Database file exists:", os.path.exists('app/database/database.db'))

try:
    conn = sqlite3.connect('app/database/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables:', tables)
    
    # Check if evaluation table exists
    if ('evaluation',) in tables:
        cursor.execute("SELECT COUNT(*) FROM evaluation;")
        count = cursor.fetchone()[0]
        print(f'Evaluation table has {count} records')
    else:
        print('Evaluation table does not exist')
        
    conn.close()
    print("Database check completed successfully")
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
