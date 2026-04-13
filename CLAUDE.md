# CLAUDE.md · 与 Claude 协作的工作约定

本文件给 Claude（以及任何使用 Claude Code 的同学）在本项目下的工作规则。
Claude 在修改代码或文档时，**必须遵守以下约定**。违反这些规则视为未完成任务。

---

## 1. 修改代码后必须同步 RFC

位置：`rfcs/`

- 每次改动涉及 **数据模型 / API 路径或字段 / 前端路由或组件边界 / 业务规则**，必须更新对应的 RFC（编号在文件头部）
- 若 RFC 已标注 `状态: Draft`，调整后保持 Draft；若已标注 `Implemented`，在文末追加 **变更记录** 小节
- 若某条 Story 的 **验收标准**（AC）被实现/被修改，在 checkbox `[ ]` 前加 `[x]` 或调整描述
- 若新增 API，先在 RFC 的「API 设计」表格里补一行，再写代码

> 原则：**RFC 先于代码**。但当代码已经落地（如 bug 修复），必须立刻回补 RFC 的描述，让文档与代码不偏离。

---

## 2. Bug 修复必须立刻提交

- 修 bug 的 PR **禁止和功能开发混在一起**
- 修完、测通之后 **立即 `git commit`**（不要攒着），提交信息遵循：
  ```
  fix(<scope>): <简短描述> (RFC-XXX / Bug-YYY)
  ```
- 随后 **立即 `git push`**（push 失败时视为任务未完成）

## 3. Bug 必须关联 RFC

每个修复必须能回答两个问题：

1. **与哪个 RFC 相关**（哪条 Story/哪条 AC 被违反？）
2. **为什么之前没被发现**（RFC 的 AC 缺失？测试未覆盖？）

如果修完 bug 发现对应 RFC 的 AC 根本没写清，**必须**顺手修 RFC（回到规则 1）。

## 4. Bug 登记：`rfcs/DEBUG.md`

每修一个 bug，在 [`rfcs/DEBUG.md`](rfcs/DEBUG.md) 追加一行。格式：

```markdown
## Bug-YYYY-MM-DD-NN: <简短标题>

- **RFC**: RFC-XXX（#Story ID）
- **表现**: <用户看到什么>
- **原因**: <根因一句话>
- **修复**: <commit hash / 简短修法>
- **预防**: <新增的测试 / 补的 AC / 约定>
```

- 每次 Bug 编号单调递增
- 如果同一个 bug 涉及多个 RFC，`RFC:` 字段列多个
- 如果发现 RFC 有缺失的 AC，必须在「预防」里明确写出"已在 RFC-XXX 补充 AC X.Y"

---

## 5. 测试先行（理想，非强制）

- 修 bug 前先写能复现 bug 的 pytest，能 fail
- 修完后同一个测试应通过
- 测试文件命名：`backend/tests/test_<module>.py`，与被测代码同名

## 6. 不允许的操作

- ❌ 修了代码不更新 RFC
- ❌ 修了 bug 不记 DEBUG.md
- ❌ 修了 bug 不 commit + push
- ❌ `git push --force` 到 `main`（保护分支）
- ❌ 把多个不相关的变更放进同一个 commit

---

## 7. 典型工作流

修一个 bug 的完整步骤：

```
1. 复现 bug，定位根因
2. 在 rfcs/ 下找对应 RFC；如 AC 不完整先补 AC
3. 写 pytest（可以先红）
4. 改代码直到测试通过 + 手工验证
5. 追加 rfcs/DEBUG.md 一行
6. git add -> commit（fix(...) 信息 + 关联 RFC/Bug 号）
7. git push origin main
8. 在对话里告诉用户 commit hash + DEBUG.md 里的 Bug 编号
```

写一个新功能：

```
1. 先写/更新对应 RFC（数据模型 + API + 前端 + AC）
2. 开发 + 写测试
3. 本地 make test + npm run build 过
4. git commit（feat(...) 信息）
5. git push
6. 如果开发过程中发现 bug → 走上面的 bug 工作流
```

---

## 8. 奥卡姆剃刀：如无必要，勿增实体

改动应当是**解决问题所必需的最小集合**。新增任何"实体"（文件、模块、类、抽象层、依赖、配置项、中间件、RFC 条款、工具脚本、feature flag、向后兼容 shim）之前，先问：

1. 能不能复用现有的东西解决？
2. 不加这个东西，问题是否依然能修？
3. 这个实体只服务于"将来可能"的需求吗？（是的话 → 不加）

具体禁止：

- ❌ 修 bug 顺手"顺便重构"相邻无关代码
- ❌ 为一次性操作写"通用工具类 / 脚本"
- ❌ 加抽象层来"为未来的扩展做准备"（未来到了再加）
- ❌ 写多余的注释重复代码已经表达的内容
- ❌ 在只有一个实现的地方引入策略模式 / 工厂模式
- ❌ 给内部函数加 try/except 包一层只为了"更稳"——错误该抛就抛
- ❌ 改一行能修的 bug，搞出跨多文件的"架构调整"

> 如果一个改动既能三行修完、也能"顺便优化"二十行修完，**选三行**。剩下的留给专门的重构 PR。

---

## 9. 和这个项目特定的约束

- Python 用 3.13；后端在 `backend/.venv`
- 两端前端分别跑在 5273（admin）/ 5174（student）；端口变更要同步改 `backend/app/core/config.py` 的 CORS 列表
- 每次修完跑一次 `make test`，至少确认 20+ 用例全绿
- Git 远程 push 可能被网络拦，需要时用 `https_proxy=http://127.0.0.1:7897 git push ...`
- 用户身份：本仓库提交者为 `Curry09 <1187524561@qq.com>`，Claude 不要改 git config

---

## 10. 修完告诉用户什么

最终消息包含：

- 修了什么（一两句）
- 对应 Bug 编号（如 Bug-2026-04-12-01）
- 对应 RFC 和 Story ID
- commit hash 和"已 push"
- 如果动了 RFC，指明动了哪份、哪一小节

不要只说"修好了"。
