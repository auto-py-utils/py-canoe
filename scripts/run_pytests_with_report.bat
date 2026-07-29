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
REM 1. Ensure uv is available and sync dependencies via helper
REM ----------------------------
call "%~dp0\uv_helper.bat" sync --link-mode=copy --all-extras
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed syncing dependencies.

REM ----------------------------
REM 2. Run Pytest with Reports
REM ----------------------------
call "%~dp0\uv_helper.bat" run pytest tests/ ^
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
