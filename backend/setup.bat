@echo off
echo ====================================
echo AI视频制作工具 - 后端环境设置
echo ====================================
echo.

echo [1/5] 检查Python版本...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.10或更高版本
    pause
    exit /b 1
)
echo.

echo [2/5] 创建虚拟环境...
if exist venv (
    echo 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    echo 虚拟环境创建成功
)
echo.

echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat
echo.

echo [4/5] 升级pip...
python -m pip install --upgrade pip
echo.

echo [5/5] 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)
echo.

echo ====================================
echo 环境设置完成!
echo ====================================
echo.
echo 下一步:
echo 1. 复制 .env.example 为 .env 并配置参数
echo 2. 确保PostgreSQL和Redis已安装并运行
echo 3. 运行: python -m alembic upgrade head (初始化数据库)
echo 4. 运行: uvicorn app.main:app --reload (启动开发服务器)
echo.
pause
