// better-auth HTTP 处理器（全部认证端点挂载在 /api/auth/*）
import { toNextJsHandler } from "better-auth/next-js";
import { auth } from "@/lib/auth";

export const { GET, POST } = toNextJsHandler(auth);
