// better-auth 实例（认证核心）
// 注意：模块顶层不得调用 next/headers（seed 脚本 tsx 环境需复用本模块），
// getSession 仅在调用时读取 headers
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "@/lib/prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "sqlite", // 部署切 Postgres 时改 "postgres"
  }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 天
  },
  user: {
    additionalFields: {
      role: {
        type: "string",
        input: false, // 客户端注册时不可传，服务端赋值
        defaultValue: "USER",
      },
      membershipLevel: {
        type: "number",
        input: false,
        defaultValue: 0,
      },
      accumulatedSpentCents: {
        type: "number",
        input: false,
        defaultValue: 0,
      },
    },
  },
  baseURL: process.env.BETTER_AUTH_URL ?? "http://localhost:3000",
  trustedOrigins: process.env.BETTER_AUTH_TRUSTED_ORIGINS?.split(",") ?? [],
});
