@echo off
chcp 65001 >nul
title Vision Env Checker

echo ========================================
echo    Vision Env Checker - 启动器
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python
    echo.
    echo 请安装 Python 3.8 或更高版本：
    echo https://www.python.org/downloads/
    echo.
    echo 安装时请务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python 已安装

:: 检查依赖
echo.
echo 检查依赖...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 streamlit...
    pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo ✅ 依赖已就绪

:: 启动应用
echo.
echo ========================================
echo  正在启动 Vision Env Checker...
echo  浏览器将自动打开...
echo ========================================
echo.

:: 获取当前目录
set "SCRIPT_DIR=%~dp0"

:: 启动 Streamlit（后台运行）
start /B python -m streamlit run "%SCRIPT_DIR%web_app.py" --server.headless=true --server.port=8501

:: 等待服务启动
timeout /t 3 /nobreak >nul

:: 打开浏览器
start http://localhost:8501

echo.
echo ✅ 应用已启动！
echo 如果浏览器没有自动打开，请手动访问：
echo http://localhost:8501
echo.
echo 按任意键停止服务并退出...
pause >nul

:: 停止服务
taskkill /F /IM python.exe >nul 2>&1
echo 已停止服务
