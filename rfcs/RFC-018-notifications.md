# RFC-018：通知体系（C2）

- **对应章节**：story.md 十八、消息通知
- **负责人**：学生C
- **迭代**：2
- **状态**：Draft

## 1. 背景与目标

所有面向用户的异步通知统一经通知中心出口，支持站内、邮件、微信服务号（预留）；失败可重试并可视化监控。

## 2. 用户故事（story.md C2.1–C2.7）

| ID | 故事 |
|---|---|
| C2.1 | 预约成功通知 |
| C2.2 | 预约取消通知 |
| C2.3 | 签到成功通知/反馈 |
| C2.4 | 自动取消与违约通知 |
| C2.5 | 关键规则变更后触达相关用户 |
| C2.6 | 查看消息发送结果（管理端） |
| C2.7 | 失败重试或错误记录 |

## 3. 数据模型

```python
class Notification:           # 参见 RFC-007
    id, user_id, type, title, body, link, read, created_at

class NotificationDispatch:   # 每次投递一次
    id: int
    notification_id: FK
    channel: str              # inbox / email / wechat
    status: str               # PENDING / SENT / FAILED
    retry_count: int
    last_error: str
    sent_at: datetime | None
```

## 4. 架构

```
业务层  ──► NotificationService.send(user, type, ctx)
                 │
                 ├─► 渲染模板（title/body/link）
                 ├─► 写 Notification 行
                 └─► 为每个启用渠道写 NotificationDispatch
                         │
                         └─► 渠道 Worker（APScheduler interval 30s）轮询 PENDING/FAILED
```

**渠道 Channel 接口**：
```python
class Channel(Protocol):
    code: str
    def send(self, user, notification) -> None: ...
```

- `InboxChannel`：只写 inbox 记录（站内）
- `EmailChannel`：SMTP（迭代 2 选做，配置在 settings）
- `WechatChannel`：预留接口，不实现

## 5. 业务事件映射

| 事件 | Type | 触发点 |
|---|---|---|
| 预约创建 | `RESV_CREATED` | RFC-004 创建后 |
| 预约取消（自己） | `RESV_CANCELLED` | RFC-005 |
| 签到成功 | `CHECKIN_OK` | RFC-006 |
| 自动违约 | `VIOLATED` | RFC-017 C1.3 |
| 预约前 15min | `REMIND_BEFORE` | RFC-017 C1.1 |
| 签到催促 | `REMIND_LATE` | RFC-017 C1.2 |
| 关键规则变更 | `CONFIG_CHANGED` | RFC-015 （仅影响未来预约的用户） |

## 6. API 设计

| 方法 | 路径 | 权限 |
|---|---|---|
| GET | `/api/notifications/me?unread=1` | 登录 |
| POST | `/api/notifications/{id}/read` | 登录 |
| GET | `/api/admin/notifications?status=` | audit.view |
| POST | `/api/admin/notifications/{dispatch_id}/retry` | audit.view |

## 7. 前端交互

- 学生端顶栏🔔下拉最近 10 条
- 管理端 `/admin/notifications` 监控面板：按状态过滤 + 手动重试

## 8. 验收标准

- [ ] 预约创建后 1 秒内 inbox 有一条 RESV_CREATED
- [ ] 邮件渠道失败时 retry_count 递增，<=3 次后置 FAILED
- [ ] 管理员可在监控页看到成功率
- [ ] 规则变更只通知未来预约涉及的用户，不全量广播

## 9. 非目标

- 不做模板编辑器（硬编码在代码里）
- 不做营销推送

## 10. 依赖与风险

- 依赖：RFC-017（由调度器驱动重试）、RFC-015（渠道开关）
- 风险：邮件服务器未配置时不能阻塞业务事务 → 渠道分发走异步，业务事务只写 inbox
