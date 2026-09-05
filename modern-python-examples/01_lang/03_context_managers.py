# ============================================================================
# 03_context_managers.py  现代 Python 示例集 · 01_lang 语言核心
# 主题: 上下文管理器 —— with 语句的完整原理与应用
# 解决的问题(基础课):
#   打开文件要 try/finally 包住 close() 才不会泄漏句柄; 数据库连接、锁、
#   临时环境变量、超时 —— 每种"用完必须清理"的资源都要手写清理代码。
#   with 语句把"进入/退出"做成协议, 用完自动清理, 异常也能安全退出。
# 这是什么: 上下文管理器 —— 实现了 __enter__/__exit__ 协议的对象;
#           with obj 时: 先调 obj.__enter__() 拿结果(可给 as 赋值),
#           执行完代码块后(无论正常还是抛异常)必调 obj.__exit__(exc_type,
#           exc, tb); __exit__ 返回 True = 吞掉异常, False/None = 继续抛出。
#           最熟悉的例子: with open(...) as f —— 免写 f.close()。
# 运行: python 03_context_managers.py
# ============================================================================

import time
from contextlib import contextmanager, ExitStack

# ---- 通用演示资源类: 打印"进入/退出"顺序 ----
class Resource:
    """带名字的资源: 打印被管理的时机, 方便观察执行顺序"""
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"   进入: {self.name}")
        return self

    def __exit__(self, exc_type, exc, tb):
        # 这是什么: __exit__ 收到三个参数 —— 异常类型/异常对象/回溯对象;
        #           无异常时三者均为 None。
        print(f"   退出: {self.name}")
        return False                                # False = 不吞异常

# ---- 1. 手写一个上下文管理器: 计时器 ----
class Timer:
    """计时器上下文: __enter__ 记录起点, __exit__ 结算耗时 —— 顺带观察顺序"""
    def __enter__(self):
        self.start = time.perf_counter()
        print("1) 进入代码块(Timer.__enter__)")
        return self                                 # as 拿到的是这里返回的对象

    def __exit__(self, exc_type, exc, tb):
        cost = time.perf_counter() - self.start
        print(f"   离开代码块(Timer.__exit__), 耗时 {cost*1000:.2f} ms\n")
        return False

with Timer():                                       # as 结果也可以忽略
    sum(i * i for i in range(1_000_000))            # 模拟一点工作

# ---- 2. __exit__ 返回 True: 吞掉异常 ----
class IgnoreError:
    """宽容的上下文: 代码块里抛出的指定异常由它消化, 不影响后续代码"""
    def __init__(self, exc_type):
        self.target = exc_type

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        if exc_type is self.target:
            print(f"2) 吞掉了 {exc_type.__name__}(演示: 视需求免责)")
            return True                             # True = 异常不再向上抛
        return False                                # 其他异常照常抛出

with IgnoreError(ValueError):
    raise ValueError("库内部错误, 但不值得崩掉整个程序")
print("   被吞掉后, 这行照常执行了 —— 程序没崩溃\n")

# ---- 3. @contextmanager 装饰器: 用生成器写小巧的上下文 ----
# 这是什么: contextlib.contextmanager —— 免写类, 把一个"用 yield 分成前后两段"
#           的生成器变成上下文管理器: yield 前 = __enter__ 要做的事,
#           yield 后 = __exit__ 要做的事(异常从 yield 那一行抛出)。
#           注意: 清理代码必须包在 try/finally 里 —— 否则异常时不会走到清理段。
@contextmanager
def tag(name):
    print(f"3) <{name}> 开始")
    try:
        yield                                       # 这行前/后就是 enter/exit 的界线
    finally:
        print(f"   </{name}> 结束")

with tag("p"):
    print("   代码块内容(在 begin/end 之间)")

# @contextmanager 在 except 里接异常:
@contextmanager
def risky():
    try:
        yield
    except ZeroDivisionError:
        print("   4) @contextmanager 内 except ZeroDivisionError, 吞掉")

with risky():
    x = 1 / 0
print("   这行照常执行 —— 异常被 contextmanager 吞了\n")

# ---- 4. ExitStack: 动态堆叠数量不定的资源 ----
# 这是什么: contextlib.ExitStack —— 以"栈"的方式登记任意多个上下文/清理回调,
#           with 块结束后按登记的反序(后进先出)逐一退出/执行;
#           适合"要清理的资源数量运行时才知道"的场景(循环里临时加句柄/锁)。
print("4) ExitStack: 循环里动态登记资源, 结束时反序清理")
with ExitStack() as stack:
    for i in range(2):                              # 动态数量演示
        stack.enter_context(Resource(f"A{i}"))
    stack.enter_context(Resource("B"))
    # 这是什么: stack.callback —— 登记一个"退出时执行一次"的任意函数(不需要上下文对象)
    stack.callback(lambda: print("   回调: 兜底清理(任何情况都会执行)"))
    print("   [代码块执行中...]")
print("   with 结束: 登记的资源按反序退出(后进先出)\n")

# ---- 5. 一条 with 开多个资源 ----
# 语法: with A(), B(): ...  —— 进入按顺序, 退出反序(都归栈管)。
print("5) 一条 with 打开多个上下文(进入顺序, 退出反序):")
with Resource("X"), Resource("Y"):
    print("   [代码块执行中...]\n")
