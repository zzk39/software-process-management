# 迭代 1 任务看板

**目标**：打通 **登录 → 浏览自习室 → 预约 → 签到 → 自动违约** 的端到端主链路。
**周期**：第 3~5 周（Review 前交付）。
**交付物**：可运行的后端 + 两个前端 + 冒烟测试通过 + 本文档同步更新勾选状态。

---

## 团队分工（6 人）

### 学生端（3 人）
| 负责人 | 负责 Feature | 模块目录 |
|---|---|---|
| **学生A** | A1 身份 / A2 浏览 / A3 搜索 | `backend/app/api/auth.py` · `rooms.py` · `search.py` · `student-web/src/views/Login.vue` · `Rooms.vue` |
| **林佳航** | A4 预约 / A5 变更取消 / A6 签到 | `backend/app/api/reservations.py` · `checkin.py` · `student-web/src/views/RoomDetail.vue` · `MyReservations.vue` |
| **学生C** | A7 提醒违约 / A8 历史 / A9 智能助手 | `backend/app/api/notifications.py` · `history.py` · `assistant.py`（迭代 1 暂不新建，只在 `MyReservations` 中展示违约状态） |

### 管理端（3 人）
| 负责人 | 负责 Feature | 模块目录 |
|---|---|---|
| **管理员D** | B1 RBAC / B2 自习室 / B3 座位 | `backend/app/api/admin/rooms.py` · `seats.py` · `admin-web/src/views/Rooms.vue` · `Seats.vue` |
| **zzk** | B4 代办 / B5 违约 / B6 参数 | `backend/app/api/admin/reservations.py` · `violations.py` · `config.py` · `admin-web/src/views/Reservations.vue` |
| **管理员F** | B7 统计 / C1 自动化 / C4 审计 | `backend/app/api/admin/stats.py` · `backend/app/tasks/scheduler.py` |

> 所有人共建的基础设施（User 模型 / JWT 鉴权 / 响应封装 / SQLAlchemy 连接）已在骨架中完成，见 `backend/app/core/`。

---

## 迭代 1 交付清单（按人分点）

### ✅ 已在骨架中完成
- [x] **基础**：FastAPI 项目 + SQLAlchemy 模型（User/Room/Seat/Reservation/Violation）+ JWT 登录 + 统一响应
- [x] **基础**：admin-web / student-web Vue3 项目 + 路由 + axios 封装
- [x] **基础**：APScheduler 自动违约任务 + 每日签到码刷新
- [x] **基础**：冒烟测试（登录 + 院系可见范围）

### 学生A（A1+A2）
- [x] Story A1.1 学号密码登录（`POST /api/auth/login`）
- [x] Story A1.2 根据用户院系过滤可见自习室
- [x] Story A2.1 自习室列表 `GET /api/rooms`
- [x] Story A2.2 展示开放时间、楼栋楼层
- [ ] Story A2.10 查看某座位未来一段时间的可预约时段（**迭代 1 交付**）
  - 新增 `GET /api/rooms/{id}/seats/{sid}/slots?date=YYYY-MM-DD`
  - 前端在 `RoomDetail.vue` 中点座位后展示时段色块
- [ ] Story A3.1 按日期+时间段搜索 `GET /api/seats/search?date=&start_hour=&hours=` (**迭代 1 选做**)

### 林佳航（A4+A5+A6）
- [x] Story A4.1 按整点+时长创建预约 `POST /api/reservations`
- [x] Story A4.2 仅允许整点
- [x] Story A4.3 ≤ 4 小时
- [x] Story A4.5 时段冲突校验
- [x] Story A4.6 自习室开放时间校验
- [x] Story A4.10 同一时段单用户唯一
- [x] Story A5.2 取消未开始的预约
- [x] Story A6.2 Web 端输入动态码签到
- [x] Story A6.4 签到时间窗口校验
- [ ] Story A5.5 前端展示 PENDING/CHECKED_IN/CANCELLED/VIOLATED 五种状态（骨架已做 4 种，需要补 FINISHED）

### 学生C（A7+A8）
- [ ] Story A7.3 违约发生后展示站内消息（迭代 1 只做页面 toast，不做邮件/微信）
  - 新增 `GET /api/notifications/me` 返回站内消息列表
  - `MyReservations.vue` 顶部通知条
- [ ] Story A8.1 历史记录 `GET /api/history/me`（`MyReservations` 已列出，需补"已完成/已取消"过滤 Tab）

