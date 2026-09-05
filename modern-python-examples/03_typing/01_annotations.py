# ============================================================================
# 01_annotations.py  现代 Python 示例集 · 03_typing 类型注解系统
# 主题: 类型注解基础 —— 语法、运行时不强制、常见类型构造
# 解决的问题(基础课):
#   Python 是动态语言: 函数参数传什么类型都不会报错, 错了延迟到运行时
#   才炸。注解给代码加上"意图", 让工具(IDE 提示/mypy 检查)可以在写代码时
#   就发现类型错误 —— 现代工程 Python 的标配(你后面会用到的 FastAPI 等
#   框架也依赖它)。
# 这是什么: 类型注解 —— x: int 这样的标记只是"元数据", 解释器不校验:
#   def f(x: int): ... 里传字符串进去照样运行; 真正**运行时强制**的是
#   isinstance, 真正的静态检查由 mypy/pyright 这类工具完成(本套件零第三方
#   依赖, 故只演示语法与运行时行为)。
# 运行: python 01_annotations.py
# ============================================================================

from typing import Optional, Union, Any, Literal, TypeAlias, get_type_hints

# ---- 1. 语法与运行时真面目 ----
def greet(name: str, times: int = 1) -> str:
    return (f"{name}!" * times)                       # f-string 拼接任何类型都行

print("1) 注解是元数据, 运行时完全不检查:")
print("   greet('小明') =", greet("小明"))
print("   greet(123, 2) =", greet(123, 2), "  ← 传 int 也照常运行 —— 注解不被运行时校验")
print("   函数对象的注解表 __annotations__ =", greet.__annotations__)

# ---- 2. Optional 与 | 联合类型写法 ----
# 这是什么: Optional[int] —— "可以是 int, 也可以是 None"(3.5 老写法);
# (3.10 及之前: 写 Optional[int]; 3.10 起可用 int | None 取代 —— 3.12
#   两种都能用, 新代码推荐 | 语法; 但库文件里 Optional 还是更常见)
def safe_div(a: int, b: int) -> int | None:
    if b == 0:
        return None
    return a // b

print("\n2) 可空类型:")
print("   safe_div(10, 3) =", safe_div(10, 3), "; safe_div(1, 0) =", safe_div(1, 0))
print("   注解是 int | None: 调用方看到类型就该判断 None 分支")

# ---- 3. Union 与 | ----
# 这是什么: Union[X, Y] —— "X 或 Y"的联合类型;
# (3.10 及之前: 只能写 Optional[int] / Union[int, str];
#  3.10 起新增等价写法 int | None / int | str, 3.12 两种都常用, 新代码推荐 |)
def display(value: Union[int, str]) -> str:
    return str(value)

print("\n3) Union[int, str]: 声明'可能是数字也可能是字符串', 但运行时不拦 ——")
print("   传个浮点数进去照样工作:", display(3.14))

# ---- 4. Literal: 只能取指定字面值 ----
# 这是什么: Literal["up", "down"] —— 参数只允许取列出的几个字面常量之一;
#           比如方向枚举、状态字符串, 由静态检查器保证调用方不打错字。
def move(direction: Literal["up", "down"]) -> str:
    return f"向{direction}移动"

print("\n4) Literal:")
print("   move('up') =", move("up"))
print("   move('left') 在静态检查器下会报错(本文件运行时跑得过去, 因为注解不校验)")

# ---- 5. Any: 类型检查的"免检" ----
# 这是什么: Any —— "什么类型都行": 告诉检查器"这里别管我"。
#           用于: 混编的动态数据(如 json 读进来的数据)、插件边界。
#           滥用 Any = 放弃类型保护, 工程上尽量小范围使用。
def process(data: Any) -> Any:
    return data

print("\n5) Any: process('anything') 直接返回:", process("anything"), "/", process(3.14))

# ---- 6. TypeAlias: 给复杂类型起个名字 ----
# 这是什么: TypeAlias —— 别名注解(3.10 起): 把"很长/很复杂"的类型赋予名字,
#           提高可读性复用性; (3.12 起新增 type 语句可完全代替它, 见 08_new/01_py312.py)
UserId = int
Score: TypeAlias = float             # 显式 TypeAlias 写法(老式)
user_id: UserId = 1001               # 别名使用: 注解处写 UserId 即可

print("\n6) TypeAlias: user_id 中 UserId 只是 int 的别名 → 运行时零开销(它就是 int):", type(user_id).__name__)

# ---- 7. 读注解: get_type_hints 解析前向引用 ----
def future_func(x: "list[int]") -> "int":        # 字符串注解(前向引用: 类型还没定义时先写字符串名)
    return len(x)

print("\n7) 读注解:")
print("   原文 __annotations__ 字符串写法:", future_func.__annotations__)
print("   get_type_hints 解析后:", get_type_hints(future_func))
print("   (前向引用是'类里方法引用自家类'等场景的处理手法)")

# ---- 8. 反例: 带参数的泛型别名不能进 isinstance ----
# 反直觉点 1: list[int] / dict[str, int] 这类"带参数的泛型"只是描述类型的
#          构造表达式, 不是运行时真实类型对象 —— isinstance(x, list[int])
#          直接 TypeError("Subscripted generics ...")。
# 反直觉点 2(实测): 例外! (3.10 起) int | None 联合类型反而可直接用于
#          isinstance, 且按成员正确判断 —— 5 年前的老教程会说"一律报错", 新版已改。
print("\n8) isinstance 与泛型:")
try:
    isinstance([1, 2], list[int])
except TypeError as e:
    print("   isinstance([1,2], list[int]) 报错:", e)
print("   isinstance 联合类型(实测合法): None→", isinstance(None, int | None),
      "; 3→", isinstance(3, int | None), "; 's'→", isinstance("s", int | None))

# ---- 9. reveal_type: 只存在于静态检查器 ----
# 注释: reveal_type(x) 是 mypy/pyright 的"显示变量类型"命令, 给工具看;
#       在普通 python 运行时调用会 NameError —— 这里只当不存在注释一句, 不调用。
print("\n9) reveal_type(x) — 只在 mypy/pyright 里存在; 运行时调用会 NameError, 因此本文件不调用")
