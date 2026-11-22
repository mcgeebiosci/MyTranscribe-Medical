@echo off
rem MyTranscribe Medical from source, without a console window (see docs\DEVELOPMENT.md).
cd /d "%~dp0"
if not exist .venv\Scripts\pythonw.exe (
    echo .venv was not found: see docs\DEVELOPMENT.md.
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "src\gui_med.py"
