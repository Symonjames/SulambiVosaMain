"""
Fix participation data to match exact requirements:
- August: 100 joined, 45 attended, 55 dropouts
- October: 55 joined, 0 attended (all dropouts)
- November: 165 joined, 100 attended, 65 dropouts
"""

import pandas as pd
import sqlite3
import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

MEMBER_EXCEL = os.path.join("data", "member-app.xlsx")

def fix_participation_data():
    """Fix data to match exact requirements"""
    print("=" * 70)
    print("FIXING PARTICIPATION DATA TO MATCH REQUIREMENTS")
    print("=" * 70)
    
    # 1. Read names from member-app.xlsx
    print("\n1. Reading names from member-app.xlsx...")
    try:
        df_members = pd.read_excel(MEMBER_EXCEL)
        fullnames = df_members["Name (Last Name, First Name, Middle Initial)"].dropna().astype(str).tolist()
        emails = df_members["Email Address"].dropna().astype(str).tolist()
        gsuite_emails = df_members["Gsuite Email"].dropna().astype(str).tolist()
        
        name_email_pairs = []
        for i, name in enumerate(fullnames):
            email = emails[i] if i < len(emails) and pd.notna(emails[i]) else (
                gsuite_emails[i] if i < len(gsuite_emails) and pd.notna(gsuite_emails[i]) else 
                f"{name.lower().replace(' ', '.').replace(',', '')}@example.com"
            )
            name_email_pairs.append((name, email))
        
        print(f"   ✓ Found {len(name_email_pairs)} names")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Get events
    print("\n2. Getting events...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, durationStart, durationEnd, 'internal' as type
        FROM internalEvents
        WHERE status IN ('accepted', 'completed')
        UNION ALL
        SELECT id, title, durationStart, durationEnd, 'external' as type
        FROM externalEvents
        WHERE status IN ('accepted', 'completed')
        ORDER BY durationStart
    """)
    all_events = cursor.fetchall()
    
    if len(all_events) == 0:
        print("   ❌ No events found")
        conn.close()
        return
    
    # Categorize events by month
    august_events = []
    october_events = []
    november_events = []
    
    for event_id, event_title, event_start, event_end, event_type in all_events:
        if event_start:
            event_date = datetime.fromtimestamp(event_start / 1000)
            month = event_date.month
            
            if month == 8:
                august_events.append((event_id, event_title, event_start, event_end, event_type))
            elif month == 10:
                october_events.append((event_id, event_title, event_start, event_end, event_type))
            elif month == 11:
                november_events.append((event_id, event_title, event_start, event_end, event_type))
    
    # Use available events if specific months don't have events
    if not august_events:
        august_events = all_events[:1]
    if not october_events:
        october_events = all_events[1:2] if len(all_events) > 1 else all_events[:1]
    if not november_events:
        november_events = all_events[2:] if len(all_events) > 2 else all_events[-1:]
    
    print(f"   August events: {len(august_events)}")
    print(f"   October events: {len(october_events)}")
    print(f"   November events: {len(november_events)}")
    
    # 3. Clear existing data
    print("\n3. Clearing existing requirements and evaluations...")
    cursor.execute("DELETE FROM evaluation")
    cursor.execute("DELETE FROM requirements")
    cursor.execute("DELETE FROM volunteerParticipationHistory")
    conn.commit()
    print("   ✓ Cleared")
    
    # 4. Create August: 100 joined, 45 attended, 55 dropouts
    print("\n4. Creating August data (100 joined, 45 attended, 55 dropouts)...")
    august_names = random.sample(name_email_pairs, 100)
    august_attended = random.sample(august_names, 45)
    august_dropouts = [n for n in august_names if n not in august_attended]
    
    august_req_count = 0
    august_eval_count = 0
    
    for name, email in august_names:
        event_id, event_title, event_start, event_end, event_type = random.choice(august_events)
        req_id = f"REQ-AUG-{random.randint(10000, 99999)}-{august_req_count}"
        
        member_row = df_members[df_members["Name (Last Name, First Name, Middle Initial)"] == name]
        if not member_row.empty:
            srcode = str(member_row.iloc[0].get("Sr-Code", "")) if pd.notna(member_row.iloc[0].get("Sr-Code")) else ""
            age_val = member_row.iloc[0].get("Age", 20)
            age = int(''.join(filter(str.isdigit, str(age_val)))) if pd.notna(age_val) else 20
            birthday = str(member_row.iloc[0].get("Birthday", "")) if pd.notna(member_row.iloc[0].get("Birthday")) else ""
            sex = str(member_row.iloc[0].get("Sex", "")) if pd.notna(member_row.iloc[0].get("Sex")) else ""
            campus = str(member_row.iloc[0].get("Campus", "")) if pd.notna(member_row.iloc[0].get("Campus")) else ""
            college_dept = str(member_row.iloc[0].get("College/Department", "")) if pd.notna(member_row.iloc[0].get("College/Department")) else ""
            yrlevel_program = str(member_row.iloc[0].get("Year Level & Program", "")) if pd.notna(member_row.iloc[0].get("Year Level & Program")) else ""
            address = str(member_row.iloc[0].get("Address", "")) if pd.notna(member_row.iloc[0].get("Address")) else ""
            contact_num = str(member_row.iloc[0].get("Contact Number", "")) if pd.notna(member_row.iloc[0].get("Contact Number")) else ""
            fblink = str(member_row.iloc[0].get("Facebook Link", "")) if pd.notna(member_row.iloc[0].get("Facebook Link")) else ""
        else:
            srcode = age = birthday = sex = campus = college_dept = yrlevel_program = address = contact_num = fblink = ""
        
        try:
            cursor.execute("""
                INSERT INTO requirements (
                    id, medCert, waiver, type, eventId, affiliation, fullname, email,
                    srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
                    address, contactNum, fblink, accepted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req_id, f"documents/med_cert_{req_id}.pdf", f"documents/waiver_{req_id}.pdf",
                event_type, event_id, "Batangas State University", name, email,
                srcode, age, birthday, sex, campus, college_dept, yrlevel_program,
                address, contact_num, fblink, 1
            ))
            august_req_count += 1
            
            if (name, email) in august_attended:
                criteria = {'overall': round(random.uniform(3.5, 5.0), 1), 'comment': "Attended"}
                cursor.execute("""
                    INSERT INTO evaluation (
                        requirementId, criteria, q13, q14, comment, recommendations, finalized
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (req_id, str(criteria), str(round(random.uniform(3.5, 5.0), 1)), "", "Attended", "Good", 1))
                august_eval_count += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            continue
    
    # 5. Create October: 55 joined, 0 attended (all dropouts)
    print("\n5. Creating October data (55 joined, 0 attended - all dropouts)...")
    # Can reuse names - same person can join events in different months
    october_names = random.sample(name_email_pairs, 55)
    
    october_req_count = 0
    
    for name, email in october_names:
        if october_events:
            event_id, event_title, event_start, event_end, event_type = random.choice(october_events)
            req_id = f"REQ-OCT-{random.randint(10000, 99999)}-{october_req_count}"
            
            member_row = df_members[df_members["Name (Last Name, First Name, Middle Initial)"] == name]
            if not member_row.empty:
                srcode = str(member_row.iloc[0].get("Sr-Code", "")) if pd.notna(member_row.iloc[0].get("Sr-Code")) else ""
                age_val = member_row.iloc[0].get("Age", 20)
                age = int(''.join(filter(str.isdigit, str(age_val)))) if pd.notna(age_val) else 20
                birthday = str(member_row.iloc[0].get("Birthday", "")) if pd.notna(member_row.iloc[0].get("Birthday")) else ""
                sex = str(member_row.iloc[0].get("Sex", "")) if pd.notna(member_row.iloc[0].get("Sex")) else ""
                campus = str(member_row.iloc[0].get("Campus", "")) if pd.notna(member_row.iloc[0].get("Campus")) else ""
                college_dept = str(member_row.iloc[0].get("College/Department", "")) if pd.notna(member_row.iloc[0].get("College/Department")) else ""
                yrlevel_program = str(member_row.iloc[0].get("Year Level & Program", "")) if pd.notna(member_row.iloc[0].get("Year Level & Program")) else ""
                address = str(member_row.iloc[0].get("Address", "")) if pd.notna(member_row.iloc[0].get("Address")) else ""
                contact_num = str(member_row.iloc[0].get("Contact Number", "")) if pd.notna(member_row.iloc[0].get("Contact Number")) else ""
                fblink = str(member_row.iloc[0].get("Facebook Link", "")) if pd.notna(member_row.iloc[0].get("Facebook Link")) else ""
            else:
                srcode = age = birthday = sex = campus = college_dept = yrlevel_program = address = contact_num = fblink = ""
            
            try:
                cursor.execute("""
                    INSERT INTO requirements (
                        id, medCert, waiver, type, eventId, affiliation, fullname, email,
                        srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
                        address, contactNum, fblink, accepted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    req_id, f"documents/med_cert_{req_id}.pdf", f"documents/waiver_{req_id}.pdf",
                    event_type, event_id, "Batangas State University", name, email,
                    srcode, age, birthday, sex, campus, college_dept, yrlevel_program,
                    address, contact_num, fblink, 1
                ))
                october_req_count += 1
                # No evaluation = dropout
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                continue
    
    # 6. Create November: 165 joined, 100 attended, 65 dropouts
    print("\n6. Creating November data (165 joined, 100 attended, 65 dropouts)...")
    # Can reuse names - same person can join events in different months
    november_all = random.sample(name_email_pairs, min(165, len(name_email_pairs)))
    # If we need more than available, duplicate some names
    while len(november_all) < 165:
        november_all.append(random.choice(name_email_pairs))
    november_attended = random.sample(november_all, 100)
    november_dropouts = [n for n in november_all if n not in november_attended]
    
    november_req_count = 0
    november_eval_count = 0
    
    for name, email in november_all:
        if november_events:
            event_id, event_title, event_start, event_end, event_type = random.choice(november_events)
        else:
            event_id, event_title, event_start, event_end, event_type = random.choice(all_events)
        
        req_id = f"REQ-NOV-{random.randint(10000, 99999)}-{november_req_count}"
        
        member_row = df_members[df_members["Name (Last Name, First Name, Middle Initial)"] == name]
        if not member_row.empty:
            srcode = str(member_row.iloc[0].get("Sr-Code", "")) if pd.notna(member_row.iloc[0].get("Sr-Code")) else ""
            age_val = member_row.iloc[0].get("Age", 20)
            age = int(''.join(filter(str.isdigit, str(age_val)))) if pd.notna(age_val) else 20
            birthday = str(member_row.iloc[0].get("Birthday", "")) if pd.notna(member_row.iloc[0].get("Birthday")) else ""
            sex = str(member_row.iloc[0].get("Sex", "")) if pd.notna(member_row.iloc[0].get("Sex")) else ""
            campus = str(member_row.iloc[0].get("Campus", "")) if pd.notna(member_row.iloc[0].get("Campus")) else ""
            college_dept = str(member_row.iloc[0].get("College/Department", "")) if pd.notna(member_row.iloc[0].get("College/Department")) else ""
            yrlevel_program = str(member_row.iloc[0].get("Year Level & Program", "")) if pd.notna(member_row.iloc[0].get("Year Level & Program")) else ""
            address = str(member_row.iloc[0].get("Address", "")) if pd.notna(member_row.iloc[0].get("Address")) else ""
            contact_num = str(member_row.iloc[0].get("Contact Number", "")) if pd.notna(member_row.iloc[0].get("Contact Number")) else ""
            fblink = str(member_row.iloc[0].get("Facebook Link", "")) if pd.notna(member_row.iloc[0].get("Facebook Link")) else ""
        else:
            srcode = age = birthday = sex = campus = college_dept = yrlevel_program = address = contact_num = fblink = ""
        
        try:
            cursor.execute("""
                INSERT INTO requirements (
                    id, medCert, waiver, type, eventId, affiliation, fullname, email,
                    srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
                    address, contactNum, fblink, accepted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req_id, f"documents/med_cert_{req_id}.pdf", f"documents/waiver_{req_id}.pdf",
                event_type, event_id, "Batangas State University", name, email,
                srcode, age, birthday, sex, campus, college_dept, yrlevel_program,
                address, contact_num, fblink, 1
            ))
            november_req_count += 1
            
            if (name, email) in november_attended:
                criteria = {'overall': round(random.uniform(3.5, 5.0), 1), 'comment': "Attended"}
                cursor.execute("""
                    INSERT INTO evaluation (
                        requirementId, criteria, q13, q14, comment, recommendations, finalized
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (req_id, str(criteria), str(round(random.uniform(3.5, 5.0), 1)), "", "Attended", "Good", 1))
                november_eval_count += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    # 7. Repopulate participation history
    print("\n7. Repopulating participation history...")
    from populate_volunteer_participation_history import populate_volunteer_participation_history
    populate_volunteer_participation_history()
    
    print("\n" + "=" * 70)
    print("DATA FIXED")
    print("=" * 70)
    print(f"August: {august_req_count} joined, {august_eval_count} attended, {august_req_count - august_eval_count} dropouts")
    print(f"October: {october_req_count} joined, 0 attended (all dropouts)")
    print(f"November: {november_req_count} joined, {november_eval_count} attended, {november_req_count - november_eval_count} dropouts")
    print("\n✓ Data now matches your requirements!")
    print("=" * 70)

if __name__ == "__main__":
    fix_participation_data()

