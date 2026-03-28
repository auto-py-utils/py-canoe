@echo off

REM ============================
REM Run Pytest with Coverage and HTML Report
REM ============================

REM Set window title
title Running Pytests with Report

REM Move to script directory and then project root
pushd %~dp0
cd ..

REM ----------------------------
REM 1. Check if uv is installed, else install it
REM ----------------------------
:CHECK_UV
where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo uv is already installed.
    uv --version
) else (
    echo uv not found. Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %ERRORLEVEL% NEQ 0 goto ERROR
    echo uv installation completed.
)

REM ----------------------------
REM 2. Sync Dependencies
REM ----------------------------
echo Syncing dependencies with uv...
uv sync --link-mode=copy
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed syncing dependencies.

REM ----------------------------
REM 4. Run Pytest with Reports
REM ----------------------------
uv run pytest tests/ ^
    --html=tests/report/test_reports/full_test_report.html --self-contained-html ^
    --cov=src ^
    --cov-report=html:tests/report/cov/htmlcov ^
    --cov-report=xml:tests/report/cov/coverage.xml ^
    --cov-report=json:tests/report/cov/coverage.json ^
    --maxfail=5 ^
    --tb=short
if %ERRORLEVEL% NEQ 0 goto ERROR

REM ----------------------------
REM 5. Cleanup
REM ----------------------------
popd
goto :EOF

REM ----------------------------
REM Error Handler
REM ----------------------------
:ERROR
title Failed to run pytests due to error %ERRORLEVEL%
popd
pause
goto :EOF
