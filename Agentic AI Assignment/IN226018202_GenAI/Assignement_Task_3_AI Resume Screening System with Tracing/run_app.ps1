$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[ERROR] venv Python not found at: $pythonExe" -ForegroundColor Red
    Write-Host "Create venv first: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Streamlit using project venv..." -ForegroundColor Green
& $pythonExe -m streamlit run app.py
