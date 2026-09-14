# ============================================================================
# 05_metaclass_abc.py  现代 Python 示例集 · 01_lang 语言核心
# 主题: 元类(metaclass)与抽象基类(abc)
# 解决的问题(基础课):
#   想定义"子类必须实现某方法, 不实现就禁止实例化"的接口约束(就像 C++
#   的纯虚函数), 基础课只教过 try/except 运行时检查 —— 太晚了, 应该在
#   "创建类/实例"那一刻就拦截。抽象基类做接口约束; 元类做"批量修改类本身"。
# 这是什么: 元类 —— "类的类": 类对象由元类创建, 就像实例对象由类创建。
#           验证: 一切类的 type 都是 type (type 自己也是 type 的实例)。
#           type(类名, bases, dict) 是"用代码动态造类"的等价写法 —— 上面三
#           行就等价于一个 class 语句。
# 注意(工程实践): 90% 的项目用不到元类(它是框架作者工具, 例: Django 模型、
#   ORM 注册、enum 的成员校验都用它)。你的项目用 ABC 约束接口就够, 元类
#   "了解概念即可" —— 强行元类解决, 往往是过度设计(仍值得理解原理)。
# 运行: python 05_metaclass_abc.py
# ============================================================================

# ---- 1. type 直接铸造出类: 类就是type的对象 ----
def speak(self):
    return "汪汪!"

Dog = type("Dog", (), {"legs": 4, "speak": speak})    # (名称, 基类元组, 类字典)
d = Dog()
print("1) 动态造类 type(...):")  # → 1) 动态造类 type(...):
print("   type(Dog) =", type(Dog), "  ← 类的类型就是 type")  # →    type(Dog) = <class 'type'>   ← 类的类型就是 type
print(f"   Dog() 实例: {d.speak()} 腿数 = {d.legs}")  # →    Dog() 实例: 汪汪! 腿数 = 4

# ---- 2. 自定义元类: 拦截"类的创建"过程 ----
# 这是什么: 用 metaclass= 指定元类后, class 语句执行时会调用元类的 __new__ 来
#           创建那个类 —— 等于"写完类定义后统一改造每个类"的钩子。
#           常用于: 自动注册到注册表、自动加属性、强制命名规范。
class SealMeta(type):
    def __new__(mcs, name, bases, namespace):
        print(f"2) [SealMeta] 正在创建类 {name!r}, 盖个章属性")
        # 每创建一个经手类各输出一行(共 2 次):
        # 2) [SealMeta] 正在创建类 'Point', 盖个章属性
        # 2) [SealMeta] 正在创建类 'Point3D', 盖个章属性
        namespace["sealed"] = True                    # 每个经手类强制加一个属性
        namespace["creator"] = mcs.__name__           # 还能记上"谁造的"
        return super().__new__(mcs, name, bases, namespace)

class Point(metaclass=SealMeta):                      # class 语句 → 元类 __new__
    pass

class Point3D(Point):                                 # 子类创建照样拦截
    pass

print("   Point.sealed =", Point.sealed, "; Point3D.sealed =", Point3D.sealed)
# 输出:    Point.sealed = True ; Point3D.sealed = True
print("   子类照样被处理(元类作用于它的所有子类)")  # →    子类照样被处理(元类作用于它的所有子类)

# ---- 3. ABC: 接口约束 —— 不实现抽象方法就不许实例化 ----
# 这是什么: ABC(Abstract Base Class) + @abstractmethod: 声明"子类必须实现
#           这些方法, 否则实例化时直接 TypeError"; 等价于 C++ 的纯虚函数
#           virtual double area() = 0; —— 编译期错误换成运行期实例化时报错。
# 这是什么: @abstractmethod 装饰的方法也叫"模板方法": 基类里可以写好"用
#           抽象方法拼业务"的骨架(如 describe), 子类只填具体实现。
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        """必须实现: 返回面积"""

    def describe(self):                               # 非抽象方法: 基类提供的模板
        return f"我的面积是 {self.area():.2f}"

try:
    Shape()
except TypeError as e:
    print("\n3) ABC 约束:")  # → 3) ABC 约束:
    print("   直接实例化抽象类报错:", e)
    # 输出:    直接实例化抽象类报错: Can't instantiate abstract class Shape without an implementation for abstract method 'area'

class Circle(Shape):
    def __init__(self, r):
        self.r = r

    def area(self):                                   # 实现了抽象方法 → 可以用了
        return 3.14159 * self.r * self.r

c = Circle(10)
print("   Circle(10).describe() =", c.describe())  # →    Circle(10).describe() = 我的面积是 314.16

# ---- 4. 抽象类方法 / 抽象属性 ----
class Registry(ABC):
    @classmethod
    @abstractmethod
    def display_name(cls):
        """必须实现: 返回人类可读名"""

class User(Registry):
    @classmethod
    def display_name(cls):
        return "用户"

class Broken(Registry):                               # 没实现 → 不许实例化
    pass

try:
    Broken()
except TypeError as e:
    print("\n4) 抽象类方法:")  # → 4) 抽象类方法:
    print("   Broken(没实现 display_name) 实例化报错:", e)
    # 输出:    Broken(没实现 display_name) 实例化报错: Can't instantiate abstract class Broken without an implementation for abstract method 'display_name'
    print("   User.display_name() =", User.display_name())  # →    User.display_name() = 用户

# ---- 5. 元类叠加 ABC 的业界样板: 注册表(看一眼就够了) ----
# 说明: 框架常把"元类注册 + ABC 约束"组合使用, 这里演示记录模板:
print("\n5) 元类+ABC 样板(简述): 现实中这行写法属于框架代码, 你只需要认识它")  # → 5) 元类+ABC 样板(简述): 现实中这行写法属于框架代码, 你只需要认识它
print("   class Plugin(ABC, metaclass=RegisteredMeta): ...")
# 输出:    class Plugin(ABC, metaclass=RegisteredMeta): ...
print("   → 约束子类实现约定接口 + 创建时自动注册, 是插件架构的经典骨架")  # →    → 约束子类实现约定接口 + 创建时自动注册, 是插件架构的经典骨架
