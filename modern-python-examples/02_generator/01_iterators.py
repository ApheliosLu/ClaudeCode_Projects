# ============================================================================
# 01_iterators.py  现代 Python 示例集 · 02_generator 迭代器与生成器
# 主题: 迭代协议 —— for 循环的底层真相
# 解决的问题(基础课):
#   for x in 列表/字典/文件 用了很多次, 但从没想过"列表能遍历"背后的规则;
#   看到自定义对象想 for 它, 加个 __iter__ 就行 —— 这是现代 Python 最常用
#   的协议之一(数据库游标/文件/生成器 都是迭代器)。
# 这是什么: 迭代器(iterator) —— 有 __next__() 方法、每次返回下一个元素并
#   自我推进的对象, 没有元素时抛 StopIteration 结束; iter(可迭代对象)
#   拿到迭代器。for 循环内部 = iter() + 不断 next() + 捕获 StopIteration 退出,
#   任何实现这套协议的"可迭代对象"都能直接用 for 遍历。
# 运行: python 01_iterators.py
# ============================================================================

# ---- 1. for 循环的手工翻版: iter() + next() ----
nums = [10, 20, 30]
it = iter(nums)                            # 这是什么: iter() —— 从"可迭代对象"拿迭代器
print("1) for 循环的手工翻版:")  # → 1) for 循环的手工翻版:
print("   iter(lst) 类型:", type(it).__name__)  # →    iter(lst) 类型: list_iterator
print("   next 依次取:", next(it), next(it), next(it))  # →    next 依次取: 10 20 30
try:
    next(it)
except StopIteration:
    print("   越界后 next 抛 StopIteration(结束信号) —— for 循环就是捕获它来停止的")
    # 输出:    越界后 next 抛 StopIteration(结束信号) —— for 循环就是捕获它来停止的

# ---- 2. 手写迭代器类: 从 0 计到 limit ----
# 语法骨架: __iter__ 返回自身(迭代器协议约定还得是 iterable), __next__ 推进。
class Countdown:
    def __init__(self, start):
        self.n = start

    def __iter__(self):
        return self                       # 迭代器自己同时是可迭代对象

    def __next__(self):
        if self.n <= 0:
            raise StopIteration           # 停止信号
        self.n -= 1
        return self.n + 1

print("\n2) 自定义迭代器 Countdown(5):")  # → 2) 自定义迭代器 Countdown(5):
for i in Countdown(5):
    print("   ", i, end="")
    # 循环 5 次各输出一段(end="" 不换行, 与下一行拼接):
    #     5    4    3    2    1 
print("   ← 直接 for 一个自己写的类")  # →    ← 直接 for 一个自己写的类

# ---- 3. iter(callable, sentinel): 哨兵迭代 ----
# 这是什么: iter(可调用对象, 哨兵值) —— 内建的两个参数迭代器: 不断调用那个
#           函数, 直到返回值等于哨兵值时结束。常用于"读到某个标记为止"。
print("\n3) iter(callable, sentinel) 哨兵迭代:")  # → 3) iter(callable, sentinel) 哨兵迭代:
# 模拟"连续掷骰子直到掷出 6":
import random

random.seed(7)                         # 固定种子保证演示可复现(序列: 3,2,4,6)
def roll():
    return random.randint(1, 6)
print("   掷骰子到 6: ", list(iter(roll, 6)), "← 掷出 6 即停(6 本身不包含)")  # →    掷骰子到 6:  [3, 2, 4] ← 掷出 6 即停(6 本身不包含)

# ---- 4. 迭代器的"一次性消费"本性 ----
print("\n4) 迭代器一次性消费:")  # → 4) 迭代器一次性消费:
it2 = iter([1, 2, 3])
print("   第一轮:", list(it2))  # →    第一轮: [1, 2, 3]
print("   第二轮:", list(it2), "← 已被消费光, 空列表(没有后退键)")  # →    第二轮: [] ← 已被消费光, 空列表(没有后退键)

# ---- 5. reversed(): 需要 __reversed__ 或 __len__ + __getitem__ ----
class CountDownExplicit:
    """用 __reversed__ 自定义反序(可选实现)"""
    def __init__(self, seq):
        self.seq = seq
    def __reversed__(self):
        return iter(reversed(self.seq))

cd = CountDownExplicit([1, 2, 3])
print("\n5) reversed() 配套:")  # → 5) reversed() 配套:
print("   reversed(自定义类) =", list(reversed(cd)))  # →    reversed(自定义类) = [3, 2, 1]
print("   (没有 __reversed__ 时, reversed 回退用 __len__+__getitem__)")
# 输出:    (没有 __reversed__ 时, reversed 回退用 __len__+__getitem__)

# ---- 6. 顺带看一眼: 为什么文件也直接能 for? ----
# 文件对象是迭代器(每 next 读一行); 这解释了为什么
#   for line in open(...)
# 是标准姿势, 也解释了为什么读文件必须重开才能再读。
print("\n6) 附: file 也是迭代器 (每 next 取一行); for line in f 即一次次 next(f)")
# 输出: 6) 附: file 也是迭代器 (每 next 取一行); for line in f 即一次次 next(f)
