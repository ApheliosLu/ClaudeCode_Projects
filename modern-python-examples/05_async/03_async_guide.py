# ============================================================================
# 03_async_guide.py  现代 Python 示例集 · 05_async 异步
# 主题: 什么时候用异步 —— 决策表与反模式
# 解决的问题(收束 01/02):
#   会写 asyncio 不等于该用 asyncio。这个文件给"我这个场景要不要异步"的
#   决策表 + 三句行内反模式, 帮你把 async 用在刀刃上、避开经典坑。
# 运行: python 03_async_guide.py
# ============================================================================

import asyncio
import sys
import time


async def main():
    sys.stdout.reconfigure(line_buffering=True)

    # ---- 1. 决策表: 先问自己"我在等什么" ----
    # 判断树(注释即口诀):
    #   "要并发等的东西" 是网络/磁盘/数据库? 且量大(百千级)?
    #     → asyncio(01/02: 等待时 CPU 闲着, 让位给别人)
    #   是"算"?(CPU 密集, 如训练/图像处理)
    #     → 别来 asyncio! 去 04: multiprocessing / ProcessPoolExecutor
    #   是第三方阻塞库?(requests/cv2/pandas 这类同步库, 改不了)
    #     → to_thread 丢线程(02/03), 或干脆用线程/进程池整段跑
    #   其实只是"串一串 IO 很简单"?
    #     → 同步代码 + 线程池就够, 别上 async(复杂度是债, 同 04 结论)
    print("1) 决策表(想清楚再动手):")
    print("   ┌────────────┬────────────────────────────────────┐")
    print("   │ 场景        │ 结论                              │")
    print("   ├────────────┼────────────────────────────────────┤")
    print("   │ 大量网络 IO │ asyncio(单循环跑千级并发等待)      │")
    print("   │ (爬虫/网关) │ ← 这是 async 唯一的舒适区         │")
    print("   │ CPU 密集    │ multiprocessing / 进程池(见 04)    │")
    print("   │ 阻塞库调用  │ to_thread / 线程池(02/03 已演示)    │")
    print("   │ 简单串行脚本│ 同步就完事, 别引 async             │")
    print("   └────────────┴────────────────────────────────────┘\n")

    # ---- 2. 反模式一: 在协程里跑同步阻塞(01/03 的延伸) ----
    # time.sleep 已实测会冻结全场(01 节 3: 两任务排队睡 0.8s)。
    # 同族杀手: requests.get(同步网络库! 请用 httpx/aiohttp 或丢线程)、
    #           cv2.imread / pandas.read_csv / 任何 C 扩展的重活 ——
    #           它们要么阻塞要么占用 GIL, 在协程里都是"不让出"。
    # 自检: async 函数体里若找不到几个 await, 它就不是异步函数。
    print("2) 反模式一(记住, 不必重跑): 协程里裸调阻塞库 = 冻住全场")
    print("   time.sleep 实测 0.8s(01); requests/cv2/pandas 同族 —— 一律 to_thread\n")

    # ---- 3. 反模式二: async 代码里用 threading.Lock ----
    # 为什么错: 事件循环是单线程协作式 —— 根本不需要"跨线程锁"。
    #   1) threading.Lock 非重入: 同线程内二次 acquire 直接死锁(自杀);
    #   2) 语义错位: 你要的"await 期间别人不能进"由事件循环保证,
    #      加 threading.Lock 只会让协程在 await 点把锁状态搞得一团糟;
    #   3) 若将来用 run_in_executor 混线程, 锁的归属更说不清。
    # 正解: asyncio.Lock —— 用法与 threading.Lock 同款, 但可跨 await 持锁
    #   (await 让出时锁不松; 别的协程 acquire 会挂起排队)。
    print("3) asyncio.Lock(threading.Lock 的 async 正解):")
    printer = asyncio.Lock()

    async def print_job(name: str, sec: float):
        async with printer:                 # 拿不到就挂起等(await 点! 不轮询)
            print(f"   [{name}] 进入打印区, 开始…")
            await asyncio.sleep(sec)        # 持锁让出: 别的协程进不来
            print(f"   [{name}] 打印完毕, 退出\n")

    await asyncio.gather(print_job("A", 0.1), print_job("B", 0.05))
    print("   看输出: A 完整跑完 B 才进 —— 若没锁/用错锁, B 会插进 A 中间")
    print("   (threading.Lock 同线程二次 acquire 死锁 → 千万别在协程里用)\n")

    # ---- 4. 反模式三: async 函数里没有 await(伪异步) ----
    # 教学点: async def 体内没有 await = 函数从头到尾"不让出",
    #   事件循环拿到它只能一口气跑完 —— 等价同步函数, 还多一层包装。
    #   给"同步逻辑却标 async"的代码: 等它等于同步等, 并发收益为零。
    async def fake_async():
        total = 0
        for i in range(3_000_000):          # 纯 CPU 循环, 无 await
            total += i * i
        return total

    async def fast_job():
        await asyncio.sleep(0.05)
        return "小任务完成"

    t0 = time.perf_counter()
    await asyncio.gather(fake_async(), fast_job())
    print(f"4) 伪异步演示: 0.3 秒级 CPU 循环 + 0.05s 小任务并发")
    print(f"   总耗时 {time.perf_counter() - t0:.2f}s —— 小任务被 CPU 循环挡住,")
    print("   等它跑完才有机会: async 救不了 CPU 活(不让出 = 同步)")
    print("   → CPU 活丢进程池(to_thread 也只是借线程, 同样治标不治本)\n")

    # ---- 5. 收尾清单 ----
    print("5) 最后清单(写异步前逐条过):")
    print("   □ 我的瓶颈真的是'大量并发等待'吗?(不然别用)")
    print("   □ 协程内没有裸阻塞调用?(time.sleep/requests/cv2… → to_thread)")
    print("   □ 锁用的是 asyncio.Lock?(threading.Lock 是坑)")
    print("   □ 长的 CPU 段已移出协程?(事件循环需要让出点)")
    print("   □ 每个协程最终都被 await/gather/create_task 收走了?")


asyncio.run(main())
