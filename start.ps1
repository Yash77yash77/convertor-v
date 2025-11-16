# PowerShell auto setup and run for Windows
param([switch]$OpenBrowser)
if (-not (Test-Path -Path .venv)) {
    Write-Output "Creating virtual environment..."
    python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Write-Output "Starting Flask server on http://127.0.0.1:5000"
Start-Process -NoNewWindow -FilePath python -ArgumentList "Scripts\app.py"
if ($OpenBrowser) { Start-Process "http://127.0.0.1:5000" }
