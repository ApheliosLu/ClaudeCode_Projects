# ============================================================================
# 03_itertools.py  现代 Python 示例集 · 02_generator 迭代器与生成器
# 主题: itertools —— 批量处理迭代器的组合工具箱
# 解决的问题(基础课):
#   想要"无限序列 / 拼接多个数据集 / 分组统计 / 密码枚举"等操作只能
#   手写循环; itertools 把最常用的一批迭代模式预置好, 全部惰性求值
#   (不会一步就建出整个大列表), 是 Python "函数式管线"的底座。
# 这是什么: itertools —— 标准库工具模块, 提供一批"迭代器工具函数":
#   无限/有限生成器、组合数学(排列/组合/笛卡尔积)、过滤变换等等;
#   每个函数返回迭代器, 可以用 islice/for/next 按需消费。
# 运行: python 03_itertools.py
# ============================================================================

from itertools import (count, cycle, repeat, islice, chain, tee, groupby,
                       product, permutations, combinations, pairwise,
                       starmap, compress)

# ---- 1. 无限迭代器: count/cycle/repeat + islice 截取 ----
# 这是什么: count(起点, 步长) 无限递增; cycle(序列) 无限重复; repeat(x[, n])
#           反复产出同一个值 —— 三者都需要截取手段(如 islice / next)否则死循环。
print("1) 无限迭代器 + islice:")
print("   list(islice(count(10, 5), 4)) =", list(islice(count(10, 5), 4)))
print("   list(islice(cycle('AB'), 6))  =", list(islice(cycle("AB"), 6)))
print("   list(repeat(7, 3))            =", list(repeat(7, 3)))
# 这是什么: islice —— 迭代器的"切片": 与 list 切片语法类似, 但不建新列表, 直接截前 n 项。
print("   (repeat(x, n) = [x]*n 的惰性版, 拿完 n 个即止)")

# ---- 2. chain: 多个迭代器串成一条 ----
# 这是什么: chain —— 把任意多个可迭代对象"串"成一条流;
#           对比: 列表拼接 x+y+z 只能拼列表, chain 能吃生成器/文件/任何迭代器。
print("\n2) chain:")
print("   list(chain([1,2], (3,4), range(2))) =", list(chain([1, 2], (3, 4), range(2))))

# ---- 3. tee: 一份数据分成两条独立迭代器 ----
# 这是什么: tee —— 把迭代器"克隆"成多个并行的独立迭代器(数据在内存缓存)。
#           注意: 必须在迭代器刚创建还没被消费时 tee, 否则后半段没有了。
print("\n3) tee:")
a, b = tee(iter("abcdef"))          # 一份源, 两条支流
print("   左支流取 2 个:", list(islice(a, 2)))
print("   右支流取 2 个:", list(islice(b, 2)))
print("   (两条流各自从头独立开始 —— 所以 tee 要趁早)")

# ---- 4. groupby: 相邻分组, 必须先排序! ----
# 这是什么: groupby(迭代器, key) —— 按 key 函数把"连续相同键"的元素分组成
#           (键, 子迭代器); 关键规矩: 输入必须先按同一键排序, 否则同名键会被
#           拆成多组(它比较的是"相邻")。
print("\n4) groupby:")
fruits = [("apple", "red"), ("banana", "yellow"), ("apple", "green"),
          ("banana", "ripe"), ("cherry", "red")]
fruits.sort()                                   # 先用键排序(元组默认按第一个元素排)
for name, group in groupby(fruits, key=lambda w: w[0]):
    print(f"   {name}: {[color for _, color in group]}")
print("   (忘了 sort 则 'apple' 会因不在相邻处而分成多组)")

# ---- 5. 组合数学: product / permutations / combinations ----
# 这是什么: product(集合, repeat=n) 笛卡尔积(密码枚举/多维度组合);
#           permutations(集合, r) 排列(有序): n 选 r 排列出不同的顺序;
#           combinations(集合, r) 组合(无序): 只在意选中哪几个。
print("\n5) 排列组合:")
print("   product('ab', repeat=2)    =", list(product("ab", repeat=2)), "   # 笛卡尔积: 2² 种")
print("   permutations('abc', 2)     =", list(permutations("abc", 2)), "   # 有序: 3×2 种")
print("   combinations('abc', 2)     =", list(combinations("abc", 2)), "   # 无序: C(3,2) 种")
print("   数学核对: permutations(5,2)=20, combinations(5,2)=10 →",
      len(list(permutations(range(5), 2))), len(list(combinations(range(5), 2))))
# 密码字典型场景: 全部 2 位小写字母组合:
print("   密码枚举视角: 2 位小写字母全组合 =", 26 ** 2, "种(手写循环要 4 行, 它一行)")

# ---- 6. pairwise: 相邻配对 (3.10 起) ----
# 这是什么: pairwise —— 把相邻两个元素配成 (x0,x1),(x1,x2)...; 3.10 新增,
#           3.12 均有; 常见用途: 列差值、折线图点对、时间序列成对遍历。
print("\n6) pairwise:")
print("   list(pairwise([1,2,3,4])) =", list(pairwise([1, 2, 3, 4])))

# ---- 7. starmap 与 compress: 变参映射 / 布尔过滤 ----
# 这是什么: starmap(函数, 序列) —— 把每个"参数元组"展开传给函数(函数接收
#           多参数时用); compress(序列, 布尔序列) —— 按第二个迭代器的真
#           假值过滤器个元素。
print("\n7) starmap / compress:")
print("   list(starmap(lambda x, y: x * y, [(1,2),(3,4)])) =",
      list(starmap(lambda x, y: x * y, [(1, 2), (3, 4)])))
print("   list(compress('ABCDE', [1,0,1,0,1])) =", list(compress("ABCDE", [1, 0, 1, 0, 1])))

# ---- 8. 实战微例: 常见管线组合 ----
print("\n8) 组合微例: 数字流里每对数的差(pairwise 的典型用法):")
numbers = [10, 25, 40, 55]
print("   相邻差值 =", [b - a for a, b in pairwise(numbers)])
