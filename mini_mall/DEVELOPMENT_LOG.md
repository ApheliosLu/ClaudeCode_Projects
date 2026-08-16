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

## 阶段 2：认证（Phase C，2026-08-16）

**计划**：lib/auth.ts + auth-client + api/auth/[...all] + proxy.ts + guards + 登录注册页 + 补 seed 账号。

**实际过程**：

1. **shadcn/ui 初始化**（计划 Phase A 遗漏项，此处补上）
   - `npx shadcn@latest init -b base -p nova -y`：2026 版 CLI 新增组件库选择，官方默认 **Base UI**（替代 Radix）+ Nova 预设（Lucide/Geist）。
   - add 14 个组件（button/card/input/label/badge/table/select/dialog/dropdown-menu/textarea/skeleton/separator/sheet/sonner）→ `src/components/ui/`。
   - 生成了 `src/lib/utils.ts`（cn 工具）。
2. **认证核心** ✅
   - `src/lib/auth.ts`：betterAuth 实例——emailAndPassword（min 8 位）、session 7 天、additionalFields 注入 role/membershipLevel/accumulatedSpentCents（input:false 防客户端篡改）、顶层不碰 next/headers（seed 可复用）。
   - `src/lib/auth-client.ts`、`src/app/api/auth/[...all]/route.ts`、`src/lib/guards.ts`（getSession/requireAuth/requireAdmin）、`src/proxy.ts`（Next16 认证 UX 层，Node runtime 可查库，仅跳转）。
3. **登录/注册页** ✅（客户端组件 + shadcn Card 表单；login 支持 callbackURL 回跳；Suspense 包裹 useSearchParams）
4. **(account)/(admin) layout** ✅（服务端鉴权兜底 + admin 侧边栏）
5. **seed 补账号** ✅ 重跑成功：admin@minimall.dev(ADMIN)、demo@minimall.dev(USER)、vip@minimall.dev(心悦2 预置 8 万元累计)。经 better-auth signUpEmail 注册保证密码哈希正确。
6. **运行验证** ✅（dev server + curl）：
   - 首页/登录页 200；未登录 /orders、/admin → 307 /login?callbackURL=…；登录后 /orders 放行（404 因页面未建，属正常）；非 ADMIN 访问 /admin → 307 首页；错误密码 401。

**遇到的问题与解决**：
- **better-auth 1.6 API 变化**：`auth.handlers` 不存在（TS 报错）。第一次尝试 `auth.handler`（单数函数），Next 路由要求 {GET, POST} 导出又不匹配 → 用官方适配器 `toNextJsHandler(auth)` 解决。
- **shadcn init 交互卡住**：`-y` 不能跳过组件库/预设选择 → 查 help 发现 `-b base -p nova` 参数，非交互完成。

**下一步（计划）**：Phase D 前台（商品浏览/购物车/下单/会员中心）。

---

## 阶段 3：前台功能（Phase D，2026-08-16）

**计划**：工具函数 + 会员规则 → 商品浏览（首页/列表/详情）→ 购物车 → 下单 → 订单 → 会员中心。

**实际过程**：

1. **基础层** ✅
   - `lib/utils.ts`：cn（shadcn 生成）+ formatCents/toCents/genOrderNo + 会员/订单状态中文名
   - `lib/membership.ts`：会员等级/阈值/折扣常量表（单一事实源）+ applyDiscount/getUpgradedLevel/getNextTier
   - `stores/cart.ts`：Zustand + persist（localStorage）；金额仅展示用，下单以服务端为准
2. **商品浏览** ✅：首页（hero + 分类入口 + featured 8 个）、列表页（q/category/sort 全部 searchParams 驱动）、详情页（画廊 + 加购 + 会员权益提示）
3. **购物车/下单** ✅：购物车页、结算页（收货表单 + createOrder）、订单列表/详情（归属校验 + 快照展示 + 折扣标注）
4. **会员中心** ✅：等级徽章、当前折扣、累计金额、距下一级差额、升级规则表
5. **中途插入：安全审查**（用户要求 /security-review）：技能因无 git remote 无法自动运行 → 手动审查，结论"无高危问题，5 项部署期配置项已记录"。
6. **用户新安排（Phase F 生效）**：管理端改用 **api-crud-generator skill 生成 REST API 形态**模块（用户明确指定接口清单）：
   - 商品：GET/POST `/api/admin/products` + PUT/DELETE `/api/admin/products/[id]`
   - 订单：GET `/api/admin/orders` + PUT `/api/admin/orders/[id]`（状态流转）
   - 分类：GET/POST `/api/admin/categories` + DELETE `/api/admin/categories/[id]`
   - 所有后台页面/接口校验 ADMIN。
   - 注：与项目买家端 Server Actions 架构并存，届时把 skill 生成物调整为 REST 形态（保留安全约定）。

**遇到的问题与解决**：
- **Base UI 组件 API 差异（3 处修复）**：shadcn Base UI 版 Button 不支持 Radix `asChild` → 改用 `render={<Link/>}`（TS 报错定位）。
- **Prisma 7 生成类型**：模型类型名为 `ProductModel` 非 `Product`；基础类型不含 include relation → ProductCard 改自有 DTO 类型。
- **createOrder 错误处理缺陷（自检发现）**：商品校验 throw 在 try 块外会变 500 → 重构为整体 try/catch 返回 `{ error }`；`orderNo` 作用域同步修复。
- **ActionResult 类型收窄**：`"error" in res && res.error` 复合条件无法收窄 → 改判别式 `"error" in res`。
- **用户安排**：整体开发完成后调用 /review 做整体代码审查（已加入任务清单）。

**下一步（计划）**：Phase E 模拟支付 + 会员升级（mockPay 含会员累加升级、cancelOrder 归还库存、支付页）。

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
