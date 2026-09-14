// ============================================================================
// 08_ctad_and_inline.cpp  现代 C++ 示例集 · C++17 · 补充(此前遗漏的强烈推荐特性)
// 主题: CTAD(类模板实参推导) + inline 变量 + 自定义推导指引
// 解决的问题:
//   1) C++11 函数能写 auto 了, 但"创建类模板对象"还得手写全部类型参数:
//      std::pair<std::string, int> p; std::vector<int> v{...}; ——
//      右半边完全是噪音。C++17 起编译器从初始化式推导(CTAD);
//   2) 头文件里定义"内联全局变量 / 类静态成员": C++98 属 ODR 违规
//      (只能声明, 再挑一个 .cpp 定义一次); C++17 的 inline 变量让
//      header-only 写法安全;
//   3) 想让推导"更聪明"(如把 const char* 键自动变 std::string):
//      写自定义推导指引(deduction guide)。
// 编译: g++ -std=c++17 -Wall -Wextra 08_ctad_and_inline.cpp -o demo
// ============================================================================
#include <array>
#include <iostream>
#include <optional>
#include <string>
#include <utility>
#include <vector>

// ---- 自定义类型: 有构造函数的类可以直接 CTAD ----
template <typename T>
class Box {
public:
    explicit Box(T v) : value_(v) {}
    T value() const { return value_; }
private:
    T value_;
};

// ---- 聚合类型没有构造函数, C++17 需要"推导指引"才能推导 ----
template <typename K, typename V>
struct DictEntry {
    K key;
    V value;
};
// 自定义推导指引: 告诉编译器"看到 DictEntry{...} 时怎么推导 K、V"
template <typename K, typename V>
DictEntry(K, V) -> DictEntry<K, V>;

// ---- inline 变量: 头文件放心的全局/静态成员(C++98 要挪到 .cpp 定义) ----
class AppConfig {
public:
    static inline int         verbosity = 2;        // 直接在头文件初始化
    static inline std::string version   = "1.0";
};
// C++98 写法: class AppConfig { static int verbosity; }; + 在某个 .cpp:
//   int AppConfig::verbosity = 2;   —— header-only 库做不到

int main()
{
    // ---- 1. CTAD: 标准库容器/工具类型全部支持 ----
    // C++11: std::pair<std::string, int> p("name", 1);
    std::pair p("name", 1);              // 推导出 pair<const char*, int>
    std::vector v{3, 1, 2};              // vector<int> —— 类型参数是噪音
    std::array a{1, 2, 3};               // array<int, 3>
    std::optional o(42);                 // optional<int>
    std::cout << "pair: (" << p.first << ", " << p.second << ")\n"
              << "vector.size = " << v.size() << ", array.size = "
              << a.size() << ", optional = " << *o << '\n';
    // 输出:
    //   pair: (name, 1)
    //   vector.size = 3, array.size = 3, optional = 42

    // ---- 2. 自定义类型直接推导 ----
    Box b(10);                           // C++11: Box<int> b(10);
    std::cout << "Box::value = " << b.value() << '\n';  // 输出: Box::value = 10

    // ---- 3. 聚合 + 自定义推导指引 ----
    DictEntry e{"age", 30};              // 无指引时聚合无法推导, 加上即可
    std::cout << "DictEntry: " << e.key << " -> " << e.value << '\n';  // 输出: DictEntry: age -> 30

    // ---- 4. inline 变量 ----
    std::cout << "verbosity = " << AppConfig::verbosity << '\n';  // 输出: verbosity = 2
    AppConfig::verbosity = 3;            // 可变; 换头文件改一处即可
    std::cout << "改后 verbosity = " << AppConfig::verbosity
              << ", version = " << AppConfig::version << '\n';
    // 输出: 改后 verbosity = 3, version = 1.0
    return 0;
}
