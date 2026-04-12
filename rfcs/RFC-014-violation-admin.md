# RFC-014：违约记录与信用治理（B5）

- **对应章节**：story.md 十四、管理端：违约管理
- **负责人**：zzk
- **迭代**：2
- **状态**：Draft

## 1. 背景与目标

管理员全局看违约、处理申诉、导出给学工/图书馆做分析。

## 2. 用户故事

| ID | 故事 |
|---|---|
| B5.1 | 查看所有违约记录 |
| B5.2 | 按学生/时段/自习室筛选 |
| B5.3 | 查看指定学生累计违约次数与分布 |
| B5.4 | 处理申诉或人工修正误判 |
| B5.5 | 查看未签到被自动取消的明细 |
| B5.6 | 导出违约数据（CSV / XLSX） |

## 3. 数据模型

复用 RFC-007 定义的 `Violation` 和 `Appeal`。

## 4. API 设计

| 方法 | 路径 | 权限 | Story |
|---|---|---|---|
| GET | `/api/admin/violations` | violation.view | B5.1, B5.2 |
| GET | `/api/admin/violations/{id}` | violation.view | B5.5 |
| GET | `/api/admin/violations/stats?user_id=` | violation.view | B5.3 |
| GET | `/api/admin/appeals?status=` | violation.view | B5.4 |
| POST | `/api/admin/appeals/{id}/approve` `{note}` | violation.handle | B5.4 |
| POST | `/api/admin/appeals/{id}/reject` `{note}` | violation.handle | B5.4 |
| POST | `/api/admin/violations/{id}/revoke` `{reason}` | violation.handle | B5.4 |
| GET | `/api/admin/violations/export?format=csv&...` | violation.view | B5.6 |

**申诉通过** 副作用：
1. `Appeal.status=APPROVED`
2. 对应 `Violation` 删除或置 `revoked=true`
3. `User.violation_count -= 1`
4. 生成通知发给学生（RFC-018）
5. 审计日志

## 5. 前端交互

- `/admin/violations`：筛选 + 表格，行展开显示对应预约详情与签到窗口
- 【导出】按钮下载 CSV
- `/admin/appeals`：Tab 展示 待审核 / 已通过 / 已驳回
- 单条详情弹窗：学生填写内容 + 证据图片 + 管理员决定按钮

## 6. 验收标准

严格对齐 story.md B5.1–B5.6 每条 AC。

- [ ] 管理员通过申诉 → 该学生 `violation_count` 立即 -1
- [ ] 导出 CSV 含学号/姓名/时间/教室/座位/原因/是否申诉成功
- [ ] `AUDITOR` 角色只能 view 不能 approve/reject

## 7. 非目标

- 不做违约人员名单公示（隐私合规）
- 不做违约自动封禁解封流水（由 RFC-007 信用等级规则决定）

## 8. 依赖与风险

- 依赖：RFC-007, RFC-017, RFC-010, RFC-018, RFC-020
- 风险：申诉通过需幂等，避免重复 -1
