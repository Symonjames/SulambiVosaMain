# Backend Setup Commands

## Step-by-Step Backend Setup

```powershell
# 1. Navigate to backend directory
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Initialize database (run this first time or after reset)
python server.py --init

# 4. Start the API server
python server.py
```

## What Each Command Does

1. **`cd ...`** - Changes to the backend directory
2. **`pip install -r requirements.txt`** - Installs all Python packages (Flask, flask-cors, etc.)
3. **`python server.py --init`** - Creates database tables and default accounts
4. **`python server.py`** - Starts the Flask server on port 8000

## Expected Output

After `python server.py`, you should see:
```
 * Running on http://127.0.0.1:8000
 * Running on http://[your-ip]:8000
```

## Default Login Credentials (After --init)

- **Admin:** Username: `Admin`, Password: `sulambi@2024`
- **Officer:** Username: `Sulambi-Officer`, Password: `password@2024`












