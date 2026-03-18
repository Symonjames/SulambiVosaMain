import requests as re
import pandas as pd
import json
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Excel file path - try multiple possible names (including with spaces)
EXCEL_FILE = os.path.join(SCRIPT_DIR, "..", "member-app.xlsx")
EXCEL_FILE_ALT1 = os.path.join(SCRIPT_DIR, "..", "member- app.xlsx")  # With space
EXCEL_FILE_ALT2 = os.path.join(SCRIPT_DIR, "..", "members-app.xlsx")
EXCEL_FILE_ALT3 = os.path.join(SCRIPT_DIR, "..", "member_app.xlsx")
EXCEL_FILE_ALT4 = os.path.join(SCRIPT_DIR, "..", "members_app.xlsx")
EXCEL_FILE_ALT5 = os.path.join(SCRIPT_DIR, "..", "member app.xlsx")  # With space, no dash

# Try to find the Excel file
excel_file_to_use = None
for file_path in [EXCEL_FILE, EXCEL_FILE_ALT1, EXCEL_FILE_ALT2, EXCEL_FILE_ALT3, EXCEL_FILE_ALT4, EXCEL_FILE_ALT5]:
    if os.path.exists(file_path):
        excel_file_to_use = file_path
        break

# If still not found, try to find any .xlsx file in data folder that contains "member"
if not excel_file_to_use:
    data_dir = os.path.join(SCRIPT_DIR, "..")
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.xlsx') and 'member' in file.lower():
                excel_file_to_use = os.path.join(data_dir, file)
                print(f"⚠️  Found Excel file with 'member' in name: {file}")
                break

if not excel_file_to_use:
    print(f"❌ Excel file not found. Tried:")
    print(f"   - {EXCEL_FILE}")
    print(f"   - {EXCEL_FILE_ALT1} (with space)")
    print(f"   - {EXCEL_FILE_ALT2}")
    print(f"   - {EXCEL_FILE_ALT3}")
    print(f"   - {EXCEL_FILE_ALT4}")
    print(f"   - {EXCEL_FILE_ALT5}")
    print(f"\nPlease ensure the Excel file exists in the 'data' folder.")
    exit(1)

print(f"✓ Reading Excel file: {excel_file_to_use}")
loadData = pd.read_excel(excel_file_to_use)
# print(list(loadData.columns))
# columns = ['Email Address', "I'm applying as", 'Do you have any prior volunteerism experience?',
# 'How much time can you devote for volunteering activities on weekdays?', 
# 'How much time can you devote for volunteering activities on weekends?',
# 'What areas or interests do you want to volunteer in? Check the area(s) that interest you. ',
# '1. What volunteering activities of Sulambi VOSA last Academic Year did you join?',
# '2. What volunteering activities did you join outside Sulambi VOSA and/or the University?',
# '2.1 Upload proof for the volunteering activities you joined outside(e.g. Pictures, Certificate)',
# 'Why do you want to become a member?', 'What can you contribute to the organization?',
# 'Name (Last Name, First Name, Middle Initial)', 'Gsuite Email', 'Sr-Code', 'Age', 'Birthday', 'Sex', 'Campus', 'College/Department',
# 'Year Level & Program', 'Address', 'Contact Number', 'Facebook Link', 'Blood Type', 'Blood Donation',
# 'Do you have any existing medical condition/s? If yes, please specify. If none, type N/A.',
# 'Payment Options', 'What areas or interests do you want to volunteer in? Check the area(s) that interest you.']
# Outreach (Medical mission, Dental mission, Optical mission, Blood donation, Visit to orphanages, Visit to prison camps, Visit to rehabilitation center, Relief operation, Gift-giving activity, Sports and Recreation)
# dataFormat = {
#   "applyyingAs",
#   "volunterismExperience",
#   "weekdaysTimeDevotion",
#   "weekendsTimeDevotion",
#   "fullname",
#   "email",
#   "affiliation",
#   "srcode",
#   "age",
#   "birthday",
#   "sex",
#   "campus",
#   "collegeDept",
#   "yrlevelprogram",
#   "address",
#   "contactNum",
#   "fblink",
#   "bloodType",
#   "bloodDonation",
#   "paymentOption",
#   "username",
#   "areasOfInterest",
#   "password"
# }

API_ENDPOINT = "http://localhost:8000/api/auth/register"

def insertData(data):
  response = re.post(API_ENDPOINT, json=data, headers={'Content-Type': 'application/json'})
  if (response.status_code != 200):
    print("[Response] Status Code: ", response.status_code)
    print("[Response] Raw Response: ", response.text)

for index, data in loadData.iterrows():
  if (index == 0): continue
  areaOfInterest = data["What areas or interests do you want to volunteer in? Check the area(s) that interest you. "]

  dataFormat = {
    "applyingAs": data["I'm applying as"],
    "volunterismExperience": data["Do you have any prior volunteerism experience?"].lower(),
    "weekdaysTimeDevotion": data["How much time can you devote for volunteering activities on weekdays?"],
    "weekendsTimeDevotion": data["How much time can you devote for volunteering activities on weekends?"],
    "fullname": data["Name (Last Name, First Name, Middle Initial)"],
    "email": data["Email Address"],
    "affiliation": "Batangas State University",
    "srcode": data["Sr-Code"],
    "age": data["Age"],
    "birthday": data["Birthday"] if type(data["Birthday"]) is str else data["Birthday"].strftime("%B, %d %Y"),
    "sex": data["Sex"],
    "campus": data["Campus"],
    "collegeDept": data["College/Department"],
    "yrlevelprogram": data["Year Level & Program"],
    "address": data["Address"],
    "contactNum": data["Contact Number"],
    "fblink": data["Facebook Link"],
    "bloodType": data["Blood Type"],
    "bloodDonation": data["Blood Donation"],
    "paymentOption": data["Payment Options"],
    "username": data["Name (Last Name, First Name, Middle Initial)"].split(" ")[0].replace(" ", "").replace(",", "") + str(index),
    "areasOfInterest": json.dumps(areaOfInterest.split(", ") if type(areaOfInterest) is str else []),
    "password": "password"
  }

  # print("[+] Registering: ", dataFormat["username"], ":", dataFormat["password"])
  insertData(dataFormat)