### 管理员D（B2+B3，RBAC 留到迭代 2）
- [x] Story B2.1 登记新自习室 `POST /api/admin/rooms`
- [x] Story B2.2 维护基本信息（名称/院系/时间）
- [x] Story B2.7 停用自习室 `DELETE /api/admin/rooms/{id}`
- [x] Story B3.1 登记座位 `POST /api/admin/seats`
- [x] Story B3.4 标记插座/靠窗
- [x] Story B3.5 停用座位
- [ ] Story B3.7 批量导入（**迭代 1 选做**：接受 CSV）

### zzk（B4，B5/B6 迭代 2 做）
- [x] Story B4.1 查看所有预约 `GET /api/admin/reservations`
- [x] Story B4.2 按学生、自习室、日期、状态筛选
- [ ] Story B4.4 代预约 `POST /api/admin/reservations/manual`（**迭代 1 交付**）
- [ ] Story B4.5 代取消 `POST /api/admin/reservations/{id}/cancel`（**迭代 1 交付**）

### 管理员F（C1，B7/C4 迭代 2 做）
- [x] Story C1.3 预约开始 15 分钟后自动取消（`scheduler.auto_cancel_no_show`）
- [x] Story C1.4 自动取消后座位回到可预约
- [x] Story C1.5 记录违约 + 用户 violation_count +1
- [x] Story C1.7 每日刷新签到码

---

## 迭代 1 刻意不做（推到迭代 2+）

- B1 RBAC 细粒度权限（当前仅用 `is_admin` 单标志）
- A3 搜索筛选高级条件
- A7.1 预约前 15 分钟提醒 + A7.2 签到催促
- A9 智能助手
- B5 违约管理细化 / B6 系统参数热更 / B7 统计图表
- 微信端、二维码签到、平面图
- A8 历史复订、A8.4 一键再次预约

---

## 接口契约（迭代 1 稳定版）

统一响应 `{ "code": 0, "message": "ok", "data": ... }`，除登录外均需 `Authorization: Bearer <token>`。

| 方法 | 路径 | 说明 | 负责人 |
|---|---|---|---|
| POST | `/api/auth/login` | 登录 | 学生A |
| GET | `/api/auth/me` | 当前用户 | 学生A |
| GET | `/api/rooms` | 可见自习室列表 | 学生A |
| GET | `/api/rooms/{id}` | 自习室详情 | 学生A |
| GET | `/api/rooms/{id}/seats` | 自习室座位 | 学生A |
| POST | `/api/reservations` | 创建预约 | 林佳航 |
| GET | `/api/reservations/me` | 我的预约 | 林佳航 |
| POST | `/api/reservations/{id}/cancel` | 取消 | 林佳航 |
| POST | `/api/checkin` | 动态码签到 | 林佳航 |
| GET | `/api/admin/rooms` | 全部自习室（含停用） | 管理员D |
| POST | `/api/admin/rooms` | 登记自习室 | 管理员D |
| PUT | `/api/admin/rooms/{id}` | 更新自习室 | 管理员D |
| DELETE | `/api/admin/rooms/{id}` | 停用 | 管理员D |
| GET/POST/DELETE | `/api/admin/seats` | 座位 CRUD | 管理员D |
| GET | `/api/admin/reservations` | 查询预约 | zzk |

---

## 开发约定

1. **分支**：`feat/<story-id>-<short>`，例如 `feat/A4.1-create-reservation`
2. **提交**：`<type>(<scope>): <subject>`，例如 `feat(reservations): 整点校验`
3. **PR Review**：至少 1 人 approve 才合并，CI 跑 pytest + 前端 build
4. **冲突**：先 `git pull --rebase origin main` 再推
5. **接口变更**：必须同步更新本文档 + `backend/README.md` 的接口契约表
6. **测试**：每个 Story 至少 1 个 pytest 冒烟测试（集成测试即可，不强求单元）

---

## 迭代 1 Done 的定义（DoD）

- [ ] 后端：pytest 全部通过
- [ ] 前端：两个 Vue 项目 `npm run build` 成功
- [ ] 手工回归：**学生A → 林佳航 → 管理员D** 三人协作跑通一次
  1. 管理员D 登记 1 间自习室 + 5 个座位
  2. 学生A 登录能看到该自习室
  3. 林佳航（或任一学生）选座预约 2 小时
  4. 管理员从后台查到这条记录
  5. （演示）手动把预约时间调到 20 分钟前 → 等 1 分钟观察调度器自动标为 VIOLATED
- [ ] 每个负责人在本文档中勾选自己完成的 Story
