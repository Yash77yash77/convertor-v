# PowerShell script to start the Flask server
Set-Location -Path "$PSScriptRoot\Scripts"
if (-Not (Test-Path venv)) {
    python -m venv venv
}
& "venv\Scripts\Activate.ps1"
pip install -r ..\requirements.txt
python app.py
