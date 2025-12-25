"""
Update satisfaction-ratings.xlsx with real names from member-app.xlsx and real event titles from database
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join("app", "database", "database.db")
elif not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_PATH)

EXCEL_OUTPUT = os.path.join("data", "satisfaction-ratings.xlsx")
EXCEL_OUTPUT_TEMP = os.path.join("data", "satisfaction-ratings-temp.xlsx")
MEMBER_EXCEL = os.path.join("data", "member-app.xlsx")

def update_satisfaction_excel():
    """Update satisfaction ratings Excel with real names and event titles"""
    print("=" * 70)
    print("UPDATING SATISFACTION RATINGS EXCEL WITH REAL DATA")
    print("=" * 70)
    
    # Read names from member-app.xlsx
    print("\n1. Reading names from member-app.xlsx...")
    try:
        member_df = pd.read_excel(MEMBER_EXCEL)
        names = member_df['Name (Last Name, First Name, Middle Initial)'].dropna().tolist()
        emails = member_df['Gsuite Email'].dropna().tolist()
        # Use GSuite email if available, otherwise use regular email
        regular_emails = member_df['Email Address'].dropna().tolist()
        
        # Combine names with emails
        name_email_pairs = []
        for i, name in enumerate(names):
            email = emails[i] if i < len(emails) and pd.notna(emails[i]) else (regular_emails[i] if i < len(regular_emails) and pd.notna(regular_emails[i]) else f"{name.lower().replace(' ', '.').replace(',', '')}@example.com")
            name_email_pairs.append((name, email))
        
        print(f"   ✓ Found {len(name_email_pairs)} names from member-app.xlsx")
    except Exception as e:
        print(f"   ❌ Error reading member-app.xlsx: {e}")
        return
    
    # Get real events from database
    print("\n2. Reading events from database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get internal events
        cursor.execute("SELECT id, title, 'internal' as type FROM internalEvents")
        internal_events = cursor.fetchall()
        
        # Get external events
        cursor.execute("SELECT id, title, 'external' as type FROM externalEvents")
        external_events = cursor.fetchall()
        
        all_events = internal_events + external_events
        conn.close()
        
        if len(all_events) == 0:
            print("   ⚠️  No events found in database. Using sample events...")
            all_events = [
                (1, "Community Health Outreach Program", "internal"),
                (2, "Educational Workshop Series", "internal"),
                (3, "Environmental Cleanup Drive", "external"),
                (4, "Youth Leadership Training", "internal"),
                (5, "Food Distribution Event", "external")
            ]
        else:
            print(f"   ✓ Found {len(all_events)} events from database")
            print(f"   Sample events:")
            for e in all_events[:5]:
                print(f"     - {e[1]} ({e[2]})")
    except Exception as e:
        print(f"   ❌ Error reading events: {e}")
        return
    
    # Sample comments
    positive_comments = [
        "Excellent event! Very well organized and informative.",
        "Great experience, learned a lot from this event.",
        "The volunteers were very helpful and professional.",
        "Well-structured program with clear objectives.",
        "Enjoyed the activities and the learning experience.",
        "Very satisfied with the overall event quality.",
        "The materials provided were comprehensive and useful.",
        "Good communication throughout the event.",
        "The venue was appropriate and accessible.",
        "Would definitely recommend this to others."
    ]
    
    improvement_comments = [
        "Could improve on time management.",
        "More materials would be helpful.",
        "Better communication before the event needed.",
        "Venue could be more accessible.",
        "Some activities could be more engaging."
    ]
    
    recommendations = [
        "Keep up the good work!",
        "Continue organizing similar events.",
        "More events like this would be great.",
        "Well done!",
        "Excellent initiative.",
        "Please organize more frequently."
    ]
    
    data_rows = []
    
    # Generate volunteer responses (30 samples) using real names
    print("\n3. Generating volunteer responses with real names...")
    for i in range(30):
        if not name_email_pairs:
            break
        
        event_id, event_title, event_type = random.choice(all_events)
        name, email = random.choice(name_email_pairs)
        
        # Generate ratings (1-5 scale, bias towards higher ratings)
        overall = random.choices([3, 4, 5], weights=[2, 3, 5])[0]
        organization = max(1, min(5, overall + random.randint(-1, 1)))
        communication = max(1, min(5, overall + random.randint(-1, 1)))
        venue = max(1, min(5, overall + random.randint(-1, 1)))
        materials = max(1, min(5, overall + random.randint(-1, 1)))
        support = max(1, min(5, overall + random.randint(-1, 1)))
        
        comment = random.choice(positive_comments)
        if overall <= 3:
            comment += " " + random.choice(improvement_comments)
        
        submitted_date = (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d %H:%M:%S")
        
        data_rows.append({
            "ID": i + 1,
            "Event ID": event_id,
            "Event Type": event_type,
            "Event Title": event_title,
            "Requirement ID": f"REQ-{random.randint(10000, 99999)}",
            "Respondent Type": "Volunteer",
            "Respondent Email": email,
            "Respondent Name": name,
            "Overall Satisfaction (1-5)": overall,
            "Volunteer Rating (1-5)": overall,
            "Beneficiary Rating (1-5)": "",
            "Organization Rating (1-5)": organization,
            "Communication Rating (1-5)": communication,
            "Venue Rating (1-5)": venue,
            "Materials Rating (1-5)": materials,
            "Support Rating (1-5)": support,
            "Q13 (Volunteer Score)": str(overall),
            "Q14 (Beneficiary Score)": "",
            "Comment": comment,
            "Recommendations": random.choice(recommendations),
            "Would Recommend": "Yes" if overall >= 4 else "No",
            "Areas for Improvement": random.choice(improvement_comments) if overall <= 3 else "",
            "Positive Aspects": comment if overall >= 4 else "",
            "Submitted At": submitted_date,
            "Finalized": "Yes"
        })
    
    # Generate beneficiary responses (20 samples) using real names
    print("4. Generating beneficiary responses with real names...")
    for i in range(20):
        if not name_email_pairs:
            break
        
        event_id, event_title, event_type = random.choice(all_events)
        name, email = random.choice(name_email_pairs)
        
        # Generate ratings (1-5 scale, bias towards higher ratings)
        overall = random.choices([3, 4, 5], weights=[2, 3, 5])[0]
        organization = max(1, min(5, overall + random.randint(-1, 1)))
        communication = max(1, min(5, overall + random.randint(-1, 1)))
        venue = max(1, min(5, overall + random.randint(-1, 1)))
        materials = max(1, min(5, overall + random.randint(-1, 1)))
        support = max(1, min(5, overall + random.randint(-1, 1)))
        
        comment = random.choice(positive_comments)
        if overall <= 3:
            comment += " " + random.choice(improvement_comments)
        
        submitted_date = (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d %H:%M:%S")
        
        data_rows.append({
            "ID": 30 + i + 1,
            "Event ID": event_id,
            "Event Type": event_type,
            "Event Title": event_title,
            "Requirement ID": f"REQ-{random.randint(10000, 99999)}",
            "Respondent Type": "Beneficiary",
            "Respondent Email": email,
            "Respondent Name": name,
            "Overall Satisfaction (1-5)": overall,
            "Volunteer Rating (1-5)": "",
            "Beneficiary Rating (1-5)": overall,
            "Organization Rating (1-5)": organization,
            "Communication Rating (1-5)": communication,
            "Venue Rating (1-5)": venue,
            "Materials Rating (1-5)": materials,
            "Support Rating (1-5)": support,
            "Q13 (Volunteer Score)": "",
            "Q14 (Beneficiary Score)": str(overall),
            "Comment": comment,
            "Recommendations": random.choice(recommendations),
            "Would Recommend": "Yes" if overall >= 4 else "No",
            "Areas for Improvement": random.choice(improvement_comments) if overall <= 3 else "",
            "Positive Aspects": comment if overall >= 4 else "",
            "Submitted At": submitted_date,
            "Finalized": "Yes"
        })
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(EXCEL_OUTPUT), exist_ok=True)
    
    # Export to Excel (try temp file first if main file is locked)
    try:
        # Try to delete old file if it exists and is not locked
        if os.path.exists(EXCEL_OUTPUT):
            try:
                os.remove(EXCEL_OUTPUT)
            except:
                print(f"   ⚠️  Could not delete old file (may be open in Excel)")
                # Use temp filename
                output_file = EXCEL_OUTPUT_TEMP
                print(f"   Creating temporary file: {output_file}")
            else:
                output_file = EXCEL_OUTPUT
        else:
            output_file = EXCEL_OUTPUT
        
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n✓ Successfully updated satisfaction-ratings.xlsx with:")
        print(f"  - Real names from member-app.xlsx: {len(name_email_pairs)} names")
        print(f"  - Real event titles from database: {len(all_events)} events")
        print(f"  - Total records: {len(data_rows)}")
        print(f"    * Volunteer responses: 30")
        print(f"    * Beneficiary responses: 20")
        print(f"\nFile location: {output_file}")
        
        if output_file == EXCEL_OUTPUT_TEMP:
            print(f"\n⚠️  Please close satisfaction-ratings.xlsx in Excel, then rename:")
            print(f"   {EXCEL_OUTPUT_TEMP}")
            print(f"   to")
            print(f"   {EXCEL_OUTPUT}")
    except Exception as e:
        print(f"\n❌ Error exporting to Excel: {e}")
        return
    
    print("\n" + "=" * 70)
    print("EXCEL FILE UPDATED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    update_satisfaction_excel()

