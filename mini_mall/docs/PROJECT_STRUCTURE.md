# mini_mall 项目目录结构（逐文件）

> 实际文件清单（2026-08-16，docs/ 归类整理后）。排除：`node_modules/`、`.next/`、`src/generated/`（Prisma 生成，postinstall 重建）、`dev.db`（本地库）、`.env`（本地配置）。

```
mini_mall/
├─ .claude/
│  ├─ settings.json                    # 项目权限配置（allow/deny + hooks + autoCompact）
│  ├─ settings.local.json              # 本地个性化（不入库）
│  └─ skills/                          # 20 个 superpowers-zh skills + api-crud-generator
│                                     # （各 skill 清单见 CLAUDE.md superpowers 段）
├─ docs/                               # 项目文档（分类整理）
│  ├─ DEVELOPMENT_LOG.md               # 开发实录（9 个阶段，与计划对比，含排障过程）
│  ├─ LEARNING_ROADMAP.md              # 学习复盘与全栈工程师路线图
│  ├─ PROJECT_STRUCTURE.md             # 本文档（逐文件目录结构）
│  └─ DEPLOYMENT_GUIDE.md              # 部署上线步骤（Vercel + Neon）
├─ e2e/
│  ├─ full-flow-test.py                # E2E 全流程测试（Playwright + Edge，21 项断言）
│  └─ README.md                        # E2E 运行说明（备份/恢复数据库）
├─ prisma/
│  ├─ schema.prisma                    # 9 张表数据模型（认证契约 4 + 业务 5）
│  ├─ seed.ts                          # 种子数据：4 分类 × 16 商品 + 3 个演示账号（幂等）
│  └─ migrations/
│     ├─ migration_lock.toml           # 迁移锁
│     └─ 20260816081941_init/
│        └─ migration.sql              # 初始建表 SQL
├─ public/                             # 静态资源（SVG 占位图标）
│  ├─ file.svg / globe.svg / next.svg / vercel.svg / window.svg
├─ src/
│  ├─ proxy.ts                         # Next16 认证 UX 层（middleware 更名）：登录/角色跳转
│  ├─ app/
│  │  ├─ layout.tsx                    # 根布局：Navbar + Footer + Toaster + 全局字体
│  │  ├─ page.tsx                      # 首页：hero + 分类入口 + 精选商品 [Server]
│  │  ├─ globals.css                   # Tailwind v4 @import + @theme 主题变量
│  │  ├─ not-found.tsx                 # 404 页
│  │  ├─ error.tsx                     # 全局错误边界
│  │  ├─ loading.tsx                   # 全局加载骨架
│  │  ├─ favicon.ico
│  │  ├─ (shop)/                       # 买家公开区
│  │  │  └─ products/
│  │  │     ├─ page.tsx                # 商品列表（q 搜索/category 筛选/sort 排序）[Server]
│  │  │     └─ [slug]/page.tsx         # 商品详情（画廊+加购+会员权益）
│  │  ├─ (auth)/                       # 认证页
│  │  │  ├─ login/page.tsx             # 登录（callbackURL 防 open redirect；已登录跳首页）
│  │  │  └─ register/page.tsx          # 注册
│  │  ├─ (account)/                    # 买家受保护区（layout 登录校验）
│  │  │  ├─ layout.tsx                 # requireAuth 兜底
│  │  │  ├─ cart/page.tsx              # 购物车（Zustand，mounted 防闪烁）
│  │  │  ├─ checkout/page.tsx          # 结算（收货表单 → createOrder）
│  │  │  ├─ pay/[orderNo]/page.tsx     # 收银台（归属+PENDING 预校验）
│  │  │  ├─ orders/page.tsx            # 我的订单列表 [Server]
│  │  │  ├─ orders/[orderNo]/page.tsx  # 订单详情（归属校验+取消按钮）
│  │  │  └─ membership/page.tsx        # 会员中心（等级/折扣/距下一级）
│  │  ├─ admin/                        # 管理端（真实目录，URL 带 /admin 前缀）
│  │  │  ├─ layout.tsx                 # requireAdmin + 侧边栏
│  │  │  ├─ page.tsx                   # 仪表盘（订单数/销售额/最近 10 单）[Server]
│  │  │  ├─ products/
│  │  │  │  ├─ page.tsx                # 商品管理表格（搜索/下架/编辑入口）
│  │  │  │  ├─ new/page.tsx            # 新建商品
│  │  │  │  └─ [slug]/edit/page.tsx    # 编辑商品（以 slug 定位）
│  │  │  ├─ orders/page.tsx            # 订单管理（状态筛选 + 流转按钮）
│  │  │  └─ categories/page.tsx        # 分类管理（列表 + 新增/编辑表单）
│  │  └─ api/
│  │     ├─ auth/[...all]/route.ts     # better-auth handlers（toNextJsHandler）
│  │     └─ admin/                     # 管理端 REST API（全部 getAdminSession 401）
│  │        ├─ products/route.ts       # GET 列表 + POST 创建
│  │        ├─ products/[slug]/route.ts# GET 详情 + PUT 更新 + DELETE 软删除
│  │        ├─ orders/route.ts         # GET 列表（状态枚举校验）
│  │        ├─ orders/[id]/route.ts    # PUT 状态流转（白名单+CAS+取消回库存）
│  │        ├─ categories/route.ts     # GET 列表 + POST 创建
│  │        └─ categories/[id]/route.ts# PUT 更新 + DELETE（引用保护）
│  ├─ components/
│  │  ├─ ui/                           # shadcn（Base UI）14 个组件
│  │  │  ├─ button / card / input / label / badge / table / select /
│  │  │  ├─ dialog / dropdown-menu / textarea / skeleton / separator /
│  │  │  └─ sheet / sonner
│  │  ├─ Navbar.tsx                    # 顶部导航 [Server]（session 感知）
│  │  ├─ Footer.tsx                    # 页脚
│  │  ├─ ProductCard.tsx               # 商品卡片（DTO 类型，自定 fallback 图）
│  │  ├─ Price.tsx                     # 金额展示（分→¥，可选划线原价）
│  │  ├─ ImageGallery.tsx              # 商品图画廊（主图+缩略图切换）[客户端]
│  │  ├─ AddToCartButton.tsx           # 加购按钮（数量选择 + Zustand）[客户端]
│  │  ├─ CartBadge.tsx                 # 购物车徽标（mounted 防闪烁）[客户端]
│  │  ├─ LogoutButton.tsx              # 登出按钮 [客户端]
│  │  ├─ OrderStatusBadge.tsx          # 订单状态徽章
│  │  ├─ MembershipBadge.tsx           # 会员等级徽章
│  │  ├─ PayForm.tsx                   # 支付表单（渠道单选+确认）[客户端]
│  │  ├─ CancelOrderButton.tsx         # 取消订单按钮 [客户端]
│  │  └─ admin/
│  │     └─ ProductForm.tsx            # 商品新增/编辑共享表单
│  ├─ hooks/
│  │  └─ use-mounted.ts                # 客户端挂载标志（hydration 惯例，文件级 disable）
│  ├─ lib/
│  │  ├─ auth.ts                       # betterAuth 实例（additionalFields: role/会员字段）
│  │  ├─ auth-client.ts                # createAuthClient 客户端实例
│  │  ├─ guards.ts                     # getSession / requireAuth / requireAdmin / getAdminSession
│  │  ├─ prisma.ts                     # Prisma 单例 + adapter 工厂（file:→libsql，否则→pg）
│  │  ├─ membership.ts                 # 会员常量表（阈值/折扣单一事实源）+ 折扣/升级计算
│  │  ├─ order-machine.ts              # 订单状态机白名单 + canTransition
│  │  ├─ validators.ts                 # Zod schemas（下单/支付/商品/分类）
│  │  ├─ utils.ts                      # formatCents/toCents/genOrderNo/cn/中文名
│  │  └─ actions/
│  │     └─ order.ts                   # Server Actions：createOrder / mockPay / cancelOrder
│  ├─ stores/
│  │  └─ cart.ts                       # Zustand + persist 购物车（金额仅展示）
│  └─ generated/prisma/                # Prisma 生成客户端（gitignore，postinstall 生成）
├─ .env                                # 本地环境变量（不入库）
├─ .env.example                        # 环境变量模板
├─ .gitignore
├─ .markdownlint.json                  # markdownlint 配置（中文文档规则适配）
├─ AGENTS.md                           # create-next-app 生成的 AI 代理说明
├─ CLAUDE.md                           # 项目约定（架构/命令/账号/上线清单）——必须留根目录
├─ README.md                           # 快速开始/功能/账号/部署——留根目录（GitHub/Vercel 惯例）
├─ components.json                     # shadcn 配置
├─ eslint.config.mjs                   # ESLint 配置（ignore: generated/skills）
├─ next.config.ts                      # Next 配置（serverExternalPackages）
├─ package.json                        # 依赖 + 脚本（含 postinstall: prisma generate）
├─ postcss.config.mjs                  # PostCSS（Tailwind v4）
├─ prisma.config.ts                    # Prisma 7 CLI 配置（必须位于项目根）
└─ tsconfig.json                       # TS 配置（@/* → src/*）
```

