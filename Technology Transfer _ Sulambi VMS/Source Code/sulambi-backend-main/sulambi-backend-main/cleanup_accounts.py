import sqlite3

try:
    conn = sqlite3.connect('app/database/database.db')
    cursor = conn.cursor()
    
    print("Before cleanup:")
    cursor.execute("SELECT COUNT(*) FROM accounts")
    total_before = cursor.fetchone()[0]
    print(f"Total accounts: {total_before}")
    
    # Keep only the first occurrence of each username
    cursor.execute("""
        DELETE FROM accounts 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM accounts 
            GROUP BY username
        )
    """)
    
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"\nCleanup completed:")
    print(f"Deleted {deleted_count} duplicate accounts")
    
    print("\nAfter cleanup:")
    cursor.execute("SELECT COUNT(*) FROM accounts")
    total_after = cursor.fetchone()[0]
    print(f"Total accounts: {total_after}")
    
    # Show remaining accounts
    cursor.execute("SELECT id, username, accountType FROM accounts ORDER BY id")
    accounts = cursor.fetchall()
    print("\nRemaining accounts:")
    for account in accounts:
        print(f"  ID: {account[0]} - {account[1]} ({account[2]})")
    
    conn.close()
    print("\nDatabase cleanup completed successfully!")
    
except Exception as e:
    print(f"Error during cleanup: {e}")





