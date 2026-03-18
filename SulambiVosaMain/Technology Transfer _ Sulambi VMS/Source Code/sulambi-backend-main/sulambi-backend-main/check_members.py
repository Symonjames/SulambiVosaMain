import sqlite3

try:
    conn = sqlite3.connect('app/database/database.db')
    cursor = conn.cursor()
    
    # Check accounts table
    cursor.execute("SELECT COUNT(*) FROM accounts")
    total_accounts = cursor.fetchone()[0]
    print('Total accounts:', total_accounts)
    
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE accountType = 'member'")
    member_accounts = cursor.fetchone()[0]
    print('Member accounts:', member_accounts)
    
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE accountType = 'officer'")
    officer_accounts = cursor.fetchone()[0]
    print('Officer accounts:', officer_accounts)
    
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE accountType = 'admin'")
    admin_accounts = cursor.fetchone()[0]
    print('Admin accounts:', admin_accounts)
    
    # Check membership table
    cursor.execute("SELECT COUNT(*) FROM membership")
    total_members = cursor.fetchone()[0]
    print('Total membership applications:', total_members)
    
    cursor.execute("SELECT COUNT(*) FROM membership WHERE accepted = 1")
    accepted_members = cursor.fetchone()[0]
    print('Accepted members:', accepted_members)
    
    cursor.execute("SELECT COUNT(*) FROM membership WHERE accepted = 0")
    rejected_members = cursor.fetchone()[0]
    print('Rejected members:', rejected_members)
    
    cursor.execute("SELECT COUNT(*) FROM membership WHERE accepted IS NULL")
    pending_members = cursor.fetchone()[0]
    print('Pending members:', pending_members)
    
    # Show sample accounts
    cursor.execute("SELECT username, accountType, active FROM accounts LIMIT 10")
    accounts = cursor.fetchall()
    print('\nSample accounts:')
    for account in accounts:
        print(f'  {account[0]} - {account[1]} - Active: {account[2]}')
    
    # Show sample members
    cursor.execute("SELECT username, fullname, accepted, active FROM membership LIMIT 10")
    members = cursor.fetchall()
    print('\nSample members:')
    for member in members:
        print(f'  {member[0]} - {member[1]} - Accepted: {member[2]} - Active: {member[3]}')
    
    conn.close()
    print('\nMember credentials check completed!')
    
except Exception as e:
    print(f'Error checking member credentials: {e}')