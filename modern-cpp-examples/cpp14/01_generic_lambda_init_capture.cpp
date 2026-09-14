// ============================================================================
// 01_generic_lambda_init_capture.cpp  现代 C++ 示例集 · C++14
// 主题: 泛型 Lambda + 初始化捕获(init-capture)
// 解决的问题(相对 C++11):
//   1) C++11 的 lambda 参数必须写明具体类型 —— 同样的逻辑想复用到
//      int/double/自定义类型上, 只能再写一个模板函数或复制粘贴;
//   2) C++11 的捕获只有 [=] 拷贝 和 [&] 引用 —— 无法把 move-only 类型
//      (unique_ptr/thread/stream)或"移动过来的大对象"装进 lambda;
//   3) C++14 还放宽了 lambda 返回类型推导(多语句体也可推导)。
// 替代旧写法: 具名模板函数 -> 泛型 lambda; [=] 捕获大对象 -> [x = std::move(v)]
// 编译: g++ -std=c++14 -Wall -Wextra 01_generic_lambda_init_capture.cpp -o demo
// ============================================================================
#include <iostream>
#include <string>
#include <utility>
#include <vector>

int main()
{
    // ---- 1. 泛型 lambda: 参数写 auto, 相当于一个匿名模板函数 ----
    // C++11: [](int a, int b) { return a + b; }  —— 换类型就要换签名
    auto add = [](auto a, auto b) { return a + b; };
    std::cout << add(1, 2) << ' '
              << add(1.5, 2.5) << ' '
              << add(std::string("ab"), std::string("cd")) << '\n';  // int / double / string
    // 输出: 3 4 abcd

    // 同一套"打印容器"逻辑, 容器元素类型随便换
    auto print_vec = [](const auto& v) {
        for (const auto& x : v)
            std::cout << x << ' ';  // 输出: 元素后跟一个空格
        std::cout << '\n';
    };
    std::vector<int>    vi{3, 1, 2};
    std::vector<double> vd{2.5, 0.5, 1.5};
    print_vec(vi);  // 输出: 3 1 2
    print_vec(vd);  // 输出: 2.5 0.5 1.5

    // ---- 2. 初始化捕获: 把"移动过来的对象"关进 lambda ----
    // 经典场景: 大对象 + 只在线程/回调里用一次 —— 拷贝毫无必要
    std::string big = "hello, I am an expensive buffer";
    auto reader = [s = std::move(big)] { return s.size(); };
    std::cout << "captured size = " << reader() << '\n';  // 输出: captured size = 31
    // 注意: big 已被搬走, 处于"合法但未指定"状态, 之后不要再使用它

    // ---- 3. auto&& 参数: 泛型 lambda 内部做完美转发 ----
    // (auto&& 在此处等价于转发引用 T&&, 见 cpp11/06)
    auto invoke = [](auto&& f, auto&& arg) {
        return f(std::forward<decltype(arg)>(arg));
    };
    auto twice = [](auto x) { return x * 2; };
    std::cout << "invoke(twice, 21) = " << invoke(twice, 21) << '\n';
    // 输出: invoke(twice, 21) = 42
    return 0;
}
