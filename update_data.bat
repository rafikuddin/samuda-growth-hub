@echo off
REM Samuda Growth Hub - make a fresh data.json from the Excel workbook.
REM 1) Refresh and SAVE the workbook in Excel first.  2) Double-click this file.
cd /d "%~dp0"
python build_data.py "Samuda_Growth_Dashboard_v5.xlsx" data.json
if errorlevel 1 (echo. & echo Something went wrong - see the message above. & pause & exit /b 1)
echo.
echo data.json is ready. Upload it to GitHub (Add file - Upload files - Commit changes).
pause
