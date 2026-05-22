@echo off
cd /d "%~dp0"
if exist "StartDesktopPet.lnk" (
  start "" "%~dp0StartDesktopPet.lnk"
) else (
  call "%~dp0创建桌面快捷方式.bat"
)
