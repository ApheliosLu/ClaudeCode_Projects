# ============================================================================
# 01_gil_threads.py  现代 Python 示例集 · 04_concurrency 并发
# 主题: GIL 与 threading —— 线程是怎么回事、竞争怎么防
# 解决的问题(基础课):
#   基础课全是单线程: 程序卡住就卡住, 想"下载同时算数据"没门;
#   Python 线程就能做到"并行等待 IO"; 但自带一个让新手迷路的设定 —— GIL。
# 这是什么: GIL(全局解释器锁) —— CPython 解释器里的一个全局锁: 任何时刻只
#   有一个线程在执行字节码(注意: 只是"实现细节", 不是语言规范; 别的原
#   理实现如 Jython 无此锁)。后果: 多线程用于"并发等待"(IO 密集)很有效,
#   用于"同时算数"(CPU 密集)却几乎不加速 —— 这才有"CPU 密集用多进程"的行规。
# (3.13 新增) 可编译"自由线程(free-threaded)"构建, 运行时用
#   sys._is_gil_enabled() 探测: 返回 False 即本解释器没装 GIL(本机默认版为 True)。
# 运行: python 01_gil_threads.py
# ============================================================================

import os
import queue
import sys
import threading
import time

print("0) 环境快照:")
print("   CPU 核数(os.cpu_count) =", os.cpu_count())
print("   sys._is_gil_enabled() =", sys._is_gil_enabled(),
      "  # (3.13 起提供; False = 本程序运行在自由线程构建)")

# ---- 1. 数据竞争: 无锁 vs 加锁 ----
# 竞争的本质: counter += 1 在底层是"读 → 改 → 写"三步, 两个线程的交错可能
# 互相覆盖: 线程 A 读了旧值, 还没写回, 线程 B 也读了旧值并写回; A 再写回时
# 就把 B 的 +1 覆盖了(损失一次)。锁(Lock)保证这段"读改写"原子成块, 谁也不能插队。
# 一个重要事实(3.13/3.14 实测): 纯字节码的 counter += 1 循环, 无锁也几乎不丢!
#   原因: 3.13 起 GIL 切换只在"eval 分支点"(极稀)发生, 而"读改写"三步之间没有
#   检查点 —— 老教程里"跑几次必然出竞争"的演示在新版本跑不出损失。
#   但"真实竞争场景"往往命中: 临界区里带着 IO/睡眠(读网络/查库/写文件都会让出
#   GIL), 切换就落进"读改写"窗口中间 → 必丢。下面用展开三步 + sleep(0) 模拟,
#   sleep(0) = "本次让出执行权但不真睡", 是最小粒度的让出(任何系统调用/IO 同理)。
N = 200_000

def race_counter(with_lock: bool):
    counter = 0
    lock = threading.Lock()

    def loop():
        nonlocal counter
        for _ in range(N):
            if with_lock:
                with lock:
                    # 读-改-写在锁内原子成块, sleep(0) 也插不进来
                    v = counter
                    time.sleep(0)
                    counter = v + 1
            else:
                # 无锁: sleep(0) 让出 GIL 时, 另一个线程可能已把 counter 改了;
                # 我们醒来还拿旧 v 写回 → 覆盖对方的 +1
                v = counter              # 读
                time.sleep(0)            # ← 窗口: 模拟真实临界区里的 IO/等待
                counter = v + 1          # 写(可能基于过期读值)

    threads = [threading.Thread(target=loop) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return counter

print("\n1) 数据竞争演示(两线程各 +200_000, 临界区里带 sleep(0) 模拟 IO):")
no_lock = race_counter(False)
print("   无锁:   ", no_lock, " ← 远小于 400_000! 读改写被打断 → 更新互相覆盖(损失",
      2 * N - no_lock, "次)")
with_lock = race_counter(True)
print("   加 Lock:", with_lock, " ← 恰好 400_000(锁让'读-改-写'原子成块, 谁也插不进)")
print("   [教学注] 若把上面 sleep(0) 删掉(纯算数循环): 3.13+ 实测零损失 ——")
print("             GIL 切换点不在三步之间; 但临界区有 IO 就是另一回事了,")
print("             且自由线程版 Python(无 GIL)纯算数也丢 → 锁仍旧必须写")

# ---- 2. Lock/RLock 三件套简述 + 事件(Event) ----
# 这是什么: Lock —— 互斥锁(一次只放一个线程), RLock —— 可重入锁(同一线程
#           可重复 acquire, 递归函数用它), Condition —— 条件变量(等某个条件
#           通知再走), Semaphore —— 计数信号量(限最多 N 个并发)。
# 这是什么: Event —— 事件信号: wait() 阻塞等待, 别的线程 set() 放行;
#           例子: 主线程等 worker 准备好再开始。
ready = threading.Event()

def worker_waiter():
    time.sleep(0.15)                     # 模拟准备(如连数据库)
    print("   worker 已就绪, 发事件")
    ready.set()

print("\n2) Event 同步:")
t = threading.Thread(target=worker_waiter)
t.start()
t.join(0.05)                             # 主线程只等 50ms(还没 ready)—— 看下面
ready.wait()                             # 阻塞等到 set()
print("   主线程等到 ready 后才继续(上面 worker 先打印了)")

# ---- 3. Queue: 最省心的线程安全通道 ----
# 这是什么: queue.Queue —— 线程安全的队列(入队/出队自带锁):
#           生产-消费模型的标准连接器; get() 阻塞等待数据, put() 排入;
#           "None(毒药丸)"这个约定值常用来告诉消费者"没了, 收工"。
print("\n3) 生产者-消费者(Queue):")
q: "queue.Queue[int | None]" = queue.Queue(maxsize=3)

def producer():
    for i in range(1, 4):
        time.sleep(0.05)                 # 模拟慢速产出
        q.put(i)
        print(f"   生产者放入了 {i}")
    q.put(None)                          # 毒药丸: 结束信号

def consumer():
    while True:
        item = q.get()
        if item is None:
            print("   消费者收到结束信号, 收工\n")
            break
        print(f"        消费者拿走了 {item}")

pt = threading.Thread(target=producer)
ct = threading.Thread(target=consumer)
pt.start()
ct.start()
pt.join()
ct.join()

# ---- 4. daemon 线程与 join ----
# 这是什么: daemon=True 的后台线程 —— 主线程结束时直接带走(不等待),
#           用于"后台守护任务"; 非 daemon 线程会拖住解释器直到自己结束;
#           join() = 主线程等着它跑完(可带秒数超时)。
print("4) daemon 与 join:")
t = threading.Thread(target=lambda: (time.sleep(2), print("   [daemon] 我刚醒, 主人已经没了…")),
                     daemon=True)
t.start()
time.sleep(0.05)
print("   主线程走了, daemon 线程若没跑完会被直接终结(上面 sleep(2) 的打印看不到 = daemon 生效)")
t.join(timeout=0.01)                     # 演示 join 超时(不等完就继续)

# ---- 5. 结论: 什么时候用线程 ----
print("\n5) 结论(教科书级口诀):")
print("   * IO 密集(网络/文件/爬虫/数据库查询): 线程 → 等待不被浪费, 真加速")
print("   * CPU 密集(计算/图像处理/训练): 线程几乎无加速(GIL) → 用 multiprocessing")
print("   * 单线程脚本: 不需要并发就不引并发(复杂度是债)")
