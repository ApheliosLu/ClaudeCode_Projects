# mini_mall 部署上线指引（L0 演示版公网部署）

> 目标：把当前功能完备的演示版部署到公网可访问（Vercel + Neon Postgres）。
> 前置：GitHub 账号、Vercel 账号、（可选）Neon 账号。预计半天内完成。

## Step 1：代码适配（本地）

```bash
# 1.1 安装 Postgres 驱动（当前只支持 SQLite 的 file: 前缀，部署硬阻塞）
npm i @prisma/adapter-pg pg
```

1.2 修改 `prisma/schema.prisma`：

```prisma
datasource db {
  provider = "postgresql"   // 原来是 "sqlite"
}
```

1.3 修改 `src/lib/prisma.ts`：把注释掉的 pg 分支启用（删除 throw）：

```ts
if (url.startsWith("file:")) {
  const adapter = new PrismaLibSql({ url });
  return new PrismaClient({ adapter });
}
// 生产：PostgreSQL
const { PrismaPg } = await import("@prisma/adapter-pg");
return new PrismaClient({ adapter: new PrismaPg({ connectionString: url }) });
```

1.4 验证：`npx tsc --noEmit` + `npm run build` + 本地 E2E 回归（本地仍用 `file:` 跑 SQLite，不受影响）→ 提交。

## Step 2：生产数据库（Neon 免费层）

1. 注册 [neon.tech](https://neon.tech) → Create Project（选离你近的 region）
2. 复制连接串，形如：

   ```
   postgresql://user:pass@ep-xxx.region.aws.neon.tech/mini_mall?sslmode=require
   ```

   （注意：不要用 `prisma://` 开头的 Data Proxy URL——Vercel 上有已知问题）
3. 本地建生产表（连远端库执行迁移）：

   ```bash
   DATABASE_URL="postgresql://..." npx prisma migrate deploy
   ```

## Step 3：推送到 GitHub

当前代码在 ClaudeCode_Projects 仓库的 mini_mall/ 子目录，需要**独立仓库**供 Vercel 导入：

```bash
# 在 GitHub 新建空仓库（如 mini-mall），然后：
git subtree split --prefix=mini_mall -b deploy   # 把 mini_mall 历史拆到 deploy 分支
git remote add github https://github.com/<你的用户名>/mini-mall.git
git push github deploy:main
```

## Step 4：Vercel 部署

1. vercel.com → Add New → Project → Import 刚推送的 mini-mall 仓库
2. Framework 自动识别为 Next.js，**构建命令保持默认**（postinstall 已配 `prisma generate`）
3. 配置环境变量（Settings → Environment Variables，Production 环境）：

   | 变量 | 值 |
   | --- | --- |
   | `DATABASE_URL` | Step 2 的 Neon 连接串 |
   | `BETTER_AUTH_SECRET` | `openssl rand -base64 32` 生成 |
   | `BETTER_AUTH_URL` | `https://<项目名>.vercel.app` |
   | `BETTER_AUTH_TRUSTED_ORIGINS` | `https://<项目名>.vercel.app` |

4. Deploy，等待构建完成（首次约 2-3 分钟）

## Step 5：上线检查

1. 访问部署域名：
   - 首页/商品列表/搜索/详情正常
   - 注册新账号 → 登录 → 加购 → 下单 → 支付（模拟）→ 订单
   - 管理端：部署后**立即**改 admin 密码或删演示账号（seed 密码在 git 公开）
2. 自定义域名（可选）：Settings → Domains → 绑定你的域名，同步更新 `BETTER_AUTH_URL` / `TRUSTED_ORIGINS`
3. 后续代码更新：push 到 GitHub 即自动触发 Vercel 重新部署；**schema 变更后**需在本地跑 `DATABASE_URL=<生产串> npx prisma migrate deploy`

## 常见问题

- **部署后登录失败**：检查 `BETTER_AUTH_URL`/`TRUSTED_ORIGINS` 是否与访问域名完全一致（含 https://）
- **500 错误**：Vercel 日志（Deployments → 对应版本 → Logs）定位；常见为环境变量缺失
- **本地与生产数据隔离**：本地 `.env` 保持 `file:` SQLite；生产在 Vercel 配 Postgres——代码按 URL 前缀自动分流，互不干扰
- **费用**：Vercel Hobby（免费）+ Neon 免费层足够演示；注意免费层数据库闲置会休眠（再次访问需等唤醒）
