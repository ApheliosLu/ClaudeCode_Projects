// ============================================================================
// 06_coroutine_generator.cpp  现代 C++ 示例集 · C++20
// 主题: 协程(Coroutines) —— 最小可运行示例: 手写"生成器"
// 解决的问题(C++98/11):
//   "按需产出一串值"(如无穷数列/流式读取)传统做法: 手写状态机类,
//   进度塞进一堆成员变量, 逻辑被撕成 next()/has_next() 碎片;
//   想写一个"能暂停、能恢复"的函数, 语言层面没有任何支持。
//   C++20 协程: 函数体内出现 co_await/co_yield/co_return 即为协程,
//   编译器自动生成"暂停/恢复"机制, 逻辑保持自然直写。
// 最简协程要实现的四个件(promise_type 是协程的控制器):
//   * promise_type::get_return_object()  返回给调用方的对象(本例 Generator);
//   * initial_suspend / final_suspend    起始/收尾要不要先挂起;
//   * yield_value(v)                     co_yield v 的落脚点;
//   * coroutine_handle                   驱动协程恢复/销毁的句柄。
// 生产环境直接用 C++23 的 std::generator(见 cpp23/01)或现成库;
// 本文件手写最小 Generator<T>, 用来弄懂原理。
// 编译: g++ -std=c++20 -Wall -Wextra 06_coroutine_generator.cpp -o demo
// ============================================================================
#include <coroutine>
#include <exception>
#include <iostream>

template <typename T>
class Generator {
public:
    struct promise_type {
        T current_value;

        Generator get_return_object()
        {
            return Generator{
                std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        // noexcept = 承诺函数不抛异常(协程框架要求这些钩子不得抛出)
        std::suspend_always initial_suspend() noexcept { return {}; } // 先挂起, 等第一次推进
        std::suspend_always final_suspend() noexcept { return {}; }   // 结束保持挂起, 由我们 destroy
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }              // 生成器内异常: 简化处理

        std::suspend_always yield_value(T v) noexcept                // co_yield v 的落脚点
        {
            current_value = v;
            return {};
        }
    };
    using handle_t = std::coroutine_handle<promise_type>;

    explicit Generator(handle_t h) : h_(h) {}
    Generator(const Generator&) = delete;
    Generator& operator=(const Generator&) = delete;
    Generator(Generator&& o) noexcept : h_(o.h_) { o.h_ = nullptr; }
    ~Generator() { if (h_) h_.destroy(); }      // 协程帧只能由句柄销毁

    // ---- 让生成器可以被范围 for 驱动: 内置迭代器 ----
    class iterator {
    public:
        iterator() = default;
        explicit iterator(handle_t h) : h_(h) {}
        const T& operator*() const { return h_.promise().current_value; }
        iterator& operator++()
        {
            h_.resume();                         // 恢复执行到下一个 co_yield 或结束
            if (h_.done()) h_ = nullptr;         // 跑完了 -> 变成"尾迭代器"
            return *this;
        }
        friend bool operator==(iterator a, iterator b) { return a.h_ == b.h_; }
        friend bool operator!=(iterator a, iterator b) { return !(a == b); }
    private:
        handle_t h_ = nullptr;
    };

    iterator begin()
    {
        if (!h_ || h_.done()) return iterator{};
        h_.resume();                             // 第一次推进: 跑到第一个 co_yield
        return h_.done() ? iterator{} : iterator{h_};
    }
    iterator end() { return iterator{}; }

private:
    handle_t h_;
};

// ==================== 协程本体: 长得像普通函数 ====================
// 区别: 返回类型换成"支持协程的类型", 内部出现 co_yield 即成为协程
Generator<int> naturals_to(int n)
{
    for (int i = 1; i <= n; ++i)
        co_yield i;                              // 挂起并把 i 交给调用方
}                                                // 调用方每 ++ 一次, 这里恢复一次

Generator<unsigned long long> fibonacci()        // 无穷序列: 想要多少要多少
{
    unsigned long long a = 0, b = 1;
    while (true) {
        co_yield b;
        auto t = a + b;
        a = b;
        b = t;
    }
}

int main()
{
    std::cout << "naturals_to(5): ";  // 输出: naturals_to(5):
    for (int v : naturals_to(5))
        std::cout << v << ' ';  // 输出: 1 2 3 4 5
    std::cout << '\n';

    std::cout << "fibonacci 前 12 个: ";  // 输出: fibonacci 前 12 个:
    int count = 0;
    for (auto v : fibonacci()) {
        std::cout << v << ' ';  // 输出: 1 1 2 3 5 8 13 21 34 55 89 144
        if (++count == 12) break;
    }
    std::cout << '\n';
    return 0;
}
