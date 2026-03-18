# Backend Error Fix

## Problem
- `pip install` fails: "Unable to create process using 'C:\python.exe'"
- `python server.py` fails: "ModuleNotFoundError: No module named 'flask'"

## Root Cause
The `pip` command is pointing to a wrong Python path. Use `python -m pip` instead.

## ✅ Fixed Commands

### Use these commands instead:

```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"

# Use python -m pip instead of just pip
python -m pip install -r requirements.txt

# Then continue as normal
python server.py --init
python server.py
```

## Alternative: Check Python Installation

If `python -m pip` also fails, check your Python:

```powershell
# Check Python version
python --version

# Check if pip is available
python -m pip --version

# If pip is not available, install it:
python -m ensurepip --upgrade
```












