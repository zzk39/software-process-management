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

---

## Bug-2026-04-13-02: 管理端座位停用后无法重新启用

- **RFC**: RFC-012（Story B3.5 临时停用）
- **表现**: 管理端"座位管理"页面点击"停用"后，该行状态变为"停用"，但操作列没有"启用"按钮，管理员无法把座位恢复为可用。与 Bug-2026-04-12-01（自习室）同构。
- **原因**:
  1. 后端 `backend/app/api/admin/seats.py` 仅实现 `DELETE /api/admin/seats/{id}`（软删→ `is_active=false`），未提供反向 reactivate 端点
  2. 前端 `admin-web/src/views/Seats.vue` 操作列只在 `s.is_active=true` 时显示"停用"按钮，没有"启用"按钮
  3. RFC-012 §4 API 表格漏了 reactivate 接口；§6 AC 只覆盖"停用后不可见"，没保护"启用能力存在"——这正是 Bug-2026-04-12-01 的预防条款在 seat 维度的遗漏，说明当时只补了 room 一份
- **修复**:
  - 后端新增 `POST /api/admin/seats/{id}/reactivate`（`backend/app/api/admin/seats.py`）
  - 前端操作列按 `is_active` 分支显示"停用 / 启用"两种按钮
  - commit: `484699c`
- **预防**:
  - RFC-012 §4 补 `POST /api/admin/seats/{id}/reactivate`；§6 新增 AC："停用的座位可通过 reactivate 接口恢复，管理端在 is_active=false 时展示'启用'按钮"
  - `backend/tests/test_admin.py` 新增 `test_admin_seat_deactivate_and_reactivate`，对称覆盖 room 侧的 reactivate 测试
  - 约定：今后任何 `DELETE` 软删端点必须成对引入 `POST /{id}/reactivate`，前端按 `is_active` 双向渲染按钮（已在 room、seat 两处兑现）

---

## Bug-2026-04-13-03: 管理端"为当前教室新增"按钮没有响应

- **RFC**: RFC-012（Story B3.1 为自习室登记座位）
- **表现**: 管理端"座位管理"页面点击"为当前教室新增"按钮没有任何反应，用户以为按钮坏了。
- **原因**:
  1. `admin-web/src/views/Seats.vue` 的新增按钮用 `:disabled="!roomId"` 控制；页面初始加载时筛选下拉框默认为"全部"，`roomId=null`，按钮实际处于 **disabled** 状态
  2. 按钮被禁用时没有任何视觉/文字提示，用户无法意识到"需要先在筛选器里选一个自习室"才能新增——筛选器被一岗两用（既控制列表过滤又决定新增目标教室）
  3. 后端 `POST /api/admin/seats` 实际工作正常（curl 直调返回 200），属于纯前端 UX 缺陷
  4. RFC-012 §5 只写了"筛选自习室 + 单条增删改"，未对"无自习室被选中时新增按钮的禁用态反馈"给出约定
- **修复**:
  - `admin-web/src/views/Seats.vue`：
    - 扩展 disabled 条件到 `!roomId || !form.code`（未填编号时也不允许提交）
    - 加 `title` 按状态给出悬浮提示
    - 在按钮右侧追加红字提示 `← 请先选择一个自习室`，仅在 `!roomId` 时显示
  - commit: `bfd4add`
- **预防**:
  - RFC-012 §6 新增 AC："新增按钮在未选择具体自习室或未填写座位编号时禁用，并在旁边给出明确提示"
  - 约定：今后任何"依赖上游筛选器状态才能启用"的按钮，必须显式把禁用原因写在按钮旁（红字或 title 任一），不能只靠灰化

---

## Bug-2026-04-13-04: 管理端座位新增要选自习室，但入口不明显（-03 的跟进）

- **RFC**: RFC-012（Story B3.1）
- **表现**: 修完 Bug-2026-04-13-03 后用户仍问"自习室咋选择啊？"。原先页面只有一个"筛选自习室"下拉，既要做列表过滤又要决定"新增"的目标教室，语义高度耦合——选"全部"则新增按钮被禁用，用户没意识到必须把筛选器改成某个具体自习室才能触发新增。
- **原因**:
  1. `admin-web/src/views/Seats.vue` 里 `roomId` 同时充当"列表过滤键"和"新增目标 room_id"（`create()` 传 `room_id: roomId.value`）
  2. 顶部文案只有"筛选自习室"，按字面意思这个下拉只管过滤，没人会想到切换它会改变"新增"的目标
  3. -03 只加了禁用提示，没解决"选择入口不明显"的本质耦合
- **修复**:
  - 把"新增座位"拆成独立区块，带自己的"目标自习室"下拉（新 ref `createRoomId`）
  - `create()` 改为使用 `createRoomId.value`，与筛选器 `roomId` 彻底解耦
  - 筛选器下拉保留"全部"，不再影响新增是否可用
  - commit: `ac441f5`
- **预防**:
  - RFC-012 §5 前端交互改写为"三块"结构（筛选 / 新增 / 表格），约束"筛选器不得复用为新增目标"
  - RFC-012 §6 新增 AC："新增座位区块拥有独立的目标自习室下拉，不依赖列表过滤器"
  - 通用约定：管理端任何"新增"类表单都应显式包含所有必填字段的输入控件，禁止把筛选器状态隐式当成表单字段

