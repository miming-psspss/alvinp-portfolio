@echo off
setlocal enabledelayedexpansion
title Batch Financial Report Processing for VAs - Part 2

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE="

if exist "%SCRIPT_DIR%python_path.txt" (
    set /p PYTHON_EXE=<"%SCRIPT_DIR%python_path.txt"
    if not exist "!PYTHON_EXE!" set "PYTHON_EXE="
)

if "!PYTHON_EXE!"=="" (
    for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYVER_OUTPUT=%%v"
    echo !PYVER_OUTPUT! | findstr /C:"Python 3" >nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
    )
)

if "!PYTHON_EXE!"=="" (
    echo ============================================
    echo   Python was not found on this computer
    echo ============================================
    echo.
    echo If you just saw a message about the Microsoft Store, that
    echo is a Windows placeholder, not a real Python installation.
    echo This tool needs the real thing, which install_setup_part2.bat
    echo can download and install for you automatically.
    echo.
    set /p "RUNSETUP=Run install_setup_part2.bat now to fix this? (Y/N): "
    if /I "!RUNSETUP!"=="Y" (
        if exist "%SCRIPT_DIR%install_setup_part2.bat" (
            call "%SCRIPT_DIR%install_setup_part2.bat"
            if exist "%SCRIPT_DIR%python_path.txt" (
                set /p PYTHON_EXE=<"%SCRIPT_DIR%python_path.txt"
            )
        ) else (
            echo.
            echo install_setup_part2.bat was not found in this folder.
            echo Please make sure it's saved in the same folder as
            echo this file, then try again.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo No changes made. Please run install_setup_part2.bat yourself
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

REM Also check openpyxl specifically, since Python alone isn't enough
REM for this tool the way it was for Part 1.
"!PYTHON_EXE!" -c "import openpyxl" >nul 2>nul
if !errorlevel! neq 0 (
    echo.
    echo Python was found, but the openpyxl add-on is missing.
    set /p "FIXPYXL=Run install_setup_part2.bat now to fix this? (Y/N): "
    if /I "!FIXPYXL!"=="Y" (
        call "%SCRIPT_DIR%install_setup_part2.bat"
    ) else (
        echo.
        echo No changes made. Please run install_setup_part2.bat yourself
        echo when you're ready, then try this again.
        echo.
        pause
        exit /b 1
    )
)

"!PYTHON_EXE!" "%SCRIPT_DIR%financial_report_consolidator_part2.py"

if !errorlevel! neq 0 (
    echo.
    echo The tool closed unexpectedly. If this keeps happening,
    echo take a screenshot of any error above and send it to your
    echo supervisor for help.
    pause
)
