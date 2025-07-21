@echo off
echo Google Sheets Combiner
echo =====================
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

REM Run the main script
echo Running Google Sheets Combiner...
echo.
".venv\Scripts\python.exe" main.py

echo.
echo Done! Check for the output Excel file.
pause
