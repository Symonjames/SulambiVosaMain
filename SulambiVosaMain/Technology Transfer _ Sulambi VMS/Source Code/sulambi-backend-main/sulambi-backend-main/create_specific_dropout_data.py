"""
Create specific dropout data:
- August semester: 100 people joined, 45 attended, 55 dropouts
- October: 55 people joined (website only), 0 attended (all dropouts)
- November semester: 165 people joined, 100 attended, 65 dropouts
"""

import pandas as pd
import sqlite3
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

MEMBER_EXCEL = os.path.join("data", "member-app.xlsx")

def create_specific_dropout_data():
    """Create specific dropout data as requested"""
    print("=" * 70)
    print("CREATING SPECIFIC DROPOUT DATA")
    print("=" * 70)
    
    # 1. Read names from member-app.xlsx
    print("\n1. Reading names from member-app.xlsx...")
    try:
        df_members = pd.read_excel(MEMBER_EXCEL)
        fullnames = df_members["Name (Last Name, First Name, Middle Initial)"].dropna().astype(str).tolist()
        emails = df_members["Email Address"].dropna().astype(str).tolist()
        gsuite_emails = df_members["Gsuite Email"].dropna().astype(str).tolist()
        
        # Create name-email pairs
        name_email_pairs = []
        for i, name in enumerate(fullnames):
            email = emails[i] if i < len(emails) and pd.notna(emails[i]) else (
                gsuite_emails[i] if i < len(gsuite_emails) and pd.notna(gsuite_emails[i]) else 
                f"{name.lower().replace(' ', '.').replace(',', '')}@example.com"
            )
            name_email_pairs.append((name, email))
        
        print(f"   ✓ Found {len(name_email_pairs)} names from member-app.xlsx")
    except Exception as e:
        print(f"   ❌ Error reading member-app.xlsx: {e}")
        return
    
    # 2. Get events from database and categorize by month
    print("\n2. Reading events from database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all events
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
        print("   ❌ No events found in database. Please create events first.")
        conn.close()
        return
    
    print(f"   ✓ Found {len(all_events)} events")
    
    # Categorize events by month
    august_events = []
    october_events = []
    november_events = []
    
    for event_id, event_title, event_start, event_end, event_type in all_events:
        if event_start:
            event_date = datetime.fromtimestamp(event_start / 1000)
            month = event_date.month
            year = event_date.year
            
            if month == 8:  # August
                august_events.append((event_id, event_title, event_start, event_end, event_type))
            elif month == 10:  # October
                october_events.append((event_id, event_title, event_start, event_end, event_type))
            elif month == 11:  # November
                november_events.append((event_id, event_title, event_start, event_end, event_type))
    
    # If no events in those months, use available events and assign them
    if not august_events:
        august_events = all_events[:min(2, len(all_events))]
        print(f"   ⚠️  No August events found, using first {len(august_events)} events for August")
    if not october_events:
        october_events = all_events[min(2, len(all_events)):min(4, len(all_events))]
        print(f"   ⚠️  No October events found, using next {len(october_events)} events for October")
    if not november_events:
        november_events = all_events[min(4, len(all_events)):]
        print(f"   ⚠️  No November events found, using remaining {len(november_events)} events for November")
    
    print(f"   August events: {len(august_events)}")
    print(f"   October events: {len(october_events)}")
    print(f"   November events: {len(november_events)}")
    
    # 3. Clear existing requirements and evaluations
    print("\n3. Clearing existing requirements and evaluations...")
    cursor.execute("DELETE FROM evaluation")
    cursor.execute("DELETE FROM requirements")
    conn.commit()
    print("   ✓ Cleared existing data")
    
    # 4. Create August semester data: 100 joined, 45 attended, 55 dropouts
    print("\n4. Creating August semester data (100 joined, 45 attended, 55 dropouts)...")
    august_names = random.sample(name_email_pairs, min(100, len(name_email_pairs)))
    august_attended = random.sample(august_names, 45)
    august_dropouts = [n for n in august_names if n not in august_attended]
    
    august_requirements = 0
    august_evaluations = 0
    
    for name, email in august_names:
        # Each person joins 1-2 events in August
        num_events = random.randint(1, 2)
        selected_events = random.sample(august_events, min(num_events, len(august_events)))
        
        for event_id, event_title, event_start, event_end, event_type in selected_events:
            req_id = f"REQ-AUG-{random.randint(10000, 99999)}-{august_requirements}"
            
            # Get member data
            member_row = df_members[df_members["Name (Last Name, First Name, Middle Initial)"] == name]
            if not member_row.empty:
                srcode = str(member_row.iloc[0].get("Sr-Code", "")) if pd.notna(member_row.iloc[0].get("Sr-Code")) else ""
                age_val = member_row.iloc[0].get("Age", 20)
                if pd.notna(age_val):
                    try:
                        # Extract number from string like "21 yrs old"
                        age = int(''.join(filter(str.isdigit, str(age_val))))
                    except:
                        age = 20
                else:
                    age = 20
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
                august_requirements += 1
                
                # Create evaluation only if this person attended
                if (name, email) in august_attended:
                    criteria = {
                        'overall': round(random.uniform(3.5, 5.0), 1),
                        'satisfaction': round(random.uniform(3.5, 5.0), 1),
                        'comment': "Attended August event"
                    }
                    cursor.execute("""
                        INSERT INTO evaluation (
                            requirementId, criteria, q13, q14, comment, recommendations, finalized
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        req_id, str(criteria), str(round(random.uniform(3.5, 5.0), 1)), "",
                        "Attended August event", "Keep it up!", 1
                    ))
                    august_evaluations += 1
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                continue
    
    # 5. Create October data: 55 joined (website only), 0 attended (all dropouts)
    print("\n5. Creating October data (55 joined, 0 attended - all dropouts)...")
    # Use different names for October
    remaining_names = [n for n in name_email_pairs if n not in august_names]
    october_names = random.sample(remaining_names, min(55, len(remaining_names)))
    
    october_requirements = 0
    
    for name, email in october_names:
        # Each person joins 1 event in October
        if october_events:
            event_id, event_title, event_start, event_end, event_type = random.choice(october_events)
            req_id = f"REQ-OCT-{random.randint(10000, 99999)}-{october_requirements}"
            
            member_row = df_members[df_members["Name (Last Name, First Name, Middle Initial)"] == name]
            if not member_row.empty:
                srcode = str(member_row.iloc[0].get("Sr-Code", "")) if pd.notna(member_row.iloc[0].get("Sr-Code")) else ""
                age_val = member_row.iloc[0].get("Age", 20)
                if pd.notna(age_val):
                    try:
                        # Extract number from string like "21 yrs old"
                        age = int(''.join(filter(str.isdigit, str(age_val))))
                    except:
                        age = 20
                else:
                    age = 20
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
                october_requirements += 1
                # No evaluation = dropout
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                continue
    
    # 6. Create November semester data: 165 joined, 100 attended, 65 dropouts
    print("\n6. Creating November semester data (165 joined, 100 attended, 65 dropouts)...")
    # Use remaining names + some from August
    remaining_after_oct = [n for n in name_email_pairs if n not in august_names and n not in october_names]
    november_all = random.sample(name_email_pairs, min(165, len(name_email_pairs)))
    november_attended = random.sample(november_all, 100)
    november_dropouts = [n for n in november_all if n not in november_attended]
    
    november_requirements = 0
    november_evaluations = 0
    
    for name, email in november_all:
        # Each person joins 1-2 events in November
        num_events = random.randint(1, 2)
        if november_events:
            selected_events = random.sample(november_events, min(num_events, len(november_events)))
        else:
            selected_events = random.sample(all_events, min(num_events, len(all_events)))
        
        for event_id, event_title, event_start, event_end, event_type in selected_events:
            req_id = f"REQ-NOV-{random.randint(10000, 99999)}-{november_requirements}"
            
            member_row = df_members[df_members["Name (Last Name, First Name, Middle Initial)"] == name]
            if not member_row.empty:
                srcode = str(member_row.iloc[0].get("Sr-Code", "")) if pd.notna(member_row.iloc[0].get("Sr-Code")) else ""
                age_val = member_row.iloc[0].get("Age", 20)
                if pd.notna(age_val):
                    try:
                        # Extract number from string like "21 yrs old"
                        age = int(''.join(filter(str.isdigit, str(age_val))))
                    except:
                        age = 20
                else:
                    age = 20
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
                november_requirements += 1
                
                # Create evaluation only if this person attended
                if (name, email) in november_attended:
                    criteria = {
                        'overall': round(random.uniform(3.5, 5.0), 1),
                        'satisfaction': round(random.uniform(3.5, 5.0), 1),
                        'comment': "Attended November event"
                    }
                    cursor.execute("""
                        INSERT INTO evaluation (
                            requirementId, criteria, q13, q14, comment, recommendations, finalized
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        req_id, str(criteria), str(round(random.uniform(3.5, 5.0), 1)), "",
                        "Attended November event", "Keep it up!", 1
                    ))
                    november_evaluations += 1
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                continue
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("SPECIFIC DROPOUT DATA CREATED")
    print("=" * 70)
    print(f"August Semester:")
    print(f"  - Joined: {august_requirements} requirements")
    print(f"  - Attended: {august_evaluations} evaluations")
    print(f"  - Dropouts: {august_requirements - august_evaluations}")
    print(f"\nOctober (Website Only):")
    print(f"  - Joined: {october_requirements} requirements")
    print(f"  - Attended: 0 (all dropouts)")
    print(f"  - Dropouts: {october_requirements}")
    print(f"\nNovember Semester:")
    print(f"  - Joined: {november_requirements} requirements")
    print(f"  - Attended: {november_evaluations} evaluations")
    print(f"  - Dropouts: {november_requirements - november_evaluations}")
    print(f"\nTotal:")
    print(f"  - Requirements: {august_requirements + october_requirements + november_requirements}")
    print(f"  - Evaluations: {august_evaluations + november_evaluations}")
    print(f"  - Total Dropouts: {(august_requirements - august_evaluations) + october_requirements + (november_requirements - november_evaluations)}")
    print("\n✓ Data is now in the database and will appear in Dropout Risk Assessment!")
    print("=" * 70)

if __name__ == "__main__":
    create_specific_dropout_data()

