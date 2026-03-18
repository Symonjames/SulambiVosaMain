import sqlite3

# Connect to the database
conn = sqlite3.connect('app/database/database.db')
cursor = conn.cursor()

print("=== EXTERNAL EVENTS ===")
cursor.execute("SELECT id, title, status, durationStart, durationEnd FROM externalEvents")
external_events = cursor.fetchall()
print(f"Total external events: {len(external_events)}")
for event in external_events:
    print(f"ID: {event[0]}, Title: {event[1]}, Status: {event[2]}, Start: {event[3]}, End: {event[4]}")

print("\n=== INTERNAL EVENTS ===")
cursor.execute("SELECT id, title, status, durationStart, durationEnd FROM internalEvents")
internal_events = cursor.fetchall()
print(f"Total internal events: {len(internal_events)}")
for event in internal_events:
    print(f"ID: {event[0]}, Title: {event[1]}, Status: {event[2]}, Start: {event[3]}, End: {event[4]}")

print("\n=== STATUS COUNTS ===")
cursor.execute("SELECT status, COUNT(*) FROM externalEvents GROUP BY status")
external_status = cursor.fetchall()
print("External events by status:")
for status in external_status:
    print(f"  {status[0]}: {status[1]}")

cursor.execute("SELECT status, COUNT(*) FROM internalEvents GROUP BY status")
internal_status = cursor.fetchall()
print("Internal events by status:")
for status in internal_status:
    print(f"  {status[0]}: {status[1]}")

conn.close()
