# RFC-003：按条件找座位（A3）

- **对应章节**：story.md 三、学生端：搜索与筛选
- **负责人**：学生A
- **迭代**：2
- **状态**：Draft

## 1. 背景与目标

在资源多的场景下，按时间+属性组合筛选是提高匹配效率的关键能力。

## 2. 用户故事

| ID | 故事 | 迭代 |
|---|---|---|
| A3.1 | 按日期+时间段搜索可用座位 | 2 |
| A3.2 | 按自习室名称搜索 | 2 |
| A3.3 | 按楼栋/区域搜索 | 2 |
| A3.4 | 按院系开放范围筛选 | 2 |
| A3.5 | 按是否靠窗筛选 | 2 |
| A3.6 | 按是否带插座筛选 | 2 |
| A3.7 | 按剩余可预约时长筛选 | 2 |
| A3.8 | 按当前是否立即可用筛选 | 2 |
| A3.9 | 按空座多的自习室排序 | 2 |
| A3.10 | 系统记住常用筛选条件 | 2（localStorage） |
| A3.11 | 搜索结果包含座位号、可用时间、教室、关键标签 | 2 |

## 3. 数据模型

无新增，沿用 Seat / Room / Reservation。

## 4. API 设计

```
GET /api/seats/search
```

查询参数（全部可选）：

| 参数 | 类型 | 含义 | 对应 Story |
|---|---|---|---|
| `date` | YYYY-MM-DD | 查询日期 | A3.1 |
| `start_hour` | int 0-23 | 开始整点 | A3.1 |
| `hours` | int 1-4 | 时长（小时） | A3.1, A3.7 |
| `room_name` | str | 自习室名称模糊匹配 | A3.2 |
| `building` | str | 楼栋 | A3.3 |
| `department_open` | bool | 仅本院系可用 | A3.4 |
| `near_window` | bool | 靠窗 | A3.5 |
| `has_power` | bool | 带插座 | A3.6 |
| `available_now` | bool | 当前立即可用 | A3.8 |
| `sort` | `capacity_desc\|time_asc` | 排序 | A3.9 |

响应：
```json
{ "code":0, "data":[
  {"seat_id":1, "seat_code":"01-003", "room_id":1, "room_name":"光华一楼",
   "has_power":true, "near_window":false,
   "available_window":{"start":"2026-04-12T19:00", "end":"2026-04-12T22:00"}}
]}
```

## 5. 前端交互

- `/search` 页：
  - 顶部筛选条：日期选择器 + 开始时间 + 时长 + 5 个开关标签（靠窗、插座、本院、立即可用、通宵）
  - 搜索按钮右侧"保存为常用"，存入 `localStorage['filter_presets']`
  - 结果列表：卡片式，座位号 + 教室 + 可用时间 + 标签 + 一键预约按钮
- 进入页面时自动带出最近一次的筛选条件

## 6. 验收标准

- [ ] `near_window=true` 返回结果中所有座位 `near_window` 都为 true
- [ ] `date=today, start_hour=19, hours=3` 返回的结果中不含与现有预约冲突的座位
- [ ] 结果为空时显示"未找到匹配座位，建议放宽条件"+ 可点击的建议项
- [ ] 保存过的筛选条件刷新页面后仍可用

## 7. 非目标

- 不做模糊/拼音/同义词搜索（留给 RFC-009 智能助手）
- 不做地图范围搜索

## 8. 依赖与风险

- 依赖：RFC-002 已有 `/slots`
- 风险：筛选组合多时查询慢，需对 `seats(room_id, is_active)` + `reservations(seat_id, start_at)` 建索引
