# RFC-004：创建预约（A4）

- **对应章节**：story.md 四、学生端：预约座位
- **负责人**：林佳航
- **迭代**：1
- **状态**：Draft

## 1. 背景与目标

预约创建是整条主链路的核心。必须同时满足"整点 + 时长上限 + 院系权限 + 时段冲突 + 单用户唯一"多重约束，并在失败时给出可操作的提示。

## 2. 用户故事

| ID | 故事 | 迭代 |
|---|---|---|
| A4.1 | 选择起始整点和时长创建预约 | 1 |
| A4.2 | 仅允许整点预约 | 1 |
| A4.3 | 限制单次最长时长（默认 4h，系统参数可调） | 1 |
| A4.4 | 预约前可看到结束时间 | 1（前端计算） |
| A4.5 | 提交前校验座位该时段可用 | 1 |
| A4.6 | 校验落在自习室开放时段内 | 1 |
| A4.7 | 禁止预约院系不开放的教室 | 1 |
| A4.8 | 预约成功后展示详情 | 1 |
| A4.9 | 生成预约记录供后续查看/签到/取消 | 1 |
| A4.10 | 防止同一时间预约多个座位 | 1 |
| A4.11 | 预约失败时明确告知原因 | 1 |
| A4.12 | 在座位详情中直接预约 | 1 |
| A4.13 | 空闲时段一键 1/2/3/4 小时 | 1 |
| A4.14 | 从"现在开始"快速预约最近整点 | 2 |

## 3. 数据模型

```python
class Reservation:
    id: int
    user_id: FK(User)
    seat_id: FK(Seat)
    room_id: FK(Room)
    start_at: datetime     # 必须分秒归零
    end_at: datetime
    status: ReservationStatus  # PENDING / CHECKED_IN / CANCELLED / VIOLATED / FINISHED
    checkin_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
```

## 4. API 设计

### POST `/api/reservations`

入参：
```json
{ "seat_id": 1, "start_at": "2026-04-12T19:00:00", "hours": 2 }
```

后端校验顺序（任何一步失败立刻返回对应 4xx 错误）：

| 步骤 | 校验项 | 错误码 | 对应 Story |
|---|---|---|---|
| 1 | `start_at` 分秒为 0 | 400 `预约必须为整点` | A4.2 |
| 2 | `1 <= hours <= max_reservation_hours` | 400 `时长需 1~4 小时` | A4.3 |
| 3 | Seat 存在且 is_active | 404 `座位不存在或停用` | A4.5 |
| 4 | Room is_active | 404 `自习室不可用` | A4.5 |
| 5 | 院系匹配 | 403 `无权预约该院系自习室` | A4.7 |
| 6 | `[start, end]` 在 Room 开放时段内 | 400 `须在开放时间内` | A4.6 |
| 7 | 座位时段冲突（含 PENDING + CHECKED_IN） | 409 `该座位此时段已被预约` | A4.5 |
| 8 | 同一用户时段冲突 | 409 `同一时段你已有其它预约` | A4.10 |

成功：
```json
{ "code":0, "data":{"id":1, "start_at":"...", "end_at":"...", "status":"PENDING"} }
```

## 5. 前端交互

- `/rooms/:id` 详情页：点击座位卡片后下方出现预约表单
  - `<input type="datetime-local" step="3600">` 强制整点
  - 时长按钮组 `1h | 2h | 3h | 4h`（A4.13）
  - 实时展示 `结束时间：YYYY-MM-DD HH:00`（A4.4）
  - 错误以红字展示完整后端 `message`（A4.11）
- 提交时 **必须** 把 `datetime-local` 的原始字符串（naive 本地时间，形如 `2026-04-12T19:00`）作为 `start_at` 直接上送，禁止调用 `new Date(...).toISOString()`——后者会加 `Z` 变成 aware datetime，与后端 naive 的开放时段比较时抛 `TypeError`（见 Bug-2026-04-13-01）
- 成功后跳转到 `/my` 并滚动到最新一条（A4.8, A4.9）

## 6. 验收标准

- [x] `start_at=2026-04-12T19:30` 返回 400
- [x] `hours=5` 返回 400
- [x] 物理学院学生预约计算机学院教室返回 403
- [x] 两个学生抢同一座位同一时段，第二个返回 409
- [x] 同一学生在 19:00-21:00 已有预约后再尝试 20:00 其它座位返回 409
- [x] 预约 06:00 开始（教室 07:00 开放）返回 400
- [x] 前端提交的 `start_at` 为 naive 本地时间（不含 `Z`/时区偏移），避免与开放时段 naive datetime 比较时崩 500（Bug-2026-04-13-01）

## 7. 非目标

- 本 RFC 不含取消和签到（见 RFC-005 / RFC-006）
- 不做分布式锁；SQLite 的事务已能避免同进程竞争
- 不支持循环/重复预约

## 8. 依赖与风险

- 依赖：RFC-001（鉴权）、RFC-011（Room）、RFC-012（Seat）
- 风险：`max_reservation_hours` 可配（RFC-015），迭代 1 读 `settings` 字段，迭代 2 改为读数据库
