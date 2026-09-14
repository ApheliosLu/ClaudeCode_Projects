// ============================================================================
// 04_literals_and_digit_separators.cpp  现代 C++ 示例集 · C++14
// 主题: 二进制字面量 + 数字分隔符
// 解决的问题(C++98):
//   1) 没有二进制字面量: 位掩码必须心算成十六进制 0xC3, 可读性差;
//   2) 大数字没有分隔: 1048576 一眼看不出是 2^20, 数错一位就是 bug。
// C++14 新增:
//   * 0b 前缀的二进制字面量;
//   * 单引号 ' 数字分隔符(只能夹在数字之间, 便于分组, 编译期忽略)。
// 编译: g++ -std=c++14 -Wall -Wextra 04_literals_and_digit_separators.cpp -o demo
// ============================================================================
#include <iostream>

int main()
{
    // 位掩码直接按位写, 不再手算 16 进制
    const int flags   = 0b1100'0011;          // 高位两位与低两位是不同开关
    const int rw_mask = 0b0000'0011;          // 低 2 位 = 读写权限位

    const int   perm    = 0b101;              // 5
    const int   one_mib = 1'048'576;          // 1 MiB = 2^20, 千分位可读
    const double pi_approx = 3.141'592'653;   // 浮点字面量也能分隔

    // static_assert = 编译期断言, 为假直接编译失败(与运行时 assert 不同)
    // 字面量的值与手写十进制完全一致(编译期常量, 用 static_assert 验证)
    static_assert(0b11 == 3, "0b11 应是 3");
    static_assert(1'000 == 1000, "分隔符不改变数值");

    std::cout << "perm    = " << perm << '\n';  // 输出: perm    = 5
    std::cout << "one_mib = " << one_mib << '\n';  // 输出: one_mib = 1048576
    std::cout << "pi_approx = " << pi_approx << '\n';  // 输出: pi_approx = 3.14159

    std::cout << "读写权限位 = " << (flags & rw_mask) << " (期望 3)\n";
    // 输出: 读写权限位 = 3 (期望 3)
    std::cout << "高 6 位全清后 = " << (flags & 0b0011'1100) << " (期望 0)\n";
    // 输出: 高 6 位全清后 = 0 (期望 0)
    return 0;
}
