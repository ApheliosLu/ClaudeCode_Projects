# mini_mall 开发实录

记录实际开发过程与最初计划的差异、遇到的问题及解决方案。最初计划：`C:\Users\q1209\.claude\plans\mini-mall-github-misty-newell.md`。本文档随开发持续更新。

---

## 阶段 0：规划与选型（2026-08-16）

**计划**：调研 GitHub 相似项目 → 确定技术栈（含具体版本）→ 完整规格文档 → 分阶段实施。

**实际过程与决策**：

1. **GitHub 调研**：找到 4 个微型电商学习项目（Mini-E-commerce / shopino / Mini-Shop / mini-market）+ 4 个大型参考（Your Next Store / Spree / Saleor / GoCart）。结论：2026 生态 = Next.js 16 + React 19 + Tailwind v4 + shadcn/ui + Server Actions。
2. **版本决策 1**：项目级 CLAUDE.md 规划的 Next.js 14（2023 年）已过时，用户确认改用 **Next.js 16.3**（2026-08-03 发布）。
3. **功能范围升级**：用户明确要"尽可能完整"——买家全流程 + 管理端（商品/订单/分类 CRUD）+ 可部署互联网，而非仅学习演示。
4. **Prisma 5 vs 7 讨论**：用户提出 Prisma 5，我指出其已 EOL（2023-07 发布，超一年无安全更新）、与 Next.js 16/Turbopack 是非官方组合、旧教程配套写法过时。用户采纳 **Prisma 7.9.1**。
5. **API 形态决策**：用户问计划是否有"18 个接口的请求/响应格式"，我澄清架构用 **Server Actions**（Next 16 主流）而非 REST API 层，用户确认。
6. **规格补全**：应用户要求补全 ER 关系图、17 页路由权限表、16 个接口清单、逐文件目录、17 步实施计划。
7. **会员功能（需求中途新增）**：累计实付 8000/80000/800000 元 → 心悦1/2/3（9.8/9.5/9 折）。设计：User 表冗余 `membershipLevel` + `accumulatedSpentCents`，升级触发点在 `mockPay` 事务内，折扣在 `createOrder` 按当前等级应用并快照 `discountPercent`。
8. **better-auth 选定**：Plan agent 调研发现 Auth.js 官方推荐新项目迁移到 better-auth（其团队 2025-09 加入 Better Auth），放弃 Auth.js v5。同时确认 Next.js 16 的 `middleware.ts` 更名为 `proxy.ts`（Node runtime）。

**遇到的问题**：无（规划阶段）。

---

## 阶段 1：脚手架与数据层（2026-08-16）

**计划**：create-next-app 初始化 → 装依赖 → Prisma schema/migrate/seed → CLAUDE.md。

**实际过程**：

1. **create-next-app 初始化** ✅
   - 命令：`npx create-next-app@latest . --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --yes`
   - **问题**：npm 下载慢（国内网络），命令超过 300s 超时被转后台，最终 exit 0 完成。
   - 产出：next **16.3.1**、react **19.2.8**、tailwindcss **4.3.3**、typescript ^5、ESLint 9。
2. **依赖安装** ✅（第二次同样超时转后台，最终成功）
   - prisma 7.9.1 全家桶、better-sqlite3 12.11.1、better-auth 1.6.29、zod 4.4.3、zustand 5.0.15、tsx 4.23.12。
   - 全部装入项目本地 `node_modules`（按全局约定，不装全局/不动 Python 环境）。
   - **注意**：zod 装到的是 **v4**（计划书写 v3 时代用法，实际 v4 API 基本兼容：z.object/safeParse 一致）。
3. **配置文件** ✅
   - `prisma/config.ts`（Prisma 7 的 prisma.config.ts：dotenv + datasource url + seed 命令）
   - `.env.example`（DATABASE_URL / BETTER_AUTH_SECRET / BETTER_AUTH_URL 模板）
   - `prisma/schema.prisma`：9 张表（better-auth 契约表 4 + 业务表 5），金额整数分、快照、软删除、会员字段。
