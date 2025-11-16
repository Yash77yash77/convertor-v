@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
REM Auto-setup and run for Windows (CMD)
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo Starting Flask server...
python Scripts\app.py
ENDLOCAL