// ============================================================================
// 07_lambda.cpp  现代 C++ 示例集 · C++11
// 主题: Lambda 表达式(与 STL 算法配合, 替代手写循环)
// 解决的问题(C++98):
//   1) 给算法传"小逻辑"必须定义具名函数或函数对象类(operator() 写在
//      类外, 代码散落, 可读性差);
//   2) 想捕获外层局部变量只能靠 std::bind / bind1st / bind2nd ——
//      这些工具在 C++11 之后已被 Lambda 全面取代(勿再学);
//   3) 查找/计数/遍历大量靠手写迭代器循环, 又长又易错。
// 替代旧写法: 函数指针/函数对象 -> lambda;
//            std::bind / bind1st / bind2nd -> lambda 捕获;
//            手写查找/计数循环 -> std::find_if / count_if / sort + lambda
// 注意(版本边界):
//   * C++11 已支持: 捕获列表、显式返回类型 -> 类型
//   * 泛型 lambda(参数写 auto)与初始化捕获 [x = std::move(v)]
//     是 C++14, 见 cpp14/01
// 编译: g++ -std=c++11 -Wall -Wextra 07_lambda.cpp -o demo
// ============================================================================
#include <algorithm>
#include <functional>
#include <iostream>
#include <string>
#include <vector>

struct Item {
    std::string name;
    double      price;
};

int main()
{
    std::vector<Item> cart{{"apple", 3.5}, {"book", 22.0}, {"pen", 5.0},
                           {"cherry", 30.0}, {"milk", 8.0}};
    const double budget = 20.0;

    // ---- [&] 按引用捕获外层变量; [=] 按值捕获(拷一份进来) ----
    // C++98: 必须定义全局函数 + std::count_if(cart.begin(), cart.end(), fn),
    //        而且 budget 传不进去(bind2nd 那种写法又丑又脆)
    auto affordable = std::count_if(cart.begin(), cart.end(),
                                    [&](const Item& i) { return i.price <= budget; });
    std::cout << "预算内的商品数: " << affordable << '\n'; // 输出: 预算内的商品数: 3

    // ---- 就地定义排序规则(替代手写排序函数/比较器类) ----
    std::sort(cart.begin(), cart.end(),
              [](const Item& a, const Item& b) { return a.price < b.price; });

    // ---- 查找第一个满足条件的元素 ----
    auto it = std::find_if(cart.begin(), cart.end(),
                           [](const Item& i) { return i.price >= 20.0; });
    if (it != cart.end())
        std::cout << "排序后第一个 >=20 元的: " << it->name << '\n'; // 输出: 排序后第一个 >=20 元的: book

    std::cout << "最贵: " << cart.back().name << " = "
              << cart.back().price << '\n'; // 输出: 最贵: cherry = 30

    // ---- mutable: 值捕获的"副本"内部可改, 不影响外部变量 ----
    int counter = 0;
    auto bump = [counter]() mutable { return ++counter; };
    std::cout << "bump() = " << bump()
              << "   外部 counter 仍是 " << counter << '\n'; // 输出: bump() = 1   外部 counter 仍是 0

    // ---- 存进 std::function: 类型擦除, 可以到处传递(有少量开销) ----
    std::function<int(int, int)> add = [](int a, int b) { return a + b; };
    std::cout << "std::function add(2,3) = " << add(2, 3) << '\n'; // 输出: std::function add(2,3) = 5

    // ---- C++98 的"手写循环累加"可以换成 accumulate(仍有意义) ----
    // C++98: double over = 0; for (it = cart.begin(); ...) if (it->price > budget) over += it->price;
    double over = 0;
    for (const auto& item : cart)
        if (item.price > budget)
            over += item.price;     // 范围 for + if 直观清晰, 保留也没问题
    std::cout << "超预算商品总价: " << over << '\n'; // 输出: 超预算商品总价: 52
    return 0;
}
