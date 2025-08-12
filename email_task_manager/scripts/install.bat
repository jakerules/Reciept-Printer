@echo off
:: Installation script for Email Task Manager on Windows

echo === Email Task Manager Installation ===

:: Check if we're in the right directory
if not exist requirements.txt (
    echo Error: requirements.txt not found
    echo Please run this script from the project root directory
    exit /b 1
)

:: Check Python version
echo Checking Python version...
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found. Please install Python 3.7 or higher
    exit /b 1
)

:: Extract Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Found Python %PYTHON_VERSION%

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Failed to create virtual environment
    exit /b 1
)
echo Virtual environment created successfully

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment
    exit /b 1
)
echo Virtual environment activated

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies
    exit /b 1
)
echo Dependencies installed successfully

:: Set environment variables
set FLASK_APP=run.py

:: Initialize database
echo Initializing database...
if not exist migrations (
    flask db init
)
flask db migrate -m "Initial migration"
flask db upgrade
if %ERRORLEVEL% neq 0 (
    echo Failed to initialize database
    exit /b 1
)
echo Database initialized successfully

:: Check for Gmail API credentials
echo Checking for Gmail API credentials...
if exist credentials.json (
    echo Found credentials.json file
) else (
    echo credentials.json file not found
    echo You will need to obtain Gmail API credentials from Google Cloud Console
    echo See README.md for instructions
)

echo === Installation Complete ===
echo To start the application, run:
echo call venv\Scripts\activate  # If not already activated
echo python run.py
echo Then access the application at http://localhost:5000

pause