@echo off
chcp 65001 >nul
echo.
echo AI图片处理工具 - 正在启动...
echo.
python app.py
if errorlevel 1 (
    echo.
    echo 启动失败，请确认已安装依赖：
    echo pip install flask pillow piexif numpy
    echo.
    pause
)
