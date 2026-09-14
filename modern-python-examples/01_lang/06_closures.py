# ============================================================================
# 06_closures.py  现代 Python 示例集 · 01_lang 语言核心
# 主题: 闭包(closure) —— 嵌套函数对外层变量的引用
# 解决的问题(基础课):
#   函数一返回, 局部变量就该"销毁", 如何做出"有记忆的函数": 计数器、
#   延迟求值、专业术语"partial"。基础课的函数是纯函数进=>出, 闭包让
#   函数可以带着环境继续存活。
# 这是什么: 闭包 —— 内层函数记住了外层函数作用域里的变量, 即使外层已返回,
#           这些变量也"密封"在函数里随身携带; 读取只需直接引用, 修改则须
#           用 nonlocal 声明(否则解释器以为你在新建局部变量)。
# 运行: python 06_closures.py
# ============================================================================

# ---- 1. 最简单的闭包: 记住外层的变量 ----
def outer(x):
    def inner(y):
        return x + y          # x 在外层, inner 记住了它
    return inner              # 返回 inner —— x 随它一起活着

add5 = outer(5)
add100 = outer(100)           # 两个闭包环境互不干扰
print("1) 闭包基本形态:")  # → 1) 闭包基本形态:
print("   outer(5) 生成的函数加 10:", add5(10))  # →    outer(5) 生成的函数加 10: 15
print("   outer(100) 生成的函数加 10:", add100(10))  # →    outer(100) 生成的函数加 10: 110

# 验证环境: 闭包细胞(cell)里有 x = 100
print("   闭包里封存的变量(名称->值):", add100.__closure__[0].cell_contents)  # →    闭包里封存的变量(名称->值): 100
print("   (.__closure__ 是教学观察用; 生产代码别用这个属性)")  # →    (.__closure__ 是教学观察用; 生产代码别用这个属性)

# ---- 2. nonlocal: 修改外层变量 —— 计数器 ----
# 这是什么: nonlocal 声明 —— 告诉解释器"这个名字属于外层嵌套作用域, 我要改它",
#           不声明就 += 会被当成新局部变量(UnboundLocalError)。
def make_counter(start=0):
    count = start
    def step():
        nonlocal count            # 允许修改外层 count
        count += 1
        return count
    return step

c1 = make_counter()
c2 = make_counter(10)             # 各自独立
print("\n2) nonlocal 计数器:")  # → 2) nonlocal 计数器:
print("   c1():", c1(), c1(), c1(), "… c2() 从 10 开始:", c2(), c2())  # →    c1(): 1 2 3 … c2() 从 10 开始: 11 12
print("   两个计数器环境独立, 互不影响")  # →    两个计数器环境独立, 互不影响

# 对比: 全局变量也能计数, 但全局污染 + 多实例互斥 —— 闭包是"局部全局变量"
print("   (c1 和 c2 互不干扰 —— 这正是闭包 vs 全局变量的意义)")  # →    (c1 和 c2 互不干扰 —— 这正是闭包 vs 全局变量的意义)

# ---- 3. 函数对象属性: 不加闭包的替代方案 ----
# 这是什么: 函数也是对象, 可以挂自己的属性(func.calls = 0) —— 干净的做法之一,
#           不需要嵌套函数就能"记忆"。
def ping():
    ping.calls += 1               # 属性在函数对象上, 属于这个函数自己
    return ping.calls

ping.calls = 0
print("\n3) 函数对象属性:")  # → 3) 函数对象属性:
print("   ping() 第几次:", ping(), ping(), ping())  # →    ping() 第几次: 1 2 3

# ---- 4. 延迟求值: 把"算值"推迟到真正需要时 ----
def make_formatter(pattern):
    def fmt(value):               # pattern 被闭包捕获
        return pattern.format(value)
    return fmt

f1 = make_formatter("结果: {:.2f}")
f2 = make_formatter("答案: {}")
print("\n4) 延迟求值:")  # → 4) 延迟求值:
print("   ", f1(2.5), "|", f2(42))  # →     结果: 2.50 | 答案: 42
print("   好处: 模式只写一次, 用了再算; 类似场景还有惰性加载配置/连接")  # →    好处: 模式只写一次, 用了再算; 类似场景还有惰性加载配置/连接

# ---- 5. 经典陷阱: 循环变量迟绑定 — 教学名题 ----
# 这是什么: 闭包捕获的是"变量本身"而非"当时的快照"。循环里创建闭包
#           (如回调函数), 循环结束后才调用, 此时变量已是最终值 ——
#           Python 面试经典错题"lambda 取了最后一个 i"。
fns = []
for i in range(3):
    fns.append(lambda: i * i)      # 没绑定当前 i
print("\n5) 经典闭包陷阱(循环迟绑定):")  # → 5) 经典闭包陷阱(循环迟绑定):
print("   [错误示例] 全部调用后:", [f() for f in fns], "← 都是 4(2的平方), 不是你想要的 0,1,4")
# 输出:    [错误示例] 全部调用后: [4, 4, 4] ← 都是 4(2的平方), 不是你想要的 0,1,4

# 修复: 默认参数立即绑定 / partial —— 每次循环立刻"定格" i 的快照
def make_holder():
    return [lambda i=i: i * i for i in range(3)]     # 默认参数在此刻求值, 完成绑定
print("   [修复: 默认参数快照] :", [f() for f in make_holder()], "← 0, 1, 4 正确")
# 输出:    [修复: 默认参数快照] : [0, 1, 4] ← 0, 1, 4 正确

# ---- 6. 闭包的工程价值: 回调/装饰器/部分应用 ----
# 装饰器(01/02)的 wrapper 就是闭包; 下面用闭包实现"偏函数"用法:
def make_math(base):
    def multiply(factor):         # base 被封闭
        return base * factor
    return multiply

by3 = make_math(3)
by16 = make_math(16)
print("\n6) 偏函数视角:")  # → 6) 偏函数视角:
print("   3 的倍数表:", [by3(n) for n in range(1, 6)])  # →    3 的倍数表: [3, 6, 9, 12, 15]
print("   16 的倍数第一行:", [by16(n) for n in range(1, 4)])  # →    16 的倍数第一行: [16, 32, 48]
print("   (标准库有 functools.partial 专做这件事, 见 06_stdlib/04_functools.py)")
# 输出:    (标准库有 functools.partial 专做这件事, 见 06_stdlib/04_functools.py)
