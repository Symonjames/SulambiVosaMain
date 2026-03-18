# How to Run Sulambi VMS

## BACKEND Setup & Run

```powershell
# Navigate to backend directory
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"

# Install Python dependencies
pip install -r requirements.txt

# Initialize database (only needed first time or after reset)
python server.py --init

# Start the backend server
python server.py
```

**Note:** Make sure you have a `.env` file in the backend directory with:
```
DEBUG=True
DB_PATH="app/database/database.db"
AUTOMAILER_EMAIL=your-email@example.com
AUTOMAILER_PASSW=your-password
```

---

## FRONTEND Setup & Run

```powershell
# Navigate to frontend directory
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main"

# Install Node.js dependencies (only needed first time or after package updates)
npm install

# Start the development server
npm run dev
```

---

## Running Both Together

You'll need **TWO separate terminal windows**:

**Terminal 1 (Backend):**
```powershell
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
python server.py
```

**Terminal 2 (Frontend):**
```powershell
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main"
npm run dev
```

---

## Quick Tips

- **First time setup:** Run `npm install` and `pip install -r requirements.txt` once
- **Database reset:** Run `python server.py --reset` then `python server.py --init`
- **Backend runs on:** Usually `http://localhost:5000` (check the console output)
- **Frontend runs on:** Usually `http://localhost:5173` (Vite default port, check the console output)
