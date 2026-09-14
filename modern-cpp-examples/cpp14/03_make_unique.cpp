// ============================================================================
// 03_make_unique.cpp  现代 C++ 示例集 · C++14
// 主题: std::make_unique(unique_ptr 的标准创建方式)
// 解决的问题(历史与异常安全):
//   C++11 只有 std::make_shared, unique_ptr 只能配裸 new:
//     std::unique_ptr<T> p(new T(args...));
//   把"new 出的裸指针"传给 unique_ptr 构造的瞬间如果抛异常
//   (例如同一表达式里另一个函数实参抛错), new 出来的内存没人接管
//   -> 泄漏。std::make_unique 把分配与包装做成一步, 从根上消除该缺口。
// 最佳实践(现代 C++ 铁律):
//   * 创建 unique_ptr 一律 std::make_unique(数组版本 C++14 也有);
//   * 创建 shared_ptr 一律 std::make_shared(对象+控制块单次分配, 更快);
//   * 只有需要自定义删除器 / 自定义分配器时才退回裸 new;
//   * 永远不写 std::shared_ptr<X>(new X) 这种"裸指针裸奔"的中间态。
// 编译: g++ -std=c++14 -Wall -Wextra 03_make_unique.cpp -o demo
// ============================================================================
#include <iostream>
#include <memory>
#include <string>
#include <utility>

struct Config {
    int         port = 8080;
    std::string host = "127.0.0.1";
};

class Server {
public:
    explicit Server(Config cfg) : cfg_(std::move(cfg)) {}
    void start() const
    {
        std::cout << "监听 " << cfg_.host << ':' << cfg_.port << '\n';  // 输出: 监听 127.0.0.1:8080
    }
private:
    Config cfg_;
};

int main()
{
    // C++11 时代: std::unique_ptr<Server> s(new Server(Config{}));
    // 上面写法在极端情况有泄漏缺口, 且读起来绕 —— make_unique 一步到位:
    auto s = std::make_unique<Server>(Config{});
    s->start();  // 输出: 监听 127.0.0.1:8080

    // 数组版本: make_unique<int[]>(n) 初始化后像普通数组一样用 [] 访问
    auto arr = std::make_unique<int[]>(5);
    for (int i = 0; i < 5; ++i)
        arr[i] = i * i;
    std::cout << "arr[4] = " << arr[4] << '\n';  // 输出: arr[4] = 16

    // shared_ptr 侧: make_shared 单次分配对象+控制块, 性能更好
    auto cfg = std::make_shared<Config>();
    cfg->port = 9000;
    std::cout << "shared config port = " << cfg->port << '\n';  // 输出: shared config port = 9000
    return 0;
}
