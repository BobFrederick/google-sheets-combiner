@echo off
REM Project Maintenance Script
REM Checks structure and runs common maintenance tasks

echo.
echo ==============================================
echo   Google Sheets Combiner - Project Maintenance
echo ==============================================
echo.

echo Checking project structure...
python utils\check_project_structure.py

echo.
echo Cleaning up Python cache files...
if exist "__pycache__" rmdir /s /q __pycache__
if exist "src\__pycache__" rmdir /s /q src\__pycache__
if exist "tests\__pycache__" rmdir /s /q tests\__pycache__
if exist "utils\__pycache__" rmdir /s /q utils\__pycache__

echo.
echo Checking for .pyc files in project directories...
for /r src %%i in (*.pyc) do (
    echo Found: %%i
    del "%%i"
)
for /r tests %%i in (*.pyc) do (
    echo Found: %%i
    del "%%i"
)
for /r utils %%i in (*.pyc) do (
    echo Found: %%i
    del "%%i"
)

echo.
echo ==============================================
echo   Maintenance Complete!
echo ==============================================
echo.
pause
