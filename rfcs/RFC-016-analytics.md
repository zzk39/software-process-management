# RFC-016：利用率分析（B7）

- **对应章节**：story.md 十六、管理端：统计分析与决策支持
- **负责人**：zzk（管理员F 协作维度数据采集）
- **迭代**：2
- **状态**：Draft

## 1. 背景与目标

为管理员提供多维度数据看板，支持资源调整、容量规划、考核评估。

## 2. 用户故事

| ID | 故事 |
|---|---|
| B7.1 | 各自习室座位利用率 |
| B7.2 | 时段预约热度分布 |
| B7.3 | 自习室/区域空置率 |
| B7.4 | 预约成功率变化趋势 |
| B7.5 | 未签到率 / 违约率 |
| B7.6 | 带插座座位使用率 |
| B7.7 | 院系专属自习室利用率 |
| B7.8 | 热门座位 / 热门自习室排行 |
| B7.9 | 按日/周/月统计趋势 |
| B7.10 | 导出报表 |

## 3. 数据模型

**不新增表**，由 `Reservation + Room + Seat` 聚合 SQL 完成。若查询性能差，迭代后期加物化汇总：

```python
class DailyStat:
    date: str (YYYY-MM-DD)
    room_id: int
    total_seat_hours: int         # 开放座位时数
    booked_seat_hours: int
    checked_in_seat_hours: int
    violated_count: int
    # PK (date, room_id)
```

由调度任务每日 00:30 聚合前一天。

## 4. API 设计

| 方法 | 路径 | 出参 | Story |
|---|---|---|---|
| GET | `/api/admin/stats/overview?from=&to=` | 全局汇总 | — |
| GET | `/api/admin/stats/rooms?from=&to=` | 每个自习室 `{utilization, empty_rate, violations}` | B7.1, B7.3 |
| GET | `/api/admin/stats/hourly?date=` | 24 点位预约数 | B7.2 |
| GET | `/api/admin/stats/success-rate?bucket=day\|week\|month` | 成功率趋势 | B7.4 |
| GET | `/api/admin/stats/violation-rate?bucket=...` | 违约率趋势 | B7.5 |
| GET | `/api/admin/stats/power?...` | 带插座座位利用率 | B7.6 |
| GET | `/api/admin/stats/department?...` | 各院系专属教室利用率 | B7.7 |
| GET | `/api/admin/stats/top?dim=seat\|room&limit=10` | 热门榜 | B7.8 |
| GET | `/api/admin/stats/trend?metric=&bucket=&from=&to=` | 通用趋势 | B7.9 |
| GET | `/api/admin/stats/export?type=&from=&to=&format=csv` | 导出 | B7.10 |

**利用率计算**：
```
utilization = Σ(实际签到时长) / Σ(开放时段 × 座位数)
```

## 5. 前端交互

- `/admin/stats` 首页卡片：总预约 / 成功率 / 违约率 / TOP 自习室
- 切换：`今日 / 本周 / 本月 / 自定义区间`
- 图表：
  - 自习室利用率柱图（B7.1）
  - 小时热度折线（B7.2）
  - 成功/违约率趋势（B7.4, B7.5）
- 【导出 CSV】【导出 PDF（截图式）】

推荐前端图表库：`ECharts` 或 `@antv/g2`。

## 6. 验收标准

严格对齐 story.md B7.1–B7.10 每条 AC。

- [ ] 利用率计算与手算验证一致（至少 1 个 room 小数据集核对）
- [ ] `from=2026-04-01&to=2026-04-07` 结果等价于 7 天每日汇总求和
- [ ] 导出 CSV 能 UTF-8 正确显示中文
- [ ] 非 `stat.view` 角色返回 403

## 7. 非目标

- 不做预测类分析（时间序列预测留给未来）
- 不做实时大屏

## 8. 依赖与风险

- 依赖：RFC-004/005/006/007（所有业务数据源）、RFC-015（参数）
- 风险：SQLite 聚合性能——每日物化到 DailyStat 解决；大区间直接走原表扫描
