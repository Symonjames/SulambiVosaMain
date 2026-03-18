import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Search for danny or burke
cursor.execute("""
    SELECT id, email, fullname, username 
    FROM membership 
    WHERE email LIKE '%danny%' 
       OR email LIKE '%burke%' 
       OR fullname LIKE '%danny%' 
       OR fullname LIKE '%burke%'
""")
results = cursor.fetchall()

if results:
    print("Found members matching 'danny' or 'burke':")
    for r in results:
        print(f"  ID: {r[0]}, Email: {r[1]}, Name: {r[2]}, Username: {r[3]}")
else:
    print("No members found matching 'danny' or 'burke'")
    print("\nSearching for exact email 'dannyburke@gmail.com'...")
    cursor.execute("SELECT id, email, fullname, username FROM membership WHERE email = ?", ("dannyburke@gmail.com",))
    exact = cursor.fetchone()
    if exact:
        print(f"  Found: ID: {exact[0]}, Email: {exact[1]}, Name: {exact[2]}, Username: {exact[3]}")
    else:
        print("  Not found")

conn.close()

















