// Prisma 7 配置（prisma.config.ts）
// 注意：必须显式加载 dotenv，CLI 不会自动读取 .env
import "dotenv/config";
import { defineConfig } from "prisma/config";

export default defineConfig({
  schema: "prisma/schema.prisma",
  datasource: {
    url: process.env.DATABASE_URL!,
  },
  migrations: {
    seed: "tsx prisma/seed.ts",
  },
});
