@echo off
setlocal enabledelayedexpansion
color 0B
title Batch Financial Report Processing for VAs - Part 2 Setup

echo ============================================
echo   Part 2: Consolidation - First-Time Setup
echo ============================================
echo.
echo This will check your computer for two things it needs:
echo   1. Python (the language the tool is written in)
echo   2. openpyxl (a Python add-on used to create Excel files)
echo.
echo If either is missing, this script will download and install
echo it automatically. You need an internet connection for this.
echo.
echo Press any key to begin...
pause >nul
echo.

REM =========================================================
REM STEP 1: Check for a REAL Python install (not the Windows
REM Store stub). Windows ships fake python.exe/python3.exe
REM launchers that sit on PATH and print a "not found" message
REM instead of a version number, so checking "where python"
REM alone is not reliable. We check the actual output instead.
REM =========================================================
echo [1/2] Checking for Python...

set "REAL_PYTHON_FOUND=0"
for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYVER_OUTPUT=%%v"
echo !PYVER_OUTPUT! | findstr /C:"Python 3" >nul
if !errorlevel! equ 0 (
    set "REAL_PYTHON_FOUND=1"
    echo   Python is already installed: !PYVER_OUTPUT!
)

if "!REAL_PYTHON_FOUND!"=="1" (
    goto save_python_path
)

echo   A working Python installation was not found.
echo   ^(If you saw a message about the Microsoft Store just now,
echo   that is a Windows placeholder, not a real Python install.^)
echo.
echo   Downloading installer...
echo   ^(This file is about 25 MB, it may take a minute.^)
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"

if not exist "%TEMP%\python_installer.exe" (
    echo.
    echo   ERROR: Could not download Python. Please check your internet
    echo   connection and try running this script again.
    echo.
    pause
    exit /b 1
)

echo   Installing Python silently, this can take a few minutes...
echo   Please wait, do not close this window.
"%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_tcltk=1 Include_pip=1 Include_test=0
echo   Python installation finished.
del "%TEMP%\python_installer.exe" >nul 2>nul

set "PATH=%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts"

for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYVER_OUTPUT=%%v"
echo !PYVER_OUTPUT! | findstr /C:"Python 3" >nul
if !errorlevel! neq 0 (
    echo.
    echo   WARNING: Python was installed but is not responding correctly
    echo   in this window yet. Close this window, open a NEW one, and
    echo   run install_setup_part2.bat again to confirm.
    echo.
    pause
    exit /b 1
)

:save_python_path
for /f "delims=" %%p in ('where python 2^>nul') do (
    echo %%p | findstr /I "WindowsApps" >nul
    if !errorlevel! neq 0 (
        echo %%p> "%~dp0python_path.txt"
        goto path_saved
    )
)
if exist "C:\Program Files\Python312\python.exe" (
    echo C:\Program Files\Python312\python.exe> "%~dp0python_path.txt"
)
:path_saved

echo.
echo [2/2] Checking for openpyxl...

set "PYEXE=python"
if exist "%~dp0python_path.txt" (
    set /p PYEXE=<"%~dp0python_path.txt"
)

"!PYEXE!" -c "import openpyxl" >nul 2>nul
if !errorlevel! equ 0 (
    echo   openpyxl is already installed.
    goto done
)

echo   openpyxl was not found. Installing it now...
"!PYEXE!" -m pip install openpyxl --quiet
if !errorlevel! neq 0 (
    echo.
    echo   ERROR: Could not install openpyxl. Please check your internet
    echo   connection and try running this script again.
    echo.
    pause
    exit /b 1
)
echo   openpyxl installed successfully.

:done
echo.
echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo Python and openpyxl are ready. You can now double-click
echo run_consolidator.bat to open the tool.
echo.
echo If this is the very first time, please CLOSE this window
echo and open a NEW one before running the tool, so the changes
echo take effect.
echo.
pause
