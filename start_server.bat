@echo off
:: Start the Flask server (Windows)
pushd "%~dp0\Scripts"
python -m venv venv 2>nul || echo venv exists
call venv\Scripts\activate
pip install -r ..\requirements.txt
python app.py
popd
pause
