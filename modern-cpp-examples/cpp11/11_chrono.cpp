// ============================================================================
// 11_chrono.cpp  现代 C++ 示例集 · C++11 · 补充(此前遗漏的强烈推荐特性)
// 主题: <chrono> 时间库 —— 时钟 / 时间点 / 时长 三件套
// 解决的问题(C++98):
//   1) time(NULL) 只能到"秒", 而且是挂钟(改系统时间会跳变);
//   2) clock() 是 CPU 时间, 不是墙钟耗时;
//   3) 想测代码耗时只能调平台 API(Windows GetTickCount / Linux
//      clock_gettime), 换平台整段重写; 单位换算全靠手写乘除, 记错就是 bug。
// 替代旧写法: time()/clock() + 平台计时 API -> std::chrono
// 三个概念(类型各不相同, 混用直接编译报错 —— 这就是"类型安全"):
//   * duration<Rep, Period>  时长: 5 秒 / 500 毫秒
//   * time_point<Clock>      时间点: "某年某月某日 12:00" 这一刻
//   * clock                  时钟: steady(单调, 测耗时) / system(挂钟, 看日期)
// 编译: g++ -std=c++11 -Wall -Wextra 11_chrono.cpp -o demo
//       本机 MinGW 动态链接缺 CRT 入口点(0xC0000139), 需加 -static;
//       一般发行版直接编译即可(见 README 工具链特例)
// ============================================================================
#include <chrono>
#include <ctime>
#include <iostream>
#include <thread>

// 测耗时的通用小工具(模板 + 转发引用, 复习 cpp11/06)
template <typename F>
long long time_ms(F&& f)
{
    auto t0 = std::chrono::steady_clock::now();
    f();
    auto t1 = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0)
        .count();
}

// 干点费 CPU 的活(volatile 防编译器优化掉)
void busy_work()
{
    volatile long long s = 0;
    for (long long i = 0; i < 30000000; ++i)
        s += i;
}

int main()
{
    // ---- 1. duration: 时长自带单位 ----
    // C++98: 想表达 5 秒只能写魔法数 5000, 单位全靠自觉
    std::chrono::seconds      five_s(5);
    std::chrono::milliseconds half_s(500);
    auto total = five_s + half_s;            // 不同单位相加: 编译期自动换算
    std::cout << "5 秒 + 500 毫秒 = " << total.count() << " 毫秒\n";   // 5500

    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(five_s);
    std::cout << "5 秒 = " << ms.count() << " 毫秒\n";

    // ---- 2. 测耗时: steady_clock(单调钟, 不受改系统时间影响) ----
    std::cout << "busy_work 约耗时 " << time_ms(busy_work) << " ms\n";

    // ---- 3. 挂钟时间 system_clock: 给人看的年月日时分秒 ----
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::cout << "当前挂钟时间: " << std::ctime(&t);    // ctime 自带换行

    // ---- 4. 线程睡眠: sleep_for(粒度由平台决定, 自动换算) ----
    auto t0 = std::chrono::steady_clock::now();
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    auto t1 = std::chrono::steady_clock::now();
    std::cout << "sleep_for(20ms) 实际睡了 "
              << std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0)
                     .count()
              << " 微秒\n";
    return 0;
}
