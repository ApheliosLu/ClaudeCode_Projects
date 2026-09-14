// ============================================================================
// 07_jthread_stop_token.cpp  现代 C++ 示例集 · C++20 · 补充(强烈推荐特性)
// 主题: std::jthread —— 自动 join 的线程 + 协作式取消(stop_token)
// 解决的问题(对比 cpp11/09 的 std::thread):
//   1) std::thread 析构时若仍 joinable 会直接 std::terminate ——
//      代码里提前 return 的路径一多, 漏掉 join 就崩;
//   2) 想"礼貌地让线程停下来": C++11 只能手写原子 bool 标志, 再手动
//      传指针给线程函数, 每个项目各写各的;
//   3) C++20 把两件事做成标配: 析构自动 join(RAII) + 内置 stop_source /
//      stop_token 协作式停止信号。
// 注意: 停止是"协作式"的 —— 线程必须自己轮询 stop_requested() 才能停下;
//      现代 C++ 从不"暴力杀线程"(那是 C 时代 pthread_cancel 的野蛮做法)。
// 编译: g++ -std=c++20 -Wall -Wextra -pthread 07_jthread_stop_token.cpp -o demo
//       本机 MinGW 动态链接缺 CRT/winpthread 入口点(0xC0000139), 需加 -static;
//       一般发行版直接编译即可(见 README 工具链特例)
// ============================================================================
#include <chrono>
#include <iostream>
#include <thread>

int main()
{
    // ---- 1. 自动 join: 忘写 join 也不会 terminate ----
    {
        std::jthread t([] {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            std::cout << "后台任务完成\n";  // 输出: 后台任务完成
        });
        std::cout << "主线程不等它, 继续干活...\n";  // 输出: 主线程不等它, 继续干活...
    }   // 离开作用域: 析构自动 join —— 任务一定跑完才往下走
    std::cout << "jthread 已自动 join, 程序安全退出\n";  // 输出: jthread 已自动 join, 程序安全退出

    // ---- 2. 协作式取消: 线程函数直接收 stop_token ----
    long long ticks = 0;
    std::jthread worker([&ticks](std::stop_token st) {
        while (!st.stop_requested())      // 每圈检查一次停止信号
            ++ticks;                      // 干活(计数代替真实任务)
    });
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    worker.request_stop();                // 主线程发出停止请求
    // 析构时自动 join —— join 建立了 happens-before, ticks 的读取无数据竞争
    std::cout << "worker 收到停止信号, 累计跑了 " << ticks << " 圈\n";
    // 输出(示例, 每次运行数值不同): worker 收到停止信号, 累计跑了 10884341 圈

    // ---- 3. stop_source 可独立于 jthread 使用(发给多个观察者) ----
    long long watches = 0;
    {
        std::stop_source src;             // 停止信号的"源头"
        std::jthread watcher([&watches, tk = src.get_token()] {
            while (!tk.stop_requested())
                ++watches;                // 观察中...
        });
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
        src.request_stop();               // 通知所有持有 token 的观察者
    }                                     // join 完成, 信号已生效
    std::cout << "watcher 观察到停止信号, 停止前看了 " << watches << " 次\n";
    // 输出(示例, 每次运行数值不同): watcher 观察到停止信号, 停止前看了 5285452 次
    return 0;
}
