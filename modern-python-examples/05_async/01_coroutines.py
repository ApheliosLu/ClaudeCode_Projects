# ============================================================================
# 01_coroutines.py  现代 Python 示例集 · 05_async 异步
# 主题: 协程与事件循环 —— async/await 的最小原理
# 解决的问题(基础课/承接 04):
#   线程能并行等 IO, 但线程贵(每个 ~MB 级栈)且切换靠系统; asyncio 换思路:
#   一个线程、一个事件循环, 循环里排队跑无数个"可暂停函数"(协程)——
#   谁在等 IO 谁就暂停让位, 事件循环立刻去跑别人。等 IO 的人多到十万级也不怕。
# 这是什么: async def —— 定义协程函数: 调用它不执行函数体! 只造一个协程对象,
#           等事件循环来调度; await —— 暂停自己, 把控制权还给事件循环
#           ("我在这等, 你先跑别人"), 事件就绪后从暂停处继续。
# 记忆锚点: 线程切换 = 系统强制(随时可能); 协程切换 = 自己让出(只在 await 点)。
#           与 04 的 GIL 让出呼应: threading 里 time.sleep(0) 让出 GIL,
#           这里 asyncio.sleep(0) 让出事件循环。
# 运行: python 01_coroutines.py
# ============================================================================

import asyncio
import sys
import time


async def fetch(name: str, sec: float) -> str:
    """模拟一次网络请求: 等 sec 秒再返回(await 让出期间别人能跑)。"""
    print(f"   [fetch-{name}] 发起请求, 等 {sec}s…")
    await asyncio.sleep(sec)
    return f"[fetch-{name}] 数据到了"


async def main():
    sys.stdout.reconfigure(line_buffering=True)

    # ---- 1. 最小形态: 调用协程函数 ≠ 执行 ----
    # 教学点: async def 的函数, 调用只返回 coroutine 对象, 函数体一行都没跑;
    #         想让它跑: 要么 await 它, 要么交给 asyncio.run/gather/create_task。
    print("1) 协程是'可暂停函数', 调用不执行:")

    async def hello():
        print("   (函数体执行了)")

    c = hello()
    print(f"   hello() 返回: {type(c).__name__} ← 注意上面没有'函数体执行了'")
    await c                                  # 事件循环调度它, 函数体此刻才跑
    print("   await 之后: 函数体执行了\n")

    # ---- 2. asyncio.run + 顺序等待 vs gather 并发 ----
    # 这是什么: asyncio.run(协程) —— 程序入口: 建事件循环、跑完、关循环(一杆子);
    # 这是什么: asyncio.gather(a(), b()) —— 同时调度多个协程, 等全部完成,
    #           返回结果列表(顺序 = 传入顺序)。下面同一批 0.5s 任务:
    #           顺序版逐个等 ≈ 1.0s; gather 版两个一起等 ≈ 0.5s。
    print("2) 顺序 await vs gather 并发(两个 0.5s 的'请求'):")

    async def two_serial():
        await fetch("A", 0.5)
        await fetch("B", 0.5)                # 等 A 完才开始 B

    async def two_parallel():
        await asyncio.gather(fetch("A", 0.5), fetch("B", 0.5))

    t0 = time.perf_counter()
    await two_serial()
    t1 = time.perf_counter()
    await two_parallel()
    t2 = time.perf_counter()
    print(f"   顺序 await: {t1 - t0:.2f}s   gather: {t2 - t1:.2f}s"
          " ← 同是两次 0.5s 等待, 并发几乎减半(两个请求同时在外头飞)")
    print("   (关键: 0.5s 里 CPU 基本闲着 —— 等网络是 asyncio 的主场)\n")

    # ---- 3. asyncio.sleep vs time.sleep: 一个让位, 一个冻住全场 ----
    # 反例教学: 事件循环只有一个线程。谁在协程里调 time.sleep, 整个线程就真睡了,
    #           别的协程(包括 asyncio.sleep 的)全被冻住 —— 新手第一杀手。
    async def bad_io():
        print("   [坏] 我 time.sleep(0.4) 模拟'等待'… 期间全场冻结")
        time.sleep(0.4)                      # 真睡眠: 冻结事件循环 0.4s!
        print("   [坏] time.sleep 结束")

    async def good_io():
        await asyncio.sleep(0.4)             # 让出: 循环去跑别人, 0.4s 后回来

    print("3) asyncio.sleep vs time.sleep(两个 0.4s 任务, 一个用 time.sleep):")
    t0 = time.perf_counter()
    await asyncio.gather(bad_io(), good_io())
    print(f"   总耗时 {time.perf_counter() - t0:.2f}s ≈ 0.8s = 两个任务排队睡"
          " ← 坏任务把循环冻住, good_io 全程没机会跑")
    print("   对照: 第 2 节全用 asyncio.sleep 的 gather = 单任务时长(~0.5s)")
    print("   → 规则: 协程里等东西一律 await, 绝不 time.sleep\n")

    # ---- 4. 协程不 await 的代价(故意留活例子给 GC) ----
    # 教学点: 造了协程对象却既不 await 也不 create_task, 它永远不会执行,
    #         垃圾回收时会打 RuntimeWarning —— 下面的 leftover 在 main 结束
    #         后被回收, 运行末尾(stderr)会看到那条警告(教学故意, 见下注释)。
    print("4) 故意丢弃一个协程(看程序末尾 stderr 的 RuntimeWarning):")
    leftover = fetch("孤儿", 0.1)            # 不 await、不调度 → 永不执行
    print("   已创建但丢弃(函数体不会跑); 这是 bug 信号: 忘了 await 或 return\n")


asyncio.run(main())                          # 入口: 建事件循环跑 main, 完了收摊
