# RFC-020：审计、安全与合规（C4）

- **对应章节**：story.md 二十、审计、安全与合规
- **负责人**：管理员F
- **迭代**：2
- **状态**：Draft

## 1. 背景与目标

满足课程要求的"留痕、鉴权、隐私"，为 RBAC 提供底层审计支持。

## 2. 用户故事

| ID | 故事 |
|---|---|
| C4.1 | 关键操作审计日志 |
| C4.2 | 记录谁在何时修改了自习室/座位/参数/角色权限 |
| C4.3 | 学生仅能访问自己的预约/历史/违约 |
| C4.4 | 管理员按权限范围看数据（最小权限） |
| C4.5 | 签到码/二维码有效期与防伪校验 |
| C4.6 | 接口身份鉴权和权限校验 |

## 3. 数据模型

```python
class AuditLog:
    id: int
    actor_id: FK(User) | None
    action: str           # ROOM_CREATE / ROOM_DEACTIVATE / RESV_MANUAL_CANCEL / CONFIG_UPDATE ...
    target_type: str
    target_id: str
    payload_json: str     # 变更前后快照
    ip: str
    user_agent: str
    at: datetime
```

## 4. 实施策略

### 审计切面

FastAPI 依赖 + 装饰器：
```python
@audit("ROOM_CREATE")
def create_room(...): ...
```

或统一中间件拦截写操作：对所有 `POST/PUT/DELETE /api/admin/**` 自动记录。

**写操作清单（必须审计）**：
- RFC-011 自习室 CRUD
- RFC-012 座位 CRUD
- RFC-013 代预约/代取消/强制释放
- RFC-014 申诉审核、违约撤销
- RFC-015 参数修改
- RFC-010 角色/权限变更

### 鉴权（C4.6）

- 所有非登录接口走 `get_current_user` 依赖
- 所有 `/api/admin/**` 走 `require_perm(code)` 依赖（RFC-010）
- 学生端接口内置 `user_id=current.id` 过滤（C4.3）

### 签到码安全（C4.5）

- 每日刷新（RFC-017 C1.7）
- 服务端仅存当日 code；历史 code 不留
- 签到接口带时间窗口校验（RFC-006）

### 数据范围（C4.4）

- 学生只能查 `user_id=self` 的 Reservation/Notification/Violation
- AUDITOR 只读所有
- ROOM_ADMIN 看不到 Reservation（除非再加 reservation.view）

## 5. API 设计

| 方法 | 路径 | 权限 |
|---|---|---|
| GET | `/api/admin/audit` | audit.view |
| GET | `/api/admin/audit/export` | audit.view |

筛选：`actor_id / action / target_type / from / to`。

## 6. 前端交互

- `/admin/audit`：表格，按筛选条件查；行展开看 `payload_json`
- 导出 CSV

## 7. 验收标准

- [ ] 管理员创建自习室后，`/api/admin/audit` 有对应记录，含 payload
- [ ] 学生 A 调用 `/api/reservations/me` 看不到学生 B 的数据
- [ ] 未登录调任一保护接口返回 401
- [ ] 无权限管理员调受限接口返回 403 并记一条审计（action=ACCESS_DENIED）
- [ ] 签到码每日 00:05 后旧 code 立即失效

## 8. 非目标

- 不做 SIEM 对接
- 不做国密算法

## 9. 依赖与风险

- 依赖：RFC-001, RFC-010
- 风险：审计日志增长快——每季度归档（迁移到独立表/备份）
