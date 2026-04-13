# RFC-012：座位建档与维护（B3）

- **对应章节**：story.md 十二、管理端：座位管理
- **负责人**：管理员D
- **迭代**：1（单条 CRUD）；2（批量导入 + 平面图）
- **状态**：Draft

## 1. 背景与目标

座位是预约最小单元，建档准确性直接决定学生能否找到/筛选合适资源。

## 2. 用户故事

| ID | 故事 | 迭代 |
|---|---|---|
| B3.1 | 为自习室登记座位 | 1 |
| B3.2 | 配置唯一编号 | 1 |
| B3.3 | 设置空间属性（靠窗、普通） | 1 |
| B3.4 | 标记固定插座或导轨插座 | 1 |
| B3.5 | 临时停用座位 | 1 |
| B3.6 | 注销不再可用的座位 | 1（软删） |
| B3.7 | 批量导入座位 | 2 |
| B3.8 | 批量修改属性 | 2 |
| B3.9 | 平面图查看座位分布 | 2 |

## 3. 数据模型

沿用 `Seat`；迭代 2 新增可视化：

```python
class Seat:
    pos_x: int | None        # 平面图坐标（迭代 2）
    pos_y: int | None
```

"编号唯一" 在 `(room_id, code)` 上建 UNIQUE。

## 4. API 设计

| 方法 | 路径 | 权限 | Story |
|---|---|---|---|
| GET | `/api/admin/seats?room_id=&is_active=` | seat.write / stat.view | — |
| POST | `/api/admin/seats` | seat.write | B3.1-B3.4 |
| PUT | `/api/admin/seats/{id}` | seat.write | B3.3-B3.4 |
| POST | `/api/admin/seats/{id}/deactivate` | seat.write | B3.5 |
| POST | `/api/admin/seats/{id}/reactivate` | seat.write | B3.5（反向，Bug-2026-04-13-02） |
| DELETE | `/api/admin/seats/{id}` | seat.write | B3.6 |
| POST | `/api/admin/seats/bulk` | seat.write | B3.7（CSV / JSON 数组） |
| PATCH | `/api/admin/seats/bulk` | seat.write | B3.8（批量改属性） |
| PUT | `/api/admin/seats/{id}/position` | seat.write | B3.9 |

CSV 批量导入格式：

```csv
room_id,code,has_power,near_window
1,01-101,true,false
1,01-102,true,true
```

## 5. 前端交互

- `/admin/seats`：页面分三块——顶部"筛选自习室"下拉（仅控制表格过滤）、独立的"新增座位"区块（带自己的"目标自习室"下拉，与筛选解耦）、以及座位表格（按行增删改）
- 【批量导入】按钮：拖拽 CSV → 预览冲突行 → 确认导入（迭代 2）
- `/admin/rooms/:id/layout`：画布 + 座位拖拽定位（迭代 2）

## 6. 验收标准

- [x] `(room_id, code)` 重复提交返回 409
- [x] 停用座位后，该座位不再出现在学生端 `/api/rooms/:id/seats`
- [x] 停用的座位可通过 `POST /api/admin/seats/{id}/reactivate` 恢复可用，且管理端在 `is_active=false` 时展示"启用"按钮（Bug-2026-04-13-02）
- [x] "为当前教室新增"按钮在未选择具体自习室或未填写座位编号时禁用，并在旁边给出明确提示，避免用户以为按钮失效（Bug-2026-04-13-03）
- [x] "新增座位"区块拥有独立的"目标自习室"下拉，不复用列表过滤器；即使筛选选"全部"，仍可直接选一个目标自习室完成新增（Bug-2026-04-13-04）
- [ ] CSV 导入 100 条约 < 1s（SQLite，整批事务）
- [ ] 已有 PENDING 预约的座位被停用时，RFC-019 自动触发通知+释放

## 7. 非目标

- 不做座位图片管理
- 不做分时收费

## 8. 依赖与风险

- 依赖：RFC-011、RFC-019
- 风险：`pos_x/pos_y` 平面图需要约定自习室画布尺寸，迭代 2 设计时再定
