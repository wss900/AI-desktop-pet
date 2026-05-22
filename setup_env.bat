@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === 桌面宠物 · 环境安装 ===
echo.

where py >nul 2>&1
if %errorlevel%==0 (
  echo 使用 Python 3.12 创建虚拟环境...
  py -3.12 -m venv .venv
) else (
  echo 使用 python 创建虚拟环境（建议安装 Python 3.12）...
  python -m venv .venv
)

if not exist .venv\Scripts\python.exe (
  echo [错误] 虚拟环境创建失败。请安装 Python 3.12:
  echo https://www.python.org/downloads/
  pause
  exit /b 1
)

call .venv\Scripts\activate
python --version
echo.
echo 安装依赖...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo 验证 PySide6...
python -c "from PySide6.QtCore import Qt; print('PySide6 OK')"
if errorlevel 1 (
  echo.
  echo [失败] 仍无法加载 Qt。请安装 VC++ 运行库后重试:
  echo https://aka.ms/vs/17/release/vc_redist.x64.exe
  pause
  exit /b 1
)

if not exist .env copy .env.example .env
echo.
echo === 安装成功 ===
echo 运行: python main.py  或双击 run.bat
pause
