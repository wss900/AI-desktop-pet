@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .venv\Scripts\activate
if not exist .env copy .env.example .env
python main.py
pause
