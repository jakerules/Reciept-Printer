#!/bin/bash

# This script installs dependencies and runs the local development server.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Installing/updating dependencies from requirements.txt and requirements-dev.txt ---"
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo ""
echo "--- Starting the application server ---"
echo "--- You can access the web UI at http://localhost:8000 ---"
echo "--- Press CTRL+C to stop the server ---"
uvicorn app.main:app --reload
