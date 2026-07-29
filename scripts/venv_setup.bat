@echo off

REM ============================
REM Create or Update Python Virtual Environment and Install Dependencies using uv
REM ============================

title Creating/Updating Tool Environment with uv...

REM Move to script directory and then project root
pushd %~dp0
cd ..

REM ----------------------------
REM 1. Ensure uv is available and sync dependencies via helper
REM ----------------------------
call "%~dp0\uv_helper.bat" sync --link-mode=copy
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed syncing dependencies.

popd
goto :EOF

REM ----------------------------
REM Error Handler
REM ----------------------------
:ERROR
echo Failed to set up virtual environment and install dependencies due to error %ERRORLEVEL%.
popd
pause
goto :EOF