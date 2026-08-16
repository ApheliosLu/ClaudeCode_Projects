# mini_mall — 微型电商全栈应用

学习用 Claude Code 从零搭建完整前后端电商项目，目标可部署到互联网（Vercel）。完整规格见计划文件 `C:\Users\q1209\.claude\plans\mini-mall-github-misty-newell.md`；实际开发过程、问题与解决方案见 [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)（开发实录，与计划对比）。

## 技术栈（2026-08 确认）

| 层 | 技术 | 版本 |
| --- | --- | --- |
| 框架 | Next.js | 16.3.1（App Router + RSC + Server Actions + Turbopack） |
| UI | React | 19.2.8 |
| 样式 | Tailwind CSS | 4.3.3（v4 CSS-first，配置在 globals.css `@theme`） |
| 数据库 | SQLite（本地）→ Postgres（Vercel 部署） | adapter 工厂按 URL 自动切换 |
| ORM | Prisma | 7.9.1（v7 新范式：driver adapter + prisma.config.ts + 生成客户端 output） |
| 认证 | better-auth | 1.6.x（邮箱密码 + 数据库 session + role 字段） |
| 状态 | Zustand 5 + persist | 购物车 localStorage |
| 校验 | Zod 4 | Server Action 输入校验 |
| 组件 | shadcn/ui | Next 16 + Tailwind v4 兼容 |
| 支付 | 模拟支付（mockPay） | 订单状态机驱动，无真实网关 |

## 功能范围

- **买家**：浏览 → 搜索/分类筛选 → 详情 → 注册登录 → 购物车 → 下单 → 模拟支付 → 查看订单
- **会员**：按累计实付升级（只升不降，新订单生效）：
  - 心悦1：累计 ≥ 8000 元 → 9.8 折（98%）
  - 心悦2：累计 ≥ 80000 元 → 9.5 折（95%）
  - 心悦3：累计 ≥ 800000 元 → 9 折（90%）
  - 常量表单一事实源在 `src/lib/membership.ts`；升级触发点在 `mockPay` 事务内
- **管理员**：商品 CRUD（软删除下架）、订单状态流转、分类管理、仪表盘

## 架构约定

- **读**：Server Component 直连 Prisma（无 API 层）
- **写**：Server Action（`src/lib/actions/*`），固定模式：`requireAuth/requireAdmin()` → Zod safeParse → Prisma 事务 → revalidatePath → 返回 `{ error?: string }`
- **金额统一整数分**（priceCents/totalCents），展示用 `formatCents()`；折扣整数运算 `round(cents × qty × discount ÷ 100)`
- **快照**：Order/OrderItem 存商品名、单价、收货信息快照；商品删除走 `isActive=false` 软删除
- **订单状态机**（白名单校验，非法流转报错）：`PENDING → PAID(买家支付) | CANCELLED`；`PAID → SHIPPED | CANCELLED`；`SHIPPED → DELIVERED | CANCELLED`；`DELIVERED` 终态
- **权限双层**：`src/proxy.ts`（Next 16 的 middleware 更名，仅 UX 跳转）+ Server Component layout / Server Action 内真实校验
- **库存防超卖**：`updateMany({ where: { id, stock: { gte: qty } }, data: { stock: { decrement: qty } } })` 原子扣减；取消订单事务内回补

## 数据模型（9 张表）

- better-auth 契约表（字段名须精确匹配 adapter）：`User`（含 `role`、`membershipLevel`、`accumulatedSpentCents`）、`Session`、`Account`、`Verification`
- 业务表：`Category`、`Product`、`ProductImage`（SQLite 无 String[] 故独立表）、`Order`、`OrderItem`

## 常用命令

```bash
npm run dev          # 开发（localhost:3000）
npm run build        # 生产构建验证
npx prisma migrate dev --name <name>   # 改 schema 后建迁移
npx prisma db seed   # 种子数据（tsx prisma/seed.ts）
npx prisma studio    # 可视化查看数据
```

## 种子账号（prisma/seed.ts）

| 账号 | 密码 | 角色 | 用途 |
| --- | --- | --- | --- |
| admin@minimall.dev | Admin@123456 | ADMIN | 管理端 |
| demo@minimall.dev | Demo@123456 | USER | 普通买家（可测升级） |
| vip@minimall.dev | Demo@123456 | USER（预置心悦2） | 会员折扣演示（9.5 折） |

## 目录结构

```
mini_mall/
├─ prisma/            # schema.prisma / config.ts(prisma.config.ts) / seed.ts
├─ src/
│  ├─ proxy.ts        # 认证 UX 跳转（Next16 middleware 更名）
│  ├─ app/
│  │  ├─ (shop)/      # products 列表与详情
│  │  ├─ (auth)/      # login / register
│  │  ├─ (account)/   # cart / checkout / pay/[orderNo] / orders / membership（需登录）
│  │  └─ (admin)/     # 仪表盘 / products / orders / categories（仅 ADMIN）
│  ├─ components/     # ui/（shadcn）+ 业务组件
│  ├─ lib/            # auth.ts / auth-client.ts / prisma.ts / membership.ts / guards.ts / validators.ts / utils.ts / actions/
│  ├─ stores/cart.ts  # Zustand + persist
│  └─ generated/prisma/   # Prisma 生成客户端（gitignore，postinstall 生成）
```

## 注意事项

