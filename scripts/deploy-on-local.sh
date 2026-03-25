#!/bin/bash

# Exit on any error
set -e

# Navigate to the project root (one level up from scripts/)
cd "$(dirname "$0")/.."

# Detect OS to find the correct venv activation path
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or WSL)
    VENV_ACTIVATE=".venv/Scripts/activate"
else
    # macOS / Linux
    VENV_ACTIVATE=".venv/bin/activate"
fi

# Check if the virtual environment exists
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
    echo "💿 Virtual environment activated"
else
    echo "❌ Virtual environment not found at $VENV_ACTIVATE"
    echo "Try creating one: python3 -m venv .venv"
    exit 1
fi


# Start FastAPI with Uvicorn
echo "🚀 Starting FastAPI app with Uvicorn..."
uvicorn stellar.main:app --reload
