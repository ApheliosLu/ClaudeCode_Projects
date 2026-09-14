// ============================================================================
// 08_everyday_tools.cpp  现代 C++ 示例集 · C++20 · 补充(强烈推荐特性)
// 主题: 三个日常高频语法: std::erase 系列 / 指定初始化 / 模板化 Lambda
// ============================================================================
// 解决的问题:
//   1) 容器删"满足条件的元素", C++17 前是易错的"erase-remove 惯用法":
//        v.erase(std::remove_if(v.begin(), v.end(), pred), v.end());
//      两个迭代器成对写、返回值容易漏; C++20 的 std::erase / erase_if
//      一步到位, 还顺带处理了关联容器;
//   2) 聚合初始化按位置传值 {1,0,3}, 哪项是哪项全凭记忆;
//      C++20 指定初始化 {.x = 1, .z = 3} 自文档化;
//   3) C++14 泛型 lambda 参数只有 auto, 想"拿到类型名做分支"要写
//      decltype 绕弯; C++20 模板化 lambda []<typename T>(T) 直接给名字。
// 编译: g++ -std=c++20 -Wall -Wextra 08_everyday_tools.cpp -o demo
// ============================================================================
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

struct Point3D {
    int x;
    int y;
    int z;
};

int main()
{
    // ---- 1. std::erase / std::erase_if: 删元素一步到位 ----
    std::vector<int> v{1, 2, 3, 4, 5, 6, 2};
    std::erase(v, 2);                                        // 删所有 == 2
    std::erase_if(v, [](int x) { return x % 2 == 0; });      // 删所有偶数
    std::cout << "删掉 2 和所有偶数后: ";  // 输出: 删掉 2 和所有偶数后:
    for (int x : v)
        std::cout << x << ' ';                               // 1 3 5  // 输出: 每轮输出一个元素
    std::cout << '\n';

    // ---- 2. 指定初始化: 字段名自解释, 缺省字段自动补 0 ----
    // C++98: Point3D p = {1, 0, 3};   哪个是 x 哪个是 z? 全凭记忆
    Point3D p{.x = 1, .z = 3};                               // y 自动为 0
    std::cout << "p = (" << p.x << ", " << p.y << ", " << p.z << ")\n";  // 输出: p = (1, 0, 3)
    // 约束: 按声明顺序写、不能重复; 但可以跳字段(如这里跳过 y)

    // ---- 3. 模板化 Lambda: []<typename T>(const T&) ----
    // C++14: [](const auto& v) { if constexpr(...decltype 绕弯...) }
    auto describe = []<typename T>(const T&) {
        if constexpr (std::is_integral_v<T>)
            return "整数";
        else if constexpr (std::is_floating_point_v<T>)
            return "浮点";
        else
            return "其它";
    };
    std::cout << describe(42) << ' ' << describe(2.5) << ' '  // 输出: 整数 浮点 其它
              << describe(std::string("s")) << '\n';
    return 0;
}
