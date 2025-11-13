# AI视频制作工具

一款结合多模态大模型能力的智能视频创作平台，支持从故事梗概到完整视频的全流程自动化制作。

## 技术栈

### 前端
- React 18+ + TypeScript
- Ant Design 5.x
- Electron (桌面应用)
- Redux Toolkit (状态管理)
- React Flow (流程图可视化)

### 后端
- Python 3.10+
- FastAPI (Web框架)
- Celery (异步任务队列)
- SQLAlchemy (ORM)
- Redis (缓存和消息队列)
- PostgreSQL (数据库)

### AI集成
- 通义千问 (文本生成)
- 智谱AI (文本生成)
- 百度文心 (文本生成)
- Stable Diffusion (图像生成)
- 通义万相 (图像生成)
- 可灵AI (视频生成)

### 视频处理
- FFmpeg (视频合成)
- OpenCV (视频处理)

## 项目结构

```
.
├── backend/                 # 后端服务
│   ├── app/                # 应用代码
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   ├── tasks/         # Celery任务
│   │   └── utils/         # 工具函数
│   ├── alembic/           # 数据库迁移
│   ├── tests/             # 测试
│   └── requirements.txt   # Python依赖
├── frontend/               # 前端应用
│   ├── src/               # 源代码
│   │   ├── components/   # React组件
│   │   ├── pages/        # 页面
│   │   ├── services/     # API服务
│   │   ├── store/        # Redux状态
│   │   └── utils/        # 工具函数
│   ├── public/           # 静态资源
│   └── electron/         # Electron主进程
├── storage/               # 本地存储目录
│   └── users/            # 用户文件
└── docs/                  # 文档
```

## 快速开始

### 后端启动

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Celery Worker启动

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### Electron启动

```bash
cd frontend
npm run electron:dev
```

## 数据库配置

```bash
# PostgreSQL连接信息
主机: localhost
端口: 5432
数据库: ai_video_creator
用户名: postgres
密码: 123456
```

## 许可证

MIT License
