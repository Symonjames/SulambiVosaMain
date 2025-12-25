
import sqlite3

print("Testing database connection...")
conn = sqlite3.connect('app/database/database.db')
print("Connected successfully")

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables found: {len(tables)}")
print("Table names:", [table[0] for table in tables])

# Check evaluation table specifically
if any('evaluation' in table for table in tables):
    cursor.execute("SELECT COUNT(*) FROM evaluation;")
    count = cursor.fetchone()[0]
    print(f"Evaluation table has {count} records")
else:
    print("Evaluation table not found")

conn.close()
print("Database check completed")



























































