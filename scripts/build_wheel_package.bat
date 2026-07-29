@echo off

REM ============================
REM Build Python Wheel Package
REM ============================

REM Set window title
title Building Python Wheel Package

REM Move to script directory and then project root
pushd %~dp0
cd ..

REM ----------------------------
REM 1. Ensure uv is available and sync dependencies via helper
REM ----------------------------
call "%~dp0\uv_helper.bat" sync --link-mode=copy
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed syncing dependencies.

REM ----------------------------
REM 2. Build the Wheel Package
REM ----------------------------
call "%~dp0\uv_helper.bat" build
if %ERRORLEVEL% NEQ 0 goto ERROR
echo wheel package built successfully.

popd
goto :EOF

REM ----------------------------
REM Error Handler
REM ----------------------------
:ERROR
title Failed to build wheel package due to error %ERRORLEVEL%
popd
pause
goto :EOF
