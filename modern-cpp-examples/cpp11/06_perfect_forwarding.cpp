// ============================================================================
// 06_perfect_forwarding.cpp  现代 C++ 示例集 · C++11
// 主题: 完美转发(转发引用 T&& + std::forward)
// 解决的问题(C++98):
//   C++98 写不出"通用转发层": 参数要么 const 拷贝/引用(丢失右值性),
//   要么固定左值引用。于是工厂、包装器想"把实参原样转交给下一个函数"
//   (保留 const 性 + 左右值性)根本做不到 —— 右值实参传下去永远变成拷贝。
// 关键语法(配合 08 变参模板使用效果最佳):
//   * T&& 出现在模板参数位置叫"转发引用"(万能引用):
//       实参是左值 -> T 推导为 T&   (引用折叠 T& && = T&)
//       实参是右值 -> T 推导为 T
//   * std::forward<T>(x) 按 T 还原实参的左右值性: T 是引用则左值, 否则右值;
//   * std::move 无条件转右值; std::forward 条件性转右值 ——
//     转发场景只能选 forward, 滥用 move 会把左值误当右值搬走。
// 替代旧写法: 按类型重载 N 个转发函数 -> 一个转发引用模板
// 编译: g++ -std=c++11 -Wall -Wextra 06_perfect_forwarding.cpp -o demo
// ============================================================================
#include <iostream>
#include <memory>
#include <string>
#include <utility>

struct Widget {
    explicit Widget(const std::string& s) : text(s)
    {
        std::cout << "Widget(const string&) —— 拷贝路径\n"; // 输出: Widget(const string&) —— 拷贝路径
    }
    explicit Widget(std::string&& s) : text(std::move(s))
    {
        std::cout << "Widget(string&&) —— 移动路径\n"; // 输出: Widget(string&&) —— 移动路径
    }
    std::string text;
};

// 核心示例: 一个模板函数把实参"原样"转交给 Widget 构造函数
template <typename T>
void forward_to_widget(T&& arg)      // T&& : 转发引用
{
    // 实参是左值时 T = std::string&  -> forward 还原为左值 -> 拷贝路径;
    // 实参是右值时 T = std::string   -> forward 还原为右值 -> 移动路径。
    Widget w(std::forward<T>(arg));
    std::cout << "   -> 构造出 Widget, text = \"" << w.text << "\"\n";
        // 输出: 行首 3 个空格 + -> 构造出 Widget, text = "<w.text>"
}

// 工业级典型用途: 手搓的"转发工厂"(参数个数任意, 见 08 变参模板)
// std::make_shared / std::make_unique 内部正是这么实现的
template <typename T, typename... Args>
std::unique_ptr<T> my_make_unique(Args&&... args)
{
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}

int main()
{
    std::string left = "left value";
    forward_to_widget(left);        // 左值 -> T = std::string&   -> 拷贝路径
    // 输出:
    //   Widget(const string&) —— 拷贝路径
    //      -> 构造出 Widget, text = "left value"
    forward_to_widget(std::string("right value"));  // 右值 -> T = std::string -> 移动路径
    // 输出:
    //   Widget(string&&) —— 移动路径
    //      -> 构造出 Widget, text = "right value"

    auto u = my_make_unique<Widget>(std::string("via my_make_unique")); // 输出: Widget(string&&) —— 移动路径
    std::cout << "工厂产物: " << u->text << '\n'; // 输出: 工厂产物: via my_make_unique
    return 0;
}