## 目录分类逻辑

| 目录 | 用途 | 能否移动 |
| --- | --- | --- |
| `src/` | 应用源码（路由/组件/逻辑） | 否（框架约定） |
| `prisma/` | 数据模型/迁移/种子 | 否（框架约定） |
| `docs/` | **项目文档**（实录/路线/结构/部署） | ✅ 本次已归类 |
| `e2e/` | E2E 测试 | ✅ 已归类 |
| `public/` | 静态资源 | 否（框架约定） |
| `.claude/` | Claude Code 配置 + skills | 否（工具约定） |
| 根目录配置文件 | package/next/ts/eslint/prisma 等 | **否**（构建工具在根目录查找，移动即失效） |
| `README.md` / `CLAUDE.md` | 惯例固定位置 | 否（README 是 GitHub/Vercel 惯例；CLAUDE.md 是 Claude Code 加载机制） |

## 关键结构说明

1. **买家端写操作**：Server Actions（`src/lib/actions/order.ts`），统一 `{ error } | 数据` 返回
2. **管理端**：REST API（`src/app/api/admin/*`）+ 客户端页面（`src/app/admin/*`），全部 ADMIN 双保险
3. **路由组**：`(shop)`/`(auth)`/`(account)` 是代码组织，不产生 URL；`admin/` 是真实目录（`/admin/*`）
4. **同层级动态段参数名必须一致**：商品统一用 `[slug]`（`/products/[slug]` 与 `/admin/products/[slug]/edit` 共享层级）
5. **Prisma 7 新范式**：`prisma.config.ts` 在根目录（CLI 只在根找）、生成客户端在 `src/generated/`
