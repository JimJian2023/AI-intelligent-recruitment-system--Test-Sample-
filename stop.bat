@echo off
chcp 65001 >nul
echo ====================================
echo   AI Recruitment System - Stop Script
echo ====================================
echo.

echo [INFO] Stopping related services...

:: Stop Django development server
echo [STOP] Django backend service...
taskkill /f /im python.exe /fi "WINDOWTITLE eq AI-Recruitment-Backend*" >nul 2>&1

:: Stop Node.js development server
echo [STOP] React frontend service...
taskkill /f /im node.exe /fi "WINDOWTITLE eq AI-Recruitment-Frontend*" >nul 2>&1

:: Stop possible npm processes
taskkill /f /im npm.cmd >nul 2>&1

:: Close possible opened command windows
taskkill /f /fi "WINDOWTITLE eq AI-Recruitment-Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq AI-Recruitment-Frontend*" >nul 2>&1

echo.
echo [DONE] All services have been stopped
echo.
echo Press any key to exit...
pause >nul