// ============================================================================
// 08_variadic_templates.cpp  现代 C++ 示例集 · C++11
// 主题: 变参模板(Variadic Templates)
// 解决的问题(C++98):
//   1) 想写"接受任意数量、任意类型实参"的普通函数只能靠 printf 家族
//      (类型不安全)或枚举重载(个数写死);
//   2) 模板参数个数固定, make_shared/emplace 这类基础设施 C++11 之前
//      只能靠编译器内部的魔法;
//   3) 把"任意参数原样转交"给别的函数无从谈起(配合 06 完美转发才完整)。
// 核心概念:
//   * template<typename... Ts> 声明"参数包"(type pack);
//   * Ts... 在调用处展开包; 处理手段: 递归拆分(本例) ——
//     C++17 起可用"折叠表达式"一行搞定(sum 见 cpp17 批次);
//   * sizeof...(Ts) 获取包内元素个数(编译期)。
// 编译: g++ -std=c++11 -Wall -Wextra 08_variadic_templates.cpp -o demo
// ============================================================================
#include <iostream>
#include <memory>
#include <string>
#include <utility>

// ---- 递归终点: 空包时调用这个重载, 结束递归 ----
void print_all()
{
    std::cout << "(print_all 结束)\n";
}

// ---- 递归步: 处理第一个实参, 其余打包继续递归 ----
template <typename First, typename... Rest>
void print_all(const First& first, const Rest&... rest)
{
    std::cout << first << ' ';
    print_all(rest...);
}

// ---- sizeof... : 数一数包里有几个参数(编译期常量) ----
template <typename... Ts>
std::size_t count_args(Ts&&...)
{
    return sizeof...(Ts);
}

// ---- 完美转发 + 变参: 任意个数、任意类型的实参原样交给 make_shared ----
// C++98: 想实现 build<Point>(x, y) 这种调用需要为每个参数个数写重载
struct Point {
    Point(int a, int b) : x(a), y(b) {}
    int x, y;
};

// std::forward 详解见 06 完美转发; 这里只记要点:
// 参数包 Args&&... 逐一生前向引用, forward<Args>(args)... 把每个参数的
// 左/右值属性原样转交 —— 否则实参全部退化成左值拷贝(见 06)
template <typename T, typename... Args>
std::shared_ptr<T> build(Args&&... args)
{
    return std::make_shared<T>(std::forward<Args>(args)...);
}

int main()
{
    // 一个函数打印任意多个、任意类型的实参 —— 类型安全(printf 做不到)
    print_all(1, 2.5, "three", std::string("four"), '5');

    std::cout << "count_args(1, 2, 3) = " << count_args(1, 2, 3) << '\n';
    std::cout << "count_args()       = " << count_args() << '\n';

    auto p = build<Point>(3, 4);     // make_shared<Point>(3, 4)
    std::cout << "build<Point>(3,4) -> (" << p->x << ", " << p->y << ")\n";
    return 0;
}
