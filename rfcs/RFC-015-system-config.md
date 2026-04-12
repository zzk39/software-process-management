# RFC-015：规则配置（B6）

- **对应章节**：story.md 十五、管理端：系统参数管理
- **负责人**：zzk
- **迭代**：2（迭代 1 参数写死在 `settings`，迭代 2 入库）
- **状态**：Draft

## 1. 背景与目标

将所有硬编码的业务参数抽出到数据库，支持即时生效 + 审计留痕。

## 2. 用户故事

| ID | 故事 |
|---|---|
| B6.1 | 调整最大单次预约时长 |
| B6.2 | 调整预约开始前提醒时间 |
| B6.3 | 调整未签到再次提醒时间 |
| B6.4 | 调整未签到自动取消宽限期 |
| B6.5 | 配置签到允许时间窗口 |
| B6.6 | 配置是否允许多个并存预约 |
| B6.7 | 配置通知渠道启用状态 |
| B6.8 | 参数修改即时生效或明确生效时间 |
| B6.9 | 所有参数变更有完整日志 |

## 3. 数据模型

```python
class SystemConfig:
    key: str          # PK, 如 "max_reservation_hours"
    value: str        # 统一字符串存储，读取时按 schema 解析
    value_type: str   # int / bool / json / str
    description: str
    updated_by: FK(User) | None
    updated_at: datetime

class SystemConfigLog:
    id: int
    key: str
    old_value: str
    new_value: str
    actor_id: FK(User)
    at: datetime
```

**参数清单（初始）**：

| key | type | 默认 | 对应 Story |
|---|---|---|---|
| `max_reservation_hours` | int | 4 | B6.1 |
| `remind_before_minutes` | int | 15 | B6.2 |
| `late_remind_minutes` | int | 10 | B6.3 |
| `checkin_grace_minutes` | int | 15 | B6.4, B6.5 |
| `allow_multi_active_reservations` | bool | false | B6.6 |
| `notify_channels_enabled` | json | `["inbox"]` | B6.7 |

## 4. API 设计

| 方法 | 路径 | 权限 |
|---|---|---|
| GET | `/api/admin/configs` | config.write / stat.view |
| PUT | `/api/admin/configs/{key}` `{value}` | config.write |
| GET | `/api/admin/configs/logs` | audit.view |
| GET | `/api/rules`（公开给学生） | — |

**即时生效实现**：
- 后端提供 `config_service.get(key)`，带 30s 本地 TTL 缓存；PUT 时广播失效（单实例直接清缓存即可）
- 调度器 / 业务逻辑每次使用都通过 `config_service.get` 获取

## 5. 前端交互

- `/admin/configs`：表格，行内编辑 + 保存
- 每个参数显示：当前值、默认值、描述、最后修改人/时间
- 修改后 toast `已生效`
- 旁边【变更历史】抽屉

## 6. 验收标准

- [ ] 将 `max_reservation_hours` 从 4 改为 6 后，学生立即能预约 5 小时
- [ ] 将 `checkin_grace_minutes` 从 15 改为 30 后，RFC-017 调度在下个周期使用新值
- [ ] 所有变更记录可查，含 actor_id 和时间戳
- [ ] 非 `config.write` 角色 PUT 返回 403

## 7. 非目标

- 不做参数生效的"未来时间点"延迟（所有参数即时）
- 不做参数模板导入/导出

## 8. 依赖与风险

- 依赖：RFC-010（权限）、RFC-020（审计）
- 风险：缓存不一致——多实例部署时需换 Redis pub/sub 或短 TTL 兜底；当前单机部署不成问题
