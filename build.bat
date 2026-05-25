@echo off
echo ============================================================
echo  Academic Intervention Sorter — Build Script
echo ============================================================
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Make sure Python 3.10+ is on your PATH.
    pause
    exit /b 1
)

REM Install / upgrade PyInstaller
echo [1/3] Installing PyInstaller...
pip install pyinstaller --quiet --upgrade

REM Clean previous build
echo [2/3] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build
echo [3/3] Building executable...
pyinstaller academic_intervention_sorter.spec --clean

echo.
if exist dist\AcademicInterventionSorter.exe (
    echo ============================================================
    echo  Build complete!
    echo  Output: dist\AcademicInterventionSorter.exe
    echo.
    echo  To distribute: copy AcademicInterventionSorter.exe to any
    echo  Windows machine — no Python installation required.
    echo ============================================================
) else (
    echo  Build may have failed — check output above for errors.
)
echo.
pause
