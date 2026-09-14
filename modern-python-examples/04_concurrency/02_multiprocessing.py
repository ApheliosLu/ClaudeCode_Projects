# ============================================================================
# 02_multiprocessing.py  现代 Python 示例集 · 04_concurrency 并发
# 主题: multiprocessing —— 绕开 GIL 的 CPU 并行
# 解决的问题(基础课/承接 01):
#   01 说 CPU 密集别用线程(GIL), 那用什么? —— 多进程: 开 N 个 Python 解释器,
#   各自有独立内存与独立 GIL, 在多核 CPU 上真·同时执行。
# 这是什么: multiprocessing —— 标准库多进程模块, API 长得像 threading,
#   但进程是"操作系统级任务": 启动贵、内存独立、崩溃隔离。
# 先读这段再跑(Windows/macOS 必须懂):
#   Windows 没有 fork(Linux 那种"复制父进程内存"的启动方式), 只能 spawn:
#   启动子进程 = 重新导入本文件 → 再执行目标函数。两个推论:
#   1) 演示代码全放 main(), 顶层只放 def —— 否则每个子进程都会把顶层代码
#      再跑一遍(无限开进程/重复打印);
#   2) 传给 Process/Pool 的函数必须写在模块顶层(能 pickle 的函数名),
#      不能用 lambda/嵌套函数。
# (3.12 及之前: 同款写法; 3.13 起出现 free-threaded 实验构建[无 GIL] ——
#  若未来默认启用, "CPU 密集用线程"或成可能; 但现在本机默认版仍有 GIL,
#  本文件的结论对当前所有主流发行版依然成立。)
# 运行: python 02_multiprocessing.py
# ============================================================================

import multiprocessing as mp
import os
import sys
import time

# ---- 顶层工作函数(原因见头部注释: spawn 只认顶层可 pickle 的函数) ----

def heavy_calc(x: int) -> int:
    """CPU 重活: 算 0..x-1 的平方和(纯 Python 循环, 吃满单核)。"""
    return sum(i * i for i in range(x))


def add_no_lock(counter, _lock):
    for _ in range(N):
        v = counter.value
        counter.value = v + 1


def add_with_lock(counter, lock):
    for _ in range(N):
        with lock:
            v = counter.value
            counter.value = v + 1


def producer(q):
    """子进程算好结果, 经 Queue 送回主进程(进程间不能直接 return)。"""
    for i in range(1, 6):
        time.sleep(0.1)                 # 模拟"边算边报进度"
        q.put(f"任务 {i} 完成: {i} ** 2 = {i * i}")


def say_pid():
    """第 1 节演示: 让子进程报自己的 pid(必须顶层函数, lambda 不可 pickle)。"""
    print("   子进程说: 我在干活, 我的 pid =", os.getpid())
    # pid 每次运行不同:
    #    子进程说: 我在干活, 我的 pid = 13268


N = 100_000                              # 共享计数器每进程累加次数


