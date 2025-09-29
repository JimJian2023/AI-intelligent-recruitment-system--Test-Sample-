@echo off
chcp 65001 >nul
echo ====================================
echo   AI Recruitment System - Setup Script
echo ====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected, please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not detected, please install Node.js 16.0+
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Environment check passed, starting installation...
echo.

:: Create backend virtual environment
echo [1/6] Creating Python virtual environment...
cd backend
if exist "venv" (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    echo [DONE] Virtual environment created successfully
)

:: Activate virtual environment and install dependencies
echo [2/6] Installing backend dependencies...
call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Backend dependencies installation failed
    pause
    exit /b 1
)
echo [DONE] Backend dependencies installed successfully

:: Database migration
echo [3/6] Initializing database...
python manage.py makemigrations
python manage.py migrate
echo [DONE] Database initialized successfully

:: Create environment variables file
echo [4/6] Configuring environment variables...
if exist ".env" (
    echo [SKIP] .env file already exists
) else (
    copy ".env.example" ".env"
    echo [DONE] .env file created successfully
)

cd ..

:: Install frontend dependencies
echo [5/6] Installing frontend dependencies...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Frontend dependencies installation failed
    pause
    exit /b 1
)
echo [DONE] Frontend dependencies installed successfully

cd ..

:: Create demo data (optional)
echo [6/6] Creating demo data...
set /p create_demo="Create demo data? (y/n): "
if /i "%create_demo%"=="y" (
    cd backend
    call venv\Scripts\activate
    python create_demo_data.py
    cd ..
    echo [DONE] Demo data created successfully
) else (
    echo [SKIP] Demo data creation skipped
)

echo.
echo ====================================
echo   Installation Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Edit backend\.env file to configure necessary parameters
echo 2. Double-click "start.bat" to launch the system
echo 3. Visit http://localhost:3000 to use the system
echo.
echo Press any key to exit...
pause >nul