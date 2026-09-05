#!/bin/bash

FIX=false
if [ "$1" = "--fix" ] || [ "$1" = "-Fix" ]; then
    FIX=true
fi

echo -e "\n========================================="
echo "     Samarth QA Check (Pre-commit)       "
echo "========================================="

ERROR_COUNT=0

# --- Backend Checks ---
echo -e "\n[1/4] Starting Backend Checks..."
cd backend || exit 1

if [ -f "venv/bin/activate" ]; then
    echo "Activating backend virtual environment..."
    source venv/bin/activate
else
    echo "Error: Virtual environment not found in backend/venv. Please run 'python -m venv venv' and install requirements."
    exit 1
fi

if [ "$FIX" = true ]; then
    echo "Running Ruff Formatter and Linter (Auto-fix)..."
    ruff format .
    ruff check --fix .
else
    echo "Running Ruff Linter..."
    ruff check . || { echo "Ruff check failed! Run './qa_check.sh --fix' to auto-fix errors."; ERROR_COUNT=$((ERROR_COUNT+1)); }
    
    echo "Running Ruff Formatter..."
    ruff format --check . || { echo "Ruff format failed! Run './qa_check.sh --fix' to format."; ERROR_COUNT=$((ERROR_COUNT+1)); }
fi

echo -e "\n[2/4] Running Pyright Type Checker..."
if command -v pyright >/dev/null 2>&1; then
    pyright || { echo "Pyright check failed! Please fix type errors in backend."; ERROR_COUNT=$((ERROR_COUNT+1)); }
elif [ -f "venv/bin/pyright" ]; then
    venv/bin/pyright || { echo "Pyright check failed! Please fix type errors in backend."; ERROR_COUNT=$((ERROR_COUNT+1)); }
else
    echo "Pyright CLI not found in PATH or venv. Skipping Pyright check."
fi

echo -e "\n[3/4] Running Pytest..."
pytest || { echo "Pytest failed! Please ensure tests pass and invariants hold."; ERROR_COUNT=$((ERROR_COUNT+1)); }

cd ..

# --- Frontend Checks ---
echo -e "\n[4/4] Starting Frontend Checks (Formatting, Linting, Types, Tests)..."
cd frontend || exit 1

if [ "$FIX" = true ]; then
    echo "Running Frontend Prettier (Auto-fix)..."
    npm run format
else
    echo "Running Frontend Prettier Check..."
    npm run format:check || { echo "Frontend format check failed! Run './qa_check.sh --fix' to auto-fix errors."; ERROR_COUNT=$((ERROR_COUNT+1)); }
fi

echo "Running Frontend ESLint..."
npm run lint:es || { echo "Frontend ESLint failed! Please fix linting errors."; ERROR_COUNT=$((ERROR_COUNT+1)); }

echo "Running Frontend TypeScript Check..."
npm run lint || { echo "Frontend typecheck failed! Please fix TypeScript errors."; ERROR_COUNT=$((ERROR_COUNT+1)); }

echo "Running Frontend Vitest Tests..."
npm run test || { echo "Frontend tests failed! Please fix broken tests."; ERROR_COUNT=$((ERROR_COUNT+1)); }

cd ..

echo -e "\n========================================="
if [ $ERROR_COUNT -gt 0 ]; then
    echo "QA Check Failed with $ERROR_COUNT error(s). Please fix them before pushing."
    exit 1
else
    echo "All QA checks passed successfully! You are ready to push."
    exit 0
fi
