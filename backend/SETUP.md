# 后端环境搭建指南

## 前置要求

- Python 3.10或更高版本
- PostgreSQL 14+ (已安装并运行)
- Redis 6+ (已安装并运行)

## 自动安装(Windows)

运行自动安装脚本:

```batch
setup.bat
```

## 手动安装步骤

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```batch
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env`:

```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac
```

编辑 `.env` 文件,配置数据库和其他参数。

### 5. 初始化数据库

```bash
# 初始化Alembic(仅首次)
alembic init alembic

# 运行迁移
alembic upgrade head
```

### 6. 启动开发服务器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 启动Celery Worker

在新的终端窗口中:

```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows

# 启动worker
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo  # Windows
# 或
celery -A app.tasks.celery_app worker --loglevel=info  # Linux/Mac
```

## 验证安装

访问 http://localhost:8000 应该看到API欢迎信息。
访问 http://localhost:8000/docs 查看自动生成的API文档。

## 常见问题

### PostgreSQL连接失败

确保PostgreSQL服务正在运行:

```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql
```

检查数据库是否存在:

```sql
psql -U postgres
CREATE DATABASE ai_video_creator;
```

### Redis连接失败

确保Redis服务正在运行:

```bash
# Windows
redis-server

# Linux
sudo systemctl start redis
```

### 依赖安装失败

如果遇到某些包安装失败,可以尝试:

1. 升级pip: `python -m pip install --upgrade pip`
2. 使用国内镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
3. 单独安装失败的包

## 下一步

环境搭建完成后,可以继续:

1. 实现用户认证系统
2. 实现AI模型适配器
3. 实现业务服务层
