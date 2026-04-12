# DevCloud 集成说明

课程要求在华为云 DevCloud 上完成 DevOps 完整流程。本目录 YAML 为参考配置——DevCloud 实际使用可视化配置界面，请按此文档上传/填写。

## 步骤对照

| 课程要求 | 对应文件/配置 | 操作 |
|---|---|---|
| 2. 组长创建 Scrum 项目 | — | DevCloud → 项目管理 → 新建 |
| 3. 编写需求规划 | `rfcs/` + `story.md` | 将 RFC 导入为 Epic/Story/Task |
| 4. 关联测试用例 | `backend/tests/` | DevCloud → 测试管理 → 导入用例 |
| 5. 创建代码库并托管 | 全仓库 | DevCloud → 代码托管 → 新建 |
| 6. 编译构建（含单元测试） | `.devcloud/build.yml` | DevCloud → 编译构建 → 新建任务 |
| 7. 部署任务 | `.devcloud/deploy.yml` | DevCloud → 部署 → 新建任务 |
| 8. 流水线 | `.devcloud/pipeline.yml` | DevCloud → 流水线 → 新建 |

## 建议的需求层级（导入到 DevCloud）

```
Project: 自习座位预约系统
├── Epic A：学生端
│   ├── Feature A1（RFC-001）身份识别
│   │   └── Story A1.1 统一身份登录
│   │       └── Task [后端] POST /api/auth/login
│   │       └── Task [前端] 登录页
│   │       └── TestCase  登录成功/失败冒烟
│   ├── Feature A2 浏览自习室
│   └── ...
└── Epic B：管理端
    └── ...
```

## 测试用例关联

`backend/tests/` 下每个 `test_*.py` 函数对应一个 DevCloud 测试用例。
CI 运行后 `backend/report.xml` 可上传到 DevCloud → 测试管理作为执行证据。

## 分支策略

- `main`：生产分支，受保护，仅接受 PR 合并
- `develop`：集成分支，日常合并
- `feat/RFC-XXX-*`：Feature 分支
- `fix/*`：Bugfix 分支

## 提交规范

```
<type>(<scope>): <subject>

type: feat | fix | docs | refactor | test | chore | ci
scope: auth | reservation | checkin | admin | ...
```

示例：`feat(reservation): 整点校验（RFC-004 A4.2）`
