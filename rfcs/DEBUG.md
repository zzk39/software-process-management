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
