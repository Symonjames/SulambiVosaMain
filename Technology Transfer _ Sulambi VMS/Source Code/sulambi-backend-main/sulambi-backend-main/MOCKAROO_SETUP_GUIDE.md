# Mockaroo Member Data Generation Guide

This guide will help you generate many member records for the Sulambi VMS using Mockaroo.

## 📋 Prerequisites

1. **Backend Server Running**: Make sure your Sulambi VMS backend is running on `http://localhost:8000`
2. **Python Installed**: Ensure Python is installed on your system
3. **Required Python Packages**: Install required packages:
   ```bash
   pip install requests pandas
   ```

## 🚀 Step-by-Step Process

### Step 1: Go to Mockaroo
1. Visit [https://www.mockaroo.com/](https://www.mockaroo.com/)
2. Sign up for a free account (allows 1,000 records per month)

### Step 2: Create New Schema
1. Click "New Schema"
2. Set the schema name to "Sulambi VMS Members"

### Step 3: Configure Fields
Use the field configuration from `mockaroo_schema_config.json` or manually add these fields:

| Field Name | Type | Format/Options |
|------------|------|----------------|
| `applyingAs` | Custom List | Student, Faculty, Staff, Alumni |
| `volunterismExperience` | Boolean | - |
| `weekdaysTimeDevotion` | Custom List | 1-2 hours, 3-4 hours, 5-6 hours, 7+ hours |
| `weekendsTimeDevotion` | Custom List | 1-2 hours, 3-4 hours, 5-6 hours, 7+ hours |
| `areasOfInterest` | Custom List | Outreach, Education, Environment, Health, Technology, Sports, Arts, Community Service |
| `fullname` | Full Name | - |
| `email` | Email Address | - |
| `affiliation` | Custom List | Batangas State University, Other University, Private Organization, Government Agency |
| `srcode` | Custom List | 21-12345, 22-12345, 23-12345, 24-12345, 25-12345 |
| `age` | Number | Min: 18, Max: 65 |
| `birthday` | Date | Format: %B, %d %Y |
| `sex` | Custom List | Male, Female |
| `campus` | Custom List | Main Campus, Alangilan, Balayan, Lemery, Lipa, Malvar, Nasugbu, Rosario, San Juan |
| `collegeDept` | Custom List | College of Engineering, College of Arts and Sciences, College of Business, College of Education, College of Nursing, College of Information and Communications Technology |
| `yrlevelprogram` | Custom List | 1st Year - BS Computer Science, 2nd Year - BS Information Technology, 3rd Year - BS Civil Engineering, 4th Year - BS Mechanical Engineering, 1st Year - BS Nursing, 2nd Year - BS Education |
| `address` | Street Address | - |
| `contactNum` | Phone Number | Format: +63 9## ### #### |
| `fblink` | URL | - |
| `bloodType` | Custom List | A+, A-, B+, B-, AB+, AB-, O+, O- |
| `bloodDonation` | Custom List | Yes, No, Maybe |
| `medicalCondition` | Custom List | None, Asthma, Diabetes, Hypertension, Heart Condition, Other |
| `paymentOption` | Custom List | GCash, PayMaya, Bank Transfer, Cash, Check |
| `volunteerExpQ1` | Text | Max: 200 characters |
| `volunteerExpQ2` | Text | Max: 200 characters |
| `volunteerExpProof` | URL | - |
| `reasonQ1` | Text | Max: 300 characters |
| `reasonQ2` | Text | Max: 300 characters |

### Step 4: Generate Data
1. Set the number of records you want (e.g., 100, 500, 1000)
2. Click "Download Data"
3. Choose CSV format
4. Save the file as `mockaroo_members.csv` in the backend directory

### Step 5: Load Data into Database

#### Option A: Using Batch Script (Windows)
1. Double-click `load_mockaroo_members.bat`
2. Follow the prompts

#### Option B: Using Python Script Directly
1. Open terminal/command prompt
2. Navigate to the backend directory
3. Run: `python mockaroo_member_loader.py`

## 📊 Expected Output

The script will:
- ✅ Load data from the CSV file
- ✅ Process each record
- ✅ Send data to the API endpoint
- ✅ Show success/failure status for each record
- ✅ Display a summary at the end

## 🔧 Troubleshooting

### Common Issues:

1. **"CSV file not found"**
   - Make sure `mockaroo_members.csv` is in the same directory as the script
   - Check the filename spelling

2. **"Server not running"**
   - Start your Sulambi VMS backend server
   - Make sure it's running on `http://localhost:8000`

3. **"Connection refused"**
   - Check if the API endpoint is correct
   - Verify the server is accessible

4. **"Invalid data format"**
   - Check the CSV file format
   - Ensure all required fields are present

### Data Validation:
- Usernames are auto-generated from full names
- Passwords are randomly assigned from a predefined list
- Areas of interest are formatted as JSON arrays
- Birthdays are formatted to match the expected format

## 📈 Tips for Better Data

1. **Realistic Data**: Use appropriate age ranges (18-65)
2. **Valid Emails**: Mockaroo generates valid email addresses
3. **Philippine Context**: Phone numbers are in Philippine format
4. **Campus Distribution**: Use various campuses for diversity
5. **Program Variety**: Include different year levels and programs

## 🎯 Sample Data Counts

Recommended record counts for testing:
- **Small Test**: 10-50 records
- **Medium Test**: 100-500 records  
- **Large Test**: 1000+ records

## 📝 Notes

- The script includes error handling and retry logic
- Data is processed with a small delay to avoid overwhelming the server
- All generated members will have `active: true` and `accepted: null` by default
- You can manually approve members through the admin interface

## 🆘 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your CSV file format
3. Ensure the backend server is running
4. Check the API endpoint configuration

Happy data generation! 🚀
























