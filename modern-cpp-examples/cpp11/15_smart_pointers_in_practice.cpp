// ============================================================================
// 15_smart_pointers_in_practice.cpp  现代 C++ 示例集 · C++11
// 主题: 智能指针的"来源 / 判断 / 实战" —— 04_smart_pointers.cpp 的续篇
// 04 讲了三个智能指针的 API, 本文件补上它没讲的三件事:
//   1) 来源: 为什么会有智能指针 —— auto_ptr 错在"用拷贝的语法表达转移的语义";
//   2) 判断: 什么时候根本不该用指针 —— 能用值就别用指针;
//   3) 实战: 多态容器 vector<unique_ptr<Base>>、weak_ptr 反向指针。
// 一句话记住所有权问题:
//   裸指针只表达"地址", 不表达"谁负责 delete" —— 智能指针就是给这句话补类型。
// 遇到指针先问四句:
//   ① 我真的需要指针吗? ② 谁拥有它? ③ 主人唯一吗? ④ 我要干涉它的死期吗?
// 编译: g++ -std=c++11 -Wall -Wextra 15_smart_pointers_in_practice.cpp -o demo
// 注: 第 1 节用已废弃的 std::auto_ptr 做反面教材。不加处理的话, 编译器会对
//     每一处 auto_ptr 报同一条警告(实测原文):
//       warning: 'template<class> class std::auto_ptr' is deprecated:
//                use 'std::unique_ptr' instead [-Wdeprecated-declarations]
//     下面用 #pragma 把它屏蔽掉, 让本文件保持 0 警告 —— 警告内容本身即结论。
//     (该 pragma 是 GCC/Clang 专用; MSVC 会忽略未知 pragma, 同样能编过)
// ============================================================================
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

// ---------- 1. 来源: auto_ptr 用"拷贝"的语法, 表达"转移"的语义 ----------
// C++98 没有移动语义(右值引用), auto_ptr 只能借拷贝构造/拷贝赋值来表达
// 所有权转移 —— 源对象被"掏空"。三个后果:
//   a) 一行看似无害的拷贝就掏空了源对象;
//   b) 按值传参时, 调用点完全看不出所有权被拿走;
//   c) 因此不能放进容器(vector 内部会拷贝元素)。
// C++11 有了移动语义, 才第一次能把"复制"和"转移"在类型层面分开 —— 这正是
// unique_ptr 存在的前提。它不是"改良版 auto_ptr", 而是"有了移动语义之后,
// 才第一次可能被写对"的那个 auto_ptr。
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"

void sink(std::auto_ptr<std::string> p)
{
    std::cout << "  函数内拿到: " << *p << '\n'; // 输出: 函数内拿到: <*p>, 如   函数内拿到: world
}

void demo_auto_ptr()
{
    std::cout << "-- 1. auto_ptr: 拷贝的语法, 转移的语义 --\n"; // 输出: -- 1. auto_ptr: 拷贝的语法, 转移的语义 --

    std::auto_ptr<std::string> a(new std::string("hello"));
    std::auto_ptr<std::string> b = a; // 语法上是拷贝
    std::cout << "  b 拿到: " << *b << '\n';                                  // 输出:   b 拿到: hello
    std::cout << "  而 a: " << (a.get() ? "还有效" : "已被掏空(nullptr)") << '\n'; // 输出:   而 a: 已被掏空(nullptr)

    std::auto_ptr<std::string> c(new std::string("world"));
    std::cout << "  调用前 c: " << (c.get() ? "有效" : "空") << '\n'; // 输出:   调用前 c: 有效
    sink(c);                                                        // 输出:   函数内拿到: world (同时 c 被掏空)
    std::cout << "  调用后 c: " << (c.get() ? "有效" : "已被掏空(nullptr)") << '\n'; // 输出:   调用后 c: 已被掏空(nullptr)
}

#pragma GCC diagnostic pop

// ---------- 2. 判断: 能用值就别用指针 ----------
// 智能指针是"必须用指针时"的兜底, 不是默认选择。
// 为一个 8 字节的小对象做堆分配, 换来的只有额外开销和额外责任。
struct Pos
{
    int x;
    int y;
};

