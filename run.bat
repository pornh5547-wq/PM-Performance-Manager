@echo off
title PM Performance Manager
cd /d "%~dp0"
echo Starting PM Performance Manager...
echo.
echo NOTE: This application requires administrator privileges.
echo If prompted, click Yes to allow.
echo.
echo To run without admin (limited functionality), press Ctrl+C
echo and use: python main.py --no-admin
echo.
"C:\Program Files\Python312\python.exe" main.py
pause
