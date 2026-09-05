# ============================================================================
# 02_py313.py  现代 Python 示例集 · 08_new 版本新特性
# 主题: Python 3.13 实装特性总览(GIL 探测/错误消息/TypeIs/ReadOnly/JIT)
# 解决的问题(基础课):
#   3.13 的更新大多是"内功"(性能、错误提示、类型系统), 普通代码写法
#   几乎不变 —— 但你该认得这些名词, 免得在文档/讨论里被吓到。
#   本文件按本机 3.14.3 实测落笔, 标 3.13 的特性在 3.14 均存在。
# 运行: python 02_py313.py
# ============================================================================

import sys

# stdout 行缓冲: 教学 print 与 traceback(走 stderr)顺序对位(同系列惯例)
sys.stdout.reconfigure(line_buffering=True)

# ---- 1. sys._is_gil_enabled(): 我跑的到底是哪种构建? ----
# 这是什么: GIL 与自由线程 —— 默认 CPython 有全局解释器锁(GIL, 见 04/01);
#           3.13 起官方支持"自由线程构建"(去掉 GIL 的实验性构建, 又称
#           free-threaded / no-GIL)。同一份代码在不同构建下并发行为不同,
#           所以要先探测。sys._is_gil_enabled() 返回 True = 默认带 GIL。
print("1) 当前解释器 GIL 状态:")
print("   sys._is_gil_enabled():", sys._is_gil_enabled())
print("   → True: 默认 GIL 构建(3.14 实测; 若 False 则是自由线程构建)")
print("   Python 版本:", sys.version.split()[0])

# ---- 2. 错误消息增强: 拼写建议帮你快速定位 ----
# 这是什么: 报错消息可读性 —— 3.10 起 NameError/AttributeError 会给
#           "Did you mean ...?" 拼写建议; 3.13 继续大规模改进各种内置
#           错误的提示文本(把"常见坑"直接写进报错)。注意实测: 建议是
#           traceback 打印时附加的, str(异常) 本身没有 —— 所以用
#           traceback.print_exc() 展示。下面故意写错名:
import traceback
unspellable = 42
try:
    print(unsplleable)                        # 故意拼错 → 触发 NameError
except NameError:
    print("\n2) 错误消息的拼写建议(3.13 增强的错误提示同族):")
    traceback.print_exc()
    print("   ↑ traceback 尾行直接给出建议写法 —— 少一行猜谜时间")

# ---- 3. typing.TypeIs(3.13+): 类型窄化的精确版 ----
# 这是什么: TypeIs —— 3.13+ 的类型谓词注解: 标记"函数返回 True ⟹ 参数就是
#           该类型", 让静态检查器在 if 分支内把变量窄化。和 TypeGuard
#           (3.10+) 的差别: TypeGuard 窄化到"所标类型", TypeIs 允许窄化到
#           更精确的子类型/字面量(isinstance 语义), 更贴近真实检查函数。
from typing import TypeIs, TypeGuard

def is_str_list(x: object) -> TypeIs[list[str]]:   # 3.13+: 窄化断言
    return isinstance(x, list) and all(isinstance(i, str) for i in x)

def is_str_guard(x: object) -> TypeGuard[list[str]]:  # 3.10+: 宽泛断言
    return isinstance(x, list) and all(isinstance(i, str) for i in x)

print("\n3) TypeIs(3.13+) 与 TypeGuard(3.10+) 对照:")
for checker, tag in [(is_str_list, "TypeIs  "), (is_str_guard, "TypeGuard")]:
    print(f"   {tag}: 对 ['a', 'b'] → {checker(['a', 'b'])}; 对 [1, 2] → {checker([1, 2])}")
print("   两者运行时行为一致 —— 区别只在静态检查器能窄化多准(见注释)")
print("   新代码用 TypeIs(3.13+); 要兼容旧版本才退到 TypeGuard")

# ---- 4. typing.ReadOnly(3.13+): TypedDict 字段只读标注 ----
# 这是什么: ReadOnly —— 3.13+ 在 typing 内置(TypedDict 的只读字段):
#           标注后静态检查器禁止对该字段赋值(运行时不拦截, 同属检查器契约)。
from typing import ReadOnly, TypedDict

class Movie(TypedDict):
    title: str
    year: int
    rating: ReadOnly[float]                   # 只读: 检查器禁止事后改 rating

m: Movie = {"title": "星际穿越", "year": 2014, "rating": 8.7}
print("\n4) ReadOnly TypedDict 字段(3.13+):")
print("   构造实例:", m)
print("   读字段正常: rating =", m["rating"])
print("   → 若代码里写 m['rating'] = 9.0, 静态检查器报错(运行时照常)")

# ---- 5. dbm.sqlite3 与 JIT: 两句背景知识(不展开) ----
# 这是什么: dbm —— 3.13 起标准库 dbm 的默认后端改为 sqlite3(原 gdbm/ndbm),
#           你 import dbm 照常用, 文件格式变了也不用关心 —— 知道即可。
# 这是什么: JIT —— 3.13 引入实验性 JIT(实时编译, PEP 744), 随构建版本可选;
#           3.14 继续打磨。对普通用户是透明的性能改进, 用法零变化。
print("\n5) 背景名词(见注释, 无需代码):")
print("   dbm.sqlite3 后端(3.13 起默认) / 实验性 JIT(PEP 744) —— 普通用户零感知")
