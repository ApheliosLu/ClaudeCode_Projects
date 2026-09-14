# ============================================================================
# 01_data_model.py  现代 Python 示例集 · 01_lang 语言核心
# 主题: 数据模型协议 —— 双下划线方法(常称"魔术方法")定制类行为
# 解决的问题(基础课):
#   基础课里你对对象只写过 __init__: 对象能创建, 但 print 出来是一坨
#   <__main__.ShoppingCart object at 0x...>; 不能 len(obj)、不能 obj[0]、
#   不能 in 判断、不能 == 比较、不能当成 dict 的键 —— 而这些行为其实
#   都可以自己定制。
# 这是什么: 数据模型协议 —— 解释器对特定双下划线名称有固定约定(如 __len__):
#   你定义了哪个, 对应的内建函数/运算符(如 len()/==/[]/in/for)就会自动调用它;
#   没定义就回退到默认行为(如 == 退化为 id 比较)。这是 Python 一切
#   "自定义类像内建类型一样好用"的底层机制。
# 运行: python 01_data_model.py
# ============================================================================

# ---- 1. __repr__ 与 __str__: 两种"把对象转成字符串" ----
# 这是什么: __repr__ 是"给开发者调试看"的表示(应该无歧义、最好能还原对象),
#           __str__ 是"给人看/print 展示"的表示, 两者可以不一样。
#           使用时机: repr()/列表内元素显示/交互式控制台回显 → __repr__;
#           print()/f-string → __str__。
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"        # 形如构造调用, 还原对象

    def __str__(self):
        return f"点({self.x}, {self.y})"           # 给用户看的文案

p = Point(1, 2)
print("1) str(p)  =", str(p))                       # 走 __str__  → 1) str(p)  = 点(1, 2)
print("   repr(p) =", repr(p))                      # 走 __repr__  →    repr(p) = Point(1, 2)
print("   print(p)=", p)                            # print 用 __str__  →    print(p)= 点(1, 2)
print("   列表内元素显示 [p, Point(3, 4)]:", [p, Point(3, 4)])   # 用 __repr__
# 输出:    列表内元素显示 [p, Point(3, 4)]: [Point(1, 2), Point(3, 4)]
print("   f-string 用 __str__:", f"坐标是 {p}")  # →    f-string 用 __str__: 坐标是 点(1, 2)

# ---- 2. __eq__ / __hash__ / __lt__: 比较与哈希 ----
# 这是什么: __eq__ 实现 ==(相等判断); 注意坑 —— 一旦定义了 __eq__,
#           __hash__ 会被自动置为 None, 对象立刻"不可哈希":
#           不能放进 set, 不能当 dict 的键(因为 dict 靠哈希找键)。
#           要想"相等且可哈希", 必须自己实现 __hash__。
# 这是什么: __lt__ 实现 <; 提供它之后 sorted()/min()/max() 才能给对象排序
#           (不提供就要用 key= 参数)。
class Money:
    def __init__(self, cents):
        self.cents = cents

    def __eq__(self, other):
        return isinstance(other, Money) and self.cents == other.cents

    def __lt__(self, other):
        return self.cents < other.cents

m1, m2 = Money(100), Money(100)
print("\n2) m1 == m2  →", m1 == m2)                 # 走 __eq__  → 2) m1 == m2  → True
try:
    hash(m1)
except TypeError as e:
    print("   定义了 __eq__ 后 hash(m1) 报错:", e)   # 这个"坑"就是这里  →    定义了 __eq__ 后 hash(m1) 报错: unhashable type: 'Money'

class MoneyWithHash(Money):
    def __hash__(self):
        return hash(self.cents)                      # 恢复哈希能力

prices = {MoneyWithHash(100): "咖啡"}
print("   实现 __hash__ 后可变 dict 键(映射到值):", prices[MoneyWithHash(100)])  # →    实现 __hash__ 后可变 dict 键(映射到值): 咖啡

amounts = sorted([Money(300), Money(50), Money(200)])   # 排序走 __lt__
print("   sorted() 用 __lt__ 排序:", [m.cents for m in amounts])  # →    sorted() 用 __lt__ 排序: [50, 200, 300]

# ---- 3. __bool__ 与 __len__: 真值判断 ----
# 这是什么: __len__ 实现 len(obj); 附带效果 —— 若没定义 __bool__,
#           bool(obj) 会回退成"len(obj) != 0"(这就是空 list/dict/str 为假的根源)。
# 这是什么: __bool__ 直接定义"这个对象为真/假"的规则, 优先于 __len__ 回退。
class Cart:
    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)

    def add(self, item):
        self.items.append(item)

empty = Cart()
print("\n3) 空购物车 bool:", bool(empty))            # False —— 回退 __len__  → 3) 空购物车 bool: False
empty.add("苹果")
print("   有 1 件商品 bool:", bool(empty))           # True  →    有 1 件商品 bool: True

class Flag:
    """真值规则自定义: 文本里出现 yes/1/true 视为真（覆盖默认回退规则）"""
    def __init__(self, text):
        self.text = text

    def __len__(self):
        return len(self.text)

    def __bool__(self):
        return self.text.lower() in ("1", "yes", "true", "on")

print("   Flag 自定义 bool:", bool(Flag("YES")), bool(Flag("no")))  # →    Flag 自定义 bool: True False

# ---- 4. __getitem__ 与 __contains__: 下标与 in ----
# 这是什么: __getitem__ 实现 obj[key] 下标访问, 让对象"可索引";
#           下标是 int 时走数字索引(list 原生支持负索引),
#           是 slice 时收到切片对象, 返回"切片后的结果" 。
# 这是什么: __contains__ 实现 in 判断; 没有它时 in 会退化为一遍遍 __getitem__。
class MyList:
    def __init__(self, data):
        self.data = list(data)

    def __getitem__(self, index):
        return self.data[index]                          # 转发: int 和 slice 都支持

    def __contains__(self, item):
        return item in self.data

ml = MyList([10, 20, 30, 40])
print("\n4) ml[0]   =", ml[0])  # → 4) ml[0]   = 10
print("   ml[-1]  =", ml[-1], "   # 负索引由 list 转发处理")  # →    ml[-1]  = 40    # 负索引由 list 转发处理
print("   ml[1:3] =", ml[1:3], "   # index 是 slice 对象")  # →    ml[1:3] = [20, 30]    # index 是 slice 对象
print("   20 in ml =", 20 in ml)  # →    20 in ml = True

# ---- 5. __iter__: 让对象可被 for 遍历 ----
# 这是什么: __iter__ 实现 for 循环遍历(返回迭代器对象, 详见 02_generator);
#           for 的本质 = 拿到迭代器后反复 next(), 直到 StopIteration 结束。
class Words:
    def __init__(self, text):
        self.words = text.split()

    def __iter__(self):
        return iter(self.words)

print("\n5) for 遍历 Words:")  # → 5) for 遍历 Words:
for word in Words("hello python world"):
    print("   -", word)
    # 输出:
    #    - hello
    #    - python
    #    - world

# ---- 6. __call__: 让实例像函数一样被调用 ----
# 这是什么: __call__ 实现 obj(...) 调用 —— 实例变成"有状态的函数";
#           常见用途: 构造不同基准的加法器(数学上叫"偏函数"的第一种实现)、
#           计数器、可配置回调。callable(实例) 会返回 True。
class Adder:
    def __init__(self, base):
        self.base = base

    def __call__(self, x):
        return self.base + x

add10 = Adder(10)
print("\n6) add10(5)  =", add10(5))  # → 6) add10(5)  = 15
print("   callable(实例) =", callable(add10))  # →    callable(实例) = True
