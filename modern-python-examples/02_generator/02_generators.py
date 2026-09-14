# ============================================================================
# 02_generators.py  现代 Python 示例集 · 02_generator 迭代器与生成器
# 主题: 生成器(generator) —— yield 让你的函数会"暂停"
# 解决的问题(基础课):
#   想"随时算下一个数"的序列: 斐波那契、逐行读大文件、无限流 —— 先全部
#   算好放 list 里会爆内存; 生成器把函数变成"每次 next 时才计算下一个"
#   的惰性工厂, 还能与外部双向通信(send/throw/close)。
# 这是什么: 生成器 —— 只要函数体里有一个 yield, 它就不再是普通函数:
#   调用它返回一个"生成器对象"(迭代器), 执行到 yield 就暂停并把值交出,
#   下次 next() 从 yield 行之后继续 —— 现场(局部变量)原地保留。
# 运行: python 02_generators.py
# ============================================================================

import sys
from itertools import islice          # 这是什么: islice —— 迭代器切片(取出前 n 项, 见 03_itertools.py)

# ---- 1. 生成器基本形态: 执行/暂停/现场保留 ----
def countdown(n):
    print("   [函数体开始执行]")
    # 生成器每次开始执行时输出一行(本例共 2 次):
    #    [函数体开始执行]
    while n > 0:
        yield n                       # 暂停在这里, 输出 n
        n -= 1
        print("   [从 yield 后继续]")
        # 每次从 yield 处恢复执行时输出一行(本例共 4 次):
        #    [从 yield 后继续]
        #    [从 yield 后继续]
        #    [从 yield 后继续]
        #    [从 yield 后继续]

print("1) 生成器基本形态:")  # → 1) 生成器基本形态:
g = countdown(3)
print("   g 的类型:", type(g).__name__)          # generator, 不是函数执行结果  →    g 的类型: generator
print("   next(g) →", next(g))  # →    next(g) → 3
print("   next(g) →", next(g))                   # 看注释行: 现场被保留  →    next(g) → 2
print("   遍历取完:", list(countdown(3)))         # list() 把生成器全部跑完  →    遍历取完: [3, 2, 1]

# ---- 2. 生成器表达式 vs 列表推导: 惰性 + 内存 ----
print("\n2) 生成器表达式 vs 列表推导:")  # → 2) 生成器表达式 vs 列表推导:
gen = (x * x for x in range(1_000_000))          # 生成器表达式: () 而非 []
lst = [x * x for x in range(1_000_000)]          # 列表推导: 立刻全部算出
print(f"   生成器对象大小: {sys.getsizeof(gen):>6,} 字节(不存元素)")  # →    生成器对象大小:    208 字节(不存元素)
print(f"   列表大小       : {sys.getsizeof(lst):>6,} 字节(100 万个整数)")  # →    列表大小       : 8,448,728 字节(100 万个整数)
print("   生成器是按`要一个算一个`, 列表是`先全算好` → 大数据流选生成器")  # →    生成器是按`要一个算一个`, 列表是`先全算好` → 大数据流选生成器
print("   注意: 惰性 = 只走一遍; list(gen) 之后 gen 就空了")  # →    注意: 惰性 = 只走一遍; list(gen) 之后 gen 就空了

# ---- 3. send(): 向生成器里"塞值" ----
# 这是什么: send(值) —— 比 next 多一步: 把值交给 yield 表达式作为它的结果,
#           然后继续执行到下一个 yield。注意: 首次启动必须用 next()(或 send(None))。
def averaging():
    total, count, avg = 0.0, 0, None
    while True:
        value = yield avg            # 第一次 yield 时 avg=None; send(v) 时 v 落到 value
        total += value
        count += 1
        avg = total / count

