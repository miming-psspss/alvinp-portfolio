@echo off
setlocal enabledelayedexpansion
color 0B
title Batch Financial Report Processing for VAs - Part 1: Extraction - Setup

echo ============================================
echo   Batch Financial Report Processing for VAs - Part 1: Extraction - First-Time Setup
echo ============================================
echo.
echo This will check your computer for what it needs:
echo   1. Python (the language the tool is written in)
echo   2. 7-Zip (used to open password-protected RAR archives)
echo   3. py7zr (a Python add-on used to open 7Z archives)
echo.
echo ZIP, TAR, TAR.GZ, and GZ archives do not need any extra software;
echo Python can open those on its own.
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
echo [1/3] Checking for Python...

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

REM Refresh PATH for the current window so 'python' works immediately after install
set "PATH=%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts"

REM Verify the install actually worked before moving on
for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYVER_OUTPUT=%%v"
echo !PYVER_OUTPUT! | findstr /C:"Python 3" >nul
if !errorlevel! neq 0 (
    echo.
    echo   WARNING: Python was installed but is not responding correctly
    echo   in this window yet. Close this window, open a NEW one, and
    echo   run install_setup.bat again to confirm.
    echo.
    pause
    exit /b 1
)

:save_python_path
REM Save the real python.exe location so run_extractor.bat never has
REM to guess via PATH again (this avoids the Store-stub problem entirely).
for /f "delims=" %%p in ('where python 2^>nul') do (
    echo %%p | findstr /I "WindowsApps" >nul
    if !errorlevel! neq 0 (
        echo %%p> "%~dp0python_path.txt"
        goto path_saved
    )
)
REM Fallback: check the standard install location directly
if exist "C:\Program Files\Python312\python.exe" (
    echo C:\Program Files\Python312\python.exe> "%~dp0python_path.txt"
)
:path_saved

echo.

:check_7zip
echo [2/3] Checking for 7-Zip...
set "SEVENZIP_FOUND=0"
where 7z >nul 2>nul
if !errorlevel! equ 0 set "SEVENZIP_FOUND=1"
if exist "C:\Program Files\7-Zip\7z.exe" set "SEVENZIP_FOUND=1"

if "!SEVENZIP_FOUND!"=="1" (
    echo   7-Zip is already installed.
    set "PATH=%PATH%;C:\Program Files\7-Zip"
    goto done
)

echo   7-Zip was not found. Downloading installer...
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.7-zip.org/a/7z2408-x64.exe' -OutFile '%TEMP%\7zip_installer.exe'"

if not exist "%TEMP%\7zip_installer.exe" (
    echo.
    echo   ERROR: Could not download 7-Zip. Please check your internet
    echo   connection and try running this script again.
    echo.
    pause
    exit /b 1
)

echo   Installing 7-Zip silently...
"%TEMP%\7zip_installer.exe" /S
echo   7-Zip installation finished.
del "%TEMP%\7zip_installer.exe" >nul 2>nul
set "PATH=%PATH%;C:\Program Files\7-Zip"

:check_py7zr
echo.
echo [3/3] Checking for py7zr (needed for 7Z archives)...
python -m pip show py7zr >nul 2>nul
if !errorlevel! equ 0 (
    echo   py7zr is already installed.
    goto done
)

echo   py7zr was not found. Installing it now...
python -m pip install --quiet py7zr
if !errorlevel! neq 0 (
    echo.
    echo   WARNING: py7zr could not be installed automatically.
    echo   7Z archives will not work until this is fixed. You can try
    echo   installing it manually later by opening Command Prompt and
    echo   running: python -m pip install py7zr
    echo.
) else (
    echo   py7zr installed successfully.
)

:done
echo.
echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo Python, 7-Zip, and py7zr are ready. You can now double-click
echo run_extractor.bat to open the Batch Financial Report Processing for VAs - Part 1: Extraction tool.
echo.
echo If this is the very first time, please CLOSE this window
echo and open a NEW one before running the tool, so the changes
echo take effect.
echo.
pause
