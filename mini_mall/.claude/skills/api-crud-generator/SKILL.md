---
name: api-crud-generator
version: 2.0
description: 根据 Prisma 模型生成标准的管理后台 CRUD（Server Actions + 管理页面），遵循 mini_mall 项目架构约定
trigger: ["生成CRUD", "生成接口", "生成管理页面", "商品管理", "分类管理"]
---

# API CRUD 生成器（mini_mall 适配版）

## 功能说明
根据指定的 Prisma 模型，生成符合 mini_mall 项目架构的管理后台 CRUD 代码：
1. **Server Actions**（`src/lib/actions/{model}.ts`）：create / update / delete / toggle（软删除）
2. **前端管理页面**（`src/app/(admin)/{model}/`）：数据列表页（Server Component 直连 Prisma）+ 创建/编辑表单（客户端组件）

> 本项目**不建 REST API 层**：读 = Server Component 直连 Prisma，写 = Server Action。
> 认证走 better-auth（`src/lib/auth.ts`），不要为 User/Session 等认证表生成 CRUD。

## 执行步骤

### 第 1 步：确认模型信息
询问用户：
- 要生成的模型名称（如 Product、Category）
- 页面路由（如 /admin/products）
- 模型是否有 `isActive`（软删除）、金额字段（整数分）

### 第 2 步：生成 Server Actions（`src/lib/actions/{model}.ts`）
每个 action 遵循固定模式：

```
"use server"
requireAdmin()            // ① 鉴权：管理端操作必须 ADMIN（guards.ts）
Zod safeParse             // ② 输入校验（validators.ts 或同文件定义 schema）
Prisma 事务                // ③ 数据操作
revalidatePath             // ④ 刷新页面缓存
返回 { error: string } | 数据对象
```

生成的 action 清单：
1. `create{Model}(input)` — POST 语义，返回 `{ id }`
2. `update{Model}(id, input)` — PUT 语义，返回 `{ id }`
3. `delete{Model}(id)` — 有 `isActive` 字段 → `isActive: false`（软删除，保外键）；无该字段 → 先校验无引用再物理删
4. `toggle{Model}(id)` — 仅当有 `isActive`：翻转上架/下架

### 第 3 步：生成前端管理页面（`src/app/(admin)/{model}/`）
- 列表页 `page.tsx`：**Server Component**，`await prisma.{model}.findMany(...)`，渲染 shadcn Table
- 新建页 `new/page.tsx` + 编辑页 `[id]/edit/page.tsx`：客户端表单组件（shadcn Input/Select/Textarea），提交调用第 2 步的 action
- 表格行内操作："编辑"链接、"删除/下架"按钮（带 Dialog 确认）
- TailwindCSS + shadcn/ui 样式，全部中文文案

### 第 4 步：确认并验证
- 列出所有生成的文件
- 提醒用户：若模型有变更需 `npx prisma generate`；若改了 schema 需 `npx prisma migrate dev`
- 给出测试方法（登录 admin → 访问管理页 → 增删改查）

## 项目约定（必须遵守）
- **鉴权**：每个 action 开头 `requireAdmin()`；页面布局由 `(admin)/layout.tsx` 兜底，但 action 内校验是最终防线（proxy 可被绕过）
- **错误格式**：失败返回 `{ error: string }`（不抛异常），成功返回数据对象
- **金额**：一律整数分（`*Cents` 字段），展示用 `formatCents()`，元字符串入参用 `toCents()` 转换
- **校验**：Zod v4，`safeParse` 失败返回第一条错误信息
- **密码/敏感字段**：永不返回；认证表（User/Session/Account/Verification）由 better-auth 管理，不生成 CRUD
- **快照**：Order/OrderItem 等历史数据模型不直接编辑，走状态流转 action
