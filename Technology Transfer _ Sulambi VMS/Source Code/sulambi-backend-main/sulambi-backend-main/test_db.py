import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")

def test_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if accounts table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
        if cursor.fetchone():
            print("✓ Accounts table exists")
            
            # Check accounts data
            cursor.execute("SELECT * FROM accounts")
            accounts = cursor.fetchall()
            print(f"✓ Found {len(accounts)} accounts in database:")
            for account in accounts:
                print(f"  - ID: {account[0]}, Username: {account[1]}, Type: {account[3]}")
        else:
            print("✗ Accounts table does not exist")
            
        conn.close()
        print("✓ Database connection successful")
        
    except Exception as e:
        print(f"✗ Database error: {e}")

if __name__ == "__main__":
    test_database()