class ShipWithPtr // 反面写法: 小对象也上堆
{
public:
    ShipWithPtr() : pos_(new Pos{0, 0}) {}
    ~ShipWithPtr() { delete pos_; } // 手写析构
    int x() const { return pos_->x; }
    // 注意: 没有写拷贝构造/拷贝赋值 -> 编译器生成默认的浅拷贝 ->
    // 两个对象持有同一个 Pos* -> 各自析构时双重释放(五法则见 14)

private:
    Pos *pos_;
};

class ShipWithValue // 正写: 功能与 ShipWithPtr 完全等价
{
public:
    int x() const { return pos_.x; } // 无需 new, 无需析构, 自动可拷贝
private:
    Pos pos_{0, 0}; // 值成员
};

void demo_value_vs_ptr()
{
    std::cout << "-- 2. 能用值就别用指针 --\n"; // 输出: -- 2. 能用值就别用指针 --

    ShipWithPtr a;
    ShipWithValue b;
    std::cout << "  两种写法的结果一样: " << a.x() << " / " << b.x() << '\n'; // 输出:   两种写法的结果一样: 0 / 0
    std::cout << "  差别不在结果而在代价: 堆分配 + 手写析构 + 还得补五法则\n"; // 输出:   差别不在结果而在代价: 堆分配 + 手写析构 + 还得补五法则

    // 下面这行一旦放开就是双重释放(禁止示范):
    // ShipWithPtr c = a;   // 浅拷贝: c 和 a 持有同一个 Pos*
    // 只有这三种情况才值得用指针成员:
    //   对象可能不存在(std::optional 表达) / 需要多态 / 大对象要延迟构造(如 pimpl)
}

// ---------- 3. 实战一: 多态容器 ----------
// 抽象类不能按值放进容器(会对象切片, 且无法实例化), 所以必须放指针;
// 而裸指针容器要手写 delete 循环、遇到异常还会漏。标准答案是:
//   std::vector<std::unique_ptr<Shape>>
struct Shape
{
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual std::string name() const = 0;
};

struct Circle : Shape
{
    double r;
    explicit Circle(double r_) : r(r_) {}
    double area() const override { return 3.14159 * r * r; } // 本程序里返回 3.14159
    std::string name() const override { return "Circle"; }   // 本程序里返回 "Circle"
};

struct Rect : Shape
{
    double w, h;
    Rect(double w_, double h_) : w(w_), h(h_) {}
    double area() const override { return w * h; } // 本程序里返回 6
    std::string name() const override { return "Rect"; } // 本程序里返回 "Rect"
};

void demo_polymorphic_container()
{
    std::cout << "-- 3. 多态容器: vector<unique_ptr<Shape>> --\n"; // 输出: -- 3. 多态容器: vector<unique_ptr<Shape>> --
    std::vector<std::unique_ptr<Shape>> shapes;
    // C++11 只能 new 包一层; C++14 起可写 std::make_unique<Circle>(1.0)(见 cpp14/03)
    shapes.push_back(std::unique_ptr<Shape>(new Circle(1.0)));
    shapes.push_back(std::unique_ptr<Shape>(new Rect(2.0, 3.0)));

    double total = 0;
    for (const auto &s : shapes) // 注意是 const auto&, 不是按值(unique_ptr 不能拷贝)
    {
        std::cout << "  " << s->name() << " 的面积 = " << s->area() << '\n';
        // 输出: 每个形状一行 —— "  Circle 的面积 = 3.14159" 然后 "  Rect 的面积 = 6"
        total += s->area();
    }
    std::cout << "  总面积 = " << total << '\n'; // 输出:   总面积 = 9.14159
    // 函数结束 -> vector 析构 -> 每个 unique_ptr 析构 -> 虚析构按真实类型释放
}

