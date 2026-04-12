# Backend — 自习座位预约系统

## 技术栈
- Python 3.11+
- FastAPI / Uvicorn
- SQLAlchemy 2.x + SQLite
- APScheduler（定时任务）
- JWT 鉴权

## 快速开始

```bash
cd backend
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 初始化数据库 + 灌入 demo 数据
python -m app.seed

# 启动
uvicorn app.main:app --reload --port 8000
```

访问 <http://localhost:8000/docs> 查看 Swagger。

## 目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口 + 路由装配
│   ├── core/
│   │   ├── config.py        # 系统参数（可热更）
│   │   ├── database.py      # SQLAlchemy Engine / Session
│   │   └── security.py      # JWT、密码哈希
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── schemas/             # Pydantic 出入参
│   ├── api/                 # 路由层（按 Feature 拆分，不同人各写各的文件）
│   │   ├── auth.py          # A1 身份（学生A）
│   │   ├── rooms.py         # A2 浏览（学生A）
│   │   ├── search.py        # A3 搜索（学生A）
│   │   ├── reservations.py  # A4+A5 预约 & 取消（林佳航）
│   │   ├── checkin.py       # A6 签到（林佳航）
│   │   ├── notifications.py # A7 提醒（学生C）
│   │   ├── history.py       # A8 历史（学生C）
│   │   ├── assistant.py     # A9 智能助手（学生C）
│   │   └── admin/           # 管理端 API
│   │       ├── rbac.py      # B1（管理员D）
│   │       ├── rooms.py     # B2（管理员D）
│   │       ├── seats.py     # B3（管理员D）
│   │       ├── reservations.py  # B4（zzk）
│   │       ├── violations.py    # B5（zzk）
│   │       ├── config.py        # B6（zzk）
│   │       └── stats.py         # B7（管理员F）
│   ├── services/            # 业务逻辑层（跨路由复用）
│   ├── tasks/               # APScheduler 定时任务（C1）
│   └── seed.py              # demo 数据
├── tests/
└── requirements.txt
```

## 接口契约

所有接口统一响应：

```json
{ "code": 0, "message": "ok", "data": {...} }
```

错误码：0 成功 / 非 0 失败。
鉴权：除 `/api/auth/login` 外，均需 `Authorization: Bearer <token>`。
