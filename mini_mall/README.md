# mini_mall 微型电商

从零构建的完整全栈电商 Web 应用（学习项目），可部署到互联网。

- 前端：**Next.js 16.3**（App Router + RSC + Server Actions + Turbopack）
- 样式：**Tailwind CSS 4.3** + shadcn/ui（Base UI）
- 后端：Next.js Server Actions + REST API（管理端）+ Prisma 7 ORM
- 数据库：SQLite（本地，libsql 驱动）→ PostgreSQL（Vercel 部署）
- 认证：**better-auth**（邮箱密码 + 数据库 session + 角色）
- 支付：模拟支付（无真实网关）

## 功能

**买家**：浏览商品（搜索/分类筛选/排序）→ 商品详情 → 注册登录 → 购物车 → 下单 → 模拟支付 → 查看订单 → 会员中心

**会员**（按累计实付升级，只升不降，新订单生效）：
| 等级 | 累计实付 | 后续折扣 |
| --- | --- | --- |
| 心悦1 | ≥ ¥8,000 | 9.8 折 |
| 心悦2 | ≥ ¥80,000 | 9.5 折 |
| 心悦3 | ≥ ¥800,000 | 9 折 |

**管理员**：仪表盘、商品管理（增删改查/上下架）、订单管理（状态流转：发货/完成/取消，取消自动回补库存）、分类管理

## 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 配置环境变量（复制模板并填入）
cp .env.example .env
# DATABASE_URL="file:./dev.db"
# BETTER_AUTH_SECRET=<openssl rand -base64 32 生成>

# 3. 建库 + 种子数据（4 分类 × 16 商品 + 3 个演示账号）
npx prisma migrate dev --name init
npx prisma db seed

# 4. 启动开发服务器
npm run dev        # http://localhost:3000
```

## 演示账号

| 账号 | 密码 | 角色 | 用途 |
| --- | --- | --- | --- |
| admin@minimall.dev | Admin@123456 | ADMIN | 管理端 `/admin` |
| demo@minimall.dev | Demo@123456 | USER | 普通买家（可测会员升级） |
| vip@minimall.dev | Demo@123456 | USER（心悦2） | 会员折扣演示（9.5 折） |

## 常用命令

```bash
npm run dev            # 开发
npm run build          # 生产构建
npm start              # 生产运行（构建后）
npx prisma migrate dev --name <name>   # schema 变更后建迁移
npx prisma db seed     # 种子数据
npx prisma studio      # 可视化数据库
```

## 部署（Vercel）

1. 数据库切 PostgreSQL：`prisma/schema.prisma` 的 `datasource.provider` 改为 `postgresql`，`DATABASE_URL` 指向 Neon/Prisma Postgres 的 `postgresql://` 连接串（**不要用 `prisma://`**，规避 Vercel issue #79063）
2. `src/lib/prisma.ts` 的 adapter 工厂已按 URL 前缀自动分流（`file:` → libsql，其余需补充 `@prisma/adapter-pg`）
3. 环境变量：`DATABASE_URL`、`BETTER_AUTH_SECRET`、`BETTER_AUTH_URL`（线上域名）、`BETTER_AUTH_TRUSTED_ORIGINS`（线上域名）
4. 执行 `npx prisma migrate deploy` 建生产表，然后部署

## 文档

- 完整规格：`C:\Users\q1209\.claude\plans\mini-mall-github-misty-newell.md`
- 开发实录（实际过程/问题/解决方案）：[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)
- 项目约定（架构/命令/账号）：[CLAUDE.md](CLAUDE.md)
