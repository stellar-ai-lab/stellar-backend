#!/bin/bash

set -e

cd "$(dirname "$0")/.."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    VENV_ACTIVATE=".venv/Scripts/activate"
else
    VENV_ACTIVATE=".venv/bin/activate"
fi

if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
    echo "💿 Virtual environment activated"
else
    echo "❌ Virtual environment not found at $VENV_ACTIVATE"
    echo "Try creating one: python3 -m venv .venv"
    exit 1
fi

echo "🧪 Running tests..."
uv run pytest -v
