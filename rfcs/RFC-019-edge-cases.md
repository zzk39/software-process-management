# RFC-019：复杂业务场景（C3）

- **对应章节**：story.md 十九、异常与边界场景
- **负责人**：管理员F
- **迭代**：2
- **状态**：Draft

## 1. 背景与目标

把"正常流程外"的 8 类场景显式设计，避免藏在各 RFC 的暗角落。

## 2. 用户故事

| ID | 故事 | 处理 |
|---|---|---|
| C3.1 | 自习室临时关闭，自动取消受影响预约并通知 | 事件 ROOM_DEACTIVATED |
| C3.2 | 座位停用时通知受影响预约人 | 事件 SEAT_DEACTIVATED |
| C3.3 | 停用前看到受影响预约列表 | 预览 API |
| C3.4 | 跨天开放自习室预约时段正确处理 | 开放时间解析 |
| C3.5 | 拒绝非法时段预约 | RFC-004 校验 |
| C3.6 | 高并发抢座不重复 | DB 唯一约束 + 事务 |
| C3.7 | 座位被抢走时给替代建议 | 409 响应携带 alternatives |
| C3.8 | 识别重复操作和异常请求 | 限流中间件 |

## 3. 详细设计

### C3.1 / C3.2 停用级联

接口：
- `GET /api/admin/rooms/{id}/impact` → 返回受影响未来 PENDING 预约列表
- `POST /api/admin/rooms/{id}/deactivate?force=true` → 真正执行

执行流程（事务内）：
```
rows = SELECT * FROM reservations
       WHERE room_id=? AND status='PENDING' AND start_at > now
FOR each r: r.status='CANCELLED'; r.cancelled_at=now
           enqueue_notification(r.user_id, 'ROOM_DEACTIVATED')
UPDATE rooms SET is_active=false
```

座位停用类似，影响范围 `seat_id=?`。

### C3.3 影响预览

前端管理员点"停用"时先 `GET /impact`，展示列表，二次确认后 `POST /deactivate?force=true`。

### C3.4 跨天自习室

`Room.is_overnight=true` 时：
- 开放时间校验跳过"同日 open-close 范围"约束（RFC-004 步骤 6）
- 允许 start_at < close_next_day_time

### C3.5 非法时段

已覆盖于 RFC-004 校验步骤 1/2/6。

### C3.6 高并发抢座

SQLite 单文件串行化写入本身避免重复。保险做法：在 `reservations` 上加 **唯一排除索引**（SQLAlchemy 2 层面）：

```sql
-- 不建 UNIQUE（时段交叉无法直接 UNIQUE），改为：
CREATE INDEX ix_resv_seat_time ON reservations(seat_id, status, start_at, end_at);
-- 业务代码在 FOR UPDATE 锁后再 INSERT
```

### C3.7 替代建议

当 RFC-004 返回 409 `SEAT_CONFLICT` 时，响应 body 扩展：
```json
{ "code":409, "message":"该座位此时段已被预约", "data":{
  "alternatives": [ {"seat_id":5, "code":"01-005"}, ... ]
}}
```

同教室同时段可用的前 5 个座位。

### C3.8 重复操作和限流

- FastAPI 中间件：同 IP + 同 user 同 path 10s 内 >5 次 → 429
- 预约创建接口追加 `Idempotency-Key` header 支持，10 分钟内重复 key 直接返回上次结果

## 4. 验收标准

- [ ] 停用一个有 3 条 PENDING 预约的自习室 → 3 个用户均收到 inbox 通知
- [ ] 影响预览能正确列出所有 PENDING 且 start_at > now 的预约
- [ ] 两用户同时 POST 抢同一座位 → 一个成功一个 409 且带 alternatives
- [ ] 限流触发后 429 返回 `{code:429, message:'请求过于频繁'}`

## 5. 非目标

- 不做完整的分布式锁
- 不做验证码/风控

## 6. 依赖与风险

- 依赖：RFC-004, RFC-011, RFC-012, RFC-017, RFC-018, RFC-020
- 风险：限流规则太严会误伤快速点击用户，需给合理阈值与豁免