# ============================================================================
def main():
    sys.stdout.reconfigure(line_buffering=True)      # 行缓冲: 子进程的 print 不乱插队
    print("0) 为什么需要多进程:")  # → 0) 为什么需要多进程:
    print("   01 结论: CPU 密集用线程 = GIL 一个线程在算, 其余干等(实测几乎零加速)")  # →    01 结论: CPU 密集用线程 = GIL 一个线程在算, 其余干等(实测几乎零加速)
    print("   → 这次直接开多个 Python 解释器(进程), 各算各的, 真并行")  # →    → 这次直接开多个 Python 解释器(进程), 各算各的, 真并行
    print("   (代价: 每个子进程都有一份解释器内存 → 大对象别复制着用)\n")  # →    (代价: 每个子进程都有一份解释器内存 → 大对象别复制着用)

    # ---- 1. Process + join: 最小的"开一个子进程" ----
    # 这是什么: Process(target=函数, args=(参数,)) —— 造一个子进程(不立即跑);
    #           start() 让它跑起来; join() 等它结束(与 threading.Thread 同款三步)。
    # 教学点: 子进程的 print 能打出来 = 它真的在另一个解释器里执行了;
    #         两边的 os.getpid() 不同 = 确实是"两个程序"。
    print("1) Process + join(最小组件):")  # → 1) Process + join(最小组件):
    p = mp.Process(target=say_pid)
    p.start()
    print("   主进程 pid =", os.getpid(), "→ 启动子进程")
    # pid 每次运行不同; 与下一行谁先打印取决于进程调度:
    #    主进程 pid = 10872 → 启动子进程
    p.join()                             # 主进程在这里等子进程跑完
    print("   子进程已结束(join 返回)\n")  # →    子进程已结束(join 返回)

    # ---- 2. Pool.map: CPU 重活并行(真加速实证) ----
    # 这是什么: mp.Pool(进程数) —— 进程池: 预先开好 N 个工作进程, map 把任务
    #           列表分发给它们并行执行, 一次性回收结果列表(接口像内置 map)。
    # 教学点 1: 串行 vs 8 进程, 同一批任务, 计时对比 —— 这就是"并行加速";
    # 教学点 2: 8 进程却没快 8 倍(实测约 2~3 倍)! 为什么? spawn 每个子进程要
    #           重新导入解释器(启动开销) + 任务分发的通信开销 + 每个任务只能
    #           用一个核 → "核多 ≠ 线性加速", 任务够大才值得开进程。
    print("2) Pool.map: CPU 重活并行(8 个任务 × 400 万平方和):")  # → 2) Pool.map: CPU 重活并行(8 个任务 × 400 万平方和):
    xs = [4_000_000] * 8
    t0 = time.perf_counter()
    serial = [heavy_calc(x) for x in xs]                     # 串行基准
    t1 = time.perf_counter()
    with mp.Pool(8) as pool:                                 # 池用完自动收尾
        parallel = pool.map(heavy_calc, xs)                  # 同款接口, 并行版
    t2 = time.perf_counter()
    print(f"   串行:     {t1 - t0:.2f}s")
    # 耗时随机器/负载浮动:
    #    串行:     1.49s
    print(f"   Pool(8): {t2 - t1:.2f}s   ← 加速比 {(t1 - t0) / (t2 - t1):.1f}x")
    # 耗时随机器/负载浮动:
    #    Pool(8): 0.51s   ← 加速比 2.9x
    print(f"   结果一致: {serial == parallel}(两种方式结果完全相同)\n")  # →    结果一致: True(两种方式结果完全相同)

    # ---- 3. Value/Array 共享内存 + Lock(进程版竞争!) ----
    # 这是什么: mp.Value("i", 0) —— 一块跨进程共享的小内存(类型码 "i"=int);
    #           mp.Array 同族(共享列表)。进程内存本不互通, 这是显式开的"后门"。
    # 对照 01 的重大差异(实测): 线程版纯循环无锁不丢(被 GIL 掩护),
    #   进程版是多个解释器在多核上真并行, 纯循环的"读-改-写"也必被打断!
    #   → 无锁丢不丢不用赌, 共享状态一律加锁(Lock 的用法和线程版完全相同)。
    print(f"3) 共享内存 Value + Lock(两进程各 +{N:,} 次):")  # → 3) 共享内存 Value + Lock(两进程各 +100,000 次):
    counter = mp.Value("i", 0)
    lock = mp.Lock()
    ps = [mp.Process(target=add_no_lock, args=(counter, lock)) for _ in range(2)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    print(f"   无锁:   {counter.value:,}  ← 目标 {2 * N:,}, 丢 {2 * N - counter.value:,}"
          " 次(真并行下'读-改-写'互相覆盖, 没有 GIL 挡着)")
          # 无锁结果每次不同(本例 131,600), 必远小于 200,000:
          #    无锁:   131,600  ← 目标 200,000, 丢 68,400 次(真并行下'读-改-写'互相覆盖, 没有 GIL 挡着)

    counter2 = mp.Value("i", 0)
    lock2 = mp.Lock()
    ps = [mp.Process(target=add_with_lock, args=(counter2, lock2)) for _ in range(2)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    print(f"   加 Lock: {counter2.value:,} ← 恰好, 锁跨进程同样生效\n")  # →    加 Lock: 200,000 ← 恰好, 锁跨进程同样生效

    # ---- 4. Queue: 进程间通信(送结果回主进程) ----
    # 这是什么: mp.Queue —— 跨进程队列: 数据会被 pickle 序列化后经管道搬运,
    #           所以"对象穿越进程边界"靠它(与 01 的线程 Queue 同名同用,
    #           内部实现不同: 线程版是共享内存+锁, 进程版是序列化+管道)。
    print("4) 进程间通信(Queue):")
    q = mp.Queue()
    wp = mp.Process(target=producer, args=(q,))
    wp.start()
    for _ in range(5):                   # 主进程边等边收
        print("   主进程收到:", q.get())
        # 循环 5 次, 每收到一个任务结果输出一行:
        #    主进程收到: 任务 1 完成: 1 ** 2 = 1
        #    主进程收到: 任务 2 完成: 2 ** 2 = 4
        #    主进程收到: 任务 3 完成: 3 ** 2 = 9
        #    主进程收到: 任务 4 完成: 4 ** 2 = 16
        #    主进程收到: 任务 5 完成: 5 ** 2 = 25
    wp.join()
    print("   (子进程 return 的东西主进程拿不到 → 结果一律走 Queue 类通道)\n")  # →    (子进程 return 的东西主进程拿不到 → 结果一律走 Queue 类通道)

    # ---- 5. 取舍总结 ----
    print("5) 取舍总结(什么时候用哪个):")  # → 5) 取舍总结(什么时候用哪个):
    print("   * CPU 密集(纯计算/训练/图像): 多进程 → 真并行; 代价: 启动贵、")  # →    * CPU 密集(纯计算/训练/图像): 多进程 → 真并行; 代价: 启动贵、
    print("     每进程一份解释器内存、任务太小(毫秒级)时并行反而更慢")  # →      每进程一份解释器内存、任务太小(毫秒级)时并行反而更慢
    print("   * IO 密集(网络/文件/爬虫): 线程或协程就够 → 别用进程(启动开销白花)")  # →    * IO 密集(网络/文件/爬虫): 线程或协程就够 → 别用进程(启动开销白花)
    print("   * 进程间别惦记共享变量: 内存不互通, 通信走 Queue/Pipe")  # →    * 进程间别惦记共享变量: 内存不互通, 通信走 Queue/Pipe
    print("   * 32 核机器 ≠ 32 倍速: 实测 8 进程只有 ~3 倍(见第 2 节), 加速有上限")
    # 输出:    * 32 核机器 ≠ 32 倍速: 实测 8 进程只有 ~3 倍(见第 2 节), 加速有上限


if __name__ == "__main__":               # 这行是 Windows spawn 的生命线
    main()                               # (少了它: 每个子进程会把 main 重跑一遍)
