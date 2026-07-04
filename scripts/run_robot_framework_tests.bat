@echo off

REM ============================
REM Run Robot Framework tests
REM ============================

REM Set window title
title Running Robot Framework tests

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
uv sync --link-mode=copy --all-extras
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed syncing dependencies.

REM ----------------------------
REM 4. Run Robot Framework tests
REM ----------------------------
uv run robot --outputdir=tests/report/robot --loglevel=DEBUG tests/robot_tests
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed running Robot Framework tests.

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