4. **项目 CLAUDE.md** ✅（用户要求，先于 schema 落地）
   - 含技术栈版本表、功能范围、架构约定、数据模型、命令、种子账号、目录结构、注意事项。
5. **superpowers-zh 加载** ✅（用户操作，本会话未生效）
   - 用户复制 skills 到 `mini_mall/.claude/skills/`（20 个）并在 CLAUDE.md 写入 `superpowers-zh:begin/end` 标记。
   - **注意**：Claude Code 在会话启动时注册 skills，**新添加的 skill 需重启会话才生效**。本次会话继续按 superpowers 流程规范执行，但无法直接调用 Skill 工具。
6. **首次 git 提交** ✅（用户主动提出，保开发安全）
   - 建分支 `feature/mini-mall`，提交 `75b5c23`（82 文件，21774 行）。
   - `.gitignore` 补充：`prisma/dev.db*`、`src/generated/`、`.claude/settings.local.json`；提交前用 `git ls-files` 验证无 `.env`/数据库/密钥混入。
7. **建库** ✅
   - 生成 `BETTER_AUTH_SECRET`（openssl rand -base64 32）→ 写 `.env`（本地不入库）。
   - `prisma generate` 成功（客户端 7.9.1 → `src/generated/prisma`，入口 `client.ts`）。
   - `prisma migrate dev --name init` 成功：迁移 `20260816081941_init` 应用，9 张表入库。
8. **seed（商品与分类部分）** ✅
   - 4 分类 × 16 商品（中文品名、整数分价格、picsum 占位图、featured 标记），幂等 upsert 可重复执行。
   - **用户账号推迟到 Phase C**：seed 建用户须经 better-auth 注册（正确哈希密码），依赖认证模块落地，计划偏差。

**遇到的问题与解决**：
- npm 安装超时：转后台继续，不中断（此后大命令直接加长 timeout 或后台执行）。
- schema.prisma 首次写入被拒：用户要求先写 CLAUDE.md → 调整顺序后完成。
- **prisma.config.ts 位置错误（本阶段最大问题）**：Prisma 7 CLI 只在**项目根目录**查找 `prisma.config.ts`，我按计划误放为 `prisma/config.ts`，导致 CLI 回退 schema 内读 url 而报 "datasource.url property is required"。诊断：tsx 单独加载 config 正常（url 已解析），排除 dotenv 问题 → 确认是文件位置。解决：`mv prisma/config.ts prisma.config.ts`。
- **用户工作方式反馈（重要）**：要求"一步步来，不要一次做太多"、每步完成后汇报该步做了什么、安装动作前说明装到哪。已纳入协作方式。

**下一步（计划）**：Phase C 认证（better-auth + proxy + 登录注册页）→ 补 seed 用户账号并重跑 seed。

---

## 附录：与计划的偏差汇总

| 计划项 | 实际 | 原因 |
| --- | --- | --- |
| zod v3 假设 | 实际 v4.4.3 | create-next-app 时代版本；API 兼容 |
| 安装一次性完成 | 拆步执行 + 每步汇报 | 用户工作方式要求 |
| schema 先写 | CLAUDE.md 先行 | 用户要求项目文档先落地 |
| — | superpowers-zh 加载 | 用户中途添加，非原计划；需重启会话生效 |
| `prisma/config.ts`（计划目录） | 根目录 `prisma.config.ts` | Prisma 7 CLI 只在项目根查找该文件，子目录会报 datasource.url required |
| seed 一次含用户账号 | 商品/分类先跑，账号推迟 Phase C | 账号需经 better-auth 注册（密码哈希），依赖认证落地 |
| — | 每 Phase 完成更新 devlog + git 提交 | 用户工作方式要求（已写入 CLAUDE.md 与持久记忆） |
