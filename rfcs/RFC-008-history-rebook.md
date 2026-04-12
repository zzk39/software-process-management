# RFC-008：历史记录与复订（A8）

- **对应章节**：story.md 八、学生端：历史记录与复订
- **负责人**：学生C
- **迭代**：2
- **状态**：Draft

## 1. 背景与目标

通过复订能力降低学生重复操作成本，基于历史行为做偏好预填。

## 2. 用户故事（保留 story.md 原文 AC）

### Story 8.1 历史预约记录查看
- 按时间倒序
- 展示预约时间/教室/座位/状态
- 已完成、已取消、已违约状态清晰区分
- 展示该次**座位属性快照**（靠窗、插座）

### Story 8.2 历史签到与签退记录
- 展示签到时间、签退时间
- 未签到/已签到/已签退区分
- 实际使用时长
- 座位属性快照

### Story 8.3 历史违约记录
- 在历史中筛选仅违约
- 展示时间、教室、座位、判定结果
- 正常取消不算违约
- 可跳到违约详情

### Story 8.4 一键再次预约
- 历史记录行内【再次预约】按钮
- 自动预填原 room/seat
- 提交前校验冲突
- 原座位不可用时推荐同教室其它座位

### Story 8.5 复订时自动带出常用时长与时间偏好
- 记录最近/高频时长
- 记录常用时间段偏好
- 预填后可手动修改

### Story 8.6 常用自习室与座位展示
- 基于历史统计常用 top-N
- 首页卡片展示
- 点击直接进入预约页
- 按"最近"和"高频"分开

### Story 8.7 常用自习室与座位收藏
- 支持收藏 / 取消收藏
- 首页"我的常用"
- 搜索结果中收藏项高亮
- 从收藏入口跳预约页

## 3. 数据模型

```python
class Reservation:
    # 迭代 2 新增——座位属性快照（Story 8.1/8.2）
    seat_code_snapshot: str = ""
    room_name_snapshot: str = ""
    has_power_snapshot: bool = False
    near_window_snapshot: bool = False
    checkout_at: datetime | None = None   # 签退时间（Story 8.2）

class Favorite:
    id: int
    user_id: FK
    target_type: str     # "room" | "seat"
    target_id: int
    created_at: datetime
    # UNIQUE (user_id, target_type, target_id)
```

**常用统计**不落库，按需从 `reservations` 聚合查询。

## 4. API 设计

| 方法 | 路径 | 说明 | Story |
|---|---|---|---|
| GET | `/api/history/me?status=&from=&to=` | 分页历史 | 8.1, 8.3 |
| GET | `/api/history/me/{id}` | 单条详情（含快照、签到/签退） | 8.2 |
| POST | `/api/reservations/{id}/rebook` | 基于历史一键复订 | 8.4 |
| GET | `/api/me/preferences/reservation` | 推算出的常用时长/时段 | 8.5 |
| GET | `/api/me/frequent?type=room\|seat&limit=5` | 常用 top-N | 8.6 |
| GET | `/api/me/favorites` / POST / DELETE | 收藏管理 | 8.7 |

`POST /rebook` 流程：读原预约 → `start_at = 明天同整点` / `hours = 原 hours` → 调用 RFC-004 create 逻辑 → 冲突时响应 `{alternatives: Seat[]}`。

## 5. 前端交互

- `/my` Tab `历史`：列表 + 筛选（按状态、日期范围）
- 每行展开显示签到 / 签退时间 + 属性快照
- 历史行右侧【再次预约】按钮
- 首页上方【我的常用】与【我的收藏】两个 section
- 座位/自习室列表中被收藏的加⭐

## 6. 验收标准

严格对齐 story.md 中每条 Story 下的 AC。

## 7. 非目标

- 不做跨年度归档（数据量大再做）
- 不做"学习时长"等统计（转属 B7）

## 8. 依赖与风险

- 依赖：RFC-004（Reservation）、RFC-005（状态流转）
- 风险：座位属性快照需在创建预约时写入，避免后续管理员修改座位属性污染历史记录
