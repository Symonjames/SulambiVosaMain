@echo off
echo ========================================
echo    Sulambi VMS Member Data Loader
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if CSV file exists
if not exist "mockaroo_members.csv" (
    echo Error: mockaroo_members.csv not found!
    echo.
    echo Please follow these steps:
    echo 1. Go to https://www.mockaroo.com/
    echo 2. Create a new schema with the fields from mockaroo_schema_config.json
    echo 3. Generate data and download as CSV
    echo 4. Save the CSV file as 'mockaroo_members.csv' in this directory
    echo 5. Run this script again
    echo.
    pause
    exit /b 1
)

REM Check if server is running
echo Checking if server is running...
curl -s http://localhost:8000/api/auth/login >nul 2>&1
if errorlevel 1 (
    echo Warning: Server might not be running on localhost:8000
    echo Please make sure your Sulambi VMS backend server is running
    echo.
)

echo Starting member data loading...
echo.

REM Run the Python script
python mockaroo_member_loader.py

echo.
echo Data loading completed!
pause
























