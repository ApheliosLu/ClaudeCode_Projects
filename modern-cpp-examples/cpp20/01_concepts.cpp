// ============================================================================
// 01_concepts.cpp  现代 C++ 示例集 · C++20
// 主题: 概念(Concepts)—— 给模板加"接口契约"
// 解决的问题(C++11):
//   模板实例化失败的错误信息又长又绕(报错在标准库深处几十层);
//   想表达"这个函数只接受数值类型/可打印类型"没有直接语法,
//   只能 enable_if / SFINAE 黑魔法(可读性灾难)。
// 替代旧写法: enable_if + type_traits -> concept + requires
// 三种书写位置(功能等价):
//   1) template <Number T> void f(T);              // 概念约束模板形参
//   2) template <typename T> requires Number<T> void f(T);   // requires 子句
//   3) void f(std::integral auto x);               // 受约束 auto(简写)
// 编译: g++ -std=c++20 -Wall -Wextra 01_concepts.cpp -o demo
// ============================================================================
#include <concepts>
#include <iostream>
#include <string>

// ---- 定义自己的概念 ----
// 概念体 = 常量布尔表达式, 常用两种构件:
//   逻辑组合: std::integral<T> || std::floating_point<T>
//   requires 表达式: 直接要求"某些表达式/操作合法"
template <typename T>
concept Number = std::integral<T> || std::floating_point<T>;

template <typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;   // a+b 合法, 且结果能转回 T
};

// ---- 用法 1: 模板形参受概念约束 ----
template <Number T>
T add_ten(T v)
{
    return v + 10;
}

// ---- 用法 2: 概念重载 —— 编译器挑"满足约束"的那个 ----
// C++11 时代这种分派要写两坨 enable_if:
template <std::integral T>        std::string what_type(T) { return "整数"; }
template <std::floating_point T>  std::string what_type(T) { return "浮点数"; }

// ---- 用法 3: 受约束 auto 简写 ----
std::floating_point auto half_of(std::floating_point auto v) { return v / 2.0; }

int main()
{
    std::cout << "what_type(1)   = " << what_type(1) << '\n';
    std::cout << "what_type(2.5) = " << what_type(2.5) << '\n';

    std::cout << "add_ten(5)   = " << add_ten(5) << '\n';
    std::cout << "add_ten(3.5) = " << add_ten(3.5) << '\n';
    std::cout << "half_of(9.0) = " << half_of(9.0) << '\n';

    // static_assert = 编译期断言, 为假直接编译失败(与运行时 assert 不同)
    // 概念本身就是编译期布尔量, 可静态断言:
    static_assert(Number<int>);
    static_assert(Addable<std::string>);     // string 支持 +, 满足概念
    static_assert(!Addable<void>);

    // 放开下面这行看看报错 —— 错误直接点名"约束不满足", 比 C++11 友好得多:
    // std::cout << add_ten(std::string{"x"}) << '\n';
    return 0;
}
