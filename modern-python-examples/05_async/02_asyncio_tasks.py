# ============================================================================
# 02_asyncio_tasks.py  现代 Python 示例集 · 05_async 异步
# 主题: 任务编排 —— create_task / wait_for / to_thread / Queue / TaskGroup
# 解决的问题(承接 01):
#   01 只有"await 一个协程", 真实程序要的是: 后台挂多个任务、限时等待、
#   把同步阻塞代码丢出循环、任务间传数据、一组任务"要么全成要么全撤"。
# 这是什么: Task —— 被事件循环调度的协程(比协程多了"可取消/可查状态");
#           create_task 提交协程 → Task 立刻在后台排队, 主流程不等它;
#           Task 是 Future(04 见过的票据概念)的 asyncio 版。
# 运行: python 02_asyncio_tasks.py
# ============================================================================

import asyncio
import sys
import time

# ---- 同步阻塞函数(演示用): 真实项目里是 requests 请求 / cv2 处理 / 大文件读 ----
def blocking_search(keyword: str) -> str:
    """同步阻塞操作: 睡 0.4s 模拟一段'不让出'的重活(比如 C 扩展库的调用)。"""
    time.sleep(0.4)
    return f"阻塞搜索结果: {keyword} × N"


async def job(name: str, sec: float) -> str:
    """普通异步任务: await 让出。"""
    await asyncio.sleep(sec)
    return f"{name} 完成(耗时 {sec}s)"


