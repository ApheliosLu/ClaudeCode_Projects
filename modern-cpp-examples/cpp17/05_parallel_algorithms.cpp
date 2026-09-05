// ============================================================================
// 05_parallel_algorithms.cpp  现代 C++ 示例集 · C++17
// 主题: 并行算法(执行策略 Execution Policies)
// 解决的问题(C++98/11):
//   想让排序/查找/变换用满多核, 只能自己写线程池 + 任务切分 + 归并,
//   正确性极难保证; 串行调用又是天然的单核。
// 替代旧写法: 手写线程池 -> std::sort(策略, ...) 加一个参数
// 执行策略三个档:
//   std::execution::seq       顺序执行(与普通调用一致, 当对照)
//   std::execution::par       多线程并行
//   std::execution::par_unseq 并行 + 允许向量化乱序(要求元素操作无锁、无数据竞争)
// 注意:
//   * 使用并行策略时, 你提供的操作不能有数据竞争(各元素互不干扰);
//   * 本机实测: MinGW-w64 g++ 15.2 直接可用, 无需额外链接 TBB;
//     部分 Linux 发行版的 libstdc++ 需要 -ltbb;
//   * 小数据(< 几千元素)别用 par, 线程调度开销会吃掉收益。
// 编译: g++ -std=c++17 -Wall -Wextra -O2 05_parallel_algorithms.cpp -o demo
// ============================================================================
#include <algorithm>
#include <chrono>
#include <execution>
#include <iostream>
#include <vector>

int main()
{
    const int N = 4'000'000;                       // 400 万整数(约 16 MB)
    std::vector<int> data(N);

    // 生成可复现的伪随机数据(简单 LCG 仅作演示; 生产用 <random>,
    // 见 cpp11/12_random.cpp)
    unsigned seed = 12345u;
    for (auto& x : data) {
        seed = seed * 1103515245u + 12345u;
        x    = static_cast<int>((seed >> 8) % 10000);
    }
    std::vector<int> a = data, b = data;           // 相同输入才公平对比

    auto now   = std::chrono::steady_clock::now;
    auto t0    = now();
    std::sort(std::execution::seq, a.begin(), a.end());   // 单线程
    auto t1    = now();
    std::sort(std::execution::par, b.begin(), b.end());   // 多线程
    auto t2    = now();

    auto ms = [](auto from, auto to) {
        return std::chrono::duration_cast<std::chrono::milliseconds>(to - from)
            .count();
    };
    std::cout << "seq 排序: " << ms(t0, t1) << " ms\n";
    std::cout << "par 排序: " << ms(t1, t2) << " ms\n";
    std::cout << "两种策略结果一致: " << (a == b ? "是" : "否")
              << "  排序后首元素 = " << b[0] << '\n';

    // par_unseq: 更激进的"就地变换", 元素互不干扰即可
    std::for_each(std::execution::par_unseq, b.begin(), b.end(),
                  [](int& x) { x = x % 1000; });
    std::cout << "for_each(par_unseq) 后 b[0] = " << b[0] << '\n';
    return 0;
}
