// ============================================================================
// 01_optional_monadic.cpp  现代 C++ 示例集 · C++23
// 主题: std::optional 的 Monadic 操作(and_then / transform / or_else)
// 解决的问题(相对 C++17):
//   optional 只是"有/没有"; 一连串"可能失败"的步骤只能层层 if 嵌套,
//   每个空值都要手动短路返回, 缩进地狱:
//     auto a = f(); if (!a) return nullopt; auto b = g(*a); if (!b) ...
//   C++23 给 optional 加了三个方法, 让"失败自动短路、成功继续走"以
//   管道形式直写(和 Rust 的 ? / 函数式编程的 monad 同思路):
//     * transform(f): 有值则 f(值), 结果自动包成 optional; 无值直接透传
//     * and_then(f):  同上, 但 f 返回 optional(可继续接别的 optional 步骤)
//     * or_else(f):   无值时执行 f(可注入默认值/记日志), f 返回 optional
// 编译: g++ -std=c++23 -Wall -Wextra 01_optional_monadic.cpp -o demo
// ============================================================================
#include <iostream>
#include <optional>
#include <string>
#include <string_view>

// 解析纯数字字符串为 int, 失败返回 nullopt
std::optional<int> parse_int(std::string_view s)
{
    if (s.empty())
        return std::nullopt;
    int v = 0;
    for (char c : s) {
        if (c < '0' || c > '9')
            return std::nullopt;
        v = v * 10 + (c - '0');
    }
    return v;
}

std::optional<int> checked_div(int a, int b)
{
    if (b == 0)
        return std::nullopt;
    return a / b;
}

int main()
{
    // ---- 成功链路: 解析 -> 除法 -> 放大, 一步一短路 ----
    auto result = parse_int("24")
        .and_then([](int v) { return checked_div(v, 3); })  // 8
        .transform([](int v) { return v + 100; });          // 108
    std::cout << "链路结果 = " << result.value_or(-1)
              << " (期望 108)\n";

    // ---- 中间某步失败: 整条链短路, or_else 兜底 ----
    auto fallback = parse_int("24")
        .and_then([](int) { return checked_div(1, 0); })    // 除 0 -> 空
        .or_else([] {
            std::cout << "  [日志] 除 0 了, 用默认值顶替\n";
            return std::optional<int>{42};                  // 注入默认
        })
        .transform([](int v) { return v * 2; });            // 84
    std::cout << "兜底后结果 = " << fallback.value_or(-1)
              << " (期望 84)\n";

    // ---- 对比: C++17 时代同样的逻辑要写多少层 if ----
    // (注释展示, 读者自行感受)
    // std::optional<int> v = parse_int("24");
    // if (v) v = checked_div(*v, 3);
    // if (v) v = *v + 100;
    // —— 每步都要重新判空, 错误路径和主路径混在一起
    return 0;
}
