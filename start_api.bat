@echo off
echo ================================================================================
echo AI LOAD CONSOLIDATION PLATFORM - API LAUNCHER
echo ================================================================================
echo.

echo Starting FastAPI Backend...
echo.
echo API will be available at:
echo - Base URL: http://localhost:8000
echo - Interactive Docs: http://localhost:8000/docs
echo - Alternative Docs: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the API
echo ================================================================================
echo.

python backend/main.py

pause
