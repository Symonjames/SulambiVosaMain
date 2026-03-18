"""
Add sample satisfaction rating data directly to Excel file
Creates realistic volunteer and beneficiary responses with 1-5 ratings and comments
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import random

EXCEL_OUTPUT = os.path.join("data", "satisfaction-ratings.xlsx")

def add_sample_satisfaction_data():
    """Add sample satisfaction ratings to Excel file"""
    print("=" * 70)
    print("ADDING SAMPLE SATISFACTION RATINGS TO EXCEL")
    print("=" * 70)
    
    # Sample event data
    events = [
        {"id": 1, "type": "internal", "title": "Community Health Outreach Program"},
        {"id": 2, "type": "internal", "title": "Educational Workshop Series"},
        {"id": 3, "type": "external", "title": "Environmental Cleanup Drive"},
        {"id": 4, "type": "internal", "title": "Youth Leadership Training"},
        {"id": 5, "type": "external", "title": "Food Distribution Event"}
    ]
    
    # Sample names
    volunteer_names = [
        "Maria Santos", "Juan Dela Cruz", "Anna Rodriguez", "Carlos Garcia",
        "Sofia Martinez", "Miguel Torres", "Isabella Reyes", "Diego Lopez",
        "Elena Fernandez", "Ricardo Morales", "Carmen Vargas", "Jose Gutierrez"
    ]
    
    beneficiary_names = [
        "Rosa Alcantara", "Pedro Mendoza", "Luz Villanueva", "Manuel Bautista",
        "Teresa Ramos", "Fernando Cruz", "Dolores Aquino", "Roberto Salazar",
        "Esperanza Del Rosario", "Alfredo Navarro", "Consuelo Medina", "Francisco Ortega"
    ]
    
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
    
    # Generate volunteer responses (30 samples)
    for i in range(30):
        event = random.choice(events)
        name = random.choice(volunteer_names)
        email = name.lower().replace(" ", ".") + "@example.com"
        
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
            "Event ID": event["id"],
            "Event Type": event["type"],
            "Event Title": event["title"],
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
    
    # Generate beneficiary responses (20 samples)
    for i in range(20):
        event = random.choice(events)
        name = random.choice(beneficiary_names)
        email = name.lower().replace(" ", ".") + "@example.com"
        
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
            "Event ID": event["id"],
            "Event Type": event["type"],
            "Event Title": event["title"],
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
    
    # Export to Excel
    try:
        df.to_excel(EXCEL_OUTPUT, index=False, engine='openpyxl')
        print(f"\n✓ Successfully added {len(data_rows)} sample satisfaction ratings to:")
        print(f"  {EXCEL_OUTPUT}")
        print(f"\nSample data breakdown:")
        print(f"  - Volunteer responses: 30")
        print(f"  - Beneficiary responses: 20")
        print(f"  - Total: {len(data_rows)}")
    except Exception as e:
        print(f"\n❌ Error exporting to Excel: {e}")
        print("   Make sure openpyxl is installed: pip install openpyxl")
        return
    
    print("\n" + "=" * 70)
    print("EXCEL FILE CREATED SUCCESSFULLY")
    print("=" * 70)
    print(f"File: {EXCEL_OUTPUT}")
    print(f"Records: {len(data_rows)}")
    print("=" * 70)

if __name__ == "__main__":
    add_sample_satisfaction_data()

















