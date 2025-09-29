@echo off
chcp 65001 >nul
echo ====================================
echo   AI智能招聘系统 - 停止服务脚本
echo ====================================
echo.

echo [信息] 正在停止相关服务...

:: 停止Django开发服务器
echo [停止] Django后端服务...
taskkill /f /im python.exe /fi "WINDOWTITLE eq AI招聘系统-后端*" >nul 2>&1

:: 停止Node.js开发服务器
echo [停止] React前端服务...
taskkill /f /im node.exe /fi "WINDOWTITLE eq AI招聘系统-前端*" >nul 2>&1

:: 停止可能的npm进程
taskkill /f /im npm.cmd >nul 2>&1

:: 关闭可能打开的命令行窗口
taskkill /f /fi "WINDOWTITLE eq AI招聘系统-后端*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq AI招聘系统-前端*" >nul 2>&1

echo.
echo [完成] 所有服务已停止
echo.
echo 按任意键退出...
pause >nul