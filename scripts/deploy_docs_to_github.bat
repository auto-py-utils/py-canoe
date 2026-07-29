@echo off

REM ============================
REM Deploy MkDocs Documentation to GitHub Pages
REM ============================

REM Set window title
title Deploying Documentation to GitHub Pages

REM Save original directory and move to project root
set "ORIGIN_DIR=%CD%"
pushd %~dp0
cd ..

REM ----------------------------
REM 1. Ensure uv is available and sync dependencies via helper
REM ----------------------------
call "%~dp0\uv_helper.bat" sync --link-mode=copy
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Completed syncing dependencies.

REM ----------------------------
REM 2. Deploy Documentation to GitHub Pages
REM ----------------------------
echo Deploying documentation to GitHub Pages...
call "%~dp0\uv_helper.bat" run mkdocs gh-deploy
if %ERRORLEVEL% NEQ 0 goto ERROR
echo Documentation deployed successfully.
popd
cd "%ORIGIN_DIR%"
goto :EOF

REM ----------------------------
REM Error Handler
REM ----------------------------
:ERROR
echo Failed to deploy documentation due to error %ERRORLEVEL%
popd
cd "%ORIGIN_DIR%"
pause
goto :EOF