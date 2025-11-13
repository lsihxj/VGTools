@echo off
REM Celery Worker启动脚本

echo 启动Celery Worker...
echo.

REM 激活虚拟环境
call venv\Scripts\activate

REM 设置工作目录
cd /d %~dp0

REM 启动Celery Worker
celery -A app.core.celery_app worker --loglevel=info --pool=solo

pause
