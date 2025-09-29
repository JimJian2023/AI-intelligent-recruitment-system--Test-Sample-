@echo off
chcp 65001 >nul
echo ====================================
echo   AI智能招聘系统 - 一键启动脚本
echo ====================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js，请先安装Node.js 16.0+
    pause
    exit /b 1
)

echo [信息] 正在检查项目环境...

:: 检查后端虚拟环境
if not exist "backend\venv" (
    echo [信息] 创建Python虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

:: 检查后端依赖
if not exist "backend\venv\Lib\site-packages\django" (
    echo [信息] 安装后端依赖...
    cd backend
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)

:: 检查前端依赖
if not exist "frontend\node_modules" (
    echo [信息] 安装前端依赖...
    cd frontend
    npm install
    cd ..
)

:: 检查环境变量文件
if not exist "backend\.env" (
    echo [警告] 未找到.env文件，正在复制模板...
    copy "backend\.env.example" "backend\.env"
    echo [提示] 请编辑 backend\.env 文件配置必要参数
)

echo.
echo [信息] 环境检查完成，正在启动服务...
echo.

:: 启动后端服务
echo [启动] 后端服务 (Django)...
start "AI招聘系统-后端" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && python manage.py runserver"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端服务
echo [启动] 前端服务 (React)...
start "AI招聘系统-前端" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ====================================
echo   服务启动完成！
echo ====================================
echo.
echo 后端服务: http://localhost:8000
echo 前端服务: http://localhost:3000
echo.
echo 系统将在几秒后自动打开浏览器...
echo 如需停止服务，请关闭对应的命令行窗口
echo.

:: 等待前端启动后打开浏览器
timeout /t 10 /nobreak >nul
start http://localhost:3000

echo 按任意键退出此窗口...
pause >nul