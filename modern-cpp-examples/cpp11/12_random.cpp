// ============================================================================
// 12_random.cpp  现代 C++ 示例集 · C++11 · 补充(此前遗漏的强烈推荐特性)
// 主题: <random> —— 随机数引擎 + 概率分布
// 解决的问题(C++98):
//   1) rand()/srand(): 质量差(线性同余), 全局隐藏状态(线程不安全),
//      跨平台结果还不一致;
//   2) rand() % N 有模偏差, 且只能出整数;
//   3) 想要正态分布等任意分布, 只能自己抄算法(如 Box-Muller 变换)。
// 替代旧写法: rand()/srand() -> "引擎(engine) + 分布(distribution)"
// 设计哲学: 随机源与概率形状解耦、可组合:
//   * 引擎(engine):  只管产出一串高质量乱数 —— 常用 std::mt19937(梅森旋转)
//   * 分布(distribution): 把乱数映射成目标形状(uniform/normal/bernoulli...)
//   * 随机设备: std::random_device(硬件熵), 通常只用来给引擎"播种子"
// 编译: g++ -std=c++11 -Wall -Wextra 12_random.cpp -o demo
// ============================================================================
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <random>
#include <vector>

int main()
{
    // ---- 1. 骰子: 均匀整数分布 ----
    // C++98: srand(time(NULL)); rand() % 6 + 1;   // 有偏差 + 全局状态
    std::random_device rd;                       // 硬件熵(随机种子源)
    std::mt19937       gen(rd());                // 引擎: 梅森旋转
    std::uniform_int_distribution<int> dice(1, 6);
    std::cout << "掷 6 次骰子: ";
    for (int i = 0; i < 6; ++i)
        std::cout << dice(gen) << ' ';
    std::cout << '\n';

    // ---- 2. [0,1) 实数(rand() 时代做不到的均匀实数) ----
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "3 个 [0,1) 随机数: ";
    for (int i = 0; i < 3; ++i)
        std::cout << unit(gen) << ' ';
    std::cout << '\n';

    // ---- 3. 正态分布: 均值 500、标准差 30 的"测量噪声" ----
    std::normal_distribution<double> noise(500.0, 30.0);
    std::cout << "5 个正态噪声: ";
    for (int i = 0; i < 5; ++i)
        std::cout << noise(gen) << ' ';
    std::cout << '\n';

    // ---- 4. 洗牌: std::shuffle(替代已移除的 std::random_shuffle) ----
    std::vector<int> deck(13);
    for (int i = 0; i < 13; ++i)
        deck[i] = i + 1;
    std::shuffle(deck.begin(), deck.end(), gen);
    std::cout << "洗过的 1~13: ";
    for (int v : deck)
        std::cout << v << ' ';
    std::cout << '\n';

    // ---- 5. 可复现性: 固定种子 -> 每次同样的序列(测试/对拍神器) ----
    std::mt19937 fixed(42);                      // 同种子同序列, C++98 做不到
    std::uniform_int_distribution<int> d(1, 100);
    std::cout << "固定种子 42 的前 3 个: ";
    for (int i = 0; i < 3; ++i)
        std::cout << d(fixed) << ' ';
    std::cout << "(每次重跑本程序数值不变)\n";
    return 0;
}
