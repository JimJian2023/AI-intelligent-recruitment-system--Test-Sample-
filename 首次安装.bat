@echo off
chcp 65001 >nul
echo ====================================
echo   AI智能招聘系统 - 首次安装脚本
echo ====================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js，请先安装Node.js 16.0+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo [信息] 环境检查通过，开始安装...
echo.

:: 创建后端虚拟环境
echo [1/6] 创建Python虚拟环境...
cd backend
if exist "venv" (
    echo [跳过] 虚拟环境已存在
) else (
    python -m venv venv
    echo [完成] 虚拟环境创建成功
)

:: 激活虚拟环境并安装依赖
echo [2/6] 安装后端依赖...
call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)
echo [完成] 后端依赖安装成功

:: 数据库迁移
echo [3/6] 初始化数据库...
python manage.py makemigrations
python manage.py migrate
echo [完成] 数据库初始化成功

:: 创建环境变量文件
echo [4/6] 配置环境变量...
if exist ".env" (
    echo [跳过] .env文件已存在
) else (
    copy ".env.example" ".env"
    echo [完成] .env文件创建成功
)

cd ..

:: 安装前端依赖
echo [5/6] 安装前端依赖...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)
echo [完成] 前端依赖安装成功

cd ..

:: 创建演示数据（可选）
echo [6/6] 创建演示数据...
set /p create_demo="是否创建演示数据？(y/n): "
if /i "%create_demo%"=="y" (
    cd backend
    call venv\Scripts\activate
    python create_demo_data.py
    cd ..
    echo [完成] 演示数据创建成功
) else (
    echo [跳过] 演示数据创建
)

echo.
echo ====================================
echo   安装完成！
echo ====================================
echo.
echo 接下来请：
echo 1. 编辑 backend\.env 文件，配置必要参数
echo 2. 双击 "启动项目.bat" 启动系统
echo 3. 访问 http://localhost:3000 使用系统
echo.
echo 按任意键退出...
pause >nul