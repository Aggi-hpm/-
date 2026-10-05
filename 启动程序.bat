@echo off
cd /d "%~dp0"
echo ========================================
echo   自动化识别显示程序
echo ========================================
echo.
echo 正在启动...
echo.
"%~dp0python\python.exe" main.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo 程序启动失败
    echo ========================================
    echo.
    pause
)