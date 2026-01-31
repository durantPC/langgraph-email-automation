@echo off
chcp 65001 >nul
REM 启动命令行版本（单次运行）

echo ========================================
echo   邮件自动化系统 - 命令行版本
echo ========================================
echo.

cd /d "%~dp0.."

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 设置 UTF-8 编码
set PYTHONIOENCODING=utf-8

REM 运行主程序
echo [启动] 正在运行邮件处理...
python main.py

echo.
echo [完成] 邮件处理完成
echo.
pause

