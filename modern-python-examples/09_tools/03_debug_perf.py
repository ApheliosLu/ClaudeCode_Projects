# ============================================================================
# 03_debug_perf.py  现代 Python 示例集 · 09_tools 工程工具
# 主题: 调试与性能 —— timeit 测速 + cProfile 定位慢函数 + 两个性能常识
# 解决的问题(基础课):
#   "感觉有点慢"要变成"证据": ① 一小段代码多快 → timeit;
#   ② 整个程序慢在哪个函数 → cProfile; ③ 常见写法坑:
#   字符串 += 循环(见第 1 节)与裸 for 拼列表(见第 2 节)。
# 运行: python 03_debug_perf.py
# ============================================================================

import cProfile
import io
import pstats
import sys
import timeit

sys.stdout.reconfigure(line_buffering=True)

# ---- 1. timeit: 字符串 += 循环 vs join(实测差距 ~100 倍) ----
# 这是什么: timeit.timeit(函数, number=N) —— 把函数跑 N 次取总时长(自动
#           关 GC 排除干扰)。测速小片段的标准工具(比手写 time.perf_counter
#           稳: 排除了系统噪声与循环开销的统计口径)。
# 这是什么: 为什么 join 快 —— 字符串不可变, 每次 += 都要"复制整份旧串再
#           追加" → 总代价 O(n²); join 先收集再一次性分配, O(n)。
#           所以循环里拼字符串是性能反模式, 一律收集到 list 再 join。
CHUNK = "x" * 200
N_LOOP = 8000

def slow_concat():
    s = ""
    for _ in range(N_LOOP):
        s += CHUNK                       # O(n²): 每次整串复制
    return s

def fast_join():
    return "".join([CHUNK] * N_LOOP)     # O(n): 一次分配

t_slow = timeit.timeit(slow_concat, number=3)
t_fast = timeit.timeit(fast_join, number=3)
print("1) 字符串拼接: += 循环 vs join(timeit, 3 次合计):")  # → 1) 字符串拼接: += 循环 vs join(timeit, 3 次合计):
print(f"   += 循环 : {t_slow:.4f}s")
# 耗时随机器/负载浮动:
#    += 循环 : 0.1005s
print(f"   join    : {t_fast:.4f}s   ← 快 {t_slow / t_fast:.0f} 倍")
# 倍率随机器浮动:
#    join    : 0.0009s   ← 快 114 倍
print("   结论: 循环拼串用 += 是 O(n²) 反模式, 收集进 list 再 join")  # →    结论: 循环拼串用 += 是 O(n²) 反模式, 收集进 list 再 join

# ---- 2. timeit: 裸 for 循环 vs 列表推导 ----
# 这是什么: 列表推导比裸 for+append 快(推导的循环在解释器内部优化执行);
#           且可读性更好。规则: 能用推导就不要手写空 list + for + append。
def slow_build():
    out = []
    for i in range(1_000_000):
        out.append(i * i)
    return out

def fast_build():
    return [i * i for i in range(1_000_000)]

t_sb = timeit.timeit(slow_build, number=2)
t_fb = timeit.timeit(fast_build, number=2)
print("\n2) 造 100 万整数平方: 裸 for vs 推导(timeit, 2 次合计):")  # → 2) 造 100 万整数平方: 裸 for vs 推导(timeit, 2 次合计):
print(f"   for+append: {t_sb:.3f}s")
# 耗时随机器浮动:
#    for+append: 0.084s
print(f"   列表推导  : {t_fb:.3f}s   ← 快 {t_sb / t_fb:.2f} 倍")
# 倍率随机器浮动:
#    列表推导  : 0.073s   ← 快 1.16 倍
# 实测注(3.14): 3.11+ 的自适应特化把 for+append 优化得很接近推导, 纯数值
# 场景差距只剩 ~1.1 倍(早版本差距明显更大)。真正理由转向可读性:
print("   实测结论: 差距仅 ~1.1 倍(3.11+ 特化后)—— 推导更短、无'忘初始化'")  # →    实测结论: 差距仅 ~1.1 倍(3.11+ 特化后)—— 推导更短、无'忘初始化'
print("   类低级错误, 仍是首选; 差距放大的场景是推导带条件过滤/复合映射")  # →    类低级错误, 仍是首选; 差距放大的场景是推导带条件过滤/复合映射

# ---- 3. cProfile: 整个程序慢在哪 —— 看函数级耗时排名 ----
# 这是什么: cProfile —— 标准库性能剖析器: 记录每个函数被调多少次、累计耗时,
#           pstats 负责排序展示。定位"热点"的标准流程:
#           python -m cProfile 你的脚本.py(或如本文件用 API 包一段)。
# 这是什么: 摘要头字段 —— ncalls 调用次数 / tottime 函数自身耗时(不含子调用,
#           排热点看它)/ cumtime 含子调用总耗时 / percall 单次平均。
def do_report_job():
    data = [i * 2 for i in range(200_000)]          # 造数据
    data.sort(reverse=True)                          # 排序
    total = sum(data)                                # 求和
    return total

prof = cProfile.Profile()                            # 开剖析
prof.enable()
result = do_report_job()
prof.disable()

buf = io.StringIO()
pstats.Stats(prof, stream=buf).sort_stats("tottime").print_stats(8)
print("\n3) cProfile 热点剖析(do_report_job 内部):")  # → 3) cProfile 热点剖析(do_report_job 内部):
print(f"   任务结果: {result}")  # →    任务结果: 39999800000
print("   " + "-" * 66)  # →    ------------------------------------------------------------------
lines = buf.getvalue().splitlines()
for line in lines[:14]:                              # 摘要头 + 前几行热点
    print("   " + line.rstrip())
    # cProfile 摘要(cumtime 等数值随机器浮动, 行首空格已含在输出里):
    #             4 function calls in 0.007 seconds
    #    
    #       Ordered by: internal time
    #    
    #       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    #            1    0.005    0.005    0.007    0.007 <脚本路径>:73(do_report_job)
    #            1    0.001    0.001    0.001    0.001 {method 'sort' of 'list' objects}
    #            1    0.000    0.000    0.000    0.000 {built-in method builtins.sum}
    #            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
    #    
    #    
print("   " + "-" * 66)  # →    ------------------------------------------------------------------
print("   找最慢: 看 tottime 最大的一行(本任务是排序/推导/求和三者)")  # →    找最慢: 看 tottime 最大的一行(本任务是排序/推导/求和三者)
print("   (完整文件剖析: python -m cProfile -s tottime 你的脚本.py)")  # →    (完整文件剖析: python -m cProfile -s tottime 你的脚本.py)

# ---- 4. 指向: 记忆化加速已演示于 06_stdlib/04_functools.py ----
# lru_cache/@cache 也是性能手段(重复子问题缓存), 完整演示见 06_stdlib/04;
# 这里不再重复 —— 记住工具箱位置即可:
print("\n4) 相关工具位置: 记忆化 @cache → 06_stdlib/04 | 日志排查 → 06_stdlib/02")
# 输出: 4) 相关工具位置: 记忆化 @cache → 06_stdlib/04 | 日志排查 → 06_stdlib/02
