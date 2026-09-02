param(
    [switch]$Fix = $false
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     Samarth QA Check (Pre-commit)       " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$errorCount = 0

# --- Backend Checks ---
Write-Host "`n[1/4] Starting Backend Checks..." -ForegroundColor Yellow
cd backend

if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Activating backend virtual environment..."
    . .\venv\Scripts\activate.ps1
} else {
    Write-Host "Error: Virtual environment not found in backend\venv. Please run 'python -m venv venv' and install requirements." -ForegroundColor Red
    exit 1
}

if ($Fix) {
    Write-Host "Running Ruff Formatter and Linter (Auto-fix)..." -ForegroundColor Magenta
    ruff format .
    ruff check --fix .
} else {
    Write-Host "Running Ruff Linter..." -ForegroundColor Magenta
    ruff check .
    if ($LASTEXITCODE -ne 0) { 
        Write-Host "Ruff check failed! Run '.\qa_check.ps1 -Fix' to auto-fix errors." -ForegroundColor Red
        $errorCount++ 
    }

    Write-Host "Running Ruff Formatter..." -ForegroundColor Magenta
    ruff format --check .
    if ($LASTEXITCODE -ne 0) { 
        Write-Host "Ruff format failed! Run '.\qa_check.ps1 -Fix' to format." -ForegroundColor Red
        $errorCount++ 
    }
}

Write-Host "`n[2/4] Running Pyright Type Checker..." -ForegroundColor Yellow
pyright
if ($LASTEXITCODE -ne 0) { 
    Write-Host "Pyright check failed! Please fix type errors in backend." -ForegroundColor Red
    $errorCount++ 
}

Write-Host "`n[3/4] Running Pytest..." -ForegroundColor Yellow
pytest
if ($LASTEXITCODE -ne 0) { 
    Write-Host "Pytest failed! Please ensure tests pass and invariants hold." -ForegroundColor Red
    $errorCount++ 
}

cd ..

# --- Frontend Checks ---
Write-Host "`n[4/4] Starting Frontend Checks (TypeScript)..." -ForegroundColor Yellow
cd frontend
npm run lint
if ($LASTEXITCODE -ne 0) { 
    Write-Host "Frontend lint/typecheck failed! Please fix TypeScript errors." -ForegroundColor Red
    $errorCount++ 
}
cd ..

Write-Host "`n=========================================" -ForegroundColor Cyan
if ($errorCount -gt 0) {
    Write-Host "QA Check Failed with $errorCount error(s). Please fix them before pushing." -ForegroundColor Red
    exit 1
} else {
    Write-Host "All QA checks passed successfully! You are ready to push." -ForegroundColor Green
    exit 0
}
