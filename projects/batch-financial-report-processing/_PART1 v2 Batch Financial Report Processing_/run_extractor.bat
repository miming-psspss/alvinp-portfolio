@echo off
setlocal enabledelayedexpansion
title Batch Financial Report Processing for VAs - Part 1: Extraction

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE="

REM =========================================================
REM STEP 1: Use the saved python path from install_setup.bat
REM if we have one and it still points to a real file.
REM =========================================================
if exist "%SCRIPT_DIR%python_path.txt" (
    set /p PYTHON_EXE=<"%SCRIPT_DIR%python_path.txt"
    if not exist "!PYTHON_EXE!" set "PYTHON_EXE="
)

REM =========================================================
REM STEP 2: If we don't have a saved path yet, check whether
REM "python" on PATH is a REAL install or just the Windows
REM Store placeholder. The Store placeholder makes "where
REM python" succeed even when Python isn't really installed,
REM so we check the actual version output instead.
REM =========================================================
if "!PYTHON_EXE!"=="" (
    for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYVER_OUTPUT=%%v"
    echo !PYVER_OUTPUT! | findstr /C:"Python 3" >nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
    )
)

REM =========================================================
REM STEP 3: Still nothing real found. Explain what's happening
REM and ask permission before touching anything.
REM =========================================================
if "!PYTHON_EXE!"=="" (
    echo ============================================
    echo   Python was not found on this computer
    echo ============================================
    echo.
    echo If you just saw a message about the Microsoft Store, that
    echo is a Windows placeholder, not a real Python installation.
    echo This tool needs the real thing, which install_setup.bat
    echo can download and install for you automatically.
    echo.
    set /p "RUNSETUP=Run install_setup.bat now to fix this? (Y/N): "
    if /I "!RUNSETUP!"=="Y" (
        if exist "%SCRIPT_DIR%install_setup.bat" (
            call "%SCRIPT_DIR%install_setup.bat"
            REM Re-check after setup finishes
            if exist "%SCRIPT_DIR%python_path.txt" (
                set /p PYTHON_EXE=<"%SCRIPT_DIR%python_path.txt"
            )
        ) else (
            echo.
            echo install_setup.bat was not found in this folder.
            echo Please make sure it's saved in the same folder as
            echo this file, then try again.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo No changes made. Please run install_setup.bat yourself
        echo when you're ready, then try this again.
        echo.
        pause
        exit /b 1
    )
)

if "!PYTHON_EXE!"=="" (
    echo.
    echo Setup did not complete successfully. Please close this
    echo window, open a NEW one, and try running this file again.
    echo If it still fails, take a screenshot and send it to your
    echo supervisor for help.
    echo.
    pause
    exit /b 1
)

REM =========================================================
REM Launch the tool
REM =========================================================
"!PYTHON_EXE!" "%SCRIPT_DIR%financial_report_extractor_part1.py"

if !errorlevel! neq 0 (
    echo.
    echo The tool closed unexpectedly. If this keeps happening,
    echo take a screenshot of any error above and send it to your
    echo supervisor for help.
    pause
)
