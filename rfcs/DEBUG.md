# 缺陷登记（DEBUG）

本文件追踪项目中发现并修复的所有 bug。规则见 [CLAUDE.md](../CLAUDE.md) §4。

**编号规则**：`Bug-YYYY-MM-DD-NN`（按日期顺序，同日多个递增）

**每条必须包含**：RFC 关联、表现、原因、修复、预防。

---

## Bug-2026-04-12-01: 管理端自习室停用后无法重新启用

- **RFC**: RFC-011（Story B2.7 临时停用、B2.9 查看状态）
- **表现**: 管理端点击"停用"后，该自习室在列表中状态变为"停用"，但没有"启用"按钮，无法恢复为开放状态。学生端自然也看不到它。
- **原因**:
  1. 后端仅实现 `DELETE /api/admin/rooms/{id}`（软删→ `is_active=false`），未提供反向操作的 endpoint
  2. 前端 `admin-web/src/views/Rooms.vue` 操作列只在 `is_active=true` 时显示"停用"按钮，没有"启用"按钮
  3. RFC-011 虽在 API 表格里列了 `POST /rooms/{id}/reactivate`，但这条一直是计划没落地；当时没加 AC 保护"启用能力存在"
- **修复**: 
  - 后端新增 `POST /api/admin/rooms/{id}/reactivate`（文件 `backend/app/api/admin/rooms.py`）
  - 前端在操作列按 `is_active` 分支显示"停用 / 启用"两种按钮
  - commit: `3f418a4`
- **预防**:
  - 在 RFC-011 验收标准中新增 AC："停用的自习室可通过 reactivate 接口恢复为开放，且对应学生端立即可见"
  - 在 `backend/tests/test_admin.py::test_admin_room_crud` 中追加 reactivate 步骤，保证下次测试能覆盖

---

## Bug-2026-04-12-02: 启动后端后 VSCode 内存爆炸（uvicorn --reload 死循环）

- **RFC**: RFC-017（C1.3 每分钟 `auto_cancel_no_show`）、RFC-021（本地开发性能约束）
- **表现**: 起 `make run-backend` + 两个前端后，VSCode 内存持续飙升直至卡死；后端日志不断刷 `WatchFiles detected changes` 并整体重启。
- **原因**:
  1. `Makefile:31` 使用 `uvicorn --reload` 但未指定 `--reload-dir`，watchfiles 默认监听整个 `backend/` 目录
  2. `backend/` 下包含两类会被频繁写/包含海量文件的路径：
     - `backend/study_seat.db`（SQLite，scheduler 每分钟 `commit` 写入）
     - `backend/.venv/`（虚拟环境，数万 `.py` 文件）
  3. RFC-017 C1.3 在 `app/tasks/scheduler.py:60` 注册 `interval minutes=1` 的 `auto_cancel_no_show`，每次执行若有 `PENDING` 行就 `db.commit()` → `study_seat.db` 文件变更 → uvicorn 触发重启 → `lifespan` 再起一个 scheduler → 循环
  4. VSCode 自身的 file watcher 与 uvicorn 的 watchfiles 同步扫描 `.venv/`，inode/句柄堆积推高宿主内存
- **修复**:
  - `software/Makefile:31` 将 `uvicorn app.main:app --reload --port 8000` 改为 `uvicorn app.main:app --reload --reload-dir app --port 8000`，只监听源码目录
  - commit: （见本次提交）
- **预防**:
  - 已在 RFC-017 验收标准中新增 AC："本地 `make run-backend` 启动后，uvicorn 不得因 `study_seat.db` 或 `.venv/` 变更而自动重启（即 `--reload-dir` 必须限定为 `app`）"
  - 后续若在 `backend/` 根目录新增会被任务写入的文件（日志、sqlite、缓存），必须放到 `app/` 之外的专属目录，避免再次触发重载

---

## Bug-2026-04-13-01: 学生端提交预约 500（tz-aware vs naive datetime）

- **RFC**: RFC-004（Story A4.1 / A4.6）
- **表现**: 学生端 `/rooms/:id` 选座后点击"提交预约"，接口 `POST /api/reservations` 返回 500，前端显示 `Request failed with status code 500`。
- **原因**:
  1. 后端 `app/api/reservations.py:62` 的 `_within_room_hours` 用 `datetime.combine(day, datetime.min.time()).replace(...)` 构造 `open_dt / close_dt`，是 **naive** datetime
  2. 前端 `student-web/src/views/RoomDetail.vue:75` 提交时调用 `new Date(startAt.value).toISOString()`，结果形如 `"2026-04-14T10:00:00Z"`，pydantic 解析为 **aware** datetime
  3. Python 对 aware 与 naive datetime 做 `<` 比较直接抛 `TypeError: can't compare offset-naive and offset-aware datetimes`，FastAPI 未捕获 → 500
  4. RFC-004 §4 的入参示例是 `"2026-04-12T19:00:00"`（naive），但 §5 没有明确禁止前端把本地时间转成 ISO UTC，AC 也未覆盖"前端入参时区约定"，所以此前没被测到
- **修复**:
  - `student-web/src/views/RoomDetail.vue:75` 将 `new Date(startAt.value).toISOString()` 改为 `` `${startAt.value}:00` ``，直接上送 `datetime-local` 的原始 naive 本地时间
  - commit: `9a8b353`
- **预防**:
  - 在 RFC-004 §5 前端交互小节明确禁止 `.toISOString()`，并说明原因
  - 在 RFC-004 §6 验收标准新增 AC："前端提交的 `start_at` 为 naive 本地时间（不含 `Z`/时区偏移）"
  - 现有 `backend/tests/test_reservations.py` 已全部使用 naive ISO 格式，保证后端契约被覆盖；前端后续若新增预约入口需遵循同一约定

