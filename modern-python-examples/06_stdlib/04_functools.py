# ============================================================================
# 04_functools.py  现代 Python 示例集 · 06_stdlib 标准库工具箱
# 主题: functools —— 高阶函数工具(偏函数/记忆化/分派/累积)
# 解决的问题(基础课):
#   写代码时常见套路: "每次调用都传同一批参数"、"同一个纯函数反复算
#   同样的输入"、"按类型写 if-elif 长链"、"手写循环做累加"。functools
#   把这些套路各打包成一个函数/装饰器。
# 运行: python 04_functools.py
# ============================================================================

import time
from functools import cache, cmp_to_key, lru_cache, partial, reduce, singledispatch

# ---- 1. partial: 固定部分参数, 造"专用版"函数 ----
# 这是什么: partial(原函数, 固定参数...) —— 返回一个新函数, 调用时自动补上
#           固定参数, 只需传剩下的。用途: 为日志器固定前缀、为接口固定 base_url、
#           把"两参函数"改造成"回调用的一参函数"。
def make_request(method, url, timeout):
    return f"[{method}] {url} (超时 {timeout}s)"

get_json = partial(make_request, "GET", timeout=5)   # 固定 method 和 timeout
print("1) partial 固定参数:")
print("   get_json('/api/users')  →", get_json("/api/users"))
print("   get_json('/api/orders') →", get_json("/api/orders"))
print("   make_request 原函数仍在:", make_request("POST", "/api/x", 10))

# ---- 2. lru_cache / cache: 记忆化 —— 同样的输入只算一次 ----
# 这是什么: @cache —— 装饰纯函数后, 返回值按参数缓存: 相同的参数再调用
#           直接从缓存拿, 不重算。典型场景: 递归里有大量重复子问题(fib)。
#           lru_cache(maxsize) 是它的前辈, 只缓存最近 maxsize 个(防内存无限涨);
#           (3.9 起) @cache 等价 lru_cache(maxsize=None), 无上限缓存。
#           要求函数"纯"(同样输入必然同样输出), 副作用函数别用。
def fib_plain(n):                       # 朴素版: 大量重复计算
    return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)

@cache
def fib_cached(n):                      # 记忆化版: 每个 n 只真算一次
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)

N = 37
t0 = time.perf_counter(); r_plain = fib_plain(N); t1 = time.perf_counter()
t2 = time.perf_counter(); r_cache = fib_cached(N); t3 = time.perf_counter()
print("\n2) 记忆化加速对比 fib(37):")
print(f"   朴素版  : {r_plain}, 耗时 {t1 - t0:.2f}s")
print(f"   @cache : {r_cache}, 耗时 {(t3 - t2) * 1000:.3f}ms")
print("   缓存命中统计: fib_cached.cache_info():", fib_cached.cache_info())
# 这是什么: 函数名.cache_info() —— 看缓存命中次数(hits/misses), 运维时
#           判断缓存到底帮了多少忙。

# ---- 3. singledispatch: 按"第一个参数的类型"分流, 替代 if-elif 长链 ----
# 这是什么: @singledispatch 装饰一个通用函数, 再用 @函数名.register(类型) 注册
#           各类型专属实现 —— 调用时按实参类型自动选实现(像 C++ 函数重载/
#           多态的弱化版)。对照: 手写 isinstance 链每加一种类型就要改主函数,
#           分派则每种类型一个函数, 各改各的。
@singledispatch
def show(value):
    """通用兜底: 没注册的类型走这里"""
    return f"未知类型 {type(value).__name__}: {value}"

@show.register(int)
def _(value):                            # 函数名不重要, 叫 _ 表示"这是分派实现"
    return f"整数 {value:,}"

@show.register(list)
def _(value):
    return "列表 [" + ", ".join(map(str, value)) + "]"

@show.register(str)
def _(value):
    return f"字符串「{value}」"

print("\n3) singledispatch 按类型分派:")
print("   show(1234567)        →", show(1234567))
print("   show([1, 2, 3])      →", show([1, 2, 3]))
print("   show('hi')           →", show("hi"))
print("   show(3.14)           →", show(3.14), "  # 没注册 float, 走通用兜底")

# ---- 4. reduce: 把序列"滚雪球"式累积成一个值 ----
# 这是什么: reduce(函数, 序列[, 初值]) —— 从左到右两两累积:
#           先算 f(a, b), 结果再和 c 算 f(f(a,b), c)…… 序列变单值。
#           求和/求积/拼接都行(有 sum() 的场合用 sum, reduce 留给无现成
#           函数的累积逻辑)。对照: 手写循环 + 中间变量。
nums = [1, 2, 3, 4, 5]
total = reduce(lambda acc, x: acc + x, nums, 0)          # 初值 0 起步
product = reduce(lambda acc, x: acc * x, nums, 1)        # 初值 1 起步
print("\n4) reduce 累积:")
print("   nums 求和:", total, "   # 有 sum() 的话用它, 这里演示机制")
print("   nums 求积:", product)

# ---- 5. cmp_to_key: 对接"老式比较函数"到 sorted 的 key 体系 ----
# 这是什么: cmp_to_key(老比较函数) —— 老 API 风格是比较函数 f(a, b): 返回
#           负数=a 排前, 正数=b 排前, 0=相等; 而现代 sorted 只收 key=(算一个
#           值来比), 不收比较函数。cmp_to_key 把前者包装成后者, 用于对接
#           历史代码/复杂比较规则(官方推荐新代码直接写 key)。
def compare_by_len(a, b):              # 老式比较函数: 短的排前, 同长比字典序
    if len(a) != len(b):
        return -1 if len(a) < len(b) else 1
    return -1 if a < b else (1 if a > b else 0)

words = ["pear", "kiwi", "fig", "apple", "grape"]
print("\n5) cmp_to_key 老式比较函数对接 sorted:")
print("   排序结果:", sorted(words, key=cmp_to_key(compare_by_len)))
print("   对照新写法 key=(len(x), x):", sorted(words, key=lambda x: (len(x), x)))

# ---- 6. wraps 复习(详见 01_lang/02_decorators.py) ----
# 这是什么: wraps —— 装饰器里包一层后把原函数的 __name__/__doc__ 抄回来,
#           否则 help()/自省看到的是包装函数的名字。01_lang/02 有完整演示,
#           这里只验证"没 wraps 会丢名字"这一个点。
import functools

def shout_plain(func):                 # 没 wraps 的粗糙装饰器
    def wrapper(*a, **k):
        return func(*a, **k).upper()
    return wrapper

@shout_plain
def greet():                           # 会被装饰器改成 wrapper
    """打个招呼"""

def shout_wrapped(func):               # 带 wraps 的正确版
    @functools.wraps(func)
    def wrapper(*a, **k):
        return func(*a, **k).upper()
    return wrapper

@shout_wrapped
def greet2():
    """打招呼(正确版)"""

print("\n6) wraps 复习(见 01_lang/02):")
print("   没 wraps: greet.__name__ =", greet.__name__)
print("   有 wraps: greet2.__name__ =", greet2.__name__)
