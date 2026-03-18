


# Sulambi VMS - System Reset Guide

## 📋 Overview

This guide explains how to reset your Sulambi VMS system to factory defaults, removing all data and starting fresh.

---

## ⚠️ What Gets Deleted

When you reset the system, the following data will be **PERMANENTLY DELETED**:

- ❌ All membership applications
- ❌ All volunteer accounts (except default Admin & Officer)
- ❌ All internal events and proposals
- ❌ All external events and proposals
- ❌ All event reports (internal & external)
- ❌ All evaluations and feedback
- ❌ All requirements submissions
- ❌ All help desk requests
- ❌ All uploaded files (photos, documents, waiver forms, medical certificates, etc.)
- ❌ All user sessions

---

## ✅ What Remains After Reset

After reset, you'll have:

- ✓ Fresh database with empty tables
- ✓ Two default accounts:
  - **Admin** (username: `Admin`, password: `sulambi@2024`)
  - **Officer** (username: `Sulambi-Officer`, password: `password@2024`)
- ✓ Empty uploads folder

---

## 🚀 Method 1: Using the Reset Script (Recommended)

### Step 1: Navigate to Backend Directory
```bash
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
```

### Step 2: Run the Reset Script
```bash
python reset_system.py
```

### Step 3: Confirm Reset
- The script will ask for confirmation
- Type `YES` (in capital letters) to proceed
- The script will:
  - Create a backup of your current database
  - Delete the database
  - Clear all uploaded files
  - Reinitialize the database with default accounts

### Step 4: Start the Server
```bash
python server.py
```

---

## 🔧 Method 2: Manual Reset

If you prefer to reset manually, follow these steps:

### Step 1: Stop the Server
Make sure the backend server is not running.

### Step 2: Delete Database Files
Navigate to `app/database/` and delete:
- `database.db`
- `database.db-wal` (if exists)
- `database.db-shm` (if exists)

**Location:**
```
Technology Transfer _ Sulambi VMS\
  Source Code\
    sulambi-backend-main\
      sulambi-backend-main\
        app\
          database\
            database.db  ← DELETE THIS
```

### Step 3: Clear Uploaded Files
Navigate to `uploads/` folder and delete all files **EXCEPT** `README.md`

**Location:**
```
Technology Transfer _ Sulambi VMS\
  Source Code\
    sulambi-backend-main\
      sulambi-backend-main\
        uploads\  ← DELETE ALL FILES HERE (except README.md)
```

### Step 4: Restart the Server
When you start the server, it will automatically:
- Create a new database
- Initialize all tables
- Create the default Admin and Officer accounts

```bash
python server.py
```

---

## 💾 Creating a Backup Before Reset

### Using the Reset Script
The reset script automatically creates a backup before deleting data.

### Manual Backup
Copy the database file to a safe location:

```bash
# From the backend directory
copy "app\database\database.db" "app\database\database.db.backup"
```

---

## 🔐 Default Login Credentials

After reset, use these credentials to log in:

### Admin Account
- **Username:** `Admin`
- **Password:** `sulambi@2024`
- **Role:** Full administrative access

### Officer Account
- **Username:** `Sulambi-Officer`
- **Password:** `password@2024`
- **Role:** Officer level access

---

## 📁 File Locations Reference

### Database
```
app/database/database.db
```

### Uploaded Files
```
uploads/
├── [all user-uploaded files will be here]
└── README.md (keep this file)
```

### Reset Script
```
reset_system.py (in the root of backend directory)
```

---

## ❓ Frequently Asked Questions

### Q: Can I undo a reset?
**A:** Only if you created a backup before resetting. The reset script automatically creates a backup file named `database.db.backup` (or `database.db.backup1`, `database.db.backup2`, etc.).

### Q: Will this affect the frontend?
**A:** No, the frontend code remains unchanged. Only the backend data is reset.

### Q: Do I need to reconfigure anything after reset?
**A:** No, all configurations in `.env` file remain the same. Only the data is reset.

### Q: What if I only want to delete specific data?
**A:** You'll need to manually delete records from the database using SQL commands or create a custom script. The reset tool is for complete system reset only.

### Q: Can I reset just the uploaded files?
**A:** Yes, simply delete all files in the `uploads/` folder except `README.md`. The database will still reference these files, so you may get errors if users try to view them.

---

## 🛟 Troubleshooting

### Database doesn't reinitialize
**Solution:** Start the server manually. The `tableInitializer.py` runs automatically when the app starts.

```bash
python server.py
```

### Can't delete database (file in use)
**Solution:** Make sure the backend server is completely stopped before running the reset script.

### Uploaded files not clearing
**Solution:** Make sure no processes are accessing the files. Close any file explorers viewing the uploads folder.

---

## ⚡ Quick Reference Commands

```bash
# Navigate to backend
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"

# Run reset script
python reset_system.py

# Start server after reset
python server.py
```

---

## 📞 Need Help?

If you encounter any issues during the reset process, check:
1. Server is completely stopped
2. No file explorer windows are open in the uploads folder
3. You have write permissions for the database and uploads directories

---

**Last Updated:** October 2025  
**Version:** 1.0
















































