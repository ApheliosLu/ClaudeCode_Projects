// ============================================================================
// 03_views_zip.cpp  现代 C++ 示例集 · C++23
// 主题: std::views::zip —— 把多个范围"并排拉链"成一个视图
// 解决的问题(C++17 时代):
//   要按位置同时遍历两个容器(如 名称表 + 分数表), 只能写索引循环
//   for (size_t i = 0; i < names.size(); ++i) —— 索引越界/长度不齐全靠
//   人肉保证, 语义完全隐晦。
// C++23 的 views::zip(r1, r2, ...): 一次迭代拿到各范围的"同位置引用",
//   到任一范围结束即停(自动取最短), 不拷贝、不新建容器。
// 配套新视图(同批): views::zip_transform / adjacent / chunk / stride 等;
// 本文件用 zip 演示最常用三件事: 并排读、并排写、变换聚合。
// 编译: g++ -std=c++23 -Wall -Wextra 03_views_zip.cpp -o demo
// ============================================================================
#include <iostream>
#include <ranges>
#include <string>
#include <tuple>
#include <vector>

int main()
{
    std::vector<std::string> names{"alice", "bob", "carol"};
    std::vector<int>         scores{90, 85, 88};

    // ---- 1. 并排读取(结构化绑定直接解出引用) ----
    // C++17 写法: for (size_t i = 0; i < names.size(); ++i) ...
    std::cout << "成绩单:\n";  // 输出: 成绩单:
    for (auto&& [name, score] : std::views::zip(names, scores))
        std::cout << "  " << name << ": " << score << '\n';  // 输出(循环 3 行, 行首 2 空格):
                                                             //   alice: 90
                                                             //   bob: 85
                                                             //   carol: 88

    // ---- 2. 并排写: 元素是"引用", 直接改原容器 ----
    for (auto&& [name, score] : std::views::zip(names, scores))
        if (name == "bob")
            score += 5;                          // bob 加分, 原 vector 被改
    std::cout << "bob 加分后 scores[1] = " << scores[1] << '\n';  // 输出: bob 加分后 scores[1] = 90

    // ---- 3. 长度不等: 自动停在最短处 ----
    std::vector<int> a{1, 2, 3, 4, 5};
    std::vector<int> b{10, 20, 30};
    std::cout << "zip(a, b)(短者为准): ";  // 输出: zip(a, b)(短者为准): 11 22 33
    for (auto&& [x, y] : std::views::zip(a, b))
        std::cout << x + y << ' ';               // 11 22 33  // 输出: 11 22 33
    std::cout << '\n';

    // ---- 4. 与 transform 组合: 对应元素做运算生成新序列 ----
    auto sums = std::views::zip(a, b)
              | std::views::transform([](auto&& pair) {
                    return std::get<0>(pair) + std::get<1>(pair);
                });
    std::cout << "zip->transform 的和: ";  // 输出: zip->transform 的和: 11 22 33
    for (int s : sums)
        std::cout << s << ' ';                   // 输出: 11 22 33
    std::cout << '\n';
    return 0;
}
