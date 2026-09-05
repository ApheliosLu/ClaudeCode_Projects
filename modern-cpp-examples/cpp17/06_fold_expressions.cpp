// ============================================================================
// 06_fold_expressions.cpp  现代 C++ 示例集 · C++17
// 主题: 折叠表达式(Fold Expressions) —— 参数包的"一行版"
// 解决的问题(相对 C++11):
//   变参模板处理参数包要写"递归函数 + 递归终点"两件套(见 cpp11/08),
//   阅读负担重; 想对包整体做求和/求与/打印, 没有直接语法。
// C++17 折叠表达式把四种折叠写成一行:
//   一元左折叠: (... op pack)   => ((a op b) op c)
//   一元右折叠: (pack op ...)   => (a op (b op c))
//   二元左折叠: (init op ... op pack)
//   二元右折叠: (pack op ... op init)   // 最常用, 自带"初值"
// 应用:
//   * (args + ...)                     求和(C++11 得递归)
//   * (init && ...)                    短路判全真
//   * (std::cout << ... << args)       展开输出
//   * (std::forward<Args>(args)...)    转发包(写法不变, cpp11 已见)
// 编译: g++ -std=c++17 -Wall -Wextra 06_fold_expressions.cpp -o demo
// ============================================================================
#include <iostream>
#include <string>

// ---- 求和: 二元右折叠, 0 作为空包的"初值"(空参数包也安全) ----
template <typename... Ts>
auto sum_all(Ts... args)
{
    return (args + ...);                    // 初值省略: 对空包不合法(0 个实参时推导不出)
}

// 想要"空包也能调"就写 二元折叠:
template <typename... Ts>
auto sum_all_safe(Ts... args)
{
    return (args + ... + 0);                // 等价 ((a+b)+c)+0
}

// ---- 短路判全真: && 带 true 初值, 支持短路求值 ----
template <typename... Ts>
bool all_true(Ts... bs)
{
    return (bs && ...);                     // true && a && b && ...; 遇到 false 立即短路
}

// ---- 打印任意多个任意类型: 一元左折叠吃进 cout ----
// C++11 递归版见 cpp11/08; 这里一行结束:
template <typename... Ts>
void print_all(Ts&&... args)
{
    (std::cout << ... << args) << '\n';     // ((cout << a) << b) << c
}

// ---- 对每个参数做点事: 逗号折叠(逐个调用某个函数) ----
void apply_one(int x) { std::cout << "处理: " << x * x << '\n'; }

template <typename... Ts>
void for_each_arg(Ts&&... args)
{
    (apply_one(args), ...);                 // (a, (b, (c, ...))) 逐个展开
}

int main()
{
    std::cout << "sum_all(1,2,3,4) = " << sum_all(1, 2, 3, 4) << '\n';
    std::cout << "sum_all_safe()   = " << sum_all_safe() << '\n';
    std::cout << "sum_all_safe(2.5, 1) = " << sum_all_safe(2.5, 1) << '\n';

    std::cout << "all_true(true, true, true) = "
              << all_true(true, true, true) << '\n';
    std::cout << "all_true(true, false)      = "
              << all_true(true, false) << '\n';

    print_all(1, ' ', 2.5, ' ', std::string("three"));

    for_each_arg(1, 2, 3);                  // 逐参调用 apply_one
    return 0;
}
