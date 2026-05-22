@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist .venv\Scripts\pythonw.exe (
  if not exist .venv\Scripts\python.exe (
    echo 首次运行请先双击 setup_env.bat 安装环境
    pause
    exit /b 1
  )
)

set "PYW=.venv\Scripts\pythonw.exe"
if not exist "%PYW%" set "PYW=.venv\Scripts\python.exe"

"%PYW%" -c "from PySide6.QtCore import Qt" 2>nul
if errorlevel 1 (
  echo PySide6 未就绪，请双击 setup_env.bat 重新安装
  pause
  exit /b 1
)

if not exist .env copy .env.example .env

REM 独立进程启动（关掉本窗口不影响桌宠）；pythonw 无黑框
start "" "%PYW%" main.py
exit /b 0
