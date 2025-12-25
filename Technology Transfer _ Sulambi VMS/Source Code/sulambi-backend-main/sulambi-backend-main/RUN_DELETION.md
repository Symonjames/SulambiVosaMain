# How to Delete Dummy Volunteer Data

## Option 1: Run the Verification Script (Check what exists)

### Step 1: Open Terminal/Command Prompt
- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **Mac/Linux**: Open Terminal

### Step 2: Navigate to Backend Directory
```bash
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
```

### Step 3: Run Verification Script
```bash
python verify_dummy_deletion.py
```

This will show you:
- How many dummy members exist
- How many dummy requirements exist
- How many dummy evaluations exist
- Sample dummy records

---

## Option 2: Call the API Endpoint (Actually Delete)

### Method A: Using curl (Command Line)

1. **Make sure your backend server is running** (on `http://localhost:8000`)

2. **Open Terminal/Command Prompt**

3. **Run this command:**
```bash
curl -X POST http://localhost:8000/api/analytics/dev/delete-dummy-volunteers -H "Content-Type: application/json"
```

### Method B: Using PowerShell (Windows)

1. **Open PowerShell**

2. **Run this command:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/dev/delete-dummy-volunteers" -Method POST -ContentType "application/json"
```

### Method C: Using Browser/Postman

1. **Open Postman** (or any API testing tool)

2. **Set up the request:**
   - Method: `POST`
   - URL: `http://localhost:8000/api/analytics/dev/delete-dummy-volunteers`
   - Headers: `Content-Type: application/json`

3. **Click Send**

### Method D: Using Python Script

Create a file `delete_dummy.py` in the backend directory:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analytics/dev/delete-dummy-volunteers",
    headers={"Content-Type": "application/json"}
)

print("Status Code:", response.status_code)
print("Response:", response.json())
```

Then run:
```bash
python delete_dummy.py
```

---

## What to Check After Running

### 1. Check Backend Console Logs
Look at your backend server console (where you ran `python server.py`). You should see logs like:
```
[DELETE DUMMY] Step 1: Identifying dummy members...
[DELETE DUMMY] Found X dummy members...
[DELETE DUMMY] Step 2: Finding requirements...
...
[DELETE DUMMY] Transaction committed successfully!
```

### 2. Check API Response
The API should return JSON like:
```json
{
  "success": true,
  "message": "Successfully deleted all dummy volunteer data: X total records deleted",
  "data": {
    "dummy_members_found": X,
    "deleted_counts": {
      "evaluations": X,
      "requirements": X,
      "sessions": X,
      "accounts": X,
      "memberships": X
    },
    "total_deleted": X
  }
}
```

### 3. Verify Deletion Worked
Run the verification script again:
```bash
python verify_dummy_deletion.py
```

All counts should be 0 if deletion was successful.

---

## Troubleshooting

### If you get "Connection refused" error:
- Make sure your backend server is running
- Check that it's running on port 8000
- Try: `http://127.0.0.1:8000/api/analytics/dev/delete-dummy-volunteers`

### If you get CORS error:
- The endpoint includes CORS headers, but if you still get errors, check your backend server logs

### If deletion returns success but data still shows:
1. Restart your backend server
2. Clear browser cache
3. Refresh the dashboard page
4. Run verification script again to confirm



