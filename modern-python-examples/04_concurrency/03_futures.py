# ============================================================================
# 03_futures.py  现代 Python 示例集 · 04_concurrency 并发
# 主题: concurrent.futures —— 线程/进程的"统一收银台"
# 解决的问题(承接 01/02):
#   手写 Thread/Process 要自己管 start/join/结果收集, 代码散;
#   futures 把"提交一批任务 → 拿结果"封装成同一个高级接口: 底层用线程还是
#   进程, 只差一个类名 —— 换实现 = 换类名, 业务代码一行不改。
# 这是什么: Executor(执行器) —— 提交任务、返回 Future("未来结果票据":
#           任务还没跑完, 但票据先给你, 之后随时 result() 取)。
#           ThreadPoolExecutor = 线程池(IO 密集用), ProcessPoolExecutor = 进程池
#           (CPU 密集用, Windows 下同样需要 if __name__ 保护, 见 02)。
# 运行: python 03_futures.py
# ============================================================================

import concurrent.futures as cf
import sys
import time

# ---- 顶层工作函数(原因同 02: 进程池要求可 pickle 的顶层函数) ----

def cpu_task(span: int) -> int:
    """CPU 活: 平方和(与 02 的 heavy_calc 同类, 单任务约 0.15s)。"""
    return sum(i * i for i in range(span))


def io_task(sec: float) -> str:
    """IO 活: 睡 sec 秒模拟读网络/查库(线程/进程都在等待, 不占 CPU)。"""
    time.sleep(sec)
    return f"睡了 {sec}s 的 IO 任务"


def boom(x: int) -> int:
    """必炸任务: 演示异常如何从工作线程/进程传回主线程。"""
    return 1 // x                          # x=0 → ZeroDivisionError


