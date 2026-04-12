# RFC-021：非功能需求

- **对应章节**：story.md 二十一、可以进一步补充的"非功能"故事
- **负责人**：全员（由 TL 统筹）
- **迭代**：贯穿
- **状态**：Draft

## 1. 背景与目标

把课程常提的"好用、快、稳、可扩展、可配置"显式化为可评估的目标与手段。

## 2. 用户故事（story.md 末尾 5 条）

| ID | 故事 | 目标 |
|---|---|---|
| NF.1 | 手机端页面简洁易操作 | 移动端可用性 |
| NF.2 | 搜索和预约响应够快 | 性能 |
| NF.3 | 管理后台在主流浏览器稳定运行 | 兼容性 |
| NF.4 | 系统支持未来扩展更多通知渠道和 AI 能力 | 可扩展 |
| NF.5 | 参数化配置而非写死规则 | 可配置 |

## 3. 目标指标

| 维度 | 指标 | 目标 |
|---|---|---|
| 页面性能 | 首屏 TTFB | < 1s（本地） |
| 接口性能 | p95 `/api/rooms` | < 200ms |
| 接口性能 | p95 `/api/reservations`（写） | < 500ms |
| 可用性 | SQLite + 单进程 | 单机 99% |
| 浏览器兼容 | Chrome / Edge / Safari 最近 2 个大版本 | 全支持 |
| 移动端 | 视口 375×667 以上 | 无横向滚动 |

## 4. 实施手段

### NF.1 移动端（对应学生端）
- 所有页面 `<meta viewport>` + 弹性布局 / Flex
- 按钮最小点击区 44×44
- 表格类改用卡片列表（窄屏隐藏列）

### NF.2 性能
- 后端：索引规范
  - `reservations(user_id)` / `reservations(seat_id, start_at, end_at)` / `reservations(status, start_at)`
  - `seats(room_id, is_active)`
  - `rooms(is_active, department)`
- 前端：
  - 路由懒加载：`() => import('./views/X.vue')`
  - axios 去重/取消：切页面取消未完成请求
- 压测：`locust` 10 并发跑预约创建，接口 p95 < 500ms

### NF.3 浏览器兼容
- Vite 默认 ES2020；追加 `browserslist: ["chrome>=90","safari>=14","edge>=90"]`
- CI 补 Playwright 冒烟（迭代 2 选做）

### NF.4 可扩展
- 通知渠道：RFC-018 `Channel` 接口；新增渠道只写一个类
- 智能助手：RFC-009 分层（意图识别 / 技能），LLM 升级只替换第一层
- 参数：RFC-015 入库，新增参数不改代码

### NF.5 可配置
- 所有业务阈值走 `SystemConfig`（RFC-015）
- 环境相关走 `.env` / `pydantic-settings`
- 禁止在业务代码中出现魔法数字；PR review 时作为检查项

## 5. 验收标准

- [ ] `npm run build` 产物 gzip < 200KB
- [ ] `pytest` 全绿 + 覆盖率 > 60%（迭代 2 目标 > 75%）
- [ ] 在手机浏览器（或 devtools mobile emulation）完整走完登录 → 预约 → 签到 → 取消
- [ ] `grep -r "magic-number"` 无命中（用来检查硬编码时段）
- [ ] 新增一个假的通知渠道（打印日志）仅需 < 20 行代码

## 6. 非目标

- 不追求大流量（数千并发），面向校内场景
- 不做多语言

## 7. 依赖与风险

- 依赖：所有业务 RFC
- 风险：性能目标在 SQLite 下若不够，迁移 PostgreSQL；业务代码不变（SQLAlchemy 抽象）
