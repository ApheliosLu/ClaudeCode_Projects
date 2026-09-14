// ============================================================================
// 04_span.cpp  现代 C++ 示例集 · C++20
// 主题: std::span —— 连续内存的"视图"(指针 + 长度, 不拥有)
// 解决的问题(C++98/11):
//   1) 函数想接收"一段连续整数", 参数只能写 const vector<int>&(与容器
//      类型耦合)或 int* + size 两个参数(长度与数据分离, 极易配错);
//   2) C 数组传参自动退化成指针, 长度信息静默丢失;
//   3) 想切"子区间"传给别的函数, 没有轻量表达, 只能拷贝。
// 替代旧写法: vector/数组/裸指针三种重载 -> 一个 std::span 参数;
//            string_view 是"字符的 span"(它是 C++17 先出的)
// 要点:
//   * span 不拥有元素 —— 生命周期必须短于被观察的容器(同 string_view);
//   * 只接受"连续存储"的范围(vector、array、C 数组), list 不行;
//   * 模板参数可带长度: span<int, 4> 编译期定长(数组退化的解药)。
// 编译: g++ -std=c++20 -Wall -Wextra 04_span.cpp -o demo
// ============================================================================
#include <array>
#include <iostream>
#include <span>
#include <vector>

// 一个函数通吃三种"连续序列", 不需要为容器类型写重载
double average(std::span<const int> s)
{
    long long sum = 0;
    for (int v : s)
        sum += v;
    return static_cast<double>(sum) / static_cast<double>(s.size());
}

// span<int> 是可变视图: 修改会写回原容器
void scale(std::span<int> s, int factor)
{
    for (int& v : s)
        v *= factor;
}

int main()
{
    std::vector<int> v{1, 2, 3, 4};
    std::array<int, 4> a{2, 4, 6, 8};
    int carr[]{3, 5, 7};                    // C 数组: 传参不再退化成裸指针

    std::cout << "同一函数吃三种容器:\n";  // 输出: 同一函数吃三种容器:
    std::cout << "  average(v)     = " << average(v) << '\n';  // 输出:   average(v)     = 2.5
    std::cout << "  average(a)     = " << average(a) << '\n';  // 输出:   average(a)     = 5
    std::cout << "  average(carr)  = " << average(carr) << '\n';  // 输出:   average(carr)  = 5

    scale(v, 10);                           // 改的是 v 本体
    std::cout << "scale(v, 10) 后 v = { ";  // 输出: scale(v, 10) 后 v = {
    for (int x : v) std::cout << x << ' ';  // 输出: 10 20 30 40
    std::cout << "}\n";  // 输出: }

    // 编译期定长: 从 std::array 直接得到 span<int, 4>
    std::span<int, 4> fixed = a;
    std::cout << "fixed[0] = " << fixed[0]  // 输出: fixed[0] = 2, 定长 span 大小 = 4
              << ", 定长 span 大小 = " << fixed.size() << '\n';

    // O(1) 切片: first / last / subspan —— 零拷贝
    std::span<int> s = v;
    std::cout << "v 前两个: ";  // 输出: v 前两个:
    for (int x : s.first(2)) std::cout << x << ' ';  // 输出: 10 20
    std::cout << " | 后两个: ";  // 输出:  | 后两个:
    for (int x : s.last(2)) std::cout << x << ' ';  // 输出: 30 40
    std::cout << " | 中间两个(v[1..2]): ";  // 输出:  | 中间两个(v[1..2]):
    for (int x : s.subspan(1, 2)) std::cout << x << ' ';  // 输出: 20 30
    std::cout << '\n';

    // 悬垂警告(与 string_view 同理, 只注释不执行):
    // std::span<int> dangling = std::vector<int>{1, 2, 3};  // 临时 vector 立刻销毁
    return 0;
}