async def main():
    sys.stdout.reconfigure(line_buffering=True)

    # ---- 1. create_task: 提交后台任务, 不等 ----
    # 教学点: 直接 await job(...) 会等它跑完才继续; create_task 则是
    #         "派个后台任务, 我继续干别的", 之后按需 await 收回结果。
    print("1) create_task: 后台任务不挡道:")
    task = asyncio.create_task(job("后台下载", 0.3))   # 提交即排队(不立刻跑)
    print("   已提交后台任务, 主流程继续…(任务稍后自己开始)")
    await asyncio.sleep(0.05)               # 主流程干点别的(后台任务趁机开跑)
    print("   主流程忙完别的, 现在 await 收结果:")
    print("   →", await task)                # 等后台任务完成并取回返回值
    print("   (create_task 返回 Task —— Future 的 asyncio 版, 票据概念同 04/03)\n")

    # ---- 2. wait_for: 限时等待, 超时即取消 ----
    # 这是什么: asyncio.wait_for(协程, timeout=秒) —— 给等待设上限: 超时抛
    #           TimeoutError(3.11+ 就是内置 TimeoutError), 且被等的任务会被
    #           取消(CancelledError 注入) —— 见 slow_task 里的 except。
    print("2) wait_for 限时(任务要 5s, 只等 0.3s):")

    async def slow_task():
        try:
            await asyncio.sleep(5)          # 模拟慢 API
        except asyncio.CancelledError:      # 被 wait_for 取消时收到这个
            print("   [slow_task] 收到取消信号, 清理后退出")
            raise                           # 取消必须继续向上抛(CancelledError 惯例)
        return "不可能到这"

    try:
        await asyncio.wait_for(slow_task(), timeout=0.3)
    except TimeoutError:
        print("   主流程捕获 TimeoutError → 等 0.3s 就放弃了, 不再干等 5s")
    print("   (asyncio.TimeoutError 在 3.11+ 与内置 TimeoutError 是同一个)\n")

    # ---- 3. to_thread: 把同步阻塞函数丢进线程, 循环不冻 ----
    # 这是什么: asyncio.to_thread(fn, *args) —— 把 fn 丢给线程池跑, 协程 await
    #           它结束。解决 01 节 3 的灾难: 阻塞调用(requests/cv2/纯 CPU)
    #           直接 await 不了, 丢线程是最省事的隔离(3.9+; 旧写法
    #           loop.run_in_executor(None, fn, ...) 更啰嗦)。
    print("3) to_thread: 阻塞调用不冻结循环:")
    t0 = time.perf_counter()
    blocker = asyncio.to_thread(blocking_search, "py")  # 0.4s 阻塞活在后台线程
    fast = asyncio.create_task(job("快速小任务", 0.05))
    print("   [快速小任务]", await fast)      # 先回来 = 循环没被 blocker 冻住
    print("   [blocker]", await blocker)     # 0.4s 后阻塞结果到达
    print(f"   总耗时 {time.perf_counter() - t0:.2f}s"
          " ≈ 0.4s + 线程启动开销 → 阻塞活没挡住别人")
    print("   (关键证据是打印顺序: 快速任务在 blocker 之前就完成了 ——")
    print("    若循环被 0.4s 阻塞冻住, 它得干等到 0.4s 之后才有机会)\n")

    # ---- 4. asyncio.Queue: 协程间的生产-消费 ----
    # 这是什么: asyncio.Queue —— 与 04/01 的 queue.Queue 同款 API(maxsize/put/
    #           get), 差别只在 put/get 要 await(满了/空了就挂起让位)。
    print("4) asyncio.Queue 生产者-消费者:")
    q: "asyncio.Queue[int | None]" = asyncio.Queue(maxsize=2)

    async def producer():
        for i in range(1, 4):
            await asyncio.sleep(0.05)       # 慢速产出
            await q.put(i)                  # 满了会挂起等消费者取走
            print(f"   生产者放入 {i}")
        await q.put(None)                   # 毒药丸(同 04 的惯例)

    async def consumer():
        while True:
            item = await q.get()
            if item is None:
                print("   消费者收到结束信号\n")
                return
            print(f"      消费者处理 {item}")

    await asyncio.gather(producer(), consumer())

    # ---- 5. TaskGroup: 一组任务, 一个失败全员撤退 ----
    # 这是什么: asyncio.TaskGroup(3.11 新增; 3.12 均有) —— async with 里创建
    #           的任务组成一组: 组内任一任务抛异常 → 其余任务全部取消 → 等
    #           全部收尾后把异常聚合成 ExceptionGroup 抛出(07_errors/02 细讲)。
    #           旧写法: ensure_future + gather + 手动 cancel, 样板多还易漏。
    # 教学点: 适合"三处都要成功, 一处失败就整体回滚"的批处理(如并行存三个表)。
    print("5) TaskGroup(3.11+): 一组任务, 一个失败全员撤退:")

    async def good(name: str, sec: float):
        try:
            await asyncio.sleep(sec)
            print(f"   [good-{name}] 成功(睡了 {sec}s)")
        except asyncio.CancelledError:
            print(f"   [good-{name}] 被组取消(组里有人失败了)")

    async def bad():
        await asyncio.sleep(0.2)
        raise ValueError("数据库写入失败")

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(good("A", 0.1))
            tg.create_task(bad())
            tg.create_task(good("B", 0.8))   # 会因 bad() 失败被取消
    except ExceptionGroup as eg:            # 组异常聚合抛出
        print(f"   主流程捕获 ExceptionGroup, 内含 {len(eg.exceptions)} 个异常:")
        for e in eg.exceptions:
            print(f"     - {type(e).__name__}: {e}")
    print("   (A 0.1s 已完成没被波及; B 睡 0.8s 未完成 → 被取消 → 全员撤退语义)\n")

    # ---- 6. 小结 ----
    print("6) 任务编排口诀:")
    print("   * 一个任务慢慢等 → await; 多个任务一起 → gather")
    print("   * 后台任务不等它 → create_task; 限时等待 → wait_for")
    print("   * 同步阻塞/CPU 活 → to_thread(别裸调, 会冻循环)")
    print("   * 协程间传数据 → asyncio.Queue; 同生共死 → TaskGroup")


asyncio.run(main())