- **Prisma 7**：生成客户端输出到 `src/generated/prisma`（gitignore）；`prisma.config.ts` 必须显式 `import 'dotenv/config'`；package.json 已有 `postinstall: prisma generate`（Vercel 构建必需）
- **Next.js 16**：`middleware.ts` 不存在，必须用 `proxy.ts`（Node runtime）；Turbopack 默认打包器
- **部署 Vercel**：文件系统只读 → 必须先切 Postgres（改 schema provider + adapter 自动分流 + `migrate deploy`）；连接串用 `postgresql://` 不用 `prisma://`（规避 Vercel issue #79063）；环境变量 `DATABASE_URL` / `BETTER_AUTH_SECRET` / `BETTER_AUTH_URL`（生产配 trustedOrigins）
- **better-auth**：`src/lib/auth.ts` 模块顶层不得调用 `next/headers`（seed 脚本 tsx 环境可复用）；getSession 在辅助函数内才 `await headers()`
- **购物车水合**：Zustand persist 的客户端组件用 mounted 标志防 hydration mismatch
- `prisma/dev.db`、`src/generated/`、`.env` 不入库；新功能先建 Git 分支（上层仓库管理）

<!-- superpowers-zh:begin (do not edit between these markers) -->
# Superpowers-ZH 中文增强版

本项目已安装 superpowers-zh 技能框架（20 个 skills）。

## 核心规则

1. **收到任务时，先检查是否有匹配的 skill** — 哪怕只有 1% 的可能性也要检查
2. **设计先于编码** — 收到功能需求时，先用 brainstorming skill 做需求分析
3. **测试先于实现** — 写代码前先写测试（TDD）
4. **验证先于完成** — 声称完成前必须运行验证命令

## 可用 Skills

Skills 位于 `.claude/skills/` 目录，每个 skill 有独立的 `SKILL.md` 文件。

- **brainstorming**: 在任何创造性工作之前必须使用此技能——创建功能、构建组件、添加功能或修改行为。在实现之前先探索用户意图、需求和设计。
- **chinese-code-review**: 中文 review 沟通参考——话术模板、分级标注（必须修复/建议修改/仅供参考）、国内团队常见反模式应对。仅在用户显式 /chinese-code-review 时调用，不要根据上下文自动触发。
- **chinese-commit-conventions**: 中文 commit 与 changelog 配置参考——Conventional Commits 中文适配、commitlint/husky/commitizen 中文模板、conventional-changelog 中文配置。仅在用户显式 /chinese-commit-conventions 时调用，不要根据上下文自动触发。
- **chinese-documentation**: 中文文档排版参考——中英文空格、全半角标点、术语保留、链接格式、中文文案排版指北约定。仅在用户显式 /chinese-documentation 时调用，不要根据上下文自动触发。
- **chinese-git-workflow**: 国内 Git 平台配置参考——Gitee、Coding.net、极狐 GitLab、CNB 的 SSH/HTTPS/凭据/CI 接入差异与镜像同步配置。仅在用户显式 /chinese-git-workflow 时调用，不要根据上下文自动触发。
- **dispatching-parallel-agents**: 当面对 2 个以上可以独立进行、无共享状态或顺序依赖的任务时使用
- **executing-plans**: 当你有一份书面实现计划需要在单独的会话中执行，并设有审查检查点时使用
- **finishing-a-development-branch**: 当实现完成、所有测试通过、需要决定如何集成这份工作时使用
- **mcp-builder**: MCP 服务器构建方法论 — 系统化构建生产级 MCP 工具，让 AI 助手连接外部能力
- **receiving-code-review**: 收到代码审查反馈后、实施建议之前使用，尤其当反馈不明确或技术上有疑问时——需要技术严谨性和验证，而非敷衍附和或盲目执行
- **requesting-code-review**: 完成任务、实现重要功能或合并前使用，用于验证工作成果是否符合要求
- **subagent-driven-development**: 当在当前会话中执行包含独立任务的实现计划时使用
- **systematic-debugging**: 遇到任何 bug、测试失败或异常行为时使用，在提出修复方案之前执行
- **test-driven-development**: 在实现任何功能或修复 bug 时使用，在编写实现代码之前
- **using-git-worktrees**: 当需要开始与当前工作区隔离的功能开发，或在执行实现计划之前使用——通过原生工具或 git worktree 回退机制确保隔离工作区存在
- **using-superpowers**: 在开始任何对话时使用——确立如何查找和使用技能，要求在任何响应（包括澄清性问题）之前调用 Skill 工具
- **verification-before-completion**: 在宣称工作完成、已修复或测试通过之前使用，在提交或创建 PR 之前——必须运行验证命令并确认输出后才能声称成功；始终用证据支撑断言
- **workflow-runner**: 在 Claude Code / OpenClaw / Cursor 中直接运行 agency-orchestrator YAML 工作流——无需 API key，使用当前会话的 LLM 作为执行引擎。当用户提供 .yaml 工作流文件或要求多角色协作完成任务时触发。
- **writing-plans**: 当你有规格说明或需求用于多步骤任务时使用，在动手写代码之前
- **writing-skills**: 当创建新技能、编辑现有技能或在部署前验证技能是否有效时使用

## 如何使用

当任务匹配某个 skill 时，使用 `Skill` 工具加载对应 skill 并严格遵循其流程。绝不要用 Read 工具读取 SKILL.md 文件。

如果你认为哪怕只有 1% 的可能性某个 skill 适用于你正在做的事情，你必须调用该 skill 检查。
<!-- superpowers-zh:end -->
