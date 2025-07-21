@echo off
echo Google Sheets Combiner with Auto-Conversion
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run the setup first.
    pause
    exit /b 1
)

REM Check if credentials exist
if not exist "credentials.json" (
    echo Error: credentials.json not found!
    echo Please follow the setup instructions in GOOGLE_API_SETUP.md
    pause
    exit /b 1
)

echo Choose an option:
echo 1. Run normally (no conversion)
echo 2. Convert Excel files to Google Sheets (keep originals)
echo 3. Convert Excel files and delete originals
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Running without conversion...
    ".venv\Scripts\python.exe" main.py
) else if "%choice%"=="2" (
    echo Running with Excel conversion (keeping originals)...
    ".venv\Scripts\python.exe" main.py --convert-excel
) else if "%choice%"=="3" (
    echo Running with Excel conversion (deleting originals)...
    ".venv\Scripts\python.exe" main.py --convert-excel --cleanup-originals
) else (
    echo Invalid choice. Running normally...
    ".venv\Scripts\python.exe" main.py
)

echo.
echo Done! Check for the output Excel file.
pause
