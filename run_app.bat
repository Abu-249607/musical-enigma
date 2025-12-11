@echo off
REM Census Employment Explorer - Easy Launcher for Windows
REM Just double-click this file to start the app!

cd /d "%~dp0"

if not exist "venv" (
    echo Setting up for first time use...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -e ".[web]"
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting Census Employment Explorer...
echo Opening in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the app
echo.

streamlit run app.py --server.headless true
pause
