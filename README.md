# 自习座位预约系统

高校自习室座位预约，覆盖学生端预约/签到/违约和管理端自习室/座位/预约/参数/统计。

## 目录

```
software/
├── backend/           # FastAPI + SQLite
├── admin-web/         # 管理端 Vue3（端口 5273）
├── student-web/       # 学生端 Vue3（端口 5174）
├── docs/
│   └── ITERATION_1.md # 第一阶段任务看板（按人分工）
├── story.md           # 用户故事总清单
└── 课程要求.md
```

## 技术栈

- 后端：Python 3.11+ / FastAPI / SQLAlchemy 2 / SQLite / APScheduler / JWT
- 前端：Vue 3 / Vite / Vue Router / Pinia / Axios

## 快速启动

### 1. 后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed                          # 灌 demo 数据
uvicorn app.main:app --reload --port 8000
```

Swagger：<http://localhost:8000/docs>

demo 账号：
- 学生：`20230001 / 123456`（计算机学院）、`20230002 / 123456`（物理学院）
- 管理员：`admin / admin`

### 2. 管理端

```bash
cd admin-web
npm install
npm run dev  # http://localhost:5273
```

### 3. 学生端

```bash
cd student-web
npm install
npm run dev  # http://localhost:5174
```

前端通过 Vite 代理 `/api` 指向 `http://localhost:8000`，开发期零配置。

## 测试

```bash
# 单元/集成测试（20 个用例，覆盖 A1/A2/A4/A5/A6/B2/B3/B4）
make test

# 端到端冒烟（自动启动后端，curl 跑主链路）
bash scripts/smoke.sh

# 一键跑通全部（seed + pytest + 两端 build）
make all
```

## 开发文档

- **需求清单**：[story.md](story.md) · 21 章、约 170 条用户故事
- **设计文档**：[rfcs/](rfcs/) · 与 story.md 21 章严格对齐的 21 份 RFC + 1 份索引
- **迭代看板**：[docs/ITERATION_1.md](docs/ITERATION_1.md) · 按 6 人分工的任务清单

## CI/CD

| 平台 | 配置文件 | 说明 |
|---|---|---|
| GitHub Actions | [.github/workflows/ci.yml](.github/workflows/ci.yml) | PR/push 触发：后端 pytest + 两端 build + RFC 完整性校验 |
| GitHub Actions | [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | main 分支触发：打包 release artifact |
| DevCloud | [.devcloud/](.devcloud/) | 编译构建 / 部署 / 流水线配置（课程要求） |

## Makefile 速查

```bash
make install          # 装依赖
make seed             # 重置 demo 数据
make test             # pytest
make build            # 前端 build
make run-backend      # 启动后端 8000
make run-admin        # 启动管理端 5273
make run-student      # 启动学生端 5174
make all              # seed + test + build
make clean            # 清理
