# Sulambi VMS (Frontend + Backend)

This repository contains the Sulambi VMS source code:

- **Backend (Flask/Python)**: `Technology Transfer _ Sulambi VMS/Source Code/sulambi-backend-main/sulambi-backend-main/`
- **Frontend (React + Vite)**: `Technology Transfer _ Sulambi VMS/Source Code/sulambi-frontend-main/sulambi-frontend-main/`

> Note: Local SQLite databases (`*.db`) and `uploads/` are intentionally **ignored** via `.gitignore`.

## Run locally

### Backend

Open a terminal:

```powershell
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
python -m pip install -r requirements.txt
python server.py --init
python server.py
```

### Frontend

Open another terminal:

```powershell
cd "Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main"
npm install
npm run dev
```

## Deployment notes

If you deploy, prefer a **managed database (PostgreSQL/MySQL)** instead of SQLite (SQLite files won’t persist reliably on many hosts).

