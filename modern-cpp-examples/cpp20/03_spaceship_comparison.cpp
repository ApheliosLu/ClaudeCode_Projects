// ============================================================================
// 03_spaceship_comparison.cpp  现代 C++ 示例集 · C++20
// 主题: 三路比较运算符 operator<=>
// 解决的问题(C++98):
//   让自定义类型可比较(进 set/map 当键、排序、判等), 需要手写 6 个
//   比较运算符, 或者只写 operator< 让其它五个"凑合"(!= 取反 == 之类
//   全不成立, 语义残缺); 代码全是机械重复。
// 替代旧写法: 手写六个比较 -> auto operator<=>(const T&) const = default
// 规则:
//   * = default 按成员声明顺序做三路比较, 同时生成 == != < <= > >= 六件套;
//   * 结果是强序(std::strong_ordering)时, 类型可以当无序容器的键;
//   * 浮点/指针等特殊成员要小心: 可用 std::weak_ordering / std::partial_ordering;
//   * 想自定义次序就手写 <=> 体(并补一个 ==, 见 RankOnly)。
// 编译: g++ -std=c++20 -Wall -Wextra 03_spaceship_comparison.cpp -o demo
// ============================================================================
#include <algorithm>
#include <compare>
#include <iostream>
#include <set>
#include <string>
#include <vector>

// 默认三路比较: 一个 = default, 六个运算符齐活
struct Player {
    std::string name;
    int         score;

    auto operator<=>(const Player&) const = default;
    // 自动生成: == != < <= > >=
    // 比较顺序 = 成员声明顺序: 先 name, name 相同再看 score
};

// 只想按"分数"排? 手写 <=> 体即可; 注意 == 不会自动生成, 要自己补
struct RankOnly {
    std::string name;
    int         score;

    auto operator<=>(const RankOnly& o) const { return score <=> o.score; }
    bool operator==(const RankOnly& o) const { return score == o.score; }
};

int main()
{
    Player alice{"alice", 3000};
    Player bob{"bob", 5000};

    // <=> 结果可直接与 0 比较: <0 小于 / ==0 相等 / >0 大于
    auto rel = alice <=> bob;
    if (rel < 0)  std::cout << "alice < bob (按 name)\n";  // 输出: alice < bob (按 name)
    if (rel != 0) std::cout << "两者不相等\n";  // 输出: 两者不相等

    // 直接进 set 当键 / 直接 sort(只需 <, 由 <=> 自动改写提供)
    std::set<Player> ranking{{"bob", 5000}, {"alice", 3000}, {"bob", 3000}};
    std::cout << "set 自动排序(先 name 后 score): ";  // 输出: set 自动排序(先 name 后 score):
    for (const auto& p : ranking)
        std::cout << p.name << ':' << p.score << ' ';  // 输出: alice:3000 bob:3000 bob:5000
    std::cout << '\n';

    std::vector<Player> ps{{"carol", 1000}, {"alice", 9000}, {"bob", 2000}};
    std::sort(ps.begin(), ps.end());                     // 只需要 <
    std::cout << "sort 后: ";  // 输出: sort 后:
    for (const auto& p : ps)
        std::cout << p.name << ' ';  // 输出: alice bob carol
    std::cout << '\n';

    // 自定义次序: 只按分数
    std::vector<RankOnly> rs{{"carol", 1000}, {"alice", 9000}, {"bob", 2000}};
    std::sort(rs.begin(), rs.end());
    std::cout << "只按 score 排: ";  // 输出: 只按 score 排:
    for (const auto& p : rs)
        std::cout << p.name << '(' << p.score << ") ";  // 输出: carol(1000) bob(2000) alice(9000)
    std::cout << '\n';
    return 0;
}
