// ============================================================================
// 07_if_constexpr.cpp  现代 C++ 示例集 · C++17 · 补充(此前遗漏的强烈推荐特性)
// 主题: if constexpr —— 编译期 if(模板里按"类型"裁掉分支)
// 解决的问题(C++11):
//   模板里想"按类型走不同实现": C++11 只能标签分发(tag dispatch)或
//   enable_if 重载堆, 代码被拆得七零八落;
//   变参递归还要专门写一个"递归终点"重载(见 cpp11/08 的 print_all 两件套)。
//   if constexpr: 编译期只保留匹配分支, 不匹配的分支不参与实例化。
// 关键认知:
//   * 两个分支都要"语法合法", 但只有命中分支会被实例化 —— 可以在丢弃
//     分支里写对当前类型非法的代码(如调用该类型不存在的方法);
//   * 条件是编译期常量(类型 trait / sizeof... 等), 不能依赖运行期变量;
//   * 与 if consteval(C++23)互补: if constexpr 按"类型"裁, if consteval
//     按"是否编译期求值"裁(见 cpp23/04)。
// 编译: g++ -std=c++17 -Wall -Wextra 07_if_constexpr.cpp -o demo
// ============================================================================
#include <iostream>
#include <string>
#include <type_traits>
#include <utility>

// ---- 1. 按类型分发打印: 分支平铺直叙, 不再 enable_if 重载堆 ----
template <typename T>
void describe(const T& v)
{
    using Raw = std::decay_t<T>;
    if constexpr (std::is_integral_v<Raw>)
        std::cout << "整数: " << v << '\n';  // 输出: 整数: 42
    else if constexpr (std::is_floating_point_v<Raw>)
        std::cout << "浮点: " << v << '\n';  // 输出: 浮点: 2.5
    else if constexpr (std::is_same_v<Raw, std::string>)
        std::cout << "字符串: " << v << '\n';  // 输出: 字符串: hello
    else
        std::cout << "其它类型\n";  // 输出: 其它类型(本程序未走到)
}

// ---- 2. 丢弃分支不实例化: 不同调用实例化出不同返回类型 ----
// 对算术类型返回 x*2; 对其它类型返回 0 —— 两个 return 类型不同也合法,
// 因为对每次实例化只有一个分支存在
template <typename T>
auto scale_or_zero(T x)
{
    if constexpr (std::is_arithmetic_v<T>)
        return x * 2;              // T=int 时: 返回 int
    else
        return 0;                  // T=string 时: 上面的分支被丢弃, 返回 int
}

// ---- 3. 递归终点内联化: C++11 需要独立重载做"终点", 现在一个函数搞定 ----
template <typename First, typename... Rest>
void log_all(First&& first, Rest&&... rest)
{
    std::cout << first << ' ';  // 输出: 当前实参 + 空格(递归逐个打印, 拼成一行)
    if constexpr (sizeof...(Rest) > 0)          // 还有剩余才递归
        log_all(std::forward<Rest>(rest)...);   // 空包时这个调用根本不实例化
}

int main()
{
    describe(42);  // 输出: 整数: 42
    describe(2.5);  // 输出: 浮点: 2.5
    describe(std::string("hello"));  // 输出: 字符串: hello

    std::cout << "scale_or_zero(21)    = " << scale_or_zero(21) << '\n';
    // 输出: scale_or_zero(21)    = 42
    std::cout << "scale_or_zero(\"str\") = " << scale_or_zero("str") << '\n';
    // 输出: scale_or_zero("str") = 0

    std::cout << "log_all: ";  // 输出: log_all: (本行不换行, 与 log_all 打印的值拼成一行)
    log_all(1, 2.5, std::string("three"), "four");   // 无需单独的重载终点
    // 输出: 1 2.5 three four
    std::cout << '\n';
    return 0;
}
