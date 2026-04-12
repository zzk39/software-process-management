# RFC-007：提醒、违约与信用（A7）

- **对应章节**：story.md 七、学生端：提醒、违约与信用
- **负责人**：学生C
- **迭代**：2（迭代 1 仅交付违约判定已由 RFC-017 覆盖；通知体系推到迭代 2）
- **状态**：Draft

## 1. 背景与目标

确保学生履约：提前提醒 + 开始后催促 + 超时自动违约 + 信用累计 + 申诉救济。

## 2. 用户故事（逐条来自 story.md，保留原始 AC）

### Story 7.1 预约开始前提醒
- 提前 15 分钟推送（可配）
- 同一预约同一节点只推一次（去重日志表）
- 点击提醒跳转预约详情
- 已取消/已签到/已违约不再推送

### Story 7.2 未签到催促提醒
- 开始后 10 分钟仍未签到 → 推"即将违约"
- 提醒内容包含剩余签到时间
- 前端卡片展示"待签到且即将违约"高风险态
- 签到成功后取消后续违约判定（无副作用，因为状态已切换）

### Story 7.3 违约自动取消与座位释放
- 超过宽限期自动改 status=VIOLATED
- 释放座位
- 记录违约日志 + 用户 violation_count +1
- 发送违约结果通知

### Story 7.4 违约结果通知
- 通知含原因、时间、教室名、座位号、累计违约次数
- 支持从通知跳转详情
- 同一违约事件不重复推送

### Story 7.5 违约次数与信用状态查看
- 个人页显示累计违约次数 + 信用等级（规则如下）
- 若受限显示原因
- 信用看板显示最近违约摘要

**信用等级规则（建议）**：
| 累计违约 | 等级 | 效果 |
|---|---|---|
| 0-2 | 良好 | 正常 |
| 3-5 | 警告 | 提示黄色 |
| 6+ | 受限 | 禁止预约 7 天 |

### Story 7.6 违约判定规则说明
- 学生端提供规则说明入口（静态 Markdown 页）
- 与 RFC-015 系统参数同步展示

### Story 7.7 预约状态可视化展示
- 五态颜色区分：PENDING 蓝 / CHECKED_IN 绿 / CANCELLED 灰 / VIOLATED 红 / FINISHED 灰绿
- 高风险态（接近违约）加脉冲边框

### Story 7.8 违约申诉入口
- 违约记录页有【申诉】按钮
- 填写文字说明 + 上传图片（MVP 只存 URL 字符串）
- 状态：SUBMITTED → UNDER_REVIEW → APPROVED/REJECTED
- 审核通过则清除该 Violation 并 `user.violation_count -= 1`

### Story 7.9 提醒方式偏好设置
- 用户可配置渠道：`inbox`（站内，默认） / `email` / `wechat`
- 通知发送按用户偏好调用对应 Channel
- 某渠道失败降级到 `inbox`

## 3. 数据模型

```python
class Notification:
    id: int
    user_id: FK(User)
    type: str          # REMIND_BEFORE / REMIND_LATE / VIOLATED / APPEAL_RESULT
    title: str
    body: str
    link: str          # 前端路由，如 /my?id=10
    reservation_id: FK(Reservation) | None
    read: bool
    created_at: datetime

class NotificationSent:                  # 去重日志
    id: int
    reservation_id: FK
    type: str                            # REMIND_BEFORE / REMIND_LATE
    sent_at: datetime
    # UNIQUE (reservation_id, type)

class Appeal:
    id: int
    user_id: FK(User)
    violation_id: FK(Violation)
    reason: str
    evidence_url: str
    status: str       # SUBMITTED / UNDER_REVIEW / APPROVED / REJECTED
    reviewed_by: FK(User) | None
    reviewed_at: datetime | None
    created_at: datetime

class UserPreference:
    user_id: PK
    notify_channels: str    # JSON: ["inbox","email"]
```

## 4. API 设计

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/notifications/me?unread=1` | 站内消息 |
| POST | `/api/notifications/{id}/read` | 标记已读 |
| GET | `/api/me/credit` | 累计违约 + 等级 + 最近 5 条违约 |
| GET | `/api/me/appeals` | 我的申诉列表 |
| POST | `/api/appeals` | `{violation_id, reason, evidence_url}` |
| GET | `/api/me/preferences` / PUT | 提醒渠道配置 |
| GET | `/api/rules` | 返回 B6 当前参数形成的规则说明 |

## 5. 前端交互

- 顶栏铃铛 🔔 展示未读消息数，下拉查看
- `/me/credit` 信用看板：大数字累计次数 + 等级徽标 + 最近违约时间线
- `/me/appeals` 申诉列表 + 表单弹窗
- 违约记录卡片右下角【申诉】按钮（`status=REJECTED` 时文案变灰，不可再交）

## 6. 验收标准

每条 AC 同 story.md 原文，每个 Story 至少 1 个 pytest 冒烟。

## 7. 非目标

- 迭代 2 仅实现 `inbox` 渠道，`email/wechat` 仅保留接口扩展点
- 不做 A/B 测试框架

## 8. 依赖与风险

- 依赖：RFC-017（调度器触发 T-15、T+10、T+15 三个节点），RFC-018（通知总线），RFC-015（参数）
- 风险：事务一致性——"标违约 + release seat + write violation + write notification" 需在单个事务内完成（见 RFC-017）
