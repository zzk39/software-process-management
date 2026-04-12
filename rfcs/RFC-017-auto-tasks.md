# RFC-017：自动规则执行（C1）

- **对应章节**：story.md 十七、系统自动化任务
- **负责人**：管理员F
- **迭代**：1（C1.3-C1.7）；2（提醒类 C1.1/C1.2 + 事件审计 C1.10）
- **状态**：Draft

## 1. 背景与目标

系统级定时任务与事件副作用的统一出口。保证提醒推送、违约判定、座位释放、审计日志的时序与一致性。

## 2. 用户故事（story.md C1.1–C1.10）

| ID | 故事 | 触发 | 迭代 |
|---|---|---|---|
| C1.1 | 预约开始前 15 分钟自动提醒 | `interval(1min)` 扫描 | 2 |
| C1.2 | 开始后 10 分钟未签到再次提醒 | `interval(1min)` 扫描 | 2 |
| C1.3 | 开始后 15 分钟仍未签到自动取消 | `interval(1min)` 扫描 | 1 |
| C1.4 | 自动取消后立即释放座位 | 上述任务副作用 | 1 |
| C1.5 | 自动取消后记录一次违约 | 同上 | 1 |
| C1.6 | 自动取消、释放、违约事务一致 | DB 事务 | 1 |
| C1.7 | 每天刷新各教室动态签到码 | `cron(0 0 5 * *)` | 1 |
| C1.8 | 自习室停用时自动屏蔽预约 | 事件监听 | 2 |
| C1.9 | 座位停用时自动阻止新预约 | 校验层读 is_active | 1 |
| C1.10 | 关键事件自动记录审计日志 | 事件监听 | 2 |

## 3. 调度实现

使用 `APScheduler`（`BackgroundScheduler`）在 FastAPI `lifespan` 中启动。

```python
sched.add_job(remind_before_start,  'interval', minutes=1, id='c1_1')
sched.add_job(remind_late_no_show,  'interval', minutes=1, id='c1_2')
sched.add_job(auto_cancel_no_show,  'interval', minutes=1, id='c1_3')
sched.add_job(refresh_daily_codes,  'cron', hour=0, minute=5, id='c1_7')
sched.add_job(aggregate_daily_stat, 'cron', hour=0, minute=30, id='b7_daily')
```

## 4. 核心任务

### C1.3 自动违约（已在迭代 1 落地）

伪代码：
```python
cutoff = now() - config.checkin_grace_minutes
with tx:
    rows = SELECT * FROM reservations
           WHERE status='PENDING' AND start_at <= cutoff
           FOR UPDATE
    for r in rows:
        r.status = 'VIOLATED'
        INSERT violation(user_id, reservation_id, reason='NO_CHECKIN')
        UPDATE users SET violation_count += 1 WHERE id = r.user_id
        enqueue_notification(r.user_id, 'VIOLATED')     # 迭代 2 激活
        write_audit('AUTO_CANCEL', r)                   # 迭代 2
```

**一致性保证**：单事务包住 status / violation / counter / notification / audit 五条写；失败整体回滚。

### C1.1 / C1.2 提醒

```python
remind_at_1 = start_at - config.remind_before_minutes
remind_at_2 = start_at + config.late_remind_minutes

去重：NotificationSent UNIQUE (reservation_id, type)
扫描窗口：[now-1min, now]，仅发一次
```

### C1.7 每日动态码刷新

```python
if room.checkin_code_date != today:
    room.daily_checkin_code = hex(random, 3).upper()  # 6 位
    room.checkin_code_date = today
```

### C1.8 自习室/座位停用级联

以事件方式（迭代 2）：监听 `ROOM_DEACTIVATED`/`SEAT_DEACTIVATED` 事件 → 查未来所有 PENDING 预约 → 逐条 `cancel + notify`。

## 5. 可观测性

- 每个任务执行开始/结束写 `JobRun` 表：`{job_id, started_at, ended_at, affected_rows, error}`
- Admin 页 `/admin/jobs` 看最近 100 条执行记录

## 6. 验收标准

- [x] 预约 19:00，在 19:16 时 (cutoff=15min) 自动标 VIOLATED
- [x] 同一预约不会被处理两次（因 status 变更后不再匹配 WHERE）
- [x] 自动违约后 User.violation_count +1（smoke test）
- [ ] `/api/rooms/{id}` 返回 `daily_checkin_code_date == today`
- [ ] 停用 Room 后，受影响 PENDING 预约在 1 分钟内被 notify
- [x] 本地 `make run-backend` 启动后，uvicorn 不得因 `study_seat.db` 或 `.venv/` 变更而自动重启（`--reload-dir app` 限定监听范围，避免 scheduler 每分钟 `commit` 触发重启死循环）

## 7. 非目标

- 不使用分布式调度框架（Celery/Airflow）
- 不做任务失败重试（仅日志；严重问题靠监控报警）

## 8. 依赖与风险

- 依赖：全部业务 RFC
- 风险：
  - 单实例——多实例部署时 APScheduler 需迁移到 `SQLAlchemyJobStore` 加锁
  - 时区——统一 `Asia/Shanghai`（已在 `BackgroundScheduler(timezone=...)` 配置）
