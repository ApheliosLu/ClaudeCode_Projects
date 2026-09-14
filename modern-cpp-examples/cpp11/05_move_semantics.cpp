// ============================================================================
// 05_move_semantics.cpp  现代 C++ 示例集 · C++11
// 主题: 移动语义(移动构造/移动赋值)与 std::move
// 解决的问题(C++98):
//   1) 按值返回大对象、往容器放对象时, 必然发生整块深拷贝,
//      即使源对象下一秒就被销毁;
//   2) 资源只能"转移所有权"的类型(如文件句柄)根本无法表达这种意图,
//      auto_ptr 的诡异拷贝语义更是个坑;
//   3) 没有 std::move 这样的工具来明确表达"请搬走, 别复制"。
// 替代旧写法: 传/返引用加手工搬移 -> 移动构造函数 + std::move
// 核心规则:
//   * T&& 是右值引用, 只绑定临时对象; std::move(x) 只是把 x 转成右值
//     (不搬任何东西, 本质是 static_cast<T&&>(x));
//   * 移动构造/赋值必须标记 noexcept: 否则 vector 扩容时宁可深拷贝
//     也不敢用移动(怕中途抛异常破坏强异常安全);
//   * 移动后源对象必须置为"空", 防止双重释放;
//   * 管理资源的类要写全"五法则": 析构 + 拷贝构造/赋值 + 移动构造/赋值
// 编译: g++ -std=c++11 -Wall -Wextra 05_move_semantics.cpp -o demo
//       想看"不省略拷贝/移动"的完整过程可加 -fno-elide-constructors
// ============================================================================
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

// 演示用的资源管理类: 持有一块堆内存
// (真实代码请用 std::vector<char> 等容器当成员, 这里是为了展示五法则本身)
class Buffer {
public:
    explicit Buffer(std::size_t n)
        : size_(n), data_(n ? new char[n] : nullptr)
    {
        std::cout << "构造(分配 " << n << " 字节)\n"; // 输出: 构造(分配 <n> 字节), 如 构造(分配 4 字节)
    }

    // 拷贝构造: 深拷贝 —— 昂贵
    Buffer(const Buffer& other)
        : size_(other.size_), data_(other.size_ ? new char[other.size_] : nullptr)
    {
        std::cout << "拷贝构造(整块深拷贝)\n"; // 输出: 拷贝构造(整块深拷贝)
        std::copy(other.data_, other.data_ + other.size_, data_);
    }

    // noexcept = 承诺函数不抛异常(一旦真抛就直接 terminate, 是"说到做到"的声明);
    // 移动构造必须加它: 否则容器扩容时"不敢用可能抛异常的移动", 宁可退回深拷贝,
    // 移动语义就白写了(注释见文件头)
    // 移动构造: 偷指针 —— 廉价 O(1); noexcept 必须加
    Buffer(Buffer&& other) noexcept
        : size_(other.size_), data_(other.data_)
    {
        other.size_ = 0;
        other.data_ = nullptr;          // 源对象置空, 防止双重释放
        std::cout << "移动构造(只偷指针)\n"; // 输出: 移动构造(只偷指针)
    }

    Buffer& operator=(const Buffer& other)
    {
        std::cout << "拷贝赋值\n"; // 输出: 拷贝赋值（本程序未走到）
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = size_ ? new char[size_] : nullptr;
            std::copy(other.data_, other.data_ + size_, data_);
        }
        return *this;
    }

    Buffer& operator=(Buffer&& other) noexcept
    {
        std::cout << "移动赋值\n"; // 输出: 移动赋值（本程序未走到）
        if (this != &other) {
            delete[] data_;             // 释放自己旧资源
            size_ = other.size_;
            data_ = other.data_;
            other.size_ = 0;
            other.data_ = nullptr;
        }
        return *this;
    }

    ~Buffer()
    {
        delete[] data_;
        std::cout << "析构\n"; // 输出: 析构
    }

private:
    std::size_t size_;
    char*       data_;
};

// 按值返回: 编译器常直接省略(拷贝省略/copy elision),
// 即使不省略也走移动而不是深拷贝
Buffer makeBuffer(std::size_t n)
{
    Buffer b(n);
    return b;
}

// sink 惯用法: 参数按值接收, 再用 std::move 搬进成员 ——
// 传右值实参时全程零拷贝; C++11 起 string/vector 等自带高效移动
class Greeter {
public:
    explicit Greeter(std::string name) : name_(std::move(name)) {}
    void greet() const { std::cout << "Hello, " << name_ << '\n'; } // 输出: Hello, <name_>, 如 Hello, world
private:
    std::string name_;
};

int main()
{
    // 预留容量, 把"扩容"因素单独放到第 3 步观察
    std::vector<Buffer> v;
    v.reserve(2);

    std::cout << "-- 1. 右值(临时对象): 只走移动, 不走深拷贝 --\n";
    // 输出: -- 1. 右值(临时对象): 只走移动, 不走深拷贝 --
    v.push_back(makeBuffer(4));     // 可能被省略成直接构造; 但绝不会深拷贝
    // 输出: 构造(分配 4 字节) | 移动构造(只偷指针) | 析构

    std::cout << "-- 2. 具名变量是左值: 默认拷贝; std::move 后走移动 --\n";
    // 输出: -- 2. 具名变量是左值: 默认拷贝; std::move 后走移动 --
    Buffer buf(8); // 输出: 构造(分配 8 字节)
    v.push_back(buf);               // 左值 -> 拷贝构造(深拷贝)  输出: 拷贝构造(整块深拷贝)
    v.push_back(std::move(buf));    // std::move -> 移动构造; 之后不要再碰 buf!
    // 输出: 移动构造(只偷指针) | 移动构造(只偷指针) | 析构 | 移动构造(只偷指针) | 析构
    std::cout << "(第 3 次 push 触发扩容, 旧元素被移动而非深拷贝)\n";
    // 输出: (第 3 次 push 触发扩容, 旧元素被移动而非深拷贝)

    std::cout << "-- 3. sink 惯用法 + 按值返回 --\n";
    // 输出: -- 3. sink 惯用法 + 按值返回 --
    Greeter g1("world");                              // 字符串被拷贝一次
    Greeter g2(std::string("rvalue str"));            // 直接移动, 零拷贝
    g1.greet(); // 输出: Hello, world
    g2.greet(); // 输出: Hello, rvalue str

    std::cout << "-- 程序结束, 容器元素依次析构 --\n";
    // 输出: -- 程序结束, 容器元素依次析构 --
    return 0; // 输出: 析构 | 析构 | 析构 | 析构（buf 与容器内 3 个元素在 main 结束时依次析构）
}
