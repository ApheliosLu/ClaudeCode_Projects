// ============================================================================
// 06_std_generator.cpp  现代 C++ 示例集 · C++23 · 补充(强烈推荐特性)
// 主题: std::generator —— 标准库生成器(协程落地, 免手写框架)
// 背景: cpp20/06 为了讲原理, 手写了约 80 行 Generator<T>(promise_type、
//       coroutine_handle、迭代器全套)。C++23 把这些机制收进标准库
//       <generator> 的 std::generator<T>: 协程函数只需写业务, co_yield
//       即可, 协程帧分配/异常处理/迭代器语义全部由标准库保证 —— 生产首选。
// 要求: 较新工具链(g++ 15+ / MSVC 2022 17.13+ / clang 19+), 本机已验证可用。
// 用法: 返回 std::generator<T> 的函数内部 co_yield 值, 消费方用范围 for
//       驱动 —— 与 cpp20/06 手写版完全相同, 只是不再需要那些样板代码。
// 编译: g++ -std=c++23 -Wall -Wextra 06_std_generator.cpp -o demo
// ============================================================================
#include <generator>
#include <iostream>

// 产出 [from, to] 区间内的所有偶数
std::generator<int> evens(int from, int to)
{
    for (int v = from; v <= to; ++v)
        if (v % 2 == 0)
            co_yield v;                  // 产出即挂起; 下个循环周期恢复
}

// 斐波那契数列, 直到超过 limit(想产多少产多少, 不预分配)
std::generator<unsigned long long> fibonacci_upto(unsigned long long limit)
{
    unsigned long long a = 0, b = 1;
    while (b <= limit) {
        co_yield b;
        auto t = a + b;
        a = b;
        b = t;
    }
}

int main()
{
    std::cout << "evens(1, 12): ";  // 输出: evens(1, 12): 2 4 6 8 10 12
    for (int v : evens(1, 12))
        std::cout << v << ' ';           // 2 4 6 8 10 12  // 输出: 2 4 6 8 10 12
    std::cout << '\n';

    std::cout << "fibonacci_upto(200): ";  // 输出: fibonacci_upto(200): 1 1 2 3 5 8 13 21 34 55 89 144
    for (auto v : fibonacci_upto(200))
        std::cout << v << ' ';           // 1 1 2 3 5 8 13 21 34 55 89 144  // 输出: 1 1 2 3 5 8 13 21 34 55 89 144
    std::cout << '\n';

    // 对比 cpp20/06: 手写版的核心是"实现 promise/句柄/迭代器",
    // 业务函数体与这里几乎一样 —— 那 80 行现在交给标准库了
    return 0;
}
