@echo off
echo ===============================================
echo Starting LogSec MCP Server v3.0
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Navigate to LogSec src directory
cd /d "%~dp0\..\src"

REM Check if logsec_core_v3_enhanced.py exists
if not exist "logsec_core_v3_enhanced.py" (
    echo [ERROR] logsec_core_v3_enhanced.py not found!
    echo Make sure you're in the LogSec directory
    pause
    exit /b 1
)

REM Start the MCP server
echo Starting Enhanced MCP server...
echo Press Ctrl+C to stop
echo.
python logsec_core_v3_enhanced.py

REM If we get here, the server stopped
echo.
echo MCP Server stopped.
pause
