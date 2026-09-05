# ============================================================================
# 02_packages_venv.py  现代 Python 示例集 · 09_tools 工程工具
# 主题: 模块工程 —— 包(package)的导入机制与虚拟环境(venv)
# 解决的问题(基础课):
#   基础课程序都是单文件。真实项目一拆多文件: 怎么互相 import?
#   "包"是什么? 不同项目依赖的库版本打架怎么办(venv 隔离)?
#   本文件用旁边的 demo_pkg/ 演示包导入, 用 sys.prefix 验证 venv 状态。
# 运行: python 02_packages_venv.py
# ============================================================================

import sys

# stdout 行缓冲: 保教学输出顺序(unittest/网络输出混流时尤其需要)
sys.stdout.reconfigure(line_buffering=True)

# ---- 1. 包内模块的绝对导入 ----
# 这是什么: import demo_pkg.greet —— 把 demo_pkg 目录(有 __init__.py 标记)
#           当成命名空间, 从里面导入 greet 模块。这就是"包"的日常用法:
#           目录套目录, 点号分层, import 路径与目录结构一一对应。
import demo_pkg.greet
from demo_pkg import greet as short           # from 包 import 模块 等价写法

print("1) 包内模块导入(demo_pkg/ 就在本文件同目录):")
print("   demo_pkg.greet.greet('阿黎'):", demo_pkg.greet.greet("阿黎"))
print("   short.greet('阿黎')         :", short.greet("阿黎"))
print("   模块文件:", demo_pkg.greet.__file__)

# ---- 2. 相对导入与 __package__: 为什么"跑单文件"和"当模块跑"不一样 ----
# 这是什么: 相对导入(from . import x)依赖 __package__(当前所在的包名):
#           ① 用 `python demo_pkg/greet.py` 直接跑时, 脚本被当"顶层模块",
#              __package__ 为空 → 相对导入报错 "attempted relative import";
#           ② 用 `python -m demo_pkg.greet` 跑时, 解释器把它当包成员,
#              __package__ = "demo_pkg", 相对导入才合法。
#           结论: 包内部互相引用用相对导入 + 一律 `python -m 包.模块` 运行。
print("\n2) __package__ 机制(一句话):")
print("   当前文件 __package__:", repr(__package__))
print("   → 直接跑本文件时它是空(顶层脚本); python -m 跑包成员时才有值")
print("   (demo_pkg 内注释里演示了相对导入写法 —— 需 -m 方式运行才合法)")

# ---- 3. 一个"半真"的包内调用(包与普通模块的边界) ----
# 这是什么: 把"功能函数"留在包里、把"演示逻辑"留在本文件 —— 这是真实项目
#           的组织法: 库代码不 print, 由调用方(本文件)负责展示。
from demo_pkg.greet import greet as pkg_greet
print("\n3) 功能与演示分离:")
print("   pkg_greet('世界'):", pkg_greet("世界"))

# ---- 4. venv 虚拟环境: 是什么 + 标准操作序列 ----
# 这是什么: venv —— 每个项目一套独立的 site-packages: 项目 A 要 requests 2.x、
#           项目 B 要 3.x 也不打架(装进各自 .venv, 而不是全局)。标准库自带。
#   Windows 与 Linux 的标准操作序列(注释即文档, 不必在本文件内执行):
#     Windows:  python -m venv .venv
#               .venv\Scripts\activate
#               python -m pip install requests      # 装进本项目的 .venv
#     Linux/mac: python -m venv .venv
#                source .venv/bin/activate
#                python -m pip install requests
#   判断当前是否在 venv 里: 看 sys.prefix 是否指向 venv 目录(区别于
#   sys.base_prefix —— 创建 venv 的"母解释器"路径)。
print("\n4) venv 状态探测:")
print("   sys.prefix       :", sys.prefix)
print("   sys.base_prefix  :", sys.base_prefix)
in_venv = sys.prefix != sys.base_prefix
print("   当前在 venv 中?", in_venv)
print("   → 本文件由系统 python 直接跑(未激活 venv); 若先激活 .venv 再跑,")
print("     则 sys.prefix 会指向 .venv 目录, 上方判断变 True —— 装包互不污染")
