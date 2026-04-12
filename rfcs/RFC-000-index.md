# RFC 索引

本目录下每一份 RFC 严格对应 [`../story.md`](../story.md) 中的一个章节（Feature / Epic），逐条用户故事有对应编号与验收标准。

RFC 状态：`Draft` → `Accepted` → `Implemented` → `Closed`

## 学生端

| 编号 | Feature | 对应章节 | 负责人 | 迭代 | 状态 |
|---|---|---|---|---|---|
| [RFC-001](RFC-001-student-identity.md) | A1 学生身份与访问范围 | 一 | 学生A | 1 | Draft |
| [RFC-002](RFC-002-browse-rooms.md) | A2 浏览自习室与座位 | 二 | 学生A | 1 | Draft |
| [RFC-003](RFC-003-search-filter.md) | A3 按条件找座位 | 三 | 学生A | 2 | Draft |
| [RFC-004](RFC-004-create-reservation.md) | A4 创建预约 | 四 | 林佳航 | 1 | Draft |
| [RFC-005](RFC-005-manage-reservation.md) | A5 管理自己的预约 | 五 | 林佳航 | 1 | Draft |
| [RFC-006](RFC-006-checkin.md) | A6 到场签到 | 六 | 林佳航 | 1 | Draft |
| [RFC-007](RFC-007-reminder-violation.md) | A7 提醒、违约与信用 | 七 | 学生C | 2 | Draft |
| [RFC-008](RFC-008-history-rebook.md) | A8 历史记录与复订 | 八 | 学生C | 2 | Draft |
| [RFC-009](RFC-009-smart-assistant.md) | A9 智能助手 | 九 | 学生C | 2 | Draft |

## 管理端

| 编号 | Feature | 对应章节 | 负责人 | 迭代 | 状态 |
|---|---|---|---|---|---|
| [RFC-010](RFC-010-rbac.md) | B1 角色与权限管理 | 十 | 管理员D | 2 | Draft |
| [RFC-011](RFC-011-room-admin.md) | B2 自习室生命周期 | 十一 | 管理员D | 1 | Draft |
| [RFC-012](RFC-012-seat-admin.md) | B3 座位建档与维护 | 十二 | 管理员D | 1 | Draft |
| [RFC-013](RFC-013-admin-reservations.md) | B4 预约过程干预 | 十三 | zzk | 1 | Draft |
| [RFC-014](RFC-014-violation-admin.md) | B5 违约记录与信用治理 | 十四 | zzk | 2 | Draft |
| [RFC-015](RFC-015-system-config.md) | B6 规则配置 | 十五 | zzk | 2 | Draft |
| [RFC-016](RFC-016-analytics.md) | B7 利用率分析 | 十六 | zzk | 2 | Draft |

## 系统级

| 编号 | Feature | 对应章节 | 负责人 | 迭代 | 状态 |
|---|---|---|---|---|---|
| [RFC-017](RFC-017-auto-tasks.md) | C1 自动规则执行 | 十七 | 管理员F | 1 | Draft |
| [RFC-018](RFC-018-notifications.md) | C2 通知体系 | 十八 | 学生C | 2 | Draft |
| [RFC-019](RFC-019-edge-cases.md) | C3 复杂业务场景 | 十九 | 管理员F | 2 | Draft |
| [RFC-020](RFC-020-audit-security.md) | C4 安全与留痕 | 二十 | 管理员F | 2 | Draft |
| [RFC-021](RFC-021-non-functional.md) | 非功能需求 | 二十一 | 全员 | — | Draft |

## RFC 模板

每份 RFC 至少包含以下小节：

1. **背景与目标** — 业务动机
2. **用户故事** — 逐条引用 story.md，保持编号一致
3. **数据模型** — 新增/修改的表
4. **API 设计** — 入参/出参/鉴权要求
5. **前端交互** — 页面/组件/关键交互
6. **验收标准（AC）** — 可执行的测试要点
7. **非目标** — 当前 RFC 不做的事
8. **依赖与风险** — 上下游 RFC、技术风险

## 变更流程

- 写 RFC → 在 Issue/PR 中评审 → 组长 Accept → 开发 → 实现后将状态改为 Implemented → 合入主干
- 若 story.md 发生调整，需要同步修订对应 RFC（保持章节号对齐）
