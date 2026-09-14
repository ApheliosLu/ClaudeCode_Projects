// ============================================================================
// 13_std_array.cpp  现代 C++ 示例集 · C++11 · 补充(此前遗漏的强烈推荐特性)
// 主题: std::array —— 固定大小数组的"现代正确形态"
// 解决的问题(C++98):
//   1) C 数组 int a[5]: 传参即退化成指针(长度丢失), 不能整体赋值/返回,
//      越界不检查(静默 UB), 没有 size()/迭代器语义;
//   2) 想要"固定大小但有容器功能"只能 new T[n](回到手管内存)。
// 替代旧写法: C 数组 / 裸 new[] -> std::array<T, N>
// 要点:
//   * 栈上分配、与 C 数组同样零开销; N 必须是编译期常量;
//   * 有 size()/迭代器/范围 for, 能配 STL 算法 —— 比 C 数组强得多;
//   * 可整体拷贝赋值(ar2 = ar1), C 数组做不到;
//   * operator[] 不检查(快); at() 越界抛异常(安全);
//   * 元素个数和类型由类型系统携带 —— 传给通用函数用 std::span(C++20, cpp20/04)。
// 编译: g++ -std=c++11 -Wall -Wextra 13_std_array.cpp -o demo
// ============================================================================
#include <algorithm>
#include <array>
#include <iostream>
#include <stdexcept>
#include <string>

struct Item {           // 自定义结构也能装
    std::string name;
    int         qty;
};

int main()
{
    // C++98: int scores[3] = {90, 85, 88};  长度与类型人肉配对
    std::array<int, 3> scores{90, 85, 88};
    std::cout << "size = " << scores.size()          // 类型自带长度
              << ", 第 2 个 = " << scores[1] << '\n';   // 输出: size = 3, 第 2 个 = 85

    // 范围 for / 算法直接可用(C 数组要手写长度)
    std::sort(scores.begin(), scores.end());
    std::cout << "排序后: ";   // 输出: 排序后: 85 88 90
    for (int v : scores)
        std::cout << v << ' ';   // 输出: 逐个元素 + 空格(拼成上一行)
    std::cout << '\n';

    // 整体拷贝赋值: int a2[3] = a1 是编译错误!
    std::array<int, 3> copy = scores;
    copy[0] = 0;
    std::cout << "copy[0] = " << copy[0]
              << ", 原数组 scores[0] = " << scores[0] << " (深拷贝互不影响)\n";   // 输出: copy[0] = 0, 原数组 scores[0] = 85 (深拷贝互不影响)

    // at(): 越界抛 std::out_of_range(C 数组越界 = 静默 UB)
    try {
        scores.at(99);
    } catch (const std::out_of_range&) {
        std::cout << "at(99) 越界, 异常被捕获\n";   // 输出: at(99) 越界, 异常被捕获
    }

    // fill / 按 size() 遍历
    std::array<int, 4> zeros;
    zeros.fill(7);
    std::cout << "fill(7) 后: ";   // 输出: fill(7) 后: 7777
    for (std::size_t i = 0; i < zeros.size(); ++i)
        std::cout << zeros[i];   // 输出: 逐个元素, 无分隔符(拼成 7777)
    std::cout << '\n';

    // 装自定义类型; 遍历/算法照常
    std::array<Item, 2> cart{{{"apple", 3}, {"book", 1}}};
    for (const auto& it : cart)
        std::cout << it.name << " x" << it.qty << ' ';   // 输出: apple x3 book x1 (每项后带空格, 拼成一行)
    std::cout << '\n';
    return 0;
}
