# ============================================================================
# 04_descriptors_slots.py  现代 Python 示例集 · 01_lang 语言核心
# 主题: 描述符(descriptor)与 __slots__ —— 属性访问的底层机制
# 解决的问题(基础课):
#   给"年龄不能为负、价格必须是数字"这类属性做校验, 只能在 __init__ 里
#   手写 if 判断 —— 每个类写一遍; 想每处访问都拦一遍就要把属性改成
#   方法; 而且普通类每个实例都带一个 __dict__ 字典(装属性), 数据量大时
#   内存很浪费。descriptor 与 __slots__ 分别解决这两个问题。
# 这是什么: 描述符 —— 实现了 __get__/__set__/__delete__ 的类, 以类属性存在
#   时"属性访问被接管": 实例.属性 不再是查字典, 而是调用描述符协议方法。
#   实现 __set__ 的叫"数据描述符"(优先于实例字典), 不实现的叫"非数据描述符"。
#   最熟悉的描述符标准件: property(就是写了 fget/fset/fdel 的描述符)。
# 运行: python 04_descriptors_slots.py
# ============================================================================

import sys

# ---- 1. property: 把"方法"伪装成属性(内置描述符) ----
# 这是什么: property —— 属性访问的"标准件": fget 定义读, fset 定义写, fdel 定义删;
#           魔法在于: 属性名 .x 的赋值/读取自动变成调用这些函数,
#           所以"从 _value 里读"的变量名变换都被封装, 外层看不出是函数。
class Celsius:
    def __init__(self, c):
        self._celsius = 0                 # 真正的存储, 下划线=内部约定
        self.celsius = c                  # 走 property setter 校验

    @property                             # 读: celsius 返回派生的有校验的值
    def celsius(self):
        return self._celsius

    @celsius.setter                       # 写: 赋值 = 校验后存底层变量
    def celsius(self, value):
        if value < -273.15:
            raise ValueError(f"{value}°C 低于绝对零度")
        self._celsius = value

    @property                             # 只读属性: 只有 getter, 没有 setter
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

t = Celsius(25)
print("1) property 实况:")
print("   t.celsius   =", t.celsius)
print("   t.fahrenheit =", round(t.fahrenheit, 2), "   # 派生属性, 没有 setter 就不能赋值")
try:
    t.fahrenheit = 50
except AttributeError as e:
    print("   给只读属性赋值报错:", e)

# ---- 2. 通用描述符: 防负数校验器(一次性写好, 处处复用) ----
# 这是什么: __set_name__ —— 3.6+ 新增钩子: 此类属性被放进某个类时自动调用,
#           把"我挂在哪个属性名下"告诉描述符, 省去手写 self.name。
class PositiveNumber:
    """所有属性值必须是非负数的描述符 —— 校验逻辑写一次, 复用无数类"""
    def __set_name__(self, owner, name):           # 自动获知属性名
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                            # 类上访问(类名.x)返回描述符本体
        return obj.__dict__.get(self.name, 0)      # 值存在实例字典里

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} 必须是数字")
        if value < 0:
            raise ValueError(f"{self.name} 不能为负数")
        obj.__dict__[self.name] = value            # 真正的值存实例字典

class Product:
    price = PositiveNumber()                       # 属性声明 = 装描述符
    stock = PositiveNumber()                       # 再来一个, 逻辑零复制

p = Product()
print("\n2) 自定义描述符 PositiveNumber:")
p.price = 99.9
p.stock = 42
print("   p.price =", p.price, "; p.stock =", p.stock)
try:
    p.price = -5
except ValueError as e:
    print("   给 price 赋负数 →", e)
try:
    p.price = "abc"
except TypeError as e:
    print("   给 price 赋字符串 →", e)

# ---- 3. 数据描述符 vs 实例字典: 谁优先? ----
# 这是什么: "数据描述符"(带 __set__)在属性查找中优先级高于实例 __dict__,
#           这意味着: 即使你在实例字典里强行塞同名属性, 读到的还是描述符算出来的。
class EvenOdd:
    """奇偶性只看 bits, 每次读都现算 —— 用来证明优先级"""
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        raw = obj.__dict__.get("value", 0)         # 读真实存储
        return "偶数" if raw % 2 == 0 else "奇数"

    def __set__(self, obj, val):                   # 有 __set__ = 数据描述符
        obj.__dict__["value"] = val

class Num:
    describe = EvenOdd()

n = Num()
n.describe = 4
n.__dict__["describe"] = "实例字典里塞的假值"        # 强行污染实例字典
print("\n3) 数据描述符优先于实例字典: n.describe =", n.describe, "  # 读到的是描述符结果")
print("   -- 没写 __set__ 的'非数据描述符'则反过来: 实例字典优先(此处不演示, 记结论即可)")

# ---- 4. __slots__: 没有 __dict__ 的轻量实例 ----
# 这是什么: __slots__ —— 类中的属性名列表, 声明"实例只用这些属性":
#           (a) 不再给每个实例建 __dict__ 字典 → 大量对象时省内存(可能几 MB→几十 MB);
#           (b) 拼错属性名立即 AttributeError(普通会静默新建一个属性).
def free_disk_space_demo():                        # 辅助函数, 不与 __slots__ 互动
    pass

class Slotted:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

class Normal:
    def __init__(self, x, y):
        self.x, self.y = x, y

s, n = Slotted(1, 2), Normal(1, 2)
print("\n4) __slots__ 实况:")
print("   sys.getsizeof(Slotted 实例) =", sys.getsizeof(s), "字节")
print("   sys.getsizeof(Normal 实例)  =", sys.getsizeof(n), "字节")
print("   (两个都 48: getsizeof 只算对象自身, 不算它引用的 __dict__ 字典 —— 真正的差异看规模对比)")
try:
    s.nickname = "拼错的属性"
except AttributeError as e:
    print("   slots 实例挂未声明属性报错:", e)

# 规模对比: 10 万个实例的总内存差
# 这是什么: tracemalloc —— 标准库内存统计器, 报告 Python 分配的内存峰值
import tracemalloc

def make_many(cls):
    return [cls(1, 2) for _ in range(100_000)]

tracemalloc.start()
make_many(Normal)
_, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"   Normal 类 10 万实例: 峰值约 {peak / 1024 / 1024:.1f} MB")

tracemalloc.start()
make_many(Slotted)
_, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"   Slotted 类 10 万实例: 峰值约 {peak / 1024 / 1024:.1f} MB   # 省下的就是省下的")
print("   (结论: 大量同类对象场景[如游戏实体/缓存条目]用 __slots__, 单体少量对象没必要)")
