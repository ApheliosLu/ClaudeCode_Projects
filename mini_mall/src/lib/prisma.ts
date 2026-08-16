// Prisma 客户端单例 + driver adapter 工厂
// 本地 file: → libsql（替代 better-sqlite3：规避 Node 24 下原生模块崩溃）
// 部署（postgresql://）→ pg（Vercel 部署前补充）
import { PrismaClient } from "@/generated/prisma/client";
import { PrismaLibSql } from "@prisma/adapter-libsql";

function createPrismaClient(): PrismaClient {
  const url = process.env.DATABASE_URL!;
  if (url.startsWith("file:")) {
    // 本地开发：SQLite（libsql 驱动，无原生 addon 崩溃问题）
    const adapter = new PrismaLibSql({ url });
    return new PrismaClient({ adapter });
  }
  // 部署环境：PostgreSQL（需安装 @prisma/adapter-pg + pg）
  // 部署前按此补充：
  // const { PrismaPg } = await import("@prisma/adapter-pg");
  // return new PrismaClient({ adapter: new PrismaPg({ connectionString: url }) });
  throw new Error("DATABASE_URL 暂只支持 file: 前缀（本地 SQLite）；Postgres 适配器待部署时补充");
}

// dev 热重载下防止连接池耗尽：globalThis 单例
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
