# Remove 100 People from Sulambi VMS

This script removes the 100 people that were added by `add_100_people.py`.

## What It Does

- Finds members with:
  - Password: `Password123!` (default password from the add script)
  - OR GSuite email addresses (`@g.batstate-u.edu.ph`)
- Deletes:
  - Membership records
  - Associated requirements (volunteer registrations)
  - Associated accounts

## How to Run

```bash
python remove_100_people.py
```

## Safety Features

- Shows a preview of members to be removed
- Asks for confirmation before deleting
- Shows count of what will be deleted

## Warning

⚠️ **This operation is permanent and cannot be undone!**

Make sure you want to remove these members before proceeding.

















