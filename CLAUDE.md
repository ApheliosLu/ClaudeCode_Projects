# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目性质

学习用 Claude Code 进行 VibeCoding 的工作目录。

**重要：当前仓库除 `.claude/settings.json` 与本文档外没有任何代码**——没有 package.json、src/ 或其他源文件，因此不存在可构建/可测试的代码，没有构建、lint、测试命令。git 历史仅一个初始提交（260809）。

## 规划中的技术栈（尚未落地）

- 前端：Next.js 14 + TypeScript + Tailwind CSS
- 后端：Next.js API Routes
- 数据库：Prisma + SQLite
- 部署：Vercel

开始搭建时（如 `create-next-app`）按上述栈初始化，落地后在文档中补充真实的构建与开发命令。

## 编码规范（规划中，代码落地后适用）

- 函数式组件 + React Hooks
- 组件文件 PascalCase（如 BookmarkCard.tsx），工具函数 camelCase
- API 路由统一返回 `{ success: boolean, data?: any, error?: string }`
- 数据库操作通过 Prisma Client

## 注意事项

- `prisma/dev.db`（SQLite）与 `.env` 不入库
- 新功能先建 Git 分支再开发
- 项目级权限配置见 `.claude/settings.json`：允许 Read/Write、`npm *`、`git *`、`node *`，拒绝 `rm -rf *`
- 全局沟通与 Git 规则见 `~/.claude/CLAUDE.md`
