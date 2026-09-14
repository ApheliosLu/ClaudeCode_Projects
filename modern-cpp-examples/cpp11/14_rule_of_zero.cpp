// ============================================================================
// 14_rule_of_zero.cpp  现代 C++ 示例集 · C++11 · 补充(此前遗漏的强烈推荐特性)
// 主题: Rule of Zero(=default / =delete 的正确打开方式)
// 背景: cpp11/05 手写"五法则"(析构+拷贝构造/赋值+移动构造/赋值)是为了
//       展示资源管理的原理。但真实代码里 99% 的类根本不该自己写这些。
// 现代 C++ 资源管理铁律:
//   * 零规则(Rule of Zero): 让"成员"(容器/string/智能指针)去管理资源,
//     拷贝/移动/析构全部由编译器生成 —— 天然正确, 一行特殊成员都不用写;
//   * 五法则只在"确实持有需要手工打理的资源"时才写(如 05 的教学 Buffer);
//   * 想"禁止拷贝"(独占资源): 放 unique_ptr 成员(拷贝自动删除),
//     或显式 = delete 表明意图;
//   * 需要默认实现但想显式声明: 用 = default(可读性 + 意图清晰)。
// 替代旧写法: 手写浅拷贝/深拷贝/析构 -> 编译器默认 + 按需 =default/=delete
// 编译: g++ -std=c++11 -Wall -Wextra 14_rule_of_zero.cpp -o demo
// ============================================================================
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

// ---- 1. Rule of Zero: 一行特殊成员函数都不用写 ----
class Order {
public:
    explicit Order(std::string note) : note_(std::move(note)) {}
    void add(int v) { items_.push_back(v); }
    std::size_t count() const { return items_.size(); }
private:
    std::vector<int> items_;   // 容器: 深拷贝、高效移动它自己会
    std::string      note_;    // string: 同上
};

// ---- 2. move-only 类: unique_ptr 成员 = 拷贝自动消失 ----
// C++11 起编译器生成的拷贝操作遇到 unique_ptr 会自动删除 —— 类自然变成
// "可移动不可拷贝"(fstream/thread 等标准类都是这么做的)
class Task {
public:
    explicit Task(int id) : id_(new int(id)) {}   // 教学用裸 new; 实践用 make_unique
    Task(const Task&) = delete;                   // 显式声明拷贝禁用, 意图一目了然
    Task& operator=(const Task&) = delete;
    Task(Task&&) = default;                       // 移动保留(成员支持移动)
    Task& operator=(Task&&) = default;
    ~Task() = default;                            // unique_ptr 成员负责释放
    int value() const { return *id_; }
private:
    std::unique_ptr<int> id_;
};

// ---- 3. 多态基类: 虚析构 + 默认实现 ----
class Shape {
public:
    virtual ~Shape() = default;                   // 虚析构: 必须, 默认实现: 够用
    virtual void draw() const = 0;
};
class Circle : public Shape {
public:
    void draw() const override { std::cout << "画一个圆\n"; }   // 输出: 画一个圆
};

int main()
{
    // Order 拷贝 = 深拷贝(成员容器自己复制), 改副本不影响原单
    Order o("第一单");
    o.add(10);
    o.add(20);
    Order copy = o;               // 编译器生成的拷贝构造
    copy.add(30);
    std::cout << "原单件数 " << o.count()
              << ", 副本件数 " << copy.count() << " (深拷贝)\n";   // 输出: 原单件数 2, 副本件数 3 (深拷贝)

    // Order 移动 = 高效搬移(C++11 才有; C++98 只能拷贝)
    Order moved(std::move(o));
    std::cout << "moved 件数 " << moved.count() << " (搬走后不要再碰 o)\n";   // 输出: moved 件数 2 (搬走后不要再碰 o)

    // Task 只能移动, 不能拷贝
    Task t1(7);
    Task t2(std::move(t1));
    std::cout << "t2.value() = " << t2.value() << '\n';   // 输出: t2.value() = 7
    // Task t3 = t1;    // 编译错误: 拷贝被 =delete —— 编译器替你拦住

    // 多态 + 智能指针 + 虚析构: 释放路径完全正确
    std::unique_ptr<Shape> s(new Circle);
    s->draw();   // 输出: 画一个圆
    return 0;
}
