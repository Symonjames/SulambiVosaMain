import sqlite3

try:
    conn = sqlite3.connect('app/database/database.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tables:', tables)
    
    # Check external reports
    cursor.execute("SELECT COUNT(*) FROM externalReport")
    external_count = cursor.fetchone()[0]
    print('External reports:', external_count)
    
    # Check internal reports
    cursor.execute("SELECT COUNT(*) FROM internalReport")
    internal_count = cursor.fetchone()[0]
    print('Internal reports:', internal_count)
    
    # Check if there are any reports with photos
    cursor.execute("SELECT id, photos FROM externalReport WHERE photos IS NOT NULL AND photos != ''")
    external_with_photos = cursor.fetchall()
    print('External reports with photos:', external_with_photos)
    
    cursor.execute("SELECT id, photos FROM internalReport WHERE photos IS NOT NULL AND photos != ''")
    internal_with_photos = cursor.fetchall()
    print('Internal reports with photos:', internal_with_photos)
    
    conn.close()
    print('Database check completed successfully!')
    
except Exception as e:
    print(f'Error checking database: {e}')
