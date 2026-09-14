// ============================================================================
// 05_constexpr_enhanced.cpp  现代 C++ 示例集 · C++20
// 主题: constexpr 大幅增强 + consteval + constinit
// 解决的问题(C++11):
//   C++11 的 constexpr 函数体只能写一条 return(纯函数限制过死),
//   无法表达"循环/分支的编译期计算"; 也没有"只许编译期求值"的关键字。
// C++14 放宽了函数体(循环/分支可用); C++20 补上两个新关键字:
//   * consteval: 立即函数 —— 只能编译期求值, 运行时调用直接编译错误;
//   * constinit: 静态存储期变量"必须在编译期初始化"(防静态初始化顺序问题);
//   * is_constant_evaluated(): 运行时问一句"我现在是不是在编译期求值?"
//   * (另: C++20 起 constexpr 函数可以操作部分标准容器与算法,
//      编译器支持度渐好: GCC 13+/MSVC 17.6+ 可 constexpr vector/string)
// 编译: g++ -std=c++20 -Wall -Wextra 05_constexpr_enhanced.cpp -o demo
// ============================================================================
#include <iostream>
#include <type_traits>

// ---- 1. constexpr 函数: 同一份代码, 编译期/运行期都能调 ----
// C++11 里 constexpr 函数体禁止循环 —— 算阶乘只能递归表达式
constexpr std::size_t factorial(std::size_t n)
{
    std::size_t r = 1;
    for (std::size_t i = 2; i <= n; ++i)
        r *= i;                          // C++14 起 constexpr 内可用循环
    return r;
}

// ---- 2. consteval: 只许编译期求值(立即函数) ----
consteval int square(int n) { return n * n; }
// 若参数来自运行期输入, 编译直接报错:
//   int v = square(read_from_stdin());
// consteval 常用于: 哈希表构造、位运算常量、生成表 —— 拒绝运行期误用

// ---- 3. is_constant_evaluated(): 按"求值上下文"走不同实现 ----
constexpr int mode()
{
    if (std::is_constant_evaluated())
        return 1;                        // 编译期: 走快路径(内联展开计算)
    return 2;                            // 运行期: 可能走通用实现
}

// ---- 4. constinit: 保证静态变量编译期初始化(防 SIOF) ----
constinit int g_answer = square(4);      // 编译期常量 16; constinit 只是
                                         // 保证"初值常量", 变量本身不是 const
int main()
{
    constexpr auto f6 = factorial(6);    // 编译期就算好, 零运行开销
    std::cout << "factorial(6) = " << f6 << '\n';  // 输出: factorial(6) = 720
    std::cout << "factorial(5)(运行期调用) = " << factorial(5) << '\n';
    // 输出: factorial(5)(运行期调用) = 120

    constexpr int sq = square(4);
    std::cout << "square(4) = " << sq << '\n';  // 输出: square(4) = 16

    constexpr int ce = mode();           // 常量上下文 -> 1
    int           rt = mode();           // 运行时调用   -> 2
    std::cout << "mode(): 编译期分支 = " << ce  // 输出: mode(): 编译期分支 = 1, 运行期分支 = 2
              << ", 运行期分支 = " << rt << '\n';

    std::cout << "g_answer(初值) = " << g_answer << '\n';  // 输出: g_answer(初值) = 16
    g_answer = 43;                       // 运行期仍可修改(constinit 非 const)
    std::cout << "g_answer(改后) = " << g_answer << '\n';  // 输出: g_answer(改后) = 43
    return 0;
}
