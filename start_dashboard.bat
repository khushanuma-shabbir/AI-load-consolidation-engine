@echo off
echo ================================================================================
echo AI LOAD CONSOLIDATION PLATFORM - DASHBOARD LAUNCHER
echo ================================================================================
echo.

echo Step 1: Checking JSON files...
python fix_json_files.py
if errorlevel 1 (
    echo ERROR: Failed to fix JSON files
    pause
    exit /b 1
)

echo.
echo Step 2: Starting Streamlit Dashboard...
echo.
echo Dashboard will open in your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo ================================================================================
echo.

streamlit run dashboard/app.py

pause
