# CLAUDE.md

## 项目简介

Python Web 记账工具：Streamlit + sqlite3。网页表单添加账目（金额、分类、日期、备注），
按月份和分类筛选查看列表，按 ID 删除，分类统计（柱状图 + 统计表）。

## 技术栈

- 界面：Streamlit
- 存储：SQLite（标准库 sqlite3，无 ORM）
- 统计展示：pandas

## 运行方式

```bash
pip install -e .                      # 首次：安装依赖（可编辑安装，使 import finance 可用）
streamlit run finance/web.py          # 启动，浏览器打开 http://localhost:8501
```

Windows 下也可直接双击项目根目录的 `start.bat` 一键启动（关闭弹出的窗口即停止服务）。

需要 Python 3.10+。依赖 streamlit + pandas，声明在 pyproject.toml。

## 项目结构

```text
finance-cli/
├── pyproject.toml        # 项目配置和依赖声明
├── start.bat             # Windows 一键启动（双击即开，关窗口即停）
├── expenses.db           # SQLite 数据库（首次运行自动生成，不入库）
└── finance/              # Python 包
    ├── __init__.py       # 空文件
    ├── models.py         # Record dataclass
    ├── database.py       # SQLite：建表 + 增删查 + 统计
    └── web.py            # Streamlit 界面入口
```

## 数据设计

表 records：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自动编号 |
| amount | REAL NOT NULL | 金额 |
| category | TEXT NOT NULL | 6 个预设分类之一 |
| date | TEXT NOT NULL | YYYY-MM-DD |
| note | TEXT DEFAULT '' | 备注 |

预设分类：餐饮、交通、购物、娱乐、居住、其他（常量定义在 web.py，
database.py 不感知分类清单，筛选分类由参数传入）。

## 编码规范

- 模块职责单一：database.py 只做数据库操作（函数接收 conn 参数）；
  web.py 只做界面；models.py 定义 Record
- 数据库连接每次新建、用完即关：Streamlit 每次交互都在新线程重跑脚本，
  缓存/复用连接（如 @st.cache_resource）会报 "SQLite objects created in a thread..." 错误
- database.py 的统计返回原始行数据，展示层用 pandas 转换
- 日期一律存 YYYY-MM-DD 文本，月份筛选用 substr(date, 1, 7)
- 界面文案中文，代码、变量、函数名英文
- 新功能先建 Git 分支再开发
- 不自动 git commit / push，用户明确要求才做

## 注意事项

- expenses.db、.venv/、__pycache__/、*.egg-info/ 不入库（.gitignore 已配置）
- finance_cli.egg-info/ 是 pip install -e . 自动生成的构建元数据：别手改、
  删了会自动重建；只有改 pyproject.toml 后需要重跑 pip install -e .
- Streamlit 新版本弃用 use_container_width，改用 width="stretch"（旧参数会打 deprecation 警告）
- 本机 Python 环境：Miniforge conda 环境 py314（Python 3.14.3），项目不用虚拟环境
- 学习项目（VibeCoding），改动以能看懂、能跑通为先
