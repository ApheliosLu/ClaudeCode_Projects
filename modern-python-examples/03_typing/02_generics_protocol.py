# ============================================================================
# 02_generics_protocol.py  现代 Python 示例集 · 03_typing 类型注解系统
# 主题: 泛型(TypeVar/Generic)、协议(Protocol)、类型窄化(TypeGuard)、
#       参数签名保留(ParamSpec)
# 解决的问题(基础课):
#   想写"装任意类型的容器"或者"描述接口让多个无关类满足"—— 泛型让类型
#   一段代码自适应多种类型; 协议让"鸭子类型"这件事可以被静态检查器确认;
#   这些是现代库(如 FastAPI 的 Request 抽象、pydantic 的类型系统)的地基。
# 注意: 与 01_annotations.py 相同, 运行时统统只是元数据; 本文件演示语法
#       结构 + 运行时行为, 静态校验需要 mypy/pyright(README 指引)。
# 运行: python 02_generics_protocol.py
# ============================================================================

import functools
from typing import TypeVar, Generic, Protocol, TypeGuard, ParamSpec, Callable

# ---- 1. TypeVar + Generic: 自研泛型容器 ----
# 这是什么: TypeVar("T") —— "类型变量", 泛型里的占位符: 一处声明, 使用处被
#           替换成实际类型(int/str/自定义类)。运行时只是一个哨兵对象, 无约束。
# 这是什么: class Box(Generic[T]) —— 把类声明成泛型: T 出现在方法参数/返回,
#           检查器就能推导 Box(42) 是 Box[int], 取回 get() 的类型推断为 int。
T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T):
        self._value = value

    def get(self) -> T:
        return self._value

    def put(self, new: T) -> None:                  # 泛型方法的参数类型也随 T 走
        self._value = new

print("1) 泛型类 Box[T]:")  # → 1) 泛型类 Box[T]:
b_int = Box(42)                                     # 检查器推导 Box[int]
b_str = Box("你好")
print("   Box(42).get() =", b_int.get(), type(b_int.get()).__name__)  # →    Box(42).get() = 42 int
print("   Box('你好').get() =", b_str.get(), " ← 同一类定义, 装两种类型")  # →    Box('你好').get() = 你好  ← 同一类定义, 装两种类型
b_int.put(99)
print("   b_int 换装 99 →", b_int.get())  # →    b_int 换装 99 → 99

# ---- 2. TypeVar 带 bound: 限制类型的天花板 ----
# 这是什么: TypeVar(..., bound=Base) —— 声明"类型变量 T 只能是 Base 或其子类";
#           用途: 泛型函数里要调用 T 的某些方法, 必须有保证 → 绑定基类。
class Shape:
    def area(self) -> float:
        raise NotImplementedError

class CircleShape(Shape):
    def __init__(self, r): self.r = r
    def area(self) -> float:
        return 3.14159 * self.r ** 2

ShapeT = TypeVar("ShapeT", bound=Shape)             # T 必须可调用 area()

def total_area(shapes: list[ShapeT]) -> float:
    return sum(s.area() for s in shapes)            # 有 bound 检查器才允许调用 area()

print("\n2) TypeVar bound(上限约束):")  # → 2) TypeVar bound(上限约束):
print("   total_area([CircleShape(1), CircleShape(2)]) =",
      round(total_area([CircleShape(1), CircleShape(2)]), 2))
      # 输出:    total_area([CircleShape(1), CircleShape(2)]) = 15.71
print("   (检查器视角: 传 list[CircleShape] 合法, 传 list[int] 会被拒 —— 因为 int 无 area)")
# 输出:    (检查器视角: 传 list[CircleShape] 合法, 传 list[int] 会被拒 —— 因为 int 无 area)

# ---- 3. Protocol: 结构化类型(鸭子类型的静态版) ----
# 这是什么: Protocol —— "只要长这样就算这个类型"(不需要继承): 声明若干
#           方法/属性作契约, 任何实现这些名字的类自动满足它; 这是在库代码里
#           定义"我的函数只需要这个接口"的解耦手段, 是鸭子类型(能走路游水=鸭子)
#           的静态检查化身。
class Drawable(Protocol):
    def draw(self) -> str: ...

class CircleArt:
    def draw(self) -> str:
        return "圆"

class SquareArt:
    def draw(self) -> str:
        return "方"

class Duck:
    def quack(self) -> str:
        return "嘎"                                  # 有 quack 没 draw → 不符合 Drawable

def render_all(items: list[Drawable]) -> None:       # 参数写成协议
    for it in items:
        print("   绘:", it.draw())
        # 列表里每个对象各输出一行:
        #    绘: 圆
        #    绘: 方

print("\n3) Protocol(结构类型):")  # → 3) Protocol(结构类型):
render_all([CircleArt(), SquareArt()])              # 无需继承 Drawable, 结构匹配即可
print("   (把 Duck 塞进 render_all → 静态检查报错; 运行时注解无效, 故此演示只写注释)")
# 输出:    (把 Duck 塞进 render_all → 静态检查报错; 运行时注解无效, 故此演示只写注释)

# ---- 4. TypeGuard: 类型窄化函数 ----
# 这是什么: TypeGuard[X] —— 3.10+ 的窄化(收窄)声明: 函数返回 bool,
#           但返回 True 时静态检查器认为"参数就是 X 了"; 常用于"宽类型
#           (如 list[int] | str)经它一测, 分支里变成窄类型(list[int])",
#           后面就不用 isinstance 反复判了。
def is_int_list(data: list[int] | str) -> TypeGuard[list[int]]:
    return isinstance(data, list) and all(isinstance(x, int) for x in data)

def summarize(data: list[int] | str) -> str:
    if is_int_list(data):                            # True → data 被窄化为 list[int]
        return f"整数列表: 共 {len(data)} 个, 和 {sum(data)}"
    return f"字符串: {data.capitalize()}"

print("\n4) TypeGuard(3.10+) 窄化:")  # → 4) TypeGuard(3.10+) 窄化:
print("   ", summarize([1, 2, 3]))  # →     整数列表: 共 3 个, 和 6
print("   ", summarize("hello"))  # →     字符串: Hello

# ---- 5. ParamSpec: 保留原函数签名的装饰器类型 ----
# 这是什么: ParamSpec —— "把函数签名的参数部分整体当一个类型"捕获下来
#           (配合 Callable[P, T] 使用): 装饰器场景下, 若不捕获参数,
#           包装后的函数对检查器而言"什么参数都行"(类型信息丢失);
#           P.args/P.kwargs 分别引用捕获到的位置参数/关键字参数形态。
P = ParamSpec("P")
R = TypeVar("R")

def logger_deco(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"   [记录] 调用 {func.__name__}")  # →    [记录] 调用 power
        return func(*args, **kwargs)
    return wrapper

@logger_deco
def power(base: int, exp: int) -> int:
    return base ** exp

print("\n5) ParamSpec(3.10+) 装饰器签名保留:")  # → 5) ParamSpec(3.10+) 装饰器签名保留:
print("   power(2, 3) =", power(2, 3))  # →    power(2, 3) = 8
print("   (检查器视角: power 的参数/返回类型与原名一致 —— 因 ParamSpec 把签名传住了)")
# 输出:    (检查器视角: power 的参数/返回类型与原名一致 —— 因 ParamSpec 把签名传住了)