// ---------- 4. 实战二: weak_ptr 的反向指针 ----------
// 场景 A(反面): 父子互相强引用 -> 循环引用, 两个计数都到不了 0
struct BadParent;
struct BadChild
{
    std::string name;
    std::shared_ptr<BadParent> parent; // 强引用父
    explicit BadChild(std::string n) : name(std::move(n)) {}
    ~BadChild() { std::cout << "    ~BadChild(" << name << ")\n"; } // 输出:     ~BadChild(<name>), 本程序未走到(循环引用)
};
struct BadParent
{
    std::string name;
    std::vector<std::shared_ptr<BadChild>> children; // 强引用子
    explicit BadParent(std::string n) : name(std::move(n)) {}
    ~BadParent() { std::cout << "    ~BadParent(" << name << ")\n"; } // 输出:     ~BadParent(<name>), 本程序未走到(循环引用)
};

// 场景 B(正写): 父用 shared_ptr 强引用子(父管子的死期),
//              子用 weak_ptr 观察父(子不干涉父的死期) —— 这就是"反向指针"
struct Parent;
struct Child
{
    std::string name;
    std::weak_ptr<Parent> parent; // 反向指针: 观察, 不占有
    explicit Child(std::string n) : name(std::move(n)) {}
    ~Child() { std::cout << "    ~Child(" << name << ")\n"; } // 输出:     ~Child(<name>), 如     ~Child(kid)
};
struct Parent
{
    std::string name;
    std::vector<std::shared_ptr<Child>> children;
    explicit Parent(std::string n) : name(std::move(n)) {}
    ~Parent() { std::cout << "    ~Parent(" << name << ")\n"; } // 输出:     ~Parent(<name>), 如     ~Parent(dad)
};

void demo_weak_back_pointer()
{
    std::cout << "-- 4. weak_ptr 反向指针 --\n"; // 输出: -- 4. weak_ptr 反向指针 --

    std::cout << "  A) 互相强引用(反面):\n"; // 输出:   A) 互相强引用(反面):
    {
        auto p = std::make_shared<BadParent>("dad");
        auto c = std::make_shared<BadChild>("kid");
        c->parent = p;
        p->children.push_back(c);
        std::cout << "     离开作用域...\n"; // 输出:      离开作用域...
    }
    std::cout << "     上面没打印任何析构 —— 循环引用, 内存泄漏了\n"; // 输出:      上面没打印任何析构 —— 循环引用, 内存泄漏了

    std::cout << "  B) 反向指针(正写): 父强引用子, 子用 weak_ptr 观察父\n"; // 输出:   B) 反向指针(正写): 父强引用子, 子用 weak_ptr 观察父
    {
        auto p = std::make_shared<Parent>("dad");
        auto c = std::make_shared<Child>("kid");
        c->parent = p;            // weak: 不增加 p 的计数
        p->children.push_back(c); // shared: 父持有子
        if (auto dad = c->parent.lock()) // 观察者要访问父, 先 lock 提升成强引用
            std::cout << "     孩子 " << c->name << " 的父是 " << dad->name << '\n'; // 输出:      孩子 kid 的父是 dad
        std::cout << "     离开作用域...\n"; // 输出:      离开作用域...
        // 离开作用域: 局部变量 c 先析构(子仍被父持有, 不死) -> p 析构使计数归零
    }
    // 输出: 两行析构 —— "    ~Parent(dad)" 然后 "    ~Child(kid)"
    std::cout << "     两个析构都打印了 —— 没有泄漏\n"; // 输出:      两个析构都打印了 —— 没有泄漏
}

int main()
{
    demo_auto_ptr();
    demo_value_vs_ptr();
    demo_polymorphic_container();
    demo_weak_back_pointer();

    // ---------- 四连问: 遇到"需要一个指针"时按顺序问一遍 ----------
    // ① 我真的需要指针吗?   否 -> 直接用值或引用(最优先的答案)
    // ② 谁拥有这个对象?     我 -> unique_ptr; 大家一起 -> shared_ptr
    // ③ 主人唯一吗?         唯一 -> unique_ptr(零运行时开销)
    // ④ 我要干涉它的死期吗? 不干涉, 只想观察 -> weak_ptr
    //                       只是借用 -> T* / T&(根本不是智能指针)
    return 0;
}
