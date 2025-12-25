"""
Create dummy dropout risk data using real names from member-app.xlsx
- Creates requirements (volunteers who joined events)
- Creates evaluations for some (volunteers who attended)
- Leaves some without evaluations (dropouts - joined but didn't attend)
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

def create_dropout_dummy_data():
    """Create dummy dropout data with real names from Excel"""
    print("=" * 70)
    print("CREATING DUMMY DROPOUT DATA WITH REAL NAMES")
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
    
    # 2. Get events from database
    print("\n2. Reading events from database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get internal events
    cursor.execute("SELECT id, title, durationStart, durationEnd FROM internalEvents WHERE status IN ('accepted', 'completed')")
    internal_events = cursor.fetchall()
    
    # Get external events
    cursor.execute("SELECT id, title, durationStart, durationEnd FROM externalEvents WHERE status IN ('accepted', 'completed')")
    external_events = cursor.fetchall()
    
    all_events = [(e[0], e[1], e[2], e[3], 'internal') for e in internal_events] + \
                 [(e[0], e[1], e[2], e[3], 'external') for e in external_events]
    
    if len(all_events) == 0:
        print("   ❌ No events found in database. Please create events first.")
        conn.close()
        return
    
    print(f"   ✓ Found {len(all_events)} events")
    
    # 3. Clear existing requirements and evaluations (optional - comment out if you want to keep existing)
    print("\n3. Clearing existing requirements and evaluations...")
    cursor.execute("DELETE FROM evaluation")
    cursor.execute("DELETE FROM requirements")
    conn.commit()
    print("   ✓ Cleared existing data")
    
    # 4. Create requirements and evaluations
    print("\n4. Creating requirements and evaluations...")
    print("   (Some will have evaluations = attended, some won't = dropouts)")
    
    requirements_created = 0
    evaluations_created = 0
    dropouts_created = 0
    
    # Use a subset of names (about 60% of members)
    selected_names = random.sample(name_email_pairs, min(len(name_email_pairs), int(len(name_email_pairs) * 0.6)))
    
    for name, email in selected_names:
        # Each volunteer joins 1-4 events
        num_events = random.randint(1, 4)
        selected_events = random.sample(all_events, min(num_events, len(all_events)))
        
        for event_id, event_title, event_start, event_end, event_type in selected_events:
            # Create requirement (volunteer joined)
            req_id = f"REQ-{random.randint(10000, 99999)}-{requirements_created}-{event_id}"
            
            # Extract member data if available
            member_row = df_members[df_members["Name (Last Name, First Name, Middle Initial)"] == name]
            if not member_row.empty:
                srcode = str(member_row.iloc[0].get("Sr-Code", "")) if pd.notna(member_row.iloc[0].get("Sr-Code")) else ""
                age = int(member_row.iloc[0].get("Age", 20)) if pd.notna(member_row.iloc[0].get("Age")) else 20
                birthday = str(member_row.iloc[0].get("Birthday", "")) if pd.notna(member_row.iloc[0].get("Birthday")) else ""
                sex = str(member_row.iloc[0].get("Sex", "")) if pd.notna(member_row.iloc[0].get("Sex")) else ""
                campus = str(member_row.iloc[0].get("Campus", "")) if pd.notna(member_row.iloc[0].get("Campus")) else ""
                college_dept = str(member_row.iloc[0].get("College/Department", "")) if pd.notna(member_row.iloc[0].get("College/Department")) else ""
                yrlevel_program = str(member_row.iloc[0].get("Year Level & Program", "")) if pd.notna(member_row.iloc[0].get("Year Level & Program")) else ""
                address = str(member_row.iloc[0].get("Address", "")) if pd.notna(member_row.iloc[0].get("Address")) else ""
                contact_num = str(member_row.iloc[0].get("Contact Number", "")) if pd.notna(member_row.iloc[0].get("Contact Number")) else ""
                fblink = str(member_row.iloc[0].get("Facebook Link", "")) if pd.notna(member_row.iloc[0].get("Facebook Link")) else ""
            else:
                srcode = ""
                age = 20
                birthday = ""
                sex = ""
                campus = ""
                college_dept = ""
                yrlevel_program = ""
                address = ""
                contact_num = ""
                fblink = ""
            
            try:
                cursor.execute("""
                    INSERT INTO requirements (
                        id, medCert, waiver, type, eventId, affiliation, fullname, email,
                        srcode, age, birthday, sex, campus, collegeDept, yrlevelprogram,
                        address, contactNum, fblink, accepted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    req_id, 
                    f"documents/med_cert_{req_id}.pdf", 
                    f"documents/waiver_{req_id}.pdf",
                    event_type, event_id, "Batangas State University", name, email,
                    srcode, age, birthday, sex, campus, college_dept, yrlevel_program,
                    address, contact_num, fblink,
                    1  # accepted = 1 (volunteer joined)
                ))
                requirements_created += 1
                
                # 70% attendance rate (30% dropout rate)
                # This means 70% will have evaluations (attended), 30% won't (dropouts)
                if random.random() < 0.7:
                    # Create evaluation (volunteer attended)
                    criteria = {
                        'overall': round(random.uniform(3.5, 5.0), 1),
                        'satisfaction': round(random.uniform(3.5, 5.0), 1),
                        'comment': random.choice([
                            "Great event, very informative!",
                            "Well organized and engaging.",
                            "Enjoyed the activities.",
                            "Good initiative, keep it up.",
                            "Satisfactory experience overall."
                        ])
                    }
                    
                    q13 = str(round(random.uniform(3.5, 5.0), 1))
                    q14 = ""
                    comment = criteria['comment']
                    recommendations = random.choice([
                        "More events like this.",
                        "Keep up the excellent work!",
                        "No specific recommendations, it was perfect."
                    ])
                    
                    cursor.execute("""
                        INSERT INTO evaluation (
                            requirementId, criteria, q13, q14, comment, recommendations, finalized
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        req_id,
                        str(criteria),
                        q13,
                        q14,
                        comment,
                        recommendations,
                        1  # finalized = 1 (attended)
                    ))
                    evaluations_created += 1
                else:
                    # No evaluation = dropout (joined but didn't attend)
                    dropouts_created += 1
                
            except sqlite3.IntegrityError:
                # Skip if requirement already exists
                continue
            except Exception as e:
                print(f"   ⚠️  Error creating requirement for {name}: {e}")
                continue
        
        if requirements_created % 20 == 0:
            conn.commit()
            print(f"   Processed {requirements_created} requirements...")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("DUMMY DROPOUT DATA CREATED")
    print("=" * 70)
    print(f"✓ Requirements created (volunteers joined): {requirements_created}")
    print(f"✓ Evaluations created (volunteers attended): {evaluations_created}")
    print(f"✓ Dropouts (joined but didn't attend): {dropouts_created}")
    print(f"✓ Attendance rate: {(evaluations_created / requirements_created * 100):.1f}%")
    print(f"✓ Dropout rate: {(dropouts_created / requirements_created * 100):.1f}%")
    print("\n✓ Data is now in the database and will appear in Dropout Risk Assessment!")
    print("=" * 70)

if __name__ == "__main__":
    create_dropout_dummy_data()

















