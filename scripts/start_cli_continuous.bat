@echo off
chcp 65001 >nul
REM 启动命令行版本（持续监控模式）

echo ========================================
echo   邮件自动化系统 - 持续监控模式
echo ========================================
echo.
echo 每 15 分钟自动检查新邮件
echo 按 Ctrl+C 停止监控
echo.

cd /d "%~dp0.."

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 设置 UTF-8 编码
set PYTHONIOENCODING=utf-8

REM 运行持续监控程序
python main_continuous.py

pause

