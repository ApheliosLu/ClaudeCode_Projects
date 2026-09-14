// ============================================================================
// 09_thread_and_mutex.cpp  现代 C++ 示例集 · C++11
// 主题: std::thread + std::mutex / lock_guard / std::atomic
// 解决的问题(C++98):
//   C++98 标准库没有任何线程设施 —— 只能调用平台 API(Win32 CreateThread /
//   POSIX pthread), 换平台全部重写, 还要自己回收句柄、拼结构体传参。
// 替代旧写法: CreateThread/pthread_create + 平台事件/临界区
//            -> std::thread + std::mutex/std::lock_guard/std::atomic
// 现代惯用法:
//   * 锁必须 RAII 化: lock_guard/unique_lock, 绝不裸调 lock()/unlock()
//     (中途抛异常会死锁);
//   * 纯计数/标志用 std::atomic(无锁), 不要上互斥锁;
//   * thread 析构前必须 join() 或 detach(), 否则直接 std::terminate;
//   * 需要"返回值"的任务优先 std::async(见 10), 别手搓共享变量。
// 编译(MinGW/pthread 需链接): g++ -std=c++11 -Wall -Wextra -pthread 09_thread_and_mutex.cpp -o demo
// ============================================================================
#include <atomic>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

static const int kThreads = 8;
static const int kEach    = 100000;

int main()
{
    // ---- 1. std::mutex 保护共享变量 ----
    std::mutex  mtx;
    long long   count = 0;

    std::vector<std::thread> pool;          // 线程不可拷贝, 直接 emplace
    pool.reserve(kThreads);
    for (int t = 0; t < kThreads; ++t) {
        pool.emplace_back([&] {
            for (int i = 0; i < kEach; ++i) {
                std::lock_guard<std::mutex> lock(mtx);   // RAII: 出括号自动解锁
                ++count;
            }
        });
    }
    for (auto& th : pool)
        th.join();                          // 必须 join/detach 后再析构
    std::cout << "加锁计数 = " << count
              << " (期望 " << kThreads * kEach << ")\n";   // 输出: 加锁计数 = 800000 (期望 800000)

    // ---- 2. std::atomic: 简单共享计数无锁化 ----
    std::atomic<long long> acount{0};
    std::vector<std::thread> pool2;
    for (int t = 0; t < kThreads; ++t) {
        pool2.emplace_back([&acount] {
            for (int i = 0; i < kEach; ++i)
                ++acount;                   // 等价 fetch_add(1), 原子自增
        });
    }
    for (auto& th : pool2)
        th.join();
    std::cout << "原子计数 = " << acount.load()
              << " (期望 " << kThreads * kEach << ")\n";   // 输出: 原子计数 = 800000 (期望 800000)

    // ---- 3. 线程跑一段累加: 各自写自己的局部变量, 最后汇总 ----
    // (让两个线程写同一个变量就是数据竞争 —— 现代 C++ 里这是未定义行为)
    long long part1 = 0, part2 = 0;
    std::thread t1([&part1] { for (int i = 1; i < 500000; ++i) part1 += i; });
    std::thread t2([&part2] { for (int i = 500000; i < 1000000; ++i) part2 += i; });
    t1.join();
    t2.join();
    std::cout << "1+2+...+999999 = " << part1 + part2 << '\n';   // 输出: 1+2+...+999999 = 499999500000
    return 0;
}
