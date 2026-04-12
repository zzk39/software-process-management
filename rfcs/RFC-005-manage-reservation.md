# RFC-005：管理自己的预约（A5）

- **对应章节**：story.md 五、学生端：预约变更与取消
- **负责人**：林佳航
- **迭代**：1（查看 + 取消）；2（改签）
- **状态**：Draft

## 1. 背景与目标

学生需要能看到自己所有预约的当前状态并在合理规则下取消或改签，以支持履约闭环。

## 2. 用户故事

| ID | 故事 | 迭代 |
|---|---|---|
| A5.1 | 查看当前有效预约 | 1 |
| A5.2 | 取消尚未开始的预约 | 1 |
| A5.3 | 取消后收到确认提示 | 1 |
| A5.4 | 取消后座位立即回到可预约 | 1 |
| A5.5 | 查看五态：PENDING/CHECKED_IN/CANCELLED/VIOLATED/FINISHED | 1 |
| A5.6 | 开始前修改时长或重新选位 | 2 |
| A5.7 | 不支持改签时，一键取消后重新预约 | 2 |
| A5.8 | 开始后不可改时间段 | 1（由后端约束） |

## 3. 数据模型

复用 `Reservation`，`ReservationStatus` 枚举保持 5 值。

## 4. API 设计

| 方法 | 路径 | 说明 | AC |
|---|---|---|---|
| GET | `/api/reservations/me` | 我的全部预约（按 start_at 降序，默认返回近 90 天 + 未来） | A5.1, A5.5 |
| POST | `/api/reservations/{id}/cancel` | 取消（仅 status=PENDING 且 start_at > now） | A5.2, A5.3, A5.4 |
| POST | `/api/reservations/{id}/reschedule` (迭代 2) | 改签 `{start_at, hours}`，内部事务：cancel + create | A5.6, A5.7 |

取消流程：
```
SELECT ... WHERE id=? AND user_id=? FOR UPDATE
若 status != PENDING -> 400
若 start_at <= now   -> 400
UPDATE status=CANCELLED, cancelled_at=now
COMMIT  -- 座位时段自动可被其他人预约（查询时过滤 status IN (PENDING, CHECKED_IN)）
```

## 5. 前端交互

- `/my` 页三个 Tab：`进行中 / 历史 / 违约`
- 每条记录展示状态徽标：
  - PENDING `待签到`（蓝）
  - CHECKED_IN `已签到`（绿）
  - CANCELLED `已取消`（灰）
  - VIOLATED `已违约`（红）
  - FINISHED `已完成`（灰绿）
- PENDING 且未开始才显示【取消】按钮
- 取消成功弹 toast `已取消，座位已释放`

## 6. 验收标准

- [x] GET `/api/reservations/me` 只返回当前用户的记录
- [x] 已开始的预约点取消返回 400
- [x] 取消后该座位同时段在 `/api/rooms/.../seats` 中恢复 AVAILABLE
- [x] 非本人的预约 id 取消返回 404

## 7. 非目标

- 不支持对 CHECKED_IN 状态的预约执行"提前结束"（迭代 2+）
- 不做批量取消

## 8. 依赖与风险

- 依赖：RFC-004
- 风险：若迭代 2 上改签，需考虑改签失败后回滚到原预约的策略（事务内先 create 再 cancel）
