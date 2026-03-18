# Add 100 People to Sulambi VMS

This script adds exactly 100 realistic people to the Sulambi VMS database. These members will appear as if they were manually added with realistic Filipino names and data.

## Features

- **100 Realistic Members**: All members are set to `active=True` and `accepted=True` (approved) so they appear in the system
- **Filipino Names**: Uses common Filipino first and last names
- **Realistic Data**: 
  - Proper SR codes (SR-20-XXXX-XXXX to SR-25-XXXX-XXXX)
  - GSuite email addresses (@g.batstate-u.edu.ph)
  - Philippine addresses (Batangas area)
  - Realistic contact numbers
  - Proper year levels and programs
- **Default Password**: All accounts use `Password123!` for easy testing

## Requirements

- Python 3.x
- Faker library: `pip install faker`

## How to Run

1. Make sure you have Python installed
2. Install Faker if you haven't:
   ```bash
   pip install faker
   ```

3. Run the script:
   ```bash
   python add_100_people.py
   ```

4. The script will:
   - Check if the database exists
   - Add 100 members to the membership table
   - Set all members to active and approved
   - Show progress every 10 records

## What Gets Added

Each member includes:
- Full name (Filipino format: Lastname, Firstname M.)
- SR Code
- Email (GSuite format)
- Age (18-25)
- Birthday
- Sex (male/female)
- Campus (one of 8 Batangas State University campuses)
- College/Department
- Year Level and Program
- Address (Batangas area)
- Contact number
- Facebook link
- Blood type
- Blood donation preference
- Areas of interest
- Volunteer experience (if applicable)
- Application reasons

## Notes

- All members are automatically **approved** (`accepted=1`) so they appear in the system immediately
- All members are **active** (`active=True`)
- Default password for all accounts: `Password123!`
- If duplicates are found (username, email, or SR code already exists), they will be skipped
- The script will show how many records were successfully inserted

## Verification

After running, you can verify the members were added by:
1. Opening the Sulambi VMS admin panel
2. Going to the Members/Accounts section
3. You should see 100 new members listed

















