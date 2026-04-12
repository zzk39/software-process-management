# RFC-010：角色与权限管理（B1）

- **对应章节**：story.md 十、管理端：RBAC 与账号权限
- **负责人**：管理员D
- **迭代**：2（迭代 1 仅 `is_admin` 单标志）
- **状态**：Draft

## 1. 背景与目标

课程要求管理端"必须支持 RBAC"。按用户 → 角色 → 权限三级模型实现，前端依授权动态裁剪菜单。

## 2. 用户故事（story.md B1.1–B1.12）

| ID | 故事 |
|---|---|
| B1.1 | 创建角色 |
| B1.2 | 编辑角色名称和描述 |
| B1.3 | 删除不再使用的角色 |
| B1.4 | 为角色分配权限项 |
| B1.5 | 给用户分配一个或多个角色 |
| B1.6 | 撤销用户角色 |
| B1.7 | 查看用户全部角色 |
| B1.8 | 查看角色全部权限 |
| B1.9 | 管理界面仅展示已授权菜单 |
| B1.10 | 无权限时禁止访问对应接口和页面 |
| B1.11 | 粒度覆盖：查看预约/违约、代预约/代取消、座位登记注销、自习室登记注销、系统参数调整 |
| B1.12 | 角色权限变更日志 |

## 3. 数据模型

```python
class Role:
    id: int
    code: str        # 唯一 "ROOM_ADMIN" / "AUDITOR" / ...
    name: str        # 中文名
    description: str

class Permission:
    code: str        # PK, 如 "reservation.view"
    description: str

class RolePermission:
    role_id: FK
    perm_code: FK
    # PK (role_id, perm_code)

class UserRole:
    user_id: FK
    role_id: FK
    granted_by: FK(User)
    granted_at: datetime
    # PK (user_id, role_id)

class RbacChangeLog:
    id: int
    actor_id: FK(User)
    action: str       # GRANT_ROLE / REVOKE_ROLE / EDIT_ROLE / EDIT_PERM
    target: str       # JSON
    at: datetime
```

**权限词表（覆盖 B1.11）**：

| code | 含义 |
|---|---|
| `reservation.view` | 查看预约记录（B4） |
| `reservation.manage` | 代预约/代取消（B4） |
| `violation.view` | 查看违约（B5） |
| `violation.handle` | 处理申诉/修正（B5） |
| `seat.write` | 座位登记/注销（B3） |
| `room.write` | 自习室登记/注销（B2） |
| `config.write` | 系统参数调整（B6） |
| `rbac.manage` | RBAC 管理（B1） |
| `audit.view` | 审计日志（C4） |
| `stat.view` | 统计分析（B7） |

**内置角色**：
- `SUPER_ADMIN`：所有权限
- `ROOM_ADMIN`：room.write + seat.write
- `RESV_ADMIN`：reservation.view + reservation.manage + violation.view
- `AUDITOR`：*.view 只读
- `CONFIG_ADMIN`：config.write + rbac.manage

## 4. API 设计

| 方法 | 路径 | 权限 |
|---|---|---|
| GET | `/api/admin/rbac/roles` | rbac.manage |
| POST/PUT/DELETE | `/api/admin/rbac/roles[/{id}]` | rbac.manage |
| GET | `/api/admin/rbac/permissions` | rbac.manage |
| POST | `/api/admin/rbac/roles/{id}/perms` `{codes:[...]}` | rbac.manage |
| GET | `/api/admin/rbac/users/{id}/roles` | rbac.manage |
| POST | `/api/admin/rbac/users/{id}/roles` `{role_ids:[...]}` | rbac.manage |
| DELETE | `/api/admin/rbac/users/{id}/roles/{role_id}` | rbac.manage |
| GET | `/api/admin/rbac/logs` | audit.view |

**鉴权依赖**：
```python
def require_perm(code: str):
    def dep(user = Depends(get_current_user)):
        if code not in user_perms(user):
            raise HTTPException(403, "权限不足")
        return user
    return dep
```

JWT payload 中额外携带 `perms: List[str]`；每次 login 时根据 UserRole 展开缓存。

## 5. 前端交互

- `/admin/rbac/roles`：角色表格 + 权限勾选矩阵
- `/admin/rbac/users`：用户列表 + 编辑角色
- 顶部菜单按 `perms` 过滤展示
- 无权限页面显示 403 占位

## 6. 验收标准

- [ ] 分配 `AUDITOR` 的用户调 POST `/api/admin/rooms` 返回 403
- [ ] 删除 `ROOM_ADMIN` 角色后，被关联用户的菜单不再出现"自习室管理"
- [ ] 所有 GRANT/REVOKE 操作写入 `RbacChangeLog`
- [ ] JWT 过期后拉取新 token 权限能即时同步

## 7. 非目标

- 不做资源级 ACL（如"只能管理某个教室"），仅功能级
- 不做多租户

## 8. 依赖与风险

- 依赖：RFC-001（用户模型）、RFC-020（审计日志复用）
- 风险：迁移期需保留 `is_admin` 兼容 → 升级脚本为 `is_admin=true` 的用户分配 `SUPER_ADMIN` 角色
