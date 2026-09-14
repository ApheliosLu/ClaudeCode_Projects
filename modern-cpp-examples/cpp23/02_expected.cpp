// ============================================================================
// 02_expected.cpp  现代 C++ 示例集 · C++23
// 主题: std::expected<T, E> —— 带"错误详情"的返回值
// 解决的问题(C++17 时代):
//   函数失败时, optional 只告诉你"有没有", 说不出"为什么失败";
//   想带错误原因, 只能: 抛异常(破坏性能/难审计, 某些场景禁用) 或
//   输出参数 + 错误码(绕)。Rust 的 Result / C 的 errno 各有取舍,
//   C++23 正式引入 expected<T, E>: 要么是 T, 要么是 E(错误详情)。
// 替代旧写法: 返回值 + 错误码双通道 -> expected;
//            可选: 抛异常路径 -> 用 expected 显式返回错误
// 关键操作:
//   * 构造成功值直接 T; 失败用 std::unexpected(E);
//   * if (r) / r.has_value() 判断; *r 或 r.value() 取值;
//   * value_or(默认值) / error() 取错误;
//   * 与 optional 同款 monadic: and_then / transform / or_else;
//   * E 由你定: 枚举、字符串、std::error_code 都行。
// 编译: g++ -std=c++23 -Wall -Wextra 02_expected.cpp -o demo
// ============================================================================
#include <expected>
#include <iostream>
#include <string>
#include <string_view>

// E 用 std::string 最直观(错误直接给人看); 正式项目常用枚举 + 错误码
std::expected<int, std::string> parse_int(std::string_view s)
{
    if (s.empty())
        return std::unexpected("输入为空");
    int v = 0;
    for (char c : s) {
        if (c < '0' || c > '9')
            return std::unexpected(std::string("含非法字符: ") + c);
        v = v * 10 + (c - '0');
    }
    return v;                            // 成功路径: 直接返回值
}

std::expected<int, std::string> checked_div(int a, int b)
{
    if (b == 0)
        return std::unexpected("除数为 0");
    return a / b;
}

int main()
{
    // ---- 成功路径: 级联处理(任一步失败, 错误原样透传) ----
    auto r = parse_int("42")
                 .and_then([](int v) { return checked_div(v, 2); })
                 .transform([](int v) { return v * 10; });
    if (r)
        std::cout << "成功: *r = " << *r << '\n';      // 210  // 输出: 成功: *r = 210
    else
        std::cout << "失败: " << r.error() << '\n';  // 输出(本例未走到此分支): 失败: 后跟 r.error()

    // ---- 失败路径: 中间任一步出错, 后续不再执行 ----
    auto bad = parse_int("abc")
                   .and_then([](int v) { return checked_div(v, 2); });
    std::cout << "bad: has_value = " << bad.has_value()
              << ", 错误 = " << bad.error() << '\n';  // 输出: bad: has_value = 0, 错误 = 含非法字符: a

    auto zero = parse_int("10")
                    .and_then([](int) { return checked_div(1, 0); });
    std::cout << "zero: 错误 = " << zero.error() << '\n';  // 输出: zero: 错误 = 除数为 0

    // ---- 兜底 / 防御式取值 ----
    std::cout << "parse_int(\"nope\").value_or(-1) = "
              << parse_int("nope").value_or(-1) << '\n';  // 输出: parse_int("nope").value_or(-1) = -1
    std::cout << "parse_int(\"7\").value_or(-1)    = "
              << parse_int("7").value_or(-1) << '\n';  // 输出: parse_int("7").value_or(-1)    = 7
    return 0;
}
