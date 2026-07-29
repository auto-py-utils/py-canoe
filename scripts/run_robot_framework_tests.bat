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
REM 1. Ensure uv is available and sync dependencies via helper
REM ----------------------------
call "%~dp0\uv_helper.bat" sync --link-mode=copy --all-extras
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed syncing dependencies.

REM ----------------------------
REM 2. Run Robot Framework tests
REM ----------------------------
call "%~dp0\uv_helper.bat" run robot --outputdir=tests/report/robot --loglevel=DEBUG tests/robot_tests
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