def main():
    sys.stdout.reconfigure(line_buffering=True)
    print("0) futures 一分钟: submit 提交任务 → Future 票据 → result() 取结果")
    # 输出: 0) futures 一分钟: submit 提交任务 → Future 票据 → result() 取结果
    print("   (提交的任务在后台线程/进程里跑, 主线程该干嘛干嘛)\n")  # →    (提交的任务在后台线程/进程里跑, 主线程该干嘛干嘛)

    # ---- 1. Executor.map: 换一个类名, 换一种并行 ----
    # 这是什么: ex.map(fn, 可迭代) —— 提交整批任务并等全部结果, 返回结果
    #           迭代器(顺序 = 提交顺序); ThreadPoolExecutor / ProcessPoolExecutor
    #           用法完全相同 —— 下面同一段代码只换类名, 计时天差地别。
    xs = [2_000_000] * 8
    print("1) map: CPU 活 8 个任务, 三种跑法计时:")  # → 1) map: CPU 活 8 个任务, 三种跑法计时:
    t0 = time.perf_counter()
    serial = [cpu_task(x) for x in xs]
    t1 = time.perf_counter()
    with cf.ThreadPoolExecutor(8) as ex:           # 线程池: GIL 下纯 CPU 不加速
        threaded = list(ex.map(cpu_task, xs))
    t2 = time.perf_counter()
    with cf.ProcessPoolExecutor(8) as ex:          # 进程池: 真并行
        processed = list(ex.map(cpu_task, xs))
    t3 = time.perf_counter()
    print(f"   串行       : {t1 - t0:.2f}s")
    # 耗时随机器/负载浮动:
    #    串行       : 0.69s
    print(f"   线程池 8   : {t2 - t1:.2f}s  ← 几乎没快(GIL: 纯算数大家排队)")
    # 耗时随机器/负载浮动:
    #    线程池 8   : 0.71s  ← 几乎没快(GIL: 纯算数大家排队)
    print(f"   进程池 8   : {t3 - t2:.2f}s  ← 明显快(真并行)")
    # 耗时随机器/负载浮动:
    #    进程池 8   : 0.38s  ← 明显快(真并行)
    print(f"   三份结果一致: {serial == threaded == processed}")  # →    三份结果一致: True

    # IO 活反过来: 线程池完胜进程池 —— 线程等 IO 不占 CPU, 启动又便宜;
    # 进程池每个 worker 都要重新导入解释器(本机实测 spawn 开销 ~0.1s/进程)
    print("\n   [对照] IO 活(sleep 0.2s × 8):")  # →    [对照] IO 活(sleep 0.2s × 8):
    xs_io = [0.2] * 8
    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor(8) as ex:
        list(ex.map(io_task, xs_io))
    t1 = time.perf_counter()
    with cf.ProcessPoolExecutor(4) as ex:
        list(ex.map(io_task, xs_io))
    t2 = time.perf_counter()
    print(f"   线程池 8: {t1 - t0:.2f}s  进程池 4: {t2 - t1:.2f}s  ← IO 场景线程池完胜\n")
    # 耗时随机器/负载浮动:
    #    线程池 8: 0.20s  进程池 4: 0.56s  ← IO 场景线程池完胜

    # ---- 2. submit + Future: 单个任务 + 完成状态轮询 ----
    # 这是什么: submit(fn, 参数) —— 提交"一个"任务, 立刻拿回 Future;
    #           fut.done() 查完成没(不阻塞); fut.result() 阻塞直到完成并取结果;
    #           result(timeout=秒) 限时等, 超时抛 TimeoutError。
    # 教学点: 01/02 手动 start/join 的那套, 在这里变成"提交+取票"两步。
    print("2) submit + Future(票据):")  # → 2) submit + Future(票据):
    fut = cf.ThreadPoolExecutor(2).submit(io_task, 1.0)
    time.sleep(0.2)                      # 主线程先干别的
    print(f"   0.2s 后查 done(): {fut.done()} (任务还在睡)")  # →    0.2s 后查 done(): False (任务还在睡)
    r = fut.result()                     # 阻塞等到完成, 取结果
    print(f"   result() 等完取出: {r!r}; done() 现在: {fut.done()}\n")
    # 输出:    result() 等完取出: '睡了 1.0s 的 IO 任务'; done() 现在: True

    # ---- 3. as_completed: 谁先完成先处理谁 ----
    # 这是什么: cf.as_completed([futures]) —— 迭代它 = 按"完成顺序"逐个吐出
    #           已完成任务的 Future; 对比 map 的"按提交顺序" —— 批量场景若想
    #           "最早好的结果先用"(如爬虫先回先解析), 用 as_completed。
    print("3) map(提交序) vs as_completed(完成序):")  # → 3) map(提交序) vs as_completed(完成序):
    delays = [0.4, 0.1, 0.3, 0.2]
    with cf.ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(io_task, d) for d in delays]
        print("   提交顺序:   ", [f"任务{i}" for i in range(4)])  # →    提交顺序:    ['任务0', '任务1', '任务2', '任务3']
        print("   完成顺序:   ", end=" ")
        # end=" " 不换行: 本行与下面循环的输出、以及末尾的"完"拼成同一行; 完成顺序由任务耗时决定:
        #    完成顺序:    任务1 → 任务3 → 任务2 → 任务0 → 完
        for f in cf.as_completed(futs):          # 完成一个吐一个(0.1s 的会最先)
            print(f"任务{futs.index(f)}", end=" → ")
            # 循环按完成先后各输出一段(end=" → ", 不换行):
            # 任务1 → 
            # 任务3 → 
            # 任务2 → 
            # 任务0 → 
        print("完")  # → 完

        # map 同一批任务: 返回顺序固定 = 提交顺序, 哪怕 0.4s 的最后完成
        print("   map 返回序: ", end=" ")
        # end=" " 不换行: 与下面循环输出拼成同一行:
        #    map 返回序:  结果按提交序 结果按提交序 结果按提交序 结果按提交序 
        for _ in ex.map(io_task, delays):
            print("结果按提交序", end=" ")
            # 循环 4 次各输出一段(end=" ", 不换行; 顺序固定 = 提交序):
            # 结果按提交序 
            # 结果按提交序 
            # 结果按提交序 
            # 结果按提交序 
        print("\n")

    # ---- 4. 异常: 在任务里炸, 在 result() 里接 ----
    # 教学点: 工作线程/进程里 raise, 池不会被炸穿 —— 异常被 Future 封存,
    #          等主线程 result()/迭代到它时才重新抛出(带完整 traceback)。
    print("4) 异常传播(任务内 1 // 0):")  # → 4) 异常传播(任务内 1 // 0):
    with cf.ThreadPoolExecutor(2) as ex:
        f = ex.submit(boom, 0)
        time.sleep(0.1)
        print("   任务炸了, 但池还活着(别的任务照常) —— 异常在 result() 时才来:")  # →    任务炸了, 但池还活着(别的任务照常) —— 异常在 result() 时才来:
        try:
            f.result()
        except ZeroDivisionError as e:
            print("   主线程捕获 ZeroDivisionError:", repr(e))
            # 输出:    主线程捕获 ZeroDivisionError: ZeroDivisionError('division by zero')
    print("   (with 退出正常 → 异常没有破坏执行器)\n")  # →    (with 退出正常 → 异常没有破坏执行器)

    # ---- 5. 一句话总结 ----
    print("5) 总结:")  # → 5) 总结:
    print("   * 日常并发首选 futures: 线程池跑 IO 活 / 进程池跑 CPU 活, 代码同款")
    # 输出:    * 日常并发首选 futures: 线程池跑 IO 活 / 进程池跑 CPU 活, 代码同款
    print("   * map = 整批提交按序收; submit = 单票, 何时取随意; as_completed = 完成序")
    # 输出:    * map = 整批提交按序收; submit = 单票, 何时取随意; as_completed = 完成序
    print("   * 任务里的异常在 result() 时抛回主线程 → try/except 围在取结果处")  # →    * 任务里的异常在 result() 时抛回主线程 → try/except 围在取结果处


if __name__ == "__main__":               # Windows 进程池的生命线(同 02)
    main()
