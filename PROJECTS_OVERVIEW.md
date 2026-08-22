# 项目大局总结（PROJECT OVERVIEW）

本文件按**项目维度**记录工作区（ClaudeCode_Projects）中各项目的状态：做了什么、做到什么程度、下一步是什么。

**更新约定**：每个项目完成时（由用户提醒）更新对应条目；新项目加入时追加条目。时间维度的流水记录见 `weekly-report/`。

最后更新：2026-08-22

## 总览

| 项目 | 技术栈 | 状态 | 完成度 |
|---|---|---|---|
| hello_world | Node.js 原生 http（零依赖） | ✅ 完成 | 入门练习 |
| finance-cli | Python + Streamlit + SQLite | ✅ 可用 | 可用小工具 |
| mini_mall | Next.js 16 + Prisma + better-auth 全栈 | 🟡 待部署 | 本地完成、工程化受控 |

三个项目构成一条渐进学习路线：**hello_world**（Web 最朴素形态）→ **finance-cli**（后端 + 数据层）→ **mini_mall**（全栈 + 工程化纪律）。

## 项目详情

### hello_world — 原生 Node.js 入门页

- **做了什么**：手写约 30 行 Node.js `http` 服务器（零第三方依赖），监听 3000 端口，`/` 返回 "hello ai coding" 页面，其余路径 404。前端纯 HTML + 内联 CSS。
- **状态**：✅ 完成。有意保持最小，纯学习示例，无业务。
- **学习点**：Web 服务最朴素形态；与 finance-cli 的对照表见其 CLAUDE.md。

### finance-cli — Streamlit 记账工具

- **做了什么**：Web 记账工具：表单新增账目（金额/分类/日期/备注）→ 按月份 + 分类筛选 → 按 ID 删除 → 分类统计（柱状图 + 统计表）。分层清晰（`database.py` CRUD / `web.py` 界面 / `models.py` dataclass），`start.bat` 一键启动。
- **状态**：✅ 可用。功能完整无 TODO，但无测试、无开发日志、git 仅 1 次提交。
- **下一步（可选）**：补单元测试与开发日志，工程化对齐 mini_mall 的标准。

### mini_mall — 全栈微型电商（主项目）

- **做了什么**：完整电商链路——买家端（浏览/搜索/筛选/排序 → 详情 → 注册登录 → 购物车 → 下单 → 模拟支付 → 订单 → 会员中心）、会员体系（心悦 1/2/3，9.8/9.5/9 折，下单快照折扣）、管理端（仪表盘 + 商品 CRUD 软删除 + 订单状态机 + 分类 CRUD）。工程细节：金额整数分、原子扣库存防超卖、订单状态机白名单、CAS 条件更新防竞态、权限双层校验、9 表 Prisma schema、种子数据。
- **进度**：10 个开发阶段全部完成（`docs/DEVELOPMENT_LOG.md`，2026-08-16 ~ 08-17），Playwright E2E 21/21 通过、lint/tsc/build 全绿、双轮审查（代码 + 安全）完成。关键技术排障：better-sqlite3 在 Node 24 下崩溃 → 换 Prisma libsql adapter。
- **状态**：🟡 **本地完成，待部署**。尚未公网上线（Vercel + Neon 为文档化下一步，有硬阻塞：`@prisma/adapter-pg` 未装、schema 仍为 sqlite）；已知遗留：PENDING 订单无 TTL、seed 明文密码、邮箱验证、限流、无单元测试。
- **路线图**：`docs/LEARNING_ROADMAP.md` 已定 3 个月行动路线（第 1 个月部署上线 + 补单元测试；第 2 个月 Docker + CI；第 3 个月第二个项目 + 刷题）。
- **部署方式**：需用 `git subtree split` 拆成独立仓库。

## 待办与关注

- mini_mall 部署（Vercel + Neon）是工作区当前唯一进行中的主线
- finance-cli 可回填测试与日志（低优先级）