print("\n3) send() 流式平均值:")  # → 3) send() 流式平均值:
a = averaging()
print("   next 启动:", next(a))                      # None  →    next 启动: None
print("   send(10):", a.send(10))                    # avg = 10  →    send(10): 10.0
print("   send(20):", a.send(20))                    # avg = 15  →    send(20): 15.0
print("   send(30):", a.send(30))                    # avg = 20  →    send(30): 20.0

# ---- 4. throw() 与 close(): 从外部干预生成器 ----
# 这是什么: throw(异常对象/类型, 参数) —— 把异常"砸"进生成器当前暂停的
#           yield 处(可被生成器内 try/except 接住); close() —— 触发
#           GeneratorExit 走 finally 清理, 结束生成器。
#           (3.12 及之前: 可写 throw(ValueError, "炸弹") 传类型+参数;
#           本机 3.14 起已弃用旧式三参签名, 新写法只传异常类或其实例)
def echo():
    while True:
        try:
            yield "正常工作"
        except ValueError as e:
            yield f"收到异常: {e}"

r = echo()
print("\n4) throw() / close():")  # → 4) throw() / close():
print("   ", next(r))  # →     正常工作
print("   ", r.throw(ValueError("炸弹")))            # 单参形式(新写法), 生成器内部接住  →     收到异常: 炸弹
print("   ", next(r), " ← 继续还能正常工作")  # →     正常工作  ← 继续还能正常工作

def cleanup():
    try:
        while True:
            yield "干活中"
    finally:
        print("   [generator.close() 触发 finally] 关闭资源: 连接池已清理")  # →    [generator.close() 触发 finally] 关闭资源: 连接池已清理

c = cleanup()
next(c)
c.close()                                            # close 触发 GeneratorExit → finally
print("   close() 之后生成器结束")  # →    close() 之后生成器结束

# ---- 5. yield from: 委托子生成器 ----
# 这是什么: yield from 子迭代器 —— 把子生成器/迭代器"展开"输出(自动取完,
#           还能把子生成器的 return 值接回来), 等价于手写 for y in sub: yield y。
def chain(*iterables):
    for it in iterables:
        yield from it                # 委托: 逐个展开 it

print("\n5) yield from:")  # → 5) yield from:
print("   chain([1,2], (3,4), 'ab') =", list(chain([1, 2], (3, 4), "ab")))
# 输出:    chain([1,2], (3,4), 'ab') = [1, 2, 3, 4, 'a', 'b']

def find_treasure():
    yield "前半段路"
    return "宝藏!!!"                 # 生成器 return 值是"委托方"可以接的

def main_gen():
    result = yield from find_treasure()    # yield from 表达式的值 = 子生成器的 return
    print("   [yield from] 拿到子生成器 return:", result)  # →    [yield from] 拿到子生成器 return: 宝藏!!!

list(main_gen())

# ---- 6. 无限生成器 + islice 按需截取 ----
# 这是什么: 无限生成器 —— while True 生产无限序列: 生成器惰性求值, 想要几个
#           取几个即可(没有 real list 版本, 生不出来)。
def fibonacci():
    a, b = 0, 1
    while True:
        yield a                    # 无限供给
        a, b = b, a + b

print("\n6) 无限斐波那契:")  # → 6) 无限斐波那契:
print("   list(islice(fibonacci(), 10)) =", list(islice(fibonacci(), 10)))
# 输出:    list(islice(fibonacci(), 10)) = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print("   (提示: 无限序列必须配合截取/条件再终止, 不能 list() 全接)")  # →    (提示: 无限序列必须配合截取/条件再终止, 不能 list() 全接)

# ---- 7. 生成器与列表的取舍一句话总结 ----
print("\n7) 取舍: 小数据/需要回头访问 → 列表; 大数据流/函数式管线 → 生成器")  # → 7) 取舍: 小数据/需要回头访问 → 列表; 大数据流/函数式管线 → 生成器
print("   (生成器有惰性、省内存, 负作用: 不能 len()、不能下标、只能走一遍)")  # →    (生成器有惰性、省内存, 负作用: 不能 len()、不能下标、只能走一遍)
