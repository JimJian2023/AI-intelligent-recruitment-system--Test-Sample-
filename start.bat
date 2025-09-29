@echo off
chcp 65001 >nul
echo ====================================
echo   AI Recruitment System - Start Script
echo ====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected, please install Python 3.8+
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not detected, please install Node.js 16.0+
    pause
    exit /b 1
)

echo [INFO] Checking project environment...

:: Check backend virtual environment
if not exist "backend\venv" (
    echo [INFO] Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

:: Check backend dependencies
if not exist "backend\venv\Lib\site-packages\django" (
    echo [INFO] Installing backend dependencies...
    cd backend
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)

:: Check frontend dependencies
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

:: Check environment variables file
if not exist "backend\.env" (
    echo [WARNING] .env file not found, copying template...
    copy "backend\.env.example" "backend\.env"
    echo [TIP] Please edit backend\.env file to configure necessary parameters
)

echo.
echo [INFO] Environment check complete, starting services...
echo.

:: Start backend service
echo [START] Backend service (Django)...
start "AI-Recruitment-Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && python manage.py runserver"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend service
echo [START] Frontend service (React)...
start "AI-Recruitment-Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ====================================
echo   Services Started Successfully!
echo ====================================
echo.
echo Backend service: http://localhost:8000
echo Frontend service: http://localhost:3000
echo.
echo Browser will open automatically in a few seconds...
echo To stop services, close the corresponding command windows
echo.

:: Wait for frontend to start then open browser
timeout /t 10 /nobreak >nul
start http://localhost:3000

echo Press any key to exit this window...
pause >nul