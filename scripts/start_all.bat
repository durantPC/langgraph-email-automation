@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 邮件自动化系统 - 启动脚本
echo ============================================================
echo.

cd /d %~dp0..

echo [1/2] 启动后端API服务...
start "后端API" cmd /k "cd /d %~dp0.. && python backend_api.py"

echo [2/2] 启动前端开发服务器...
timeout /t 3 /nobreak >nul
start "前端服务" cmd /k "cd /d %~dp0..\frontend && npm run dev"

echo.
echo ============================================================
echo ✅ 服务启动完成！
echo.
echo 📡 后端API: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo 🌐 前端界面: http://localhost:3000
echo.
echo 🔐 默认账号: admin / admin123
echo ============================================================
echo.
echo 按任意键退出此窗口（服务会继续运行）...
pause >nul
