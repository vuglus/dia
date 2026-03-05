# PowerShell script to run diamix.py with specified .dia and .txt files
# Usage: .\run_diamix.ps1 -TxtFile "path\to\file.txt" -DiaFile "path\to\file.dia"

param(
    [Parameter(Mandatory=$true)]
    [string]$TxtFile,
    
    [Parameter(Mandatory=$true)]
    [string]$DiaFile
)

# Get the paths
try {
    $TxtPath = Resolve-Path $TxtFile | Select-Object -ExpandProperty Path
} catch {
    Write-Error "Cannot resolve path for TXT file: $TxtFile"
    exit 1
}

try {
    $DiaPath = Resolve-Path $DiaFile | Select-Object -ExpandProperty Path
} catch {
    Write-Error "Cannot resolve path for DIA file: $DiaFile"
    exit 1
}

Write-Host "Processing files:"
Write-Host "  TXT: $TxtPath"
Write-Host "  DIA: $DiaPath"

# Check if .dia file exists
if (-not (Test-Path $DiaPath)) {
    Write-Error "Specified .dia file not found: $DiaPath"
    exit 1
}

# Check if .txt file exists
if (-not (Test-Path $TxtPath)) {
    Write-Error "Specified .txt file not found: $TxtPath"
    exit 1
}

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

# Run diamix.py with the specified files
Write-Host "Running: python $DiamixPy $DiaPath $TxtPath -o $TxtPath"
python $DiamixPy $DiaPath $TxtPath -o $TxtPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully updated speakers in $TxtFile" -ForegroundColor Green
} else {
    Write-Error "diamix.py failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}