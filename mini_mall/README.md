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
| <admin@minimall.dev> | Admin@123456 | ADMIN | 管理端 `/admin` |
| <demo@minimall.dev> | Demo@123456 | USER | 普通买家（可测会员升级） |
| <vip@minimall.dev> | Demo@123456 | USER（心悦2） | 会员折扣演示（9.5 折） |

## 常用命令

```bash
npm run dev            # 开发（热更新）
npm run build          # 生产构建
npm start              # 生产运行（构建后）
npx prisma migrate dev --name <name>   # schema 变更后建迁移
npx prisma db seed     # 种子数据
npx prisma studio      # 可视化数据库
```

## 启动与停止服务器（Windows）

```bash
# 启动（在项目根目录执行）
npm start              # 生产模式（快、稳，日常用这个）
npm run dev            # 开发模式（改代码自动热更新）
# 然后浏览器访问 http://localhost:3000

# 停止（先找到进程 PID）
netstat -ano | grep ":3000" | grep LISTENING   # 输出最后一列是 PID
taskkill //F //PID <PID>                        # Git Bash 里用双斜杠
taskkill /F /PID <PID>                          # cmd / PowerShell 里用单斜杠
# 或任务管理器：Ctrl+Shift+Esc → 详细信息 → 结束占用最大的 node.exe
```

> 注意：关机后服务器不会自动启动，需重新 `npm start`。数据（dev.db）和构建产物（.next）都在磁盘上，不会丢失。开机自启可把启动命令放进 Windows 启动文件夹（`shell:startup`）或使用 PM2。

### 终端语法对照（后台启动 / 进程操作）

`npm start` 是**前台进程**：直接关掉终端窗口 = 服务停止。想"关窗口但服务继续跑"用后台方式：

| 操作 | Git Bash | cmd | PowerShell |
| --- | --- | --- | --- |
| 后台启动 | `nohup npm start &` | `start /b npm start` | `Start-Process cmd -ArgumentList "/c","npm start" -WindowStyle Hidden` |
| 杀进程 | `taskkill //F //PID x` | `taskkill /F /PID x` | `taskkill /F /PID x` |

> 坑：`start` 是 cmd 专属语法，PowerShell 里它是 `Start-Process` 的别名，直接输 `start /b ...` 会报"找不到位置形式参数"。在 PowerShell 里先输入 `cmd` 回车进入命令提示符模式，再执行 cmd 语法即可。
> 长期运行建议用 PM2：`pm2 start "npm start" --name mini-mall` + `pm2 save` + `pm2 startup`（崩溃自动重启 + 开机自启）。

## 部署（Vercel）

1. 数据库切 PostgreSQL：`prisma/schema.prisma` 的 `datasource.provider` 改为 `postgresql`，`DATABASE_URL` 指向 Neon/Prisma Postgres 的 `postgresql://` 连接串（**不要用 `prisma://`**，规避 Vercel issue #79063）
2. `src/lib/prisma.ts` 的 adapter 工厂已按 URL 前缀自动分流（`file:` → libsql，其余需补充 `@prisma/adapter-pg`）
3. 环境变量：`DATABASE_URL`、`BETTER_AUTH_SECRET`、`BETTER_AUTH_URL`（线上域名）、`BETTER_AUTH_TRUSTED_ORIGINS`（线上域名）
4. 执行 `npx prisma migrate deploy` 建生产表，然后部署

## 文档

- 完整规格：`C:\Users\q1209\.claude\plans\mini-mall-github-misty-newell.md`
- 开发实录（实际过程/问题/解决方案）：[docs/DEVELOPMENT_LOG.md](docs/DEVELOPMENT_LOG.md)
- 项目约定（架构/命令/账号）：[CLAUDE.md](CLAUDE.md)
