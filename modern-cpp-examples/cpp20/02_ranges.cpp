// ============================================================================
// 02_ranges.cpp  现代 C++ 示例集 · C++20
// 主题: Ranges 库 —— 视图管道(懒求值) + 概念化算法 + 投影
// 解决的问题(C++11):
//   1) 容器要"过滤->变换->取前几个", 得建一堆临时容器 + 循环搬运;
//   2) 算法参数顺序别扭: sort(begin, end) 每次重复 begin/end;
//   3) "按某字段排序/查找"没有原生支持, 要写比较器 lambda。
// 替代旧写法: 手写循环/中间容器 -> 视图管道 |;
//            sort(v.begin(), v.end()) -> std::ranges::sort(v)
// 关键认知:
//   * 视图(view)是"懒"的: 只有遍历时才逐元素计算, 不拷贝容器;
//   * | 管道: 数据从左向右流; 管道端点是"消费端"(如遍历/拷贝);
//   * 视图不拥有元素, 源容器不能比视图先死。
// 编译: g++ -std=c++20 -Wall -Wextra 02_ranges.cpp -o demo
// ============================================================================
#include <algorithm>
#include <iostream>
#include <numeric>
#include <ranges>
#include <string>
#include <vector>

struct Item {
    std::string name;
    double      price;
};

int main()
{
    // ---- 1. 视图管道: 过滤 -> 变换 -> 截断 ----
    std::vector<int> nums(20);
    std::iota(nums.begin(), nums.end(), 1);              // 1..20

    // C++11 老写法: 三遍循环 + 两三个中间容器, 还要小心迭代器失效
    auto view = nums
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::transform([](int n) { return n * 3; })
        | std::views::take(4);
    std::cout << "前 4 个偶数的 3 倍: ";  // 输出: 前 4 个偶数的 3 倍:
    for (int v : view)
        std::cout << v << ' ';                           // 6 12 18 24  // 输出: 每轮输出一个元素
    std::cout << '\n';

    // ---- 2. 无限范围 + take: 概念直接表达, 不再怕"取过头" ----
    std::cout << "前 5 个奇数平方: ";  // 输出: 前 5 个奇数平方:
    for (int v : std::views::iota(1)
               | std::views::filter([](int n) { return n % 2 == 1; })
               | std::views::transform([](int n) { return n * n; })
               | std::views::take(5))
        std::cout << v << ' ';                           // 1 9 25 49 81  // 输出: 每轮输出一个元素
    std::cout << '\n';

    // ---- 3. 命名空间级算法: 直接传"容器/范围" ----
    std::ranges::sort(nums);                             // C++11: sort(begin,end)
    std::cout << "升序前 3 个: ";  // 输出: 升序前 3 个:
    for (int v : nums | std::views::take(3))
        std::cout << v << ' ';                           // 1 2 3  // 输出: 每轮输出一个元素
    std::cout << '\n';

    // ---- 4. 投影(projection): 按字段排序, 不再写比较器 ----
    std::vector<Item> items{{"pen", 5.0}, {"book", 22.0}, {"apple", 3.5}};
    std::ranges::sort(items, {}, &Item::price);          // 第三个参数: 投影
    std::cout << "按价格升序: ";  // 输出: 按价格升序:
    for (const auto& it : items)
        std::cout << it.name << '(' << it.price << ") ";  // 输出: apple(3.5) pen(5) book(22)
    std::cout << '\n';

    // ---- 5. 视图只"看"不"存": 要保存结果就拷出来 ----
    std::vector<int> doubled;
    std::ranges::copy(nums | std::views::take(3)
                          | std::views::transform([](int v) { return v * 2; }),
                      std::back_inserter(doubled));
    std::cout << "double 前 3 个 = { ";  // 输出: double 前 3 个 = {
    for (int v : doubled)
        std::cout << v << ' ';  // 输出: 2 4 6
    std::cout << "}\n";  // 输出: }
    return 0;
}
