// ============================================================================
// 05_print_format.cpp  现代 C++ 示例集 · C++23
// 主题: std::print / std::println / std::format —— 类型安全格式化
// 解决的问题(对比 C++98):
//   1) printf("%d %s", ...) 的占位符与实参类型不匹配时不报错(UB!);
//   2) iostream 的 << 链做对齐/精度/补零要堆一长串流操纵符, 又慢又丑;
//   3) 想"把格式化的结果存起来再输出"没有统一做法。
// C++20 先引入 std::format(Python 风格的 {}); C++23 再加 print/println,
// 直接把格式化结果写 stdout/stderr, 无需再 <<。
//
// ★ 本机工具链提示:
//   MinGW-w64 的 g++ 15.2 libstdc++ 少了终端直写符号(std::__open_terminal /
//   __write_to_terminal), 导致 std::println("{}", x) 链接失败 —— 这是该
//   发行版的已知构建缺陷, 不是你的代码问题。
//   在标准工具链(Linux GCC 14+ / LLVM 18+ / MSVC 17.8+)上, 直接写成:
//       #include <print>
//       std::println("Hello {}!", 42);            // 官方标准写法
//   本文件用 std::format + std::cout 实现一个同名 println, 便于本机跑通,
//   换标准工具链时把下面 println 换成 std::println 即可。
// 编译: g++ -std=c++23 -Wall -Wextra 05_print_format.cpp -o demo
// ============================================================================
#include <format>
#include <iostream>
#include <string>
#include <utility>

// ---- 兼容层: 与 std::println 同签名; 替换成真 std::println 即官方代码 ----
template <typename... Args>
void println(std::format_string<Args...> fmt, Args&&... args)
{
    std::cout << std::format(fmt, std::forward<Args>(args)...) << '\n';
}

int main()
{
    // {} 占位符按参数顺序填充; 类型在编译期校验(传错类型直接编译失败)
    println("Hello, {}! 项目第 {} 天", "Modern C++", 7);

    // ---- 格式说明: 对齐 / 宽度 / 进制 / 精度 / 补零 ----
    println("{:>10} | {:<10} |", "右对齐", "左对齐");
    println("十进制 {} = 十六进制 {:#x} = 八进制 {:#o}", 255, 255, 255);
    println("pi ≈ {:.4f}", 3.1415926535);
    println("编号 {:06d}", 42);

    // ---- 格式化结果复用: 存成 std::string ----
    std::string msg = std::format("{} 与 {} 的和是 {}", 1, 2, 1 + 2);
    std::cout << msg << '\n';

    // 注意: 格式串必须编译期可见(C++26 会增加 std::runtime_format 等动态用法)
    return 0;
}
