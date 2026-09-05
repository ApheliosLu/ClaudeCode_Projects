// ============================================================================
// 03_range_for_and_uniform_init.cpp  现代 C++ 示例集 · C++11
// 主题: 花括号初始化列表 + 范围 for 循环
// 解决的问题(C++98):
//   1) 容器初始化只能一次次 push_back / insert, 没有字面量式初值列表;
//   2) 遍历容器必须手写 begin/end 迭代器循环, 冗长且下标/边界易错;
//   3) 初始化有"收窄转换"时 C++98 默默截断(如 256 塞进 char)。
// 替代旧写法: 循环 push_back -> {1,2,3}; 手写迭代器循环 -> 范围 for
// 范围 for 取值姿势(按推荐度):
//   只读遍历  -> for (const auto& e : c)   (零拷贝, 推荐)
//   要改元素  -> for (auto& e : c)
//   元素很便宜 -> for (auto e : c)          (拷一份来玩)
// 现代 C++ 进一步推荐"算法代替手写循环", 见 07_lambda.cpp
// 编译: g++ -std=c++11 -Wall -Wextra 03_range_for_and_uniform_init.cpp -o demo
// ============================================================================
#include <iostream>
#include <map>
#include <string>
#include <vector>

int main()
{
    // ---- 1. 统一初始化 {} : 数组/容器/自定义类型都能用 ----
    // C++98 写法: 先定义 vector 再循环 push_back 逐个塞
    std::vector<int> v{1, 2, 3};
    int              arr[]{1, 2, 3};
    std::map<std::string, int> scores{{"alice", 90}, {"bob", 85}};

    // {} 初始化拒绝收窄转换(类型安全):
    // int bad = {3.14};                // 编译错误; C++98 里 int x = 3.14 静默截断

    // ---- 2. 只读遍历: const auto& (推荐) ----
    // C++98 等价写法(请勿再手写):
    //   for (std::vector<int>::const_iterator it = v.begin(); it != v.end(); ++it)
    //       std::cout << *it << ' ';
    std::cout << "只读遍历: ";
    for (const auto& n : v)
        std::cout << n << ' ';
    std::cout << '\n';

    // ---- 3. 就地修改: auto& ----
    for (auto& n : v)
        n *= 10;
    std::cout << "乘以 10 后: ";
    for (const auto& n : v)
        std::cout << n << ' ';
    std::cout << '\n';

    // ---- 4. 遍历 map: 元素类型是 std::pair<const Key, Value> ----
    for (const auto& kv : scores)
        std::cout << kv.first << "=" << kv.second << '\n';

    // ---- 5. 裸数组也支持范围 for(编译器退化为指针遍历) ----
    for (auto n : arr)
        std::cout << n;
    std::cout << " <- 数组元素\n";
    return 0;
}
