# PowerShell script to run diamix.py with automatic .dia file detection
# Usage: .\run_diamix.ps1 -TxtFile "path\to\file.txt"

param(
    [Parameter(Mandatory=$true)]
    [string]$TxtFile
)

# Get the directory and base name of the txt file
$TxtPath = Resolve-Path $TxtFile
$TxtDir = Split-Path $TxtPath -Parent
$TxtBaseName = [System.IO.Path]::GetFileNameWithoutExtension($TxtPath)

Write-Host "Processing file: $TxtPath"

# Look for corresponding .dia file in the same directory
$DiaFile = Join-Path $TxtDir "$TxtBaseName.dia"

# Check if .dia file exists
if (-not (Test-Path $DiaFile)) {
    Write-Error "No corresponding .dia file found for $TxtFile"
    Write-Host "Expected file: $DiaFile"
    exit 1
}

Write-Host "Found .dia file: $DiaFile"

# Get the directory where this script is located (where diamix.py should be)
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent
$DiamixPy = Join-Path $ScriptDir "diamix.py"

# Check if diamix.py exists
if (-not (Test-Path $DiamixPy)) {
    Write-Error "diamix.py not found in $ScriptDir"
    exit 1
}

# Check if .venv exists and activate it
$VenvPath = Join-Path $ScriptDir ".venv"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Host "Activating virtual environment: $VenvPath"
    & $VenvActivate
} else {
    Write-Host "No virtual environment found, using system Python"
}

# Run diamix.py with the found files
Write-Host "Running: python $DiamixPy $DiaFile $TxtPath -o $TxtPath"
python $DiamixPy $DiaFile $TxtPath -o $TxtPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully updated speakers in $TxtFile" -ForegroundColor Green
} else {
    Write-Error "diamix.py failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}