@echo off
title LogSec Test Fix

echo.
echo Test Import Fix
echo ===============
echo.

cd /d C:\LogSec\tests

echo Aktuelles Verzeichnis: %CD%
echo.

REM Backup der Test-Datei
if exist test_core_v3.py (
    copy test_core_v3.py test_core_v3_backup.py >nul
    echo Backup erstellt: test_core_v3_backup.py
)

REM Import-Statements mit PowerShell ersetzen
echo Fixe Import-Statements...

powershell -Command "(Get-Content test_core_v3.py) -replace 'from logsec_core_v3 import LogSecCore', 'from logsec_core_v3 import LogSecCore' | Set-Content test_core_v3.py"
powershell -Command "(Get-Content test_core_v3.py) -replace 'logsec_core_v3', 'logsec_core_v3' | Set-Content test_core_v3.py"
powershell -Command "(Get-Content test_core_v3.py) -replace 'LogSecCore', 'LogSecCore' | Set-Content test_core_v3.py"

echo Import-Statements gefixt.
echo.

REM Tests ausführen
echo Fuehre Tests aus...
python test_core_v3.py

echo.
echo Test-Fix abgeschlossen.
pause