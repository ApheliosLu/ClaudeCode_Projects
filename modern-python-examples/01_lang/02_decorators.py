# ============================================================================
# 02_decorators.py  现代 Python 示例集 · 01_lang 语言核心
# 主题: 装饰器 —— @ 语法糖的真实原理、参数化装饰器、装饰类
# 解决的问题(基础课):
#   如果每个函数都要"记日志 / 测耗时 / 校验权限", 写 10 个函数就复制
#   粘贴 10 遍同样的代码; 装饰器让"给函数加点功能"变成一行 @ 标注。
# 这是什么: 装饰器 —— 本质是"接一个函数、返回一个新函数"的函数;
#           @deco 写在 def f 上面, 等同于 f = deco(f)。新函数可以在
#           调原函数前后插代码(所以也叫"包装"), 常用在日志/缓存/鉴权/重试。
# 运行: python 02_decorators.py
# ============================================================================

# ---- 1. 最简装饰器: 函数接函数, 返回函数 ----
def log_calls(func):
    """在函数调用前后各打印一行 —— 不给原函数加一行代码"""
    def wrapper(*args, **kwargs):                    # 这是什么: *args 收集所有位置参数, **kwargs 收集所有关键字参数(基础课容器复习)
        print(f"  [日志] 开始调用 {func.__name__}")
        # 每次被装饰函数被调用时各输出一行(被调用 2 次):
        #   [日志] 开始调用 add
        #   [日志] 开始调用 sub
        result = func(*args, **kwargs)
        print(f"  [日志] 结束调用 {func.__name__}")
        # 每次被装饰函数返回前各输出一行(被调用 2 次):
        #   [日志] 结束调用 add
        #   [日志] 结束调用 sub
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

print("1) 装饰器效果:")  # → 1) 装饰器效果:
print("   add(1, 2) =", add(1, 2), "  ← 装饰器没有改变 add(1,2) 的返回值")  # →    add(1, 2) = 3   ← 装饰器没有改变 add(1,2) 的返回值

# 裸语法翻版: @ 只是把下面这行"移到了函数定义上方"
def sub(a, b):
    return a - b
sub = log_calls(sub)                                 # 与 @log_calls 完全等价

print("   裸语法翻版:", sub(5, 3))  # →    裸语法翻版: 2

# ---- 2. functools.wraps: 别把函数身份搞丢 ----
# 这是什么: functools.wraps —— 装饰器的标准补丁: 不加它, 用 @log_calls 包过的
#           函数, __name__/__doc__/help() 全变成 wrapper 的(名都没了),
#           调试与文档都很难受; 加上它, 外表与原名函数一模一样。
from functools import wraps

def traced(func):
    @wraps(func)                                     # 复制 func 的 __name__/__doc__/__dict__ 给 wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@traced
def greet(name):
    """向某人问好"""
    return f"你好 {name}"

print("\n2) functools.wraps:")  # → 2) functools.wraps:
print("   greet.__name__ =", greet.__name__)         # 原始名 greet  →    greet.__name__ = greet
print("   greet.__doc__  =", greet.__doc__)          # 原函数文档字符串保留  →    greet.__doc__  = 向某人问好
print("   greet('小明')  =", greet("小明"))           # 原函数照常工作, 外表与原名无异  →    greet('小明')  = 你好 小明
# 【对比】上一节的 log_calls 没写 @wraps —— 被它装饰过的函数, __name__ 会变成:
@log_calls
def poor_name():
    pass

print("   【对比】无 @wraps: poor_name.__name__ =", repr(poor_name.__name__), "← 名字被 wrapper 顶替, 调试/文档不便")
# 输出:    【对比】无 @wraps: poor_name.__name__ = 'wrapper' ← 名字被 wrapper 顶替, 调试/文档不便

# ---- 3. 参数化装饰器: 三层嵌套 ----
# 这是什么: 想让装饰器"带参数"(比如 @retry(times=3)), 就得再包一层:
#           外层函数接参数 → 中层接函数 → 内层接 *args, 三层结构。
def retry(times):
    def decorator(func):                             # 接被装饰的函数
        @wraps(func)
        def wrapper(*args, **kwargs):                # 接调用参数
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except ValueError as e:
                    print(f"  第 {attempt} 次失败: {e}; ", end="")
                    # 概率事件(每次 80% 失败), 本次 3 次全失败; end="" 不换行, 与下一行 print 拼成同一行:
                    #   第 1 次失败: 服务器拒绝连接;   第 2 次失败: 服务器拒绝连接;   第 3 次失败: 服务器拒绝连接; 
            print(f"经过 {times} 次重试仍失败")  # → 经过 3 次重试仍失败
        return wrapper
    return decorator

@retry(times=3)                                      # 先执行 retry(times=3) 再拿结果当装饰器
def connect():
    import random
    if random.random() < 0.8:
        raise ValueError("服务器拒绝连接")
    return "连接成功!"

print("\n3) 参数化装饰器 @retry(times=3):")  # → 3) 参数化装饰器 @retry(times=3):
r = connect()                                        # 每次 80% 概率失败, 最多重试 3 次(概率事件, 多跑几次可能看到"连接成功!")
print(r if r else "（三次都失败时才走到这里, retry 的 wrapper 此时返回 None）")  # → （三次都失败时才走到这里, retry 的 wrapper 此时返回 None）

# ---- 4. 装饰器也能装饰类 ----
# 这是什么: 类也是对象, 同样能被"接类返回类"的函数装饰 —— 常见于:
#           自动注册到框架(如 FastAPI 的路由)、给类批量注入方法/属性。
registry = {}

def register(cls):
    registry[cls.__name__.upper()] = cls             # 登记到注册表
    return cls

@register
class User:
    pass

@register
class Admin:
    pass

print("\n4) 装饰器装饰类: 注册表中有:", sorted(registry.keys()))  # → 4) 装饰器装饰类: 注册表中有: ['ADMIN', 'USER']

# ---- 5. 复习: @staticmethod / @classmethod 也是装饰器 ----
# 基础课讲过这两个内置装饰器, 这里以"装饰器通用性"视角看一眼:
class Demo:
    MAX = 10

    @staticmethod                                # 不需要 self/cls, 普通函数挂类上
    def add(x, y):
        return x + y

    @classmethod                                 # 第一个参数是类本身, 可用于访问类属性
    def limit(cls):
        print(f"5) classmethod 拿到类本身: {cls.__name__}.MAX = {cls.MAX}")  # → 5) classmethod 拿到类本身: Demo.MAX = 10

print()
Demo.limit()                                     # 无需实例, 直接类上调用
print("   staticmethod 同理:", Demo.add(3, 4))  # →    staticmethod 同理: 7
