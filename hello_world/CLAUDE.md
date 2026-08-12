# CLAUDE.md

## 项目简介

练手项目：原生 Node.js HTTP 服务器 + 纯静态页面。展示"传统 Web 最朴素形态"——
服务器手写、页面手写、无框架、无依赖、无交互。页面显示 "hello ai coding"。

## 技术栈

- 运行时：Node.js（内置 http 模块，零第三方依赖）
- 前端：纯 HTML + 内联 CSS（单页，无 JS）
- 说明：没有 package-lock.json，无需 npm install

## 运行方式

```bash
npm start                 # 等价于 node server.js
# 浏览器打开 http://localhost:3000，Ctrl+C 停止
```

## 项目结构

```text
hello_world/
├── package.json        # 项目配置；scripts.start = "node server.js"
├── server.js           # HTTP 服务器：监听端口、处理请求、返回页面
└── public/
    └── index.html      # 唯一的页面文件（纯静态）
```

## 运行逻辑（什么启动了什么）

1. `npm start` 执行 package.json 中配置的 `node server.js`
2. server.js 用 http 模块创建服务器，监听 localhost:3000
3. 浏览器请求 `/` 或 `/index.html` 时，服务器读取 public/index.html 并返回；
   其他路径返回 404
4. 浏览器渲染 HTML，展示页面

## 与 finance-cli 对照（学习要点）

| | hello_world | finance-cli（记账工具） |
| --- | --- | --- |
| 生态 | Node.js（node server.js） | Python（streamlit run） |
| 端口 | 3000 | 8501 |
| 服务器 | 手写约 30 行（http 模块） | Streamlit 内置 |
| 页面 | 手写 index.html 直接返回 | Python 脚本实时生成 |
| 交互/数据 | 无（纯静态） | 表单 + SQLite 增删查统计 |

结论：Streamlit 把"写服务器 + 写页面 + 处理交互"自动化了，
底层发到浏览器的仍是 HTML+CSS+JS。

## 注意事项

- 纯学习项目（VibeCoding），改动以能看懂、能跑通为先
- 端口 3000 被占用时会启动失败（改 server.js 里的 PORT 常量即可）
- 不自动 git commit / push，用户明确要求才做
