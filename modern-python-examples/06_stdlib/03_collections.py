# ============================================================================
# 03_collections.py  现代 Python 示例集 · 06_stdlib 标准库工具箱
# 主题: collections —— 内建 dict/list/tuple 的"专业版"补丁容器
# 解决的问题(基础课):
#   基础课的 dict/list/tuple 够用, 但常见场景总差一点:
#   "数词频还要先 if 键不在就初始化"、"缺了键直接报 KeyError"、
#   "list 头部插入慢"、"元组只能按下标取值记不住哪个是哪个"。
#   collections 提供五个高频专用容器, 一学就会, 用了代码立刻变短。
# 运行: python 03_collections.py
# ============================================================================

from collections import Counter, ChainMap, defaultdict, deque, namedtuple

# ---- 1. Counter: 统计出现次数 + most_common 排行 ----
# 这是什么: Counter —— "计数的 dict": 键是元素、值是次数; 数词频/投票/库存
#           统计时不用手写 if 判断"键在不在"。c["缺失键"] 返回 0 而不是报错。
votes = ["番茄", "土豆", "番茄", "鸡蛋", "番茄", "土豆", "番茄"]
c = Counter(votes)
print("1) Counter 投票统计:")
print("   全部票数   :", dict(c))
print("   番茄几票   :", c["番茄"])
print("   没出现候选 :", c["辣椒"], "  # 缺省返回 0, 不报 KeyError")
print("   most_common(2) 前二:", c.most_common(2))
# 这是什么: c.most_common(n) —— 按次数从高到低取前 n 个 (元素, 次数) 对,
#           榜单/热词统计一行搞定(等价旧写法: sorted(c.items(), key=lambda x: -x[1])[:n])。

# ---- 2. defaultdict: 缺键自动给默认值, 消灭 if 初始化 ----
# 这是什么: defaultdict(工厂) —— 访问不存在的键时, 自动先调用工厂生成默认值
#           存进去再返回。典型用法 defaultdict(list)/defaultdict(int)。
#           对照: dict.setdefault(key, 默认) 每次都要写一长串; defaultdict 一次配好。
word_groups = defaultdict(list)                # 缺键自动变空 list
for w in ["apple", "banana", "avocado", "cherry"]:
    word_groups[w[0]].append(w)               # 按首字母分组, 不用 if w[0] in d
print("\n2) defaultdict 按首字母分组:")
print("   dict(word_groups):", dict(word_groups))
print("   'c' 组:", word_groups["c"])

visit_count = defaultdict(int)                # 缺键自动从 0 开始
for page in ["/", "/cart", "/", "/login"]:
    visit_count[page] += 1                    # 直接 +=, 首次访问自动是 0+1
print("   页面访问计数:", dict(visit_count))

# ---- 3. deque: 双端都能 O(1) 进出的队列 ----
# 这是什么: deque —— "双端队列": 头部和尾部都能高效(popleft/appendleft)。
#           对照: list 从头部 pop(0)/insert(0, x) 是 O(n)(后面元素全要挪一位),
#           数据量大就慢; deque 两端都是 O(1)。配 maxlen 就是"环形缓冲"——
#           装满了自动挤掉最旧的一端(做"最近 N 条"日志/窗口正合适)。
dq = deque(maxlen=5)                          # 环形缓冲: 最多留 5 个
for i in range(1, 8):                         # 塞 7 个, 前两个被自动挤掉
    dq.append(i)
print("\n3) deque(maxlen=5) 环形缓冲:")
print("   塞入 1..7 后:", list(dq), "  # 1,2 被自动挤出")
print("   右端 pop :", dq.pop())
print("   左端 popleft:", dq.popleft())
dq.appendleft(0)
print("   appendleft(0) 后:", list(dq))

# ---- 4. namedtuple: 元组带上字段名 ----
# 这是什么: namedtuple —— "有名字的元组": 还是元组(不可变、可解包、省内存),
#           但每个位置有了字段名, p.x 比 p[0] 可读得多。轻量数据结构
#           (不需要方法时)用它, 比写 class 短; 想加方法就上 dataclass(见 03_typing)。
Point = namedtuple("Point", ["x", "y"])       # 第一个参数是类型名
p = Point(3, 4)
print("\n4) namedtuple:")
print("   p =", p)
print("   p.x + p.y =", p.x + p.y, "   # 字段访问; 也还能 p[0] 按下标")
print("   x, y = p 解包:", end=" ")
x, y = p
print(f"x={x}, y={y}")
try:
    p.x = 99
except AttributeError as e:
    print("   想改 p.x 报错:", e, "  # 与元组一样不可变")

# ---- 5. ChainMap: 多份 dict 的"叠加视图", 逐层查找 ----
# 这是什么: ChainMap(d1, d2, ...) —— 把多个 dict 合成一个"查找链":
#           查键时从前到后逐层找, 第一个命中的返回(前面的优先级高)。
#           对照: dict.update 会把内容"复制"进新 dict(改一份不影响原 dict、
#           每次合并都有复制开销); ChainMap 只是"视图", 零复制,
#           原 dict 变了视图跟着变 —— 层层配置覆盖(默认值 → 环境 → 用户)正好用它。
defaults = {"theme": "light", "lang": "zh", "page_size": 10}
user_cfg = {"theme": "dark"}                  # 用户只改了自己要改的键
cfg = ChainMap(user_cfg, defaults)            # 查键顺序: user_cfg 优先
print("\n5) ChainMap 配置覆盖(用户设置 → 默认值):")
print("   theme     :", cfg["theme"], "   # 命中 user_cfg")
print("   lang      :", cfg["lang"], "    # user_cfg 没有, 落到 defaults")
user_cfg["lang"] = "en"                       # 改原 dict, 视图即时生效
print("   user_cfg['lang']='en' 后 cfg['lang']:", cfg["lang"], "  # 视图跟着变(零复制)")
print("   .maps 可看查找链:", cfg.maps)
