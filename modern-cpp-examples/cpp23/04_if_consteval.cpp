// ============================================================================
// 04_if_consteval.cpp  现代 C++ 示例集 · C++23
// 主题: if consteval —— 按"是否编译期求值"选择分支
// 解决的问题(相对 C++20):
//   C++20 想区分"常量求值/运行求值"只能写:
//     if (std::is_constant_evaluated()) { ... } else { ... }
//   问题: 两个分支都会被实例化/检查, 运行时才做的操作没法放进 else;
//   而 constexpr 上下文里又可能误触发 else 分支。
//   C++23 的 if consteval 是专门语法: 编译期求值时走 then 分支,
//   否则走 else 分支; 被丢弃的分支不实例化(类似 if constexpr),
//   于是 else 里可以放心写"只有运行期才合法"的代码。
//   好记: if constexpr 看"类型", if consteval 看"求值时机"。
// 编译: g++ -std=c++23 -Wall -Wextra 04_if_consteval.cpp -o demo
// ============================================================================
#include <iostream>

// constexpr 函数同时服务"编译期建表"与"运行期计算":
// 编译期调用 -> 走 if consteval 的 then(生成纯常量结果);
// 运行期调用 -> 走 else(允许访问运行期设施)。
constexpr int price_of(int item_id)
{
    if consteval {
        // 编译期路径: 只允许常量表达式 —— 例如在这里查"价格常量表"
        return item_id * 100;
    } else {
        // 运行期路径: 可以读配置、查缓存、调非 constexpr 函数
        return item_id * 100 + 1;        // 示意: 运行期多一点处理
    }
}

int main()
{
    constexpr int compile_time = price_of(7);   // 常量上下文 -> then 分支
    std::cout << "编译期 price_of(7)  = " << compile_time << '\n';   // 700

    int runtime_id = 7;                        // 运行期输入
    int runtime_val = price_of(runtime_id);    // else 分支
    std::cout << "运行期 price_of(7)  = " << runtime_val << '\n';    // 701

    // static_assert = 编译期断言, 为假直接编译失败(与运行时 assert 不同)
    // 配合 static_assert 在编译期校验逻辑:
    static_assert(price_of(3) == 300, "编译期价格表写错会在这里炸");
    return 0;
}
