// ============================================================================
// 02_optional_variant_any.cpp  现代 C++ 示例集 · C++17
// 主题: std::optional / std::variant / std::any(三种"值语义多态"工具)
// 解决的问题(按各自场景):
//   1) optional —— C++98 里"可能没有结果"只能返回 -1/空指针/哨兵,
//      调用方容易忘判; 返回值不再有歧义(有没有结果由类型表达);
//   2) variant —— 安全版 union: C++98 的 union 无法装 std::string 等
//      非平凡类型, 且不知道当前到底存的是哪个成员(要靠人肉 tag);
//   3) any —— "任意单值"(运行时类型擦除), 用于配置项/脚本接口;
//      有动态分配与异常开销, 能不用就不用。
// 使用原则:
//   * 三者的共同点: 都不可"裸奔"访问 —— 强制你检查/处理错误路径;
//   * optional/variant 零堆分配、值语义, 属于日常高频工具;
//   * any 是最后手段(本质是类型擦除, 出错只能抛异常/any_cast 判空)。
// 编译: g++ -std=c++17 -Wall -Wextra 02_optional_variant_any.cpp -o demo
// ============================================================================
#include <any>
#include <iostream>
#include <optional>
#include <string>
#include <type_traits>
#include <variant>

// ---- optional: 用"无值"表达失败, 不再返回魔法哨兵值 ----
// C++98: double safe_div(double a, double b) { return b == 0 ? -1 : a / b; }
//        —— 调用方要拿 -1 当"错误", 与真实结果可能混淆
std::optional<double> safe_div(double a, double b)
{
    if (b == 0)
        return std::nullopt;          // 显式"无值"
    return a / b;
}

int main()
{
    // ---------- 1. std::optional ----------
    // 查询数据库/解析配置的经典模式:
    if (auto r = safe_div(10.0, 4.0); r) {          // r 可当 bool 用
        std::cout << "10/4 = " << *r << '\n';       // *r 解引用取值  // 输出: 10/4 = 2.5
    }
    auto bad = safe_div(10.0, 0.0);
    std::cout << "除 0 是否有值: " << bad.has_value()
              << ", 用 value_or 兜底 = " << bad.value_or(-1.0) << '\n';
    // 输出: 除 0 是否有值: 0, 用 value_or 兜底 = -1

    // 容器里放 optional: 稀疏表
    std::optional<int> maybe;                       // 默认无值
    std::cout << "maybe = " << maybe.value_or(0) << '\n';  // 输出: maybe = 0

    // ---------- 2. std::variant(带标签联合体) ----------
    // C++98 union 不能放 std::string(非平凡析构), 也追不上当前类型;
    // variant<int, double, std::string> 替代"手写 tag + union"组合
    using Config = std::variant<int, double, std::string>;

    Config c1 = 42;                 // 现在是 int
    Config c2 = std::string("hi");  // 现在是 string

    // 运行时类型安全的"按类型分发": std::visit(统一处理)
    std::cout << "c1 打印: ";  // 输出: c1 打印: (本行不换行, 与下面 std::visit 的输出拼成一行)
    std::visit([](const auto& x) {
        using T = std::decay_t<decltype(x)>;        // 分支判断
        if constexpr (std::is_same_v<T, int>)       // if constexpr: 编译期裁掉其它分支
            std::cout << "(int) " << x;  // 输出: (int) 42
        else if constexpr (std::is_same_v<T, double>)
            std::cout << "(double) " << x;  // 输出: (double) 值(本程序未走到, c1 是 int)
        else
            std::cout << "(string) " << x;  // 输出: (string) 值(本程序未走到, c1 是 int)
    }, c1);
    std::cout << '\n';

    // 有把握时直接 get / get_if(取错类型会抛 bad_variant_access 或返回空指针)
    if (auto p = std::get_if<std::string>(&c2))
        std::cout << "c2 里是字符串: " << *p << '\n';  // 输出: c2 里是字符串: hi
    std::cout << "c2 当前类型索引: " << c2.index() << " (2=string)\n";
    // 输出: c2 当前类型索引: 2 (2=string)

    // ---------- 3. std::any(任意类型单值, 运行时擦除) ----------
    std::any anything = 42;                          // 存 int
    anything = std::string("变成字符串了");           // 换类型
    anything = 3.14;                                 // 再换

    // 安全取法: any_cast<T>(&a) 返回指针, 类型不对是 nullptr —— 不抛异常
    if (auto d = std::any_cast<double>(&anything))
        std::cout << "anything 里是 double: " << *d << '\n';  // 输出: anything 里是 double: 3.14
    // 类型不对时按值 any_cast 会抛 bad_any_cast —— 演示一下再兜住
    try {
        int v = std::any_cast<int>(anything);        // 实际是 double, 抛异常
        (void)v;
    } catch (const std::bad_any_cast&) {
        std::cout << "any_cast<int> 失败(类型不匹配), 异常被捕获\n";
        // 输出: any_cast<int> 失败(类型不匹配), 异常被捕获
    }
    return 0;
}
