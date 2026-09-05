# demo_pkg/greet.py —— 演示包内的普通模块
# 02_packages_venv.py 会 import demo_pkg.greet 来演示"包内模块导入"。
# 也可演示包内相对导入: from . import something(相邻模块用点开头,
# 见主文件第 2 节的注释 —— 相对导入只在"作为包一部分被 import"时合法)。

def greet(name: str) -> str:
    """包内模块提供的问候函数"""
    return f"你好, {name}!(来自 demo_pkg.greet)"
