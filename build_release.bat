@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === 桌面宠物 · 发布版打包 ===
echo.

set "RELEASE_PACK="
if exist build\release_pack.txt (
  set /p RELEASE_PACK=<build\release_pack.txt
)
if not defined RELEASE_PACK set "RELEASE_PACK=透明底小女孩示例"

echo 仅打包形象包: %RELEASE_PACK%
if not exist "形象\%RELEASE_PACK%\" (
  echo [错误] 找不到文件夹: 形象\%RELEASE_PACK%\
  pause
  exit /b 1
)

set "PY=%~dp0.venv\Scripts\python.exe"
set "PI=%~dp0.venv\Scripts\pyinstaller.exe"

if not exist "%PY%" (
  echo 请先运行 setup_env.bat（用项目 .venv，不要用 Anaconda 全局打包）
  pause
  exit /b 1
)

echo 使用: %PY%
"%PY%" --version
echo.

"%PY%" -m pip install --upgrade pip -q
"%PY%" -m pip install pyinstaller -q

echo 生成图标...
"%PY%" scripts\build_app_icon.py
if errorlevel 1 (
  echo [警告] 图标生成失败，将使用已有 app_icon.ico
)

echo.
echo 正在打包（约 1～3 分钟，务必使用 .venv 内 PyInstaller）...
set "RELEASE_CHARACTER_PACK=%RELEASE_PACK%"
"%PI%" build\DesktopPet.spec --noconfirm --clean
if errorlevel 1 (
  "%PY%" -m PyInstaller build\DesktopPet.spec --noconfirm --clean
)
if errorlevel 1 (
  echo.
  echo 打包失败。若提示 PyQt5 / PySide6 冲突：
  echo   1. 确认已运行 setup_env.bat
  echo   2. 不要用 Anaconda 的 pyinstaller，应使用 .venv\Scripts\pyinstaller.exe
  pause
  exit /b 1
)

echo.
echo 复制形象包到 exe 同级（仅 %RELEASE_PACK%）...
if exist dist\DesktopPet\_internal\形象 (
  if exist dist\DesktopPet\形象 rmdir /s /q dist\DesktopPet\形象
  xcopy /E /I /Y dist\DesktopPet\_internal\形象 dist\DesktopPet\形象\ >nul
)
if exist dist\DesktopPet\_internal\assets (
  xcopy /E /I /Y dist\DesktopPet\_internal\assets dist\DesktopPet\assets\ >nul
)
if not exist dist\DesktopPet\.env.example (
  copy /Y build\.env.release.example dist\DesktopPet\.env.example >nul
)

echo.
echo 复制用户说明...
copy /Y README.md dist\DesktopPet\使用说明.txt >nul 2>&1
if exist docs\首次使用.txt (
  copy /Y docs\首次使用.txt dist\DesktopPet\首次使用.txt >nul
)
copy /Y docs\SECURITY.md dist\DesktopPet\隐私说明.txt >nul 2>&1

echo.
echo === 完成 ===
echo 发布文件夹: %CD%\dist\DesktopPet\
echo 已包含形象: 形象\%RELEASE_PACK%\  （未包含其它形象包）
echo 默认 CHARACTER_PACK=%RELEASE_PACK% ，SHOW_CHARACTER_PICKER=0
echo 请将整个 DesktopPet 文件夹打成 zip 上传分发。
echo.
pause
