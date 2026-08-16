import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // better-sqlite3 是原生 addon，Turbopack 不打包（规避 Node 24 Windows 下的原生崩溃）
  serverExternalPackages: ["better-sqlite3"],
};

export default nextConfig;
