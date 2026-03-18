import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "app/database/database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check satisfaction surveys for event 16
cursor.execute("""
    SELECT eventId, eventType, respondentType, overallSatisfaction, 
           volunteerRating, beneficiaryRating, comment
    FROM satisfactionSurveys 
    WHERE eventId = 16 AND eventType = 'internal'
""")
rows = cursor.fetchall()

print(f"Found {len(rows)} satisfaction surveys for event 16 (ecaluation form):")
for r in rows:
    print(f"  {r[2]}: Overall={r[3]}, Vol={r[4]}, Ben={r[5]}, Comment={r[6][:50] if r[6] else 'None'}...")

# Check all satisfaction surveys
cursor.execute("SELECT COUNT(*) FROM satisfactionSurveys")
total = cursor.fetchone()[0]
print(f"\nTotal satisfaction surveys in database: {total}")

conn.close()

















