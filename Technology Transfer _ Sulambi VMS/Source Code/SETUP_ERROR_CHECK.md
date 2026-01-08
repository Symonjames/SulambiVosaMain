# Setup Error Check - Frontend & Backend

## ✅ Commands Look Correct

Your commands are correct! Here's what might cause errors:

---

## 🔴 Potential Backend Errors

### 1. **Missing `.env` File** ⚠️ CRITICAL

**Error you might see:**
```
AttributeError: 'NoneType' object has no attribute 'startswith'
```
or
```
Database path not configured
```

**Fix:** Create a `.env` file in the backend directory:
```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"

# Create .env file
@"
DEBUG=True
DB_PATH=app/database/database.db
AUTOMAILER_EMAIL=
AUTOMAILER_PASSW=
"@ | Out-File -FilePath .env -Encoding utf8
```

**Or manually create `.env` with:**
```
DEBUG=True
DB_PATH=app/database/database.db
AUTOMAILER_EMAIL=
AUTOMAILER_PASSW=
```

### 2. **Missing Python Dependencies**

**Error you might see:**
```
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'flask_cors'
```

**Fix:** Make sure you're in the right directory and Python is correct:
```powershell
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt
```

### 3. **Database Directory Doesn't Exist**

**Error you might see:**
```
sqlite3.OperationalError: unable to open database file
```

**Fix:** The directory should be created automatically, but if not:
```powershell
# Create database directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "app\database"
```

### 4. **Port 8000 Already in Use**

**Error you might see:**
```
OSError: [WinError 10048] Only one usage of each socket address is permitted
```

**Fix:** 
- Close any other instance of the server
- Or change port in `.env`: `PORT=8001`

---

## 🔴 Potential Frontend Errors

### 1. **Node.js Not Installed**

**Error you might see:**
```
'npm' is not recognized as an internal or external command
```

**Fix:** Install Node.js from https://nodejs.org/

### 2. **Port 5173 Already in Use**

**Error you might see:**
```
Port 5173 is in use, trying another one...
```

**Fix:** This is usually fine - Vite will use the next available port. Check the console output for the actual port.

### 3. **TypeScript Errors**

**Error you might see:**
```
error TS2307: Cannot find module '...'
```

**Fix:** 
```powershell
# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### 4. **Missing Dependencies**

**Error you might see:**
```
Cannot find module '@mui/material'
```

**Fix:**
```powershell
npm install
```

---

## ✅ Step-by-Step Setup (With Error Prevention)

### Backend Setup:

```powershell
# 1. Navigate to backend
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"

# 2. Check if .env exists, create if missing
if (-not (Test-Path .env)) {
    @"
DEBUG=True
DB_PATH=app/database/database.db
AUTOMAILER_EMAIL=
AUTOMAILER_PASSW=
"@ | Out-File -FilePath .env -Encoding utf8
    Write-Host "✅ Created .env file"
} else {
    Write-Host "✅ .env file exists"
}

# 3. Create database directory if needed
New-Item -ItemType Directory -Force -Path "app\database" | Out-Null

# 4. Install dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# 5. Initialize database (first time only)
Write-Host "Initializing database..."
python server.py --init

# 6. Start server
Write-Host "Starting server..."
python server.py
```

### Frontend Setup:

```powershell
# 1. Navigate to frontend
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main"

# 2. Install dependencies
Write-Host "Installing Node.js dependencies..."
npm install

# 3. Start dev server
Write-Host "Starting frontend dev server..."
npm run dev
```

---

## 🔍 Common Error Messages & Solutions

### Backend Errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'X'` | Missing dependency | `pip install -r requirements.txt` |
| `DB_PATH is None` | Missing .env file | Create `.env` file (see above) |
| `Port 8000 already in use` | Another server running | Close other server or change port |
| `sqlite3.OperationalError` | Database path issue | Check DB_PATH in .env, create directory |
| `ImportError: cannot import name 'X'` | Python version mismatch | Use Python 3.8+ |

### Frontend Errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `'npm' is not recognized` | Node.js not installed | Install Node.js |
| `Cannot find module` | Missing dependency | `npm install` |
| `Port 5173 is in use` | Another dev server | Usually fine, Vite uses next port |
| `TypeScript errors` | Type issues | Check tsconfig.json, may need `npm install` |
| `ERR_NETWORK` | Backend not running | Start backend server first |

---

## ✅ Verification Checklist

After running setup, verify:

### Backend:
- [ ] `.env` file exists in backend directory
- [ ] `pip install -r requirements.txt` completed without errors
- [ ] `python server.py --init` completed successfully
- [ ] `python server.py` shows: `* Running on http://127.0.0.1:8000`
- [ ] Can access `http://localhost:8000/api/` in browser (should show JSON)

### Frontend:
- [ ] `npm install` completed without errors
- [ ] `npm run dev` shows: `Local: http://localhost:5173/`
- [ ] Frontend loads in browser
- [ ] No console errors in browser DevTools

---

## 🚨 If You Still Get Errors

1. **Check Python version:**
   ```powershell
   python --version  # Should be 3.8+
   ```

2. **Check Node.js version:**
   ```powershell
   node --version  # Should be 16+
   npm --version
   ```

3. **Check if ports are free:**
   ```powershell
   # Check port 8000 (backend)
   Test-NetConnection -ComputerName localhost -Port 8000
   
   # Check port 5173 (frontend)
   Test-NetConnection -ComputerName localhost -Port 5173
   ```

4. **Check file paths:**
   - Make sure you're in the correct directories
   - Paths are case-sensitive on some systems

5. **Check for missing files:**
   - Backend: `server.py`, `requirements.txt`, `.env`
   - Frontend: `package.json`, `vite.config.ts`

---

## 📝 Quick Test After Setup

Once both are running:

1. **Backend test:** Open `http://localhost:8000/api/` in browser
   - Should see: `{"message":"Api route is working"}`

2. **Frontend test:** Open `http://localhost:5173` in browser
   - Should see the landing page

3. **Login test:** Try logging in with:
   - Username: `Admin`
   - Password: `sulambi@2024`
   - Check browser console for `[FRONTEND_LOGIN]` logs
   - Check backend terminal for `[AUTH_LOGIN]` logs

---

**Status:** ✅ Commands are correct, but `.env` file might be missing
**Action:** Create `.env` file if it doesn't exist, then run the commands












