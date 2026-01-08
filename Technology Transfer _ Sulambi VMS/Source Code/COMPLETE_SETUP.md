# Complete Setup Guide - Frontend & Backend

## 🚀 Quick Start (Copy & Paste)

### Backend Setup (Terminal 1)

```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
pip install -r requirements.txt
python server.py --init
python server.py
```

### Frontend Setup (Terminal 2)

```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main"
npm install
npm run dev
```

---

## 📋 Detailed Explanation

### Backend Commands

#### 1. Navigate to Backend Directory
```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
```
**Purpose:** Changes to the backend folder where `server.py` is located

#### 2. Install Python Dependencies
```powershell
pip install -r requirements.txt
```
**Purpose:** Installs all required Python packages:
- flask
- flask-cors
- python-dotenv
- scikit-learn
- pandas
- numpy
- joblib
- psycopg2-binary
- gunicorn

**Expected Output:**
```
Successfully installed flask flask-cors python-dotenv ...
```

#### 3. Initialize Database
```powershell
python server.py --init
```
**Purpose:** 
- Creates database file (`app/database/database.db`)
- Creates all database tables
- Creates default Admin and Officer accounts

**Expected Output:**
```
[*] Initializing accounts table...Done
[*] Initializing sessions table...Done
[*] Initializing membership table...Done
...
```

**Note:** Only run this:
- First time setup
- After database reset
- When you need fresh data

#### 4. Start Backend Server
```powershell
python server.py
```
**Purpose:** Starts the Flask API server

**Expected Output:**
```
 * Running on http://127.0.0.1:8000
 * Running on http://[your-ip]:8000
Press CTRL+C to quit
```

**Keep this terminal open!** The server must stay running.

---

### Frontend Commands

#### 1. Navigate to Frontend Directory
```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main"
```
**Purpose:** Changes to the frontend folder where `package.json` is located

#### 2. Install Node.js Dependencies
```powershell
npm install
```
**Purpose:** Installs all required Node.js packages:
- React
- Material-UI
- Axios
- React Router
- Vite
- TypeScript
- And many more...

**Expected Output:**
```
added 500 packages, and audited 501 packages in 30s
```

**Note:** Only run this:
- First time setup
- After pulling new code
- When `package.json` changes

#### 3. Start Development Server
```powershell
npm run dev
```
**Purpose:** Starts the Vite development server with hot-reload

**Expected Output:**
```
  VITE v6.2.5  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Keep this terminal open!** The dev server must stay running.

---

## ✅ Verification

### Backend is Running If:
- Terminal shows: `* Running on http://127.0.0.1:8000`
- Browser test: Open `http://localhost:8000/api/`
  - Should see: `{"message":"Api route is working"}`

### Frontend is Running If:
- Terminal shows: `Local: http://localhost:5173/`
- Browser test: Open `http://localhost:5173`
  - Should see the landing page

---

## 🔐 Default Login Credentials

After running `python server.py --init`, use these to login:

**Admin Account:**
- Username: `Admin`
- Password: `sulambi@2024`

**Officer Account:**
- Username: `Sulambi-Officer`
- Password: `password@2024`

---

## ⚠️ Important Notes

1. **Two Terminals Required:**
   - Terminal 1: Backend server (port 8000)
   - Terminal 2: Frontend server (port 5173)

2. **Keep Both Running:**
   - Don't close the terminals while developing
   - Press `CTRL+C` to stop servers

3. **Order Matters:**
   - Start backend first (frontend needs API)
   - Then start frontend

4. **Database Reset:**
   ```powershell
   python server.py --reset  # Deletes database
   python server.py --init   # Recreates database
   ```

---

## 🐛 Troubleshooting

### Backend Issues:

**Error: `ModuleNotFoundError: No module named 'flask'`**
```powershell
# Fix: Install dependencies
pip install -r requirements.txt
```

**Error: `Port 8000 already in use`**
```powershell
# Fix: Close other server or change port in .env
# Or find and kill the process:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend Issues:

**Error: `'npm' is not recognized`**
- Install Node.js from https://nodejs.org/

**Error: `Port 5173 is in use`**
- This is fine! Vite will use the next available port (5174, 5175, etc.)
- Check the console output for the actual port

**Error: `Cannot find module`**
```powershell
# Fix: Reinstall dependencies
Remove-Item -Recurse -Force node_modules
npm install
```

---

## 📝 Quick Reference

### Backend (Terminal 1):
```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
pip install -r requirements.txt
python server.py --init
python server.py
```

### Frontend (Terminal 2):
```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main"
npm install
npm run dev
```

---

**Ready to go!** 🚀












