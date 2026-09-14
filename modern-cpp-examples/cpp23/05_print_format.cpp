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
// ★ 本机编译要点(2026-09-12): 本文件用的是**官方写法** std::println,
//   编译时要多带一个参数 -lstdc++exp:
//       g++ -std=c++23 05_print_format.cpp -o demo -lstdc++exp
//   为什么? std::print/println 在检测到输出目标是终端时, 会改用操作系统原生
//   Unicode API 直写(Windows 上 = 转 UTF-16 后调 WriteConsoleW), 从而**绕开代码页**。
//   这块"终端支持"被 libstdc++ 单独放在**实验库** libstdc++exp.a 里(该库还含
//   <stacktrace>、C++26 contracts、<text_encoding> 等), 不显式链接就会报:
//       undefined reference to `std::__open_terminal(_iobuf*)'
//       undefined reference to `std::__write_to_terminal(void*, std::span<char, ...>)'
//   —— 这是缺一个链接参数, **不是**工具链缺陷, 不需要换 MinGW, 也不用换 MSVC。
//   MSVC 17.8+ / LLVM 18+ 不需要这个参数。
//   (历史: 本文件曾因此改用 std::format + std::cout 自造一个 println 绕行;
//    2026-09-12 查明真因后改回官方写法。)
//
//   ⚠️ 终端直写只在"输出直连终端"时生效; 输出被重定向到管道/文件时退化成写
//      UTF-8 字节 —— 所以它救不了"中间隔着 PowerShell"的场景(PowerShell 会把
//      子进程输出读进去, 用自己的 gb2312 解码器再解一遍)。详见 README 文末
//      「中文乱码问题：完整记录」。
// 编译: g++ -std=c++23 -Wall -Wextra 05_print_format.cpp -o demo -lstdc++exp
// ============================================================================
#include <format>
#include <print>      // std::print / std::println (C++23)
#include <string>

int main()
{
    // {} 占位符按参数顺序填充; 类型在编译期校验(传错类型直接编译失败)
    std::println("Hello, {}! 项目第 {} 天", "Modern C++", 7);  // 输出: Hello, Modern C++! 项目第 7 天

    // ---- 格式说明: 对齐 / 宽度 / 进制 / 精度 / 补零 ----
    std::println("{:>10} | {:<10} |", "右对齐", "左对齐");  // 输出:     右对齐 | 左对齐     |
    std::println("十进制 {} = 十六进制 {:#x} = 八进制 {:#o}", 255, 255, 255);  // 输出: 十进制 255 = 十六进制 0xff = 八进制 0377
    std::println("pi ≈ {:.4f}", 3.1415926535);  // 输出: pi ≈ 3.1416
    std::println("编号 {:06d}", 42);  // 输出: 编号 000042

    // ---- print 不换行, println 换行(对比 C++98 的 puts/printf 组合) ----
    std::print("print 不加换行: ");  // 输出: print 不加换行: 1 2 3 (这行是 println, 末尾带换行)
    for (int i = 1; i <= 3; ++i) {
        std::print("{} ", i);  // 输出: 1 2 3 (不换行)
    }
    std::println("(这行是 println, 末尾带换行)");  // 输出: (这行是 println, 末尾带换行)

    // ---- 格式化结果复用: 先存成 std::string, 想什么时候输出再输出 ----
    // 这一步只有 std::format 做得到 —— printf 只能直接打到 stdout, 拿不回字符串
    std::string msg = std::format("{} 与 {} 的和是 {}", 1, 2, 1 + 2);
    std::println("{}", msg);  // 输出: 1 与 2 的和是 3

    // 注意: 格式串必须编译期可见(C++26 会增加 std::runtime_format 等动态用法)
    return 0;
}
