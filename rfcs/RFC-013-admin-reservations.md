# RFC-013：预约过程干预（B4）

- **对应章节**：story.md 十三、管理端：预约与代办操作
- **负责人**：zzk
- **迭代**：1（查询 + 代预约/代取消）；2（时间线 + 手动标记 + 释放）
- **状态**：Draft

## 1. 背景与目标

管理员需要全局视角看预约，帮助特殊场景学生代预约/代取消，处理异常占位。

## 2. 用户故事

| ID | 故事 | 迭代 |
|---|---|---|
| B4.1 | 查看所有预约记录 | 1 |
| B4.2 | 按学生姓名/学号/自习室/座位/日期筛选 | 1 |
| B4.3 | 查看指定座位的预约时间线 | 2 |
| B4.4 | 为指定学生代预约 | 1 |
| B4.5 | 为指定学生代取消 | 1 |
| B4.6 | 代预约同样触发规则校验 | 1 |
| B4.7 | 查看学生签到状态 | 1（通过预约状态） |
| B4.8 | 添加人工处理标记 | 2 |
| B4.9 | 手动释放异常占用座位 | 2 |

## 3. 数据模型

```python
class Reservation:
    # 迭代 2 新增
    admin_note: str = ""
    created_by_admin: int | None = None   # 代预约者 user_id
    force_released_at: datetime | None = None
```

## 4. API 设计

| 方法 | 路径 | 权限 | Story |
|---|---|---|---|
| GET | `/api/admin/reservations` | reservation.view | B4.1, B4.2, B4.7 |
| GET | `/api/admin/seats/{id}/timeline?date=` | reservation.view | B4.3 |
| POST | `/api/admin/reservations` `{student_no, seat_id, start_at, hours}` | reservation.manage | B4.4, B4.6 |
| POST | `/api/admin/reservations/{id}/cancel` | reservation.manage | B4.5 |
| PATCH | `/api/admin/reservations/{id}` `{admin_note}` | reservation.manage | B4.8 |
| POST | `/api/admin/reservations/{id}/force-release` | reservation.manage | B4.9 |

**代预约流程（B4.6）**：除了 actor 是 admin，其余校验与 RFC-004 完全一致（整点、时长、时段冲突、院系权限）。`created_by_admin` 记录代办者 ID。

**代取消**：无论预约是否已开始都可以，但要求 admin_note 必填，并写审计日志（RFC-020）。

**强制释放**：仅对 VIOLATED 或异常占位有效，将 Reservation 标为 CANCELLED + `force_released_at=now` + 审计日志。

## 5. 前端交互

- `/admin/reservations`：高级筛选条 + 表格
- 每行操作列：【代取消】【加备注】
- 顶部新增按钮弹出"为学生代预约"表单（学号选择 + 座位选择 + 时间）
- `/admin/seats/:id/timeline`：小时条形图，已预约/已签到用不同颜色，点击某条跳详情

## 6. 验收标准

- [x] GET 支持 student_no/room_id/date/status 组合筛选
- [x] 代预约时物理学院学生预约计算机教室仍返回 403（B4.6）
- [ ] 代取消必须填 admin_note 否则返回 400
- [ ] 强制释放后座位时段立即可被他人预约
- [ ] 代办操作在 `/api/admin/audit` 中可查（字段 actor + target）

## 7. 非目标

- 不做批量操作
- 不做预约审批流（假设所有预约立即生效）

## 8. 依赖与风险

- 依赖：RFC-004、RFC-010（权限）、RFC-020（审计）
- 风险：代取消绕过学生侧规则，必须有强审计留痕
