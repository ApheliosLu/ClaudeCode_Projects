// ============================================================================
// 10_async_future.cpp  现代 C++ 示例集 · C++11
// 主题: std::async / std::future —— "开线程算, 回头取结果"
// 解决的问题(C++98):
//   让一段计算在后台线程跑、之后再取结果 —— 只能手写:
//   线程 + 共享结果变量 + 事件/条件变量 + 手工同步, 繁琐且易错;
//   且 C++98 无法把子线程的异常传回主线程。
// 替代旧写法: 手搓线程+共享内存+事件 -> std::async + std::future
// 现代惯用法:
//   * 明确传 std::launch::async, 别依赖默认策略(deferred 可能同步执行);
//   * future::get() 阻塞等待并取回结果, 且只能调用一次;
//   * 子线程内抛出的异常会原样在 get() 处重抛 —— 异常跨线程传递
//     是 C++11 新增能力;
//   * 多个任务并行等全部完成: C++20 起有 std::ranges/线程池可用,
//     本示例演示基本的 双 async + 各自 get。
// 编译(MinGW/pthread 需链接): g++ -std=c++11 -Wall -Wextra -pthread 10_async_future.cpp -o demo
// ============================================================================
#include <cmath>
#include <future>
#include <iostream>
#include <stdexcept>

// 一个"耗时"计算(朴素递归斐波那契, 故意不优化)
long long fib(int n)
{
    return n < 2 ? n : fib(n - 1) + fib(n - 2);
}

// 一个会抛异常的任务: 演示异常跨线程传递
double square_root(double x)
{
    if (x < 0)
        throw std::invalid_argument("负数不能开平方");
    return std::sqrt(x);
}

int main()
{
    // ---- 两个任务并行跑, 主线程先忙别的, 回头 get() ----
    auto f1 = std::async(std::launch::async, fib, 30);
    auto f2 = std::async(std::launch::async, fib, 33);

    std::cout << "两个 fib 正在后台并行计算, 主线程可以干别的事...\n";

    std::cout << "fib(30) = " << f1.get() << '\n';    // 阻塞直到有结果
    std::cout << "fib(33) = " << f2.get() << '\n';

    // ---- 异常跨线程传播: 任务抛异常 -> get() 原样重抛 ----
    auto bad = std::async(std::launch::async, square_root, -4.0);
    try {
        std::cout << "sqrt(-4) = " << bad.get() << '\n';
    } catch (const std::invalid_argument& e) {
        std::cout << "主线程捕获子线程异常: " << e.what() << '\n';
    }
    return 0;
}
