// ============================================================================
// 07_tools.cpp  现代 C++ 示例集 · C++23 · 补充(强烈推荐特性)
// 主题: std::move_only_function / std::ranges::to / std::views::enumerate
// ============================================================================
// 解决的问题:
//   1) std::function(C++11)要求可调用对象"可拷贝": 捕获 unique_ptr 的
//      lambda 装不进去, move-only 回调只能手写类型擦除类;
//      C++23 的 std::move_only_function 取消拷贝要求(还可标注 const 与
//      异常说明, 类型安全更进一步);
//   2) Ranges 视图是"懒"的, 想落袋成容器要 ranges::copy + back_inserter
//      两件套(C++20); C++23 的 std::ranges::to 一步转换;
//   3) 遍历想要下标: C++23 前要么手写索引循环, 要么 enumerate 惯用法
//      自己拼 pair; views::enumerate 直接给 (index, 元素)。
// 编译: g++ -std=c++23 -Wall -Wextra 07_tools.cpp -o demo
// ============================================================================
#include <functional>
#include <iostream>
#include <memory>
#include <ranges>
#include <string>
#include <vector>

int main()
{
    // ---- 1. move_only_function: 装"独占所有权"的回调 ----
    auto p = std::make_unique<int>(42);
    std::move_only_function<int(int)> add_base = [p = std::move(p)](int x) {
        return *p + x;
    };
    std::cout << "add_base(8) = " << add_base(8) << '\n';      // 50  // 输出: add_base(8) = 50

    std::move_only_function<int(int)> other = std::move(add_base);
    std::cout << "add_base 移走后为空: " << (add_base ? "否" : "是")
              << ", other(1) = " << other(1) << '\n';          // 43  // 输出: add_base 移走后为空: 是, other(1) = 43

    // ---- 2. ranges::to: 视图结果一键落袋 ----
    // C++20 写法: std::vector<int> v; std::ranges::copy(视图, std::back_inserter(v));
    auto evens = std::views::iota(1, 11)                       // 1..10
               | std::views::filter([](int n) { return n % 2 == 0; })
               | std::ranges::to<std::vector>();               // -> vector<int>
    std::cout << "to<vector> 得 " << evens.size() << " 个偶数: ";  // 输出: to<vector> 得 5 个偶数: 2 4 6 8 10
    for (int x : evens)
        std::cout << x << ' ';                   // 输出: 2 4 6 8 10
    std::cout << '\n';

    // ---- 3. views::enumerate: 遍历自带下标 ----
    std::vector<std::string> names{"alice", "bob", "carol"};
    std::cout << "enumerate 输出:\n";  // 输出: enumerate 输出:
    for (auto&& [i, name] : std::views::enumerate(names))
        std::cout << "  [" << i << "] " << name << '\n';     // 输出(循环 3 行, 行首 2 空格):
                                                             //   [0] alice
                                                             //   [1] bob
                                                             //   [2] carol
    return 0;
}
