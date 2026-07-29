@echo off
REM Helper to ensure `uv` is installed and run common uv commands
REM Usage:
REM   call "%~dp0\uv_helper.bat" sync [sync-args]
REM   call "%~dp0\uv_helper.bat" run [command args...]
REM   call "%~dp0\uv_helper.bat" build
REM   call "%~dp0\uv_helper.bat" publish

setlocal

where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo uv not found. Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install uv.
        endlocal & exit /b 1
    )
    echo uv installation completed.
)

echo uv version:
uv --version

if "%~1"=="" (
    endlocal & exit /b 0
)

set "CMD=%~1"
shift

REM Rebuild args into ARGS and drop a leading duplicate token if present
set "ARGS=%*"
for /f "tokens=1* delims= " %%A in ("%ARGS%") do (
    set "FIRST_TOKEN=%%A"
    set "REMAINDER=%%B"
)
if /I "%FIRST_TOKEN%"=="%CMD%" (
    set "ARGS=%REMAINDER%"
) else (
    set "ARGS=%ARGS%"
)

if /I "%CMD%"=="sync" (
    echo Running: uv sync %ARGS%
    uv sync %ARGS%
    endlocal & exit /b %ERRORLEVEL%
)

if /I "%CMD%"=="run" (
    echo Running: uv run %ARGS%
    uv run %ARGS%
    endlocal & exit /b %ERRORLEVEL%
)

if /I "%CMD%"=="build" (
    echo Running: uv build %ARGS%
    uv build %ARGS%
    endlocal & exit /b %ERRORLEVEL%
)

if /I "%CMD%"=="publish" (
    echo Running: uv publish %ARGS%
    uv publish %ARGS%
    endlocal & exit /b %ERRORLEVEL%
)

REM Default: pass everything to uv
echo Running: uv %CMD% %ARGS%
uv %CMD% %ARGS%
endlocal & exit /b %ERRORLEVEL%
