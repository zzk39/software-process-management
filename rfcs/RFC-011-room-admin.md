# RFC-011：自习室生命周期（B2）

- **对应章节**：story.md 十一、管理端：自习室管理
- **负责人**：管理员D
- **迭代**：1（基础 CRUD + 停用）；2（签到码管理、通宵、影响预约告警）
- **状态**：Draft

## 1. 背景与目标

自习室是所有资源的根对象，需要完整的登记/注销/停用生命周期，并支持院系专属与通宵两种策略。

## 2. 用户故事

| ID | 故事 | 迭代 |
|---|---|---|
| B2.1 | 登记新的自习室 | 1 |
| B2.2 | 维护基本信息（名称/地点/院系/类型） | 1 |
| B2.3 | 设置开放时间 | 1 |
| B2.4 | 配置是否通宵开放 | 1 |
| B2.5 | 设置全校开放或院系专属 | 1 |
| B2.6 | 设置院系专属对应的开放院系 | 1 |
| B2.7 | 临时停用（维修、考试） | 1 |
| B2.8 | 注销不再使用的自习室 | 2 |
| B2.9 | 查看当前开放状态 | 1 |
| B2.10 | 查看当前空座数和预约数 | 2 |
| B2.11 | 生成/维护每日动态签到码 | 1（C1.7 调度） |

## 3. 数据模型

参见 RFC-001/RFC-006 定义的 `Room` 表。迭代 2 新增：

```python
class Room:
    type: str = "classroom"   # classroom / library / other
    deactivated_at: datetime | None = None   # 注销（B2.8）
```

"注销" = 硬标记 `is_active=false` + 写 `deactivated_at`；不做物理删除。

## 4. API 设计

| 方法 | 路径 | 权限 | Story |
|---|---|---|---|
| GET | `/api/admin/rooms` | room.write / stat.view | B2.9 |
| POST | `/api/admin/rooms` | room.write | B2.1-B2.6 |
| PUT | `/api/admin/rooms/{id}` | room.write | B2.2-B2.6 |
| POST | `/api/admin/rooms/{id}/deactivate` | room.write | B2.7 |
| POST | `/api/admin/rooms/{id}/reactivate` | room.write | — |
| DELETE | `/api/admin/rooms/{id}` | room.write | B2.8（软删） |
| GET | `/api/admin/rooms/{id}/stats` | stat.view | B2.10 |
| POST | `/api/admin/rooms/{id}/rotate-code` | room.write | B2.11（手动刷新） |

停用时**必须**触发 RFC-019：查受影响预约 → 通知 → 自动取消。

## 5. 前端交互

- `/admin/rooms`：表格 + 新增/编辑弹窗 + 行内停用/启用按钮 + 查看签到码（今日）
- 停用弹窗展示"将影响 X 条预约，是否继续？"
- 管理员可手动刷新今日签到码（用于当天换码补救）

## 6. 验收标准

- [x] POST 新增后学生端 `/api/rooms` 立即可见
- [x] 设置 `department=计算机学院` 后，物理学院学生 `/api/rooms` 不可见
- [x] 停用后学生端不可见，已有 PENDING 预约根据 RFC-019 策略处理
- [ ] `rotate-code` 会更新 `daily_checkin_code` 且 `checkin_code_date=today`
- [ ] `/stats` 返回 `{total_seats, active_reservations, available_now}`

## 7. 非目标

- 不做座位批量导入（属 RFC-012）
- 不做跨校区合并展示

## 8. 依赖与风险

- 依赖：RFC-012（依赖 room_id）、RFC-017（每日签到码）、RFC-019（停用联动取消）
- 风险：停用时受影响预约可能跨多天，确认"仅影响未来预约"而非已签到的
