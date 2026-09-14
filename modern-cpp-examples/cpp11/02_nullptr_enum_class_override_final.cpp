// ============================================================================
// 02_nullptr_enum_class_override_final.cpp  现代 C++ 示例集 · C++11
// 主题: nullptr / enum class / override / final
// 解决的问题(C++98):
//   1) NULL 本质是 0(int): 重载 f(int) 与 f(char*) 时 f(NULL) 会错误地
//      走进 f(int), 且不报任何警告;
//   2) 传统 enum 的成员泄漏到外层作用域, 且能隐式转 int, 极易误用;
//   3) 派生类想"覆盖"虚函数, 签名写错时 C++98 静默地变成新函数(藏雷);
//   4) C++98 没有任何机制阻止类被继承 / 虚函数被覆盖。
// 替代旧写法: NULL/0 -> nullptr; 传统 enum -> enum class;
//            无标注虚覆盖 -> override; 无防护 -> final
// 编译: g++ -std=c++11 -Wall -Wextra 02_nullptr_enum_class_override_final.cpp -o demo
// ============================================================================
#include <iostream>

// ---------- 1. nullptr: 真正的"空指针字面量", 不再是整数 0 ----------
void take(int) { std::cout << "take(int)\n"; } // 输出: take(int)（本程序未走到, 重载选中了 char* 版本）
void take(char *) { std::cout << "take(char*)\n"; } // 输出: take(char*)

// ---------- 2. enum class: 强作用域 + 强类型 ----------
// C++98 写法: enum Color { RED, GREEN };   // RED 直接污染外层作用域,
//                                          // 且可隐式转 int / 与整数比较
enum class Color : char
{
    Red,
    Green,
    Blue
}; // 可指定底层类型

// ---------- 3. override / final ----------
class Base
{
public:
    virtual ~Base() = default; // 多态基类必须有虚析构函数
    virtual void draw() const { std::cout << "Base::draw\n"; } // 输出: Base::draw（被 Derived 覆盖, 本程序未走到）
    virtual void info() const { std::cout << "Base::info\n"; } // 输出: Base::info（被 Derived 覆盖, 本程序未走到）
};

class Derived : public Base
{
public:
    // C++98 隐患: void draw() {...} 少写一个 const, 编译器不报错,
    // 悄悄变成一个全新的虚函数, 多态行为静默失效
    void draw() const override { std::cout << "Derived::draw\n"; } // 输出: Derived::draw
    void info() const final { std::cout << "Derived::info (final)\n"; } // 输出: Derived::info (final)
};

// final 类: 不允许再被继承(C++98 没有对应机制)
class Locked final : public Derived
{
};

// 下面这些一旦放开注释, 编译期直接报错 —— 这就是 override/final 的价值:
// class Bad1 : public Base { void draw() override {} };          // 少 const, 签名不符
// class Bad2 : public Derived { void info() const override {} }; // info 是 final
// class Bad3 : public Locked {};                                 // Locked 是 final

int main()
{
    // ---- nullptr ----
    // C++98: take(NULL);   NULL == 0 -> 走到 take(int), 几乎肯定是 bug
    take(nullptr); // 正确匹配 take(char*)  输出: take(char*)

    // ---- enum class ----
    Color c = Color::Red; // 必须带作用域前缀
    // int bad = c;                     // 编译错误: 不再隐式转 int
    // if (c == 0) { }                  // 编译错误: 不能与整数比较
    std::cout << "Color::Red 的底层值 = "
              << static_cast<int>(c) << '\n'; // 需要时显式转换  输出: Color::Red 的底层值 = 0

    // ---- override/final 的运行时表现 ----
    Base *p = new Derived;
    p->draw(); // 虚调用 -> Derived::draw  输出: Derived::draw
    p->info(); // 虚调用 -> Derived::info  输出: Derived::info (final)
    delete p;
    return 0;
}
