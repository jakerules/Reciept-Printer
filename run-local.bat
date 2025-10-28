@echo off
REM This script installs dependencies and runs the local development server on Windows.

echo --- Installing/updating dependencies ---
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo.
echo --- Starting the application server ---
echo --- You can access the web UI at http://localhost:8000 ---
echo --- Press CTRL+C to stop the server ---
uvicorn app.main:app --reload
