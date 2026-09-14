// ============================================================================
// 04_smart_pointers.cpp  现代 C++ 示例集 · C++11
// 主题: unique_ptr / shared_ptr / weak_ptr 智能指针
// 解决的问题(C++98):
//   1) 裸指针手动 new/delete: 忘删泄漏, 提前 return/抛异常泄漏, 重复 delete 崩溃;
//   2) C++98 的 std::auto_ptr 拷贝会"悄悄转移所有权", 极易悬垂(已从标准移除);
//   3) 动态数组 new[]/delete[] 手写管理(现在交给 std::vector 或 unique_ptr<T[]>);
//   4) 多段代码共享同一资源时, 没人说得清谁负责释放。
// 替代旧写法: new/delete -> unique_ptr/shared_ptr; auto_ptr -> unique_ptr;
//            weak_ptr 专门破解 shared_ptr 循环引用
// 选择铁律:
//   * 默认 unique_ptr: 独占所有权, 与裸指针同样零开销;
//   * 真需要共享才 shared_ptr(一律 make_shared 创建, 见 08);
//   * 对象生命周期受别人控制、自己只"借来看一看" -> weak_ptr + lock();
// 编译: g++ -std=c++11 -Wall -Wextra 04_smart_pointers.cpp -o demo
// ============================================================================
#include <iostream>
#include <memory>
#include <string>
#include <utility>

class Logger {
public:
    // "传值 + std::move 进成员" 是 sink 惯用法: 右值实参全程零拷贝(见 05)
    explicit Logger(std::string name) : name_(std::move(name)) {}
    void log(const std::string& msg) const
    {
        std::cout << '[' << name_ << "] " << msg << '\n'; // 输出: [<name_>] <msg>, 如 [main] hello unique_ptr
    }
private:
    std::string name_;
};

// 工厂函数返回 unique_ptr: 调用者独占所有权, 意图一目了然
std::unique_ptr<Logger> make_logger(const std::string& name)
{
    // C++11 只能 new; C++14 起更推荐 std::make_unique(见 cpp14/03)
    return std::unique_ptr<Logger>(new Logger(name));
}

// 循环引用的经典场景: 链表/图节点互相指向
struct Node {
    int               value;
    std::weak_ptr<Node> next;   // 弱引用: 观察对方, 不增加引用计数
    explicit Node(int v) : value(v) {}
    ~Node() { std::cout << "~Node(" << value << ") 析构\n"; } // 输出: ~Node(<value>) 析构, 如 ~Node(2) 析构
};

int main()
{
    // ---- 1. unique_ptr: 独占所有权, 出作用域自动释放(即使中途抛异常) ----
    auto p = make_logger("main");
    p->log("hello unique_ptr"); // 输出: [main] hello unique_ptr

    auto q = std::move(p);          // 所有权转移(移动), 转移后 p 为空
    if (!p)
        std::cout << "p 已为空(nullptr)\n"; // 输出: p 已为空(nullptr)
    q->log("所有权已转移到 q"); // 输出: [main] 所有权已转移到 q

    // ---- 2. 动态数组的现代写法(替代 new[]/delete[]) ----
    // C++98: int* a = new int[5]; ...; delete[] a;   还要自己记尺寸
    std::unique_ptr<int[]> arr(new int[5]{1, 2, 3, 4, 5});
    std::cout << "arr[0] = " << arr[0] << "  无需手动 delete[]\n"; // 输出: arr[0] = 1  无需手动 delete[]
    // 若元素本身更重要(动态增删/排序), 首选 std::vector<int>, 不要裸数组

    // ---- 3. shared_ptr: 引用计数共享所有权 ----
    // make_shared = 制造 shared_ptr 的标准方式: 对象与引用计数"一次分配"
    // (比裸 new + shared_ptr(ptr) 两次分配更省且异常安全, 见文件头规则)
    auto s1 = std::make_shared<Logger>("shared");   // C++11 就有 make_shared
    {
        auto s2 = s1;                               // 计数 1 -> 2
        std::cout << "内层 s1.use_count() = " << s1.use_count() << '\n'; // 输出: 内层 s1.use_count() = 2
    }                                               // s2 析构, 计数 2 -> 1
    std::cout << "外层 s1.use_count() = " << s1.use_count() << '\n'; // 输出: 外层 s1.use_count() = 1

    // 危险示范(禁止): 同一裸指针构造两个 shared_ptr -> 双重释放
    // Logger* raw = new Logger("x");
    // std::shared_ptr<Logger> a(raw), b(raw);   // 崩溃!

    // ---- 4. weak_ptr: 旁观者, 不增加计数; 使用前先 lock() ----
    std::weak_ptr<Logger> w = s1;
    if (auto locked = w.lock())                    // lock 成功才拿到共享所有权
        locked->log("weak_ptr 成功 lock"); // 输出: [shared] weak_ptr 成功 lock
    s1.reset();                                    // s1 放弃所有权 -> 对象释放
    if (w.expired())
        std::cout << "对象已释放, w.expired() == true\n"; // 输出: 对象已释放, w.expired() == true

    // ---- 5. 循环引用: weak_ptr 破解 ----
    std::cout << "-- 两个节点互相指向(下一轮离开作用域观察析构)--\n"; // 输出: -- 两个节点互相指向(下一轮离开作用域观察析构)--
    {
        auto a = std::make_shared<Node>(1);
        auto b = std::make_shared<Node>(2);
        a->next = b;                                // shared_ptr 可隐式给 weak_ptr
        b->next = a;
        // 若把 next 声明成 shared_ptr<Node>: a 持有 b、b 持有 a,
        // 引用计数永远到不了 0, 离开作用域也不析构 —— 内存泄漏。
        // 换成 weak_ptr 后互不持有, 计数正常归零。
        if (auto sp = a->next.lock())
            std::cout << "a 的下一节点是 " << sp->value << '\n'; // 输出: a 的下一节点是 2
    } // 离开作用域时 b、a 依次析构 -> 输出: ~Node(2) 析构 | ~Node(1) 析构
    std::cout << "(若上面打印了两次 ~Node, 说明没有泄漏)\n"; // 输出: (若上面打印了两次 ~Node, 说明没有泄漏)
    return 0;
}
