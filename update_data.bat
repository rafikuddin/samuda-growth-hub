@echo off
REM Samuda Growth Hub - make a fresh data.json from the Excel files in this folder
REM (dump file, product master, customer master). Double-click this file.
cd /d "%~dp0"
python build_data.py
if errorlevel 1 (echo. & echo Something went wrong - see the message above. & pause & exit /b 1)
echo.
echo data.json is ready. Upload it to GitHub (Add file - Upload files - Commit changes).
pause
