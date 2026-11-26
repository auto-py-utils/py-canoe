@echo off
REM Helper to ensure `uv` is installed and run common uv commands
REM Usage:
REM   call "%~dp0\uv_helper.bat" sync [sync-args]
REM   call "%~dp0\uv_helper.bat" run [command args...]
REM   call "%~dp0\uv_helper.bat" build
REM   call "%~dp0\uv_helper.bat" publish

setlocal

set "UV_BIN=%USERPROFILE%\.local\bin"
set "WHERE_EXE=%SystemRoot%\System32\where.exe"
if not exist "%WHERE_EXE%" set "WHERE_EXE=%SystemRoot%\Sysnative\where.exe"
if exist "%UV_BIN%\uv.exe" set "PATH=%UV_BIN%;%PATH%"

if not exist "%UV_BIN%\uv.exe" (
    "%WHERE_EXE%" uv >nul 2>nul
    if not errorlevel 1 goto uv_available
    call :install_uv
    if errorlevel 1 (
        endlocal & exit /b 1
    )
)

if not exist "%UV_BIN%\uv.exe" (
    "%WHERE_EXE%" uv >nul 2>nul
    if not errorlevel 1 goto uv_available
    echo uv is not available on PATH after installation.
    endlocal & exit /b 1
)

:uv_available
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

:install_uv
echo uv not found. Installing uv...
set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%POWERSHELL_EXE%" goto install_uv_with_absolute_powershell
set "POWERSHELL_EXE=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
if exist "%POWERSHELL_EXE%" goto install_uv_with_absolute_powershell

echo Windows PowerShell was not found in the standard installation locations.
exit /b 1

:install_uv_with_absolute_powershell
"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
goto install_uv_check_result

:install_uv_check_result
if errorlevel 1 (
    echo Failed to install uv.
    exit /b 1
)

set "PATH=%UV_BIN%;%PATH%"
if not exist "%UV_BIN%\uv.exe" (
    "%WHERE_EXE%" uv >nul 2>nul
    if not errorlevel 1 goto install_uv_succeeded
    echo The installer completed, but uv was not found in the default install directory or PATH.
    exit /b 1
)

:install_uv_succeeded
echo uv installation completed.
exit /b 0
