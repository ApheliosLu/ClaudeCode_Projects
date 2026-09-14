// ============================================================================
// 02_return_type_deduction.cpp  现代 C++ 示例集 · C++14
// 主题: 函数返回类型自动推导(auto / decltype(auto))
// 解决的问题(相对 C++11):
//   C++11 模板函数若返回类型依赖实参, 必须写冗长的尾置返回类型:
//     template<typename A, typename B>
//     auto add(A a, B b) -> decltype(a + b) { return a + b; }
//   普通函数则必须显式写类型 —— 本可交给编译器。
// C++14 起: 普通函数与模板函数的返回类型可以直接写 auto。
// 必须知道的坑:
//   * auto 返回值遵循"auto 剥顶层 const/引用"规则: 返回的是值(拷贝);
//     想返回引用, 用 decltype(auto) —— 但注意 decltype 的括号陷阱(见下);
//   * 多分支 return 的类型必须一致;
//   * 函数体必须在所有调用点之前完整可见(单编译单元内安全);
//     跨模块导出的公共 API 建议仍写显式返回类型。
// 编译: g++ -std=c++14 -Wall -Wextra 02_return_type_deduction.cpp -o demo
// ============================================================================
#include <iostream>
#include <string>

// C++11 遗留写法(能跑但啰嗦):
// template <typename A, typename B>
// auto add11(A a, B b) -> decltype(a + b) { return a + b; }

// C++14: 编译器从 return 推导, 简洁得多
template <typename A, typename B>
auto add14(A a, B b)
{
    return a + b;
}

struct Point {
    int x = 0;
    int y = 0;
};

Point g_origin;

// decltype(auto): 把 decltype 规则套在 return 表达式上
// 陷阱: return g_origin 写不写括号, 结果完全不同:
//   decltype(g_origin)   -> Point   (变量名: 取声明类型)
//   decltype((g_origin)) -> Point&  (表达式: 左值表达式给引用)
// 所以要返回"引用"必须写成 (g_origin)
decltype(auto) get_origin_ref() { return (g_origin); }     // -> Point&
auto           get_origin_copy() { return g_origin; }      // -> Point (拷贝)

int main()
{
    std::cout << add14(1, 2) << ' ' << add14(2.5, 1) << '\n';  // 输出: 3 3.5

    Point& r = get_origin_ref();        // 真的拿到引用, 才能改到全局
    r.x = 42;
    std::cout << "g_origin.x = " << g_origin.x << '\n';    // 42, 证明是引用
    // 输出: g_origin.x = 42

    Point  copy = get_origin_copy();    // 拷贝, 改它不影响全局
    copy.y = 99;
    std::cout << "g_origin.y 仍是 " << g_origin.y << " (拷贝不受影响)\n";
    // 输出: g_origin.y 仍是 0 (拷贝不受影响)

    // lambda 返回类型推导在 C++14 也放宽: 返回闭包类型无需手写
    auto make_multiplier = [](double k) {
        return [k](double x) { return k * x; };
    };
    auto times2 = make_multiplier(2.0);
    std::cout << "times2(21) = " << times2(21) << '\n';  // 输出: times2(21) = 42
    return 0;
}
