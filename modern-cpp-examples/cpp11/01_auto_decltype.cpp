// ============================================================================
// 01_auto_decltype.cpp  现代 C++ 示例集 · C++11
// 主题: auto 与 decltype 类型推导
// 解决的问题(C++98):
//   1) 类型必须手写全称, 例如 map 迭代器一长串, 难写易错;
//   2) 模板函数返回类型依赖实参时(如 a*b 的类型)几乎无法表达;
//   3) 重构时类型一变, 所有手写类型都要跟着改。
// 替代旧写法: 显式类型声明 -> auto; decltype 直接取"表达式的类型"
// 注意: 函数返回类型直接写 auto(不写尾置 ->decltype) 是 C++14 特性,
//       见 cpp14/02_return_type_deduction.cpp
// 编译: g++ -std=c++11 -Wall -Wextra 01_auto_decltype.cpp -o 01_auto_decltype
// ============================================================================
#include <iostream>
#include <map>
#include <string>
#include <type_traits>

// 尾置返回类型 (C++11): 返回类型依赖模板实参时, 写在 -> 之后
// C++98 只能靠函数重载或手写 traits 特化, 非常繁琐
template <typename L, typename R>
auto mul(const L& l, const R& r) -> decltype(l * r)
{
    return l * r;
}

int main()
{
    // ---- 1. auto: 类型交给编译器推导, 声明时必须给出初始化式 ----
    std::map<std::string, int> scores{{"alice", 90}, {"bob", 85}};

    // C++98: std::map<std::string,int>::iterator it = scores.find("alice");
    auto it = scores.find("alice");
    if (it != scores.end())
        std::cout << it->first << " -> " << it->second << '\n';

    // auto 剥掉顶层 const 与引用(传值语义); 想保留引用必须写 auto& / const auto&
    int          x = 1;
    const int&   cr = x;
    auto         y  = cr;   // int  (拷贝一份)
    auto&        z  = cr;   // const int&
    // 这是什么: 静态断言——编译期校验表达式, 为假则编译失败(报错信息是
    //           自己写的字符串, 替代 C 时代的运行时 if+return)
    // 这是什么: is_same<类型1,类型2> 编译期判断二者是否同一类型(用于类型检查/调试)
    static_assert(std::is_same<decltype(y), int>::value, "y 应是 int");
    static_assert(std::is_same<decltype(z), const int&>::value, "z 应是 const int&");
    (void)y;
    (void)z;

    // ---- 2. decltype: 不求值表达式, 只取它的类型 ----
    int    i = 3;
    double d = 2.5;
    decltype(i * d) product = i * d;   // double
    static_assert(std::is_same<decltype(product), double>::value,
                  "i*d 的类型应是 double");

    // decltype 三条规则(面试高频):
    //   decltype(变量名)       -> 变量的声明类型
    //   decltype((变量名))     -> 加括号变成"表达式", 表达式是左值 => T&
    //   decltype(表达式)       -> 按表达式值类别: 纯右值给 T, 左值给 T&
    decltype(i)     a = 5;   // int
    decltype((i))   b = a;   // int& (引用, 必须初始化)
    decltype(i + 1) c = i;   // int (i+1 是纯右值)
    static_assert(std::is_same<decltype(a), int>::value, "a 应是 int");
    static_assert(std::is_same<decltype(b), int&>::value, "b 应是 int&");
    static_assert(std::is_same<decltype(c), int>::value, "c 应是 int");
    (void)b;
    (void)c;

    std::cout << "mul(3, 4.5) = " << mul(3, 4.5) << '\n';
    return 0;
}
