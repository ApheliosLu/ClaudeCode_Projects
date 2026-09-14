// ============================================================================
// 01_structured_binding_and_if_init.cpp  现代 C++ 示例集 · C++17
// 主题: 结构化绑定 + if/switch 初始化器
// 解决的问题(C++98/11):
//   1) 取 pair/tuple 内容: C++98 得写 .first/.second; C++11 的 std::tie
//      只能赋给"已声明"的变量, 一步到位做不到;
//   2) 想在 if/switch 条件里限定一个临时变量(查找结果等)的生命周期:
//      C++98 做不到, 只能提升到外层作用域或嵌套花括号;
//   3) 条件 + 失败处理经常写成"两段式"(先查再判), 变量泄漏作用域。
// 替代旧写法: 手写 .first/.second + std::tie -> auto [k, v] = ...;
//            if 外定义哨兵变量 -> if (auto x = 取(); 条件)
// 编译: g++ -std=c++17 -Wall -Wextra 01_structured_binding_and_if_init.cpp -o demo
// ============================================================================
#include <iostream>
#include <map>
#include <string>
#include <tuple>

struct Point { int x, y; };   // 聚合类型按成员声明顺序解构

int main()
{
    // ---- 1. map 查找: if 初始化器 + 结构化绑定, 一把梭 ----
    std::map<std::string, int> scores{{"alice", 90}, {"bob", 85}};

    // C++98: std::map<std::string,int>::iterator it = scores.find("alice");
    //        if (it != scores.end()) { 再手动搬 .first/.second }
    if (auto it = scores.find("alice"); it != scores.end()) {   // if 初始化器
        const auto& [name, score] = *it;                        // 结构化绑定
        std::cout << name << " = " << score << '\n';  // 输出: alice = 90
    } else {
        std::cout << "没找到\n";     // it 在此仍可见  // 输出: 没找到(本程序未走到)
    }
    // it 离开 if 即销毁, 不会污染外层作用域

    // ---- 2. 遍历 map 直接解构 pair ----
    for (const auto& [k, v] : scores)
        std::cout << k << ':' << v << ' ';  // 输出: alice:90 bob:85(每对后跟一个空格)
    std::cout << '\n';

    // ---- 3. tuple 解构(按位置) ----
    std::tuple<int, std::string, double> t{1, "one", 1.5};
    auto [n, s, d] = t;                  // 拷贝三份; 想改原 tuple 用 auto&
    (void)n; (void)d;
    std::cout << "tuple 第二元素: " << s << '\n';  // 输出: tuple 第二元素: one

    // ---- 4. 结构体解构: 注意 auto 是拷贝, 引用绑定才写 auto& ----
    Point p{3, 4};
    auto [px, py] = p;    px = 99;       // 拷贝, 不影响 p
    std::cout << "p.x = " << p.x << " (px 是拷贝)\n";  // 输出: p.x = 3 (px 是拷贝)
    auto& [rx, ry] = p;   rx = 10;       // 引用, 直接改 p
    std::cout << "p.x = " << p.x << " (rx 是引用)\n";  // 输出: p.x = 10 (rx 是引用)

    // ---- 5. insert 的返回值 pair<iterator,bool> 解构: "插入或判断重复" ----
    auto [it2, inserted] = scores.insert({"carol", 88});
    std::cout << (inserted ? "插入成功: " : "已存在: ") << it2->first << '\n';
    // 输出: 插入成功: carol
    auto [it3, inserted2] = scores.insert({"carol", 99});
    std::cout << (inserted2 ? "插入成功" : "重复键, 未覆盖") << '\n';  // 输出: 重复键, 未覆盖

    // ---- 6. switch 初始化器: 判定值锁在 switch 内部 ----
    std::string cmd = "start";
    switch (char c = cmd.empty() ? '\0' : cmd[0]; c) {
        case 's': std::cout << "收到 start 命令\n"; break;  // 输出: 收到 start 命令
        case 'q': std::cout << "收到 quit 命令\n"; break;  // 输出: 收到 quit 命令(本程序未走到)
        default:  std::cout << "未知命令\n";  // 输出: 未知命令(本程序未走到)
    }
    // c 在这里已不可见 —— 想复用 c 或漏 break 都无从谈起, 结构更安全
    return 0;
}
