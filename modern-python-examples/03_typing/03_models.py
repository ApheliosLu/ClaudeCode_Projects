# ============================================================================
# 03_models.py  现代 Python 示例集 · 03_typing 类型注解系统
# 主题: 数据建模四件套 —— dataclasses / NamedTuple / TypedDict / Enum
# 解决的问题(基础课):
#   存少量数据"手写 6 个方法"的时代结束了: 定义"几字段一结构"的模型,
#   基础课只有 dict(键易拼错、无类型)和手写类(样板代码爆炸);
#   dataclass 一行生成 __init__/__repr__/__eq__, 其它三件各解决一类数据形态。
# 运行: python 03_models.py
# ============================================================================

from dataclasses import dataclass, field, FrozenInstanceError
from typing import NamedTuple, TypedDict
from enum import Enum, StrEnum, IntEnum

# ---- 1. dataclass 全貌: 声明即模型 ----
# 这是什么: @dataclass —— 类装饰器: 根据类上注解的字段自动生成 __init__、
#           __repr__、__eq__ 等(3.7 起); 对比旧写法: 手写这几样方法每个类
#           ~15 行样板, 字段数一变全要改。
@dataclass
class Student:
    name: str
    score: float
    grade: int = 1                      # 带默认值的字段要放最后

print("1) @dataclass:")
s = Student("小明", 95.5)
s2 = Student("小明", 95.5)
print("   自动 __repr__:", s)
print("   自动 __eq__:", s == s2)
print("   自动 __init__ 与属性访问:", s.name, s.score, f"年级{s.grade}")

# ---- 2. "可变默认值"坑的两个时代 ----
# 这是什么: field(default_factory=list) —— 给字段一个"每次实例化重新调用"的
#           工厂, 让每个实例拿到独立列表。
# 时代一(dataclass): 老教程的经典坑 "tags: list = [] 会让所有实例共享同一列表"——
# 但注意! 现代 Python(3.11 起, 3.12 均如此)的 dataclass 会在类定义时直接报错,
# 语法层面就不许你踩坑(报错信息即教学):
print("\n2) 可变默认值坑(两个时代):")
try:
    @dataclass
    class BadBook:
        tags: list = []               # 反例: 3.11+ 定义时就炸, 不再静默共享
except ValueError as e:
    print("   [dataclass 时代] tags: list = [] → 类定义时就 ValueError:")
    print("     ", e)

# 时代二(普通类默认参数): 这个坑在现代 Python 依然真实存在 —— 默认参数表达式
# 只在 def 时求值一次, 之后所有实例共享同一个 list 对象:
class OldStyle:
    def __init__(self, tags=[]):      # 默认值只求值一次!
        self.tags = tags

oa, ob = OldStyle(), OldStyle()
oa.tags.append("数学")
print("   [普通类时代] def __init__(self, tags=[]): 是共享的 ——")
print("     oa.tags =", oa.tags, "; ob.tags =", ob.tags, "← oa 改了 ob 也跟着! (这才是活着的坑)")

# 正解: dataclass 用 default_factory; 普通类用 tags=None 再在方法里换新列表
@dataclass
class Book:
    title: str
    tags: list = field(default_factory=list)        # 每个实例独立

bk1, bk2 = Book("数据结构"), Book("算法")
bk1.tags.append("计算机")
print("   [正解 default_factory] bk1.tags =", bk1.tags, "; bk2.tags =", bk2.tags, "← 各自独立")

# ---- 3. frozen=True: 不可变模型 ----
# 这是什么: frozen=True —— 生成只读实例(赋值抛 FrozenInstanceError):
#           类似 NamedTuple 的不变性, 用于"配置项/值对象", 天然线程安全。
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1, 2.5)
print("\n3) frozen=True:")
print("   Point(1, 2.5) =", p)
try:
    p.x = 9
except FrozenInstanceError as e:
    print("   改 frozen 字段报错:", e)

# ---- 4. slots=True: 轻量实例(3.10 起) ----
# (3.10 及之前: 手写 __slots__ 才能省内存, 代码烦; 3.10 起 dataclass 一个
#  参数搞定 —— 效应与 01_lang/04 节 __slots__ 相同: 无 __dict__, 省内存)
@dataclass(slots=True)
class CacheEntry:
    key: str
    hits: int = 0

ce = CacheEntry("a", 3)
print("\n4) @dataclass(slots=True)(3.10+):")
print("   CacheEntry =", ce, " ← 与普通 dataclass 用法相同, 但实例更省内存")

# ---- 5. NamedTuple: 元组 + 字段名 ----
# 这是什么: NamedTuple —— 继承元组的不可变记录: 字段名访问 + 元组索引 +
#           解包 = 兼容一切元组用法; 与 dataclass 区别: 不可变、更轻。
class Color(NamedTuple):
    r: int
    g: int
    b: int

c = Color(255, 0, 128)
r_, g_, b_ = c                          # 元组解包照常工作
print("\n5) NamedTuple:")
print("   Color(255, 0, 128): 字段访问", c.r, c.g, c.b,
      "; 索引 c[0]", c[0], "; 解包", r_, g_, b_)
print("   元组身份:", isinstance(c, tuple), " ← 它就是元组, 可进任何元组上下文")

# ---- 6. TypedDict: 有类型安全孔的 dict ----
# 这是什么: TypedDict —— 用来描述"就是字典型数据"(如 JSON 解析结果)的
#           结构: 声明字段名与类型, 静态检查器能校验键名拼写; 运行时仍是
#           普通 dict。total=False 表示字段可缺省。
class Movie(TypedDict):
    title: str
    year: int

class MovieOptional(TypedDict, total=False):
    director: str

m: Movie = {"title": "星际穿越", "year": 2014}
print("\n6) TypedDict:")
print("   m 运行时就是普通 dict:", m, type(m).__name__)
print("   (检查器视角: m['titrle'] 拼写错误会被揪出 —— dict 则抓不着)")

# ---- 7. Enum: 有名字的一组常量 ----
# 这是什么: Enum —— 枚举类型: 把相关常量组织成"类型安全的成员", 成员身份可用
#            == 比较(同一成员是同一对象), 输出名副其实; 3.6 起语法升级。
# 这是什么: StrEnum(3.11+) —— "行为像字符串"的枚举: 成员值即字符串字面量,
#           可直接与 str 用 ==/拼接; (3.11 及之前: 没有 StrEnum, 只能继承 str,
#           自己一个 mixin 或 Enum 值另转)。
# 这是什么: IntEnum —— "行为像整数"的枚举;
class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4

class Colors(StrEnum):
    RED = "red"
    BLUE = "blue"

class Status(IntEnum):
    OK = 200

print("\n7) Enum / StrEnum(3.11+) / IntEnum:")
print("   Direction.NORTH:", Direction.NORTH, "| .name =", Direction.NORTH.name, "| .value =", Direction.NORTH.value)
print("   遍历全部成员:", [d.name for d in Direction])
by_value = {d.value: d for d in Direction}          # 值反查成员的惯用姿势
print("   值反查: by_value[2] =", by_value[2].name)
print("   StrEnum 与字符串互通: Colors.RED == 'red' →", Colors.RED == "red",
      "; Colors.RED.upper() =", Colors.RED.upper())
print("   IntEnum 与整数互通: Status.OK == 200 →", Status.OK == 200)
