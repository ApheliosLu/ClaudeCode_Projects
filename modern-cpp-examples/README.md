# 现代 C++ 最佳实践示例集 (Modern C++ Idioms)

面向 **熟悉 C++98/03、想系统掌握 C++11/14/17/20/23 核心惯用法** 的学习者。
每个文件都是**完整可编译、可运行**的示例，头部注释写明"解决什么 C++98 旧写法问题 / 替代了什么"。

学习背景衔接：视频课程 (BV1et411b73Z，主流 C++ 入门课) 主线是 C++98/03
语法、面向对象与 STL 基础。本套示例把"课程里的旧写法"逐个映射到"业界现行推荐写法"。

## 版本现状 (2026-09 视角)

| 标准 | 状态 | 建议 |
| --- | --- | --- |
| C++11 | 早已普及 | 现代 C++ 的**地基**，必学 |
| C++14 | 早已普及 | C++11 的平滑补丁，必学 |
| C++17 | **生产主力之一** | 必学 |
| C++20 | **生产主力、新项目默认** | 必学 |
| C++23 | **最新正式标准** (2024 年末 ISO 出版)，2025-26 工具链已全面支持 | 推荐跟进 |
| C++26 | 标准流程最后阶段，预计 2026 年底出版，编译器仅零星预览 | **暂不学**，编译器就绪后再说 |

主流说法：存量项目 C++17/20 居多；2026 年开新项目默认 `-std=c++20`（稳妥）或 `-std=c++23`（工具链已就绪，如本机 g++ 15.2 全支持，含 `std::generator`）。C++11 的学习价值在于 C++14/17 都是它的增量——本目录先学 cpp11 的理由就在这。

## 目录结构 (全部完成 ✅, 共 41 个文件)

```text
modern-cpp-examples/
├── README.md
├── cpp11/          # 14 个 —— 地基: 推导/智能指针/移动/转发/Lambda/变参/并发 + 补齐的时间/随机/array/资源规则
│   01_auto_decltype.cpp                02_nullptr_enum_class_override_final.cpp
│   03_range_for_and_uniform_init.cpp   04_smart_pointers.cpp
│   05_move_semantics.cpp               06_perfect_forwarding.cpp
│   07_lambda.cpp                       08_variadic_templates.cpp
│   09_thread_and_mutex.cpp             10_async_future.cpp
│   11_chrono.cpp        [补] 时间库     12_random.cpp          [补] 随机库
│   13_std_array.cpp     [补] 现代数组   14_rule_of_zero.cpp    [补] =default/=delete
├── cpp14/          # 4 个 —— 增强
│   01_generic_lambda_init_capture.cpp  02_return_type_deduction.cpp
│   03_make_unique.cpp                  04_literals_and_digit_separators.cpp
├── cpp17/          # 8 个 —— 实用改进
│   01_structured_binding_and_if_init.cpp  02_optional_variant_any.cpp
│   03_string_view.cpp                     04_filesystem.cpp
│   05_parallel_algorithms.cpp             06_fold_expressions.cpp
│   07_if_constexpr.cpp        [补] 编译期 if
│   08_ctad_and_inline.cpp     [补] CTAD / inline 变量
├── cpp20/          # 8 个 —— 大版本
│   01_concepts.cpp       02_ranges.cpp        03_spaceship_comparison.cpp
│   04_span.cpp           05_constexpr_enhanced.cpp  06_coroutine_generator.cpp
│   07_jthread_stop_token.cpp   [补] 自动 join + 协作取消
│   08_everyday_tools.cpp       [补] erase 系列/指定初始化/模板化 Lambda
└── cpp23/          # 7 个 —— 前沿
    01_optional_monadic.cpp  02_expected.cpp  03_views_zip.cpp
    04_if_consteval.cpp      05_print_format.cpp
    06_std_generator.cpp   [补] 标准库生成器
    07_tools.cpp           [补] move_only_function / ranges::to / enumerate
```

## 交付一览 (各版本覆盖与验证亮点)

| 目录 | 文件数 | 覆盖清单 | 验证亮点 |
| --- | --- | --- | --- |
| cpp11 | 14 | 移动语义/完美转发、Lambda、智能指针、thread/async/future、auto/decltype、范围 for、nullptr/enum class/override/final、变参模板、`<chrono>` 时间、`<random>` 随机、std::array、Rule of Zero | weak_ptr 循环引用实测无泄漏；并发计数 800000 精确；跨线程异常正常重抛；chrono 换算 5500ms、sleep 实测；随机固定种子可复现；array 越界 at() 抛异常 |
| cpp14 | 4 | 泛型 Lambda/初始化捕获、auto 返回类型、make_unique、二进制字面量/分隔符 | 同一泛型 lambda 跑通 int/double/string |
| cpp17 | 8 | 结构化绑定/if-switch 初始化、optional/variant/any、string_view、filesystem、并行算法、折叠、if constexpr、CTAD/inline 变量 | seq/par 排序一致性通过；filesystem 建写列查清全流程；if constexpr 丢弃分支不实例化 |
| cpp20 | 8 | Concepts、Ranges、`<=>`、span、constexpr/consteval/constinit、协程、jthread/stop_token、erase 系列/指定初始化/模板化 Lambda | 手写 Generator 输出自然数与斐波那契；jthread 协作取消实测（1.69 亿圈后收到停止）；consteval 双路径验证 |
| cpp23 | 7 | optional monadic、expected、views::zip、if consteval、print/format、std::generator、move_only_function/ranges::to/enumerate | expected 链路 210/错误传导；zip 写回生效 (bob 85→90)；std::generator 生产版与手写版对照 |

每文件的"解决什么 C++98 旧写法 / 替代为 X"见各 .cpp 头部注释；文件主题一览见上方目录树。

## 编译与运行

本机实测编译器：**g++ 15.2.0 (MinGW-W64 x86_64-ucrt-posix-seh)**。
全部 **41 个文件** 编译通过 (`-Wall -Wextra` 零警告) 并运行验证，见文末测试记录。

```bash
# 通用单文件命令（替换 {std} 与文件名；并发/并行示例保留 -pthread）
g++ -std={c++11|c++14|c++17|c++20|c++23} -Wall -Wextra -O1 -pthread 路径/文件.cpp -o demo && ./demo
```

**本机工具链特例**（换标准工具链/正常 Linux 时全部不需要，见"验证与问题记录"）:

```bash
# 1) 动态链接启动即挂(0xC0000139/127)的三个文件: filesystem / chrono / jthread —— 需静态链接:
g++ -std=c++17 -static -O1 cpp17/04_filesystem.cpp -o demo && ./demo
g++ -std=c++11 -static -O1 cpp11/11_chrono.cpp -o demo && ./demo
g++ -std=c++20 -static -pthread -O1 cpp20/07_jthread_stop_token.cpp -o demo && ./demo
# 2) cpp23/05_print_format.cpp —— 本机 libstdc++ 缺终端直写符号, std::println 链不上;
#    文件内已内置 std::format 兼容层可直接跑; 标准工具链上换成真 std::println 即可
# 3) cpp17/05_parallel_algorithms.cpp —— 排序大数组建议 -O2
```

编译器需求速查：

| 标准 | g++ (libstdc++) | clang (libc++) | MSVC (Visual Studio) |
| --- | --- | --- | --- |
| C++11 | 4.9+ | 3.4+ | VS 2015+ |
| C++14 | 5+ | 3.4+ | VS 2015+ |
| C++17 | 8+ | 6+ | VS 2017 15.7+ |
| C++20 | 10+ (较全 12+) | 13+ (较全 16+) | VS 2022 17.0+ |
| C++23 | 13+ 部分 / 14+ 大部分 / **15+ 含 std::generator** | 17+ / 18+ 较多 | VS 2022 17.8+ 逐步覆盖 |

## 对照速查: C++98 旧写法 → 现代写法

| C++98/03 时代写法 | 现代推荐写法 | 示例文件 |
| --- | --- | --- |
| `NULL` / `0` 当空指针 | `nullptr` | cpp11/02 |
| `enum { ... }` 泄漏作用域 | `enum class` | cpp11/02 |
| 手写迭代器 for 循环 | 范围 for / STL 算法 / Ranges 管道 | cpp11/03,07 cpp20/02 |
| `new`/`delete`、`new[]`/`delete[]` 手动管理 | `unique_ptr` / `shared_ptr` / `vector` | cpp11/04 cpp14/03 |
| 手写拷贝/析构三件套管理资源 | Rule of Zero（成员管资源）+ `=default`/`=delete` | cpp11/14 cpp11/05 |
| C 数组 int a[5]（退化/越界/不能赋值） | `std::array` / `std::vector` / `std::span` | cpp11/13 cpp20/04 |
| 大对象拷贝搬运 | 移动语义 `std::move` | cpp11/05 |
| 写死的转发/包装函数 | 转发引用 `T&&` + `std::forward` | cpp11/06 |
| 函数指针 / 函数对象回调 | Lambda（泛型版 C++14） | cpp11/07 cpp14/01 |
| 手写类模板实参 | CTAD（C++17） | cpp17/08 |
| 手写平台线程 API | `std::thread` / `std::async` / `std::jthread` | cpp11/09,10 cpp20/07 |
| `time()` / `clock()` / 平台计时 API | `<chrono>` | cpp11/11 |
| `rand()` / `srand()` / `random_shuffle` | `<random>` 引擎+分布 / `std::shuffle` | cpp11/12 |
| 手写类型全名 | `auto` / `decltype` | cpp11/01 |
| 返回 -1 / 空指针当"失败" | `std::optional` / `std::expected` | cpp17/02 cpp23/02 |
| `union` + 手写 tag | `std::variant` + `std::visit` | cpp17/02 |
| `const std::string&` 传只读串 | `std::string_view` (零拷贝) | cpp17/03 |
| opendir / FindFirstFile 平台 API | `std::filesystem` | cpp17/04 |
| 单线程 sort / 查找 | 执行策略 `execution::par` | cpp17/05 |
| enable_if / SFINAE / 标签分发 | if constexpr (C++17) / Concepts (C++20) | cpp17/07 cpp20/01 |
| 手写六个比较运算符 | `auto operator<=>(...) = default` | cpp20/03 |
| 手写循环 + 中间容器做数据加工 | Ranges 视图管道 `\|` / `ranges::to` | cpp20/02 cpp23/07 |
| erase-remove 惯用法 | `std::erase` / `erase_if` | cpp20/08 |
| 手搓状态机做"惰性序列" | 协程 `co_yield` → C++23 `std::generator` | cpp20/06 cpp23/06 |
| `printf("%d", ...)` 类型不安全 | `std::print` / `std::format` | cpp23/05 |
| 层层 if 判空做流水线 | optional / expected 的 monadic 链 | cpp23/01,02 |
| 手写双容器索引循环 | `std::views::zip` / `enumerate` | cpp23/03,07 |
| 原子 bool 停止标志 + 手动 join | `std::jthread` + stop_token | cpp20/07 |
| `std::function` 装不下 move-only 回调 | `std::move_only_function` | cpp23/07 |

## 淘汰清单（看到直接绕开, 不要学）

| 别再使用 | 原因 | 替代 |
| --- | --- | --- |
| `std::auto_ptr` | 拷贝即转移所有权, 已移除 | `std::unique_ptr` |
| `std::bind` / `bind1st` / `bind2nd` / `ptr_fun` / `mem_fun` | 可读性差, 已废弃 | Lambda 捕获 |
| `throw()` / `throw(类型)` 动态异常规范 | 运行时才检查, C++17 移除 | `noexcept` (C++11) |
| `std::random_shuffle` | C++17 移除 | `std::shuffle` + `<random>` |
| `register` | 提示无效, C++17 移除 | 无（编译器自动处理） |
| 裸 `new` / `delete` 管理数组 | 易漏易错 | `std::vector` / `unique_ptr<T[]>` |
| 手写迭代器循环 | 冗长易错 | 范围 for / 算法 / Ranges 视图 |
| `std::iterator` 手动 traits | C++17 废弃 | 容器自供 `iterator_traits` |
| `rand()` | 质量差、非线程安全 | `<random>` 的分布引擎 |
| 裸 `std::uncaught_exception()` | 语义错误（已改 `uncaught_exceptions`） | 通常根本不需要 |
| C 风格强制转换 `(int)x` | 编译器不查 | `static_cast` 等四种具名 cast |
| 手写三/五法则当日常 | 99% 的类不需要 | Rule of Zero（成员管资源） |

## 建议学习顺序 (全批次, 编号即推荐顺序)

1. `cpp11/01` auto/decltype
2. `cpp11/02+03` 关键字 / 遍历与初始化
3. `cpp11/07` Lambda
4. `cpp11/04+05+06` 智能指针 / 移动 / 转发（最核心, 连读）
5. `cpp11/08` 变参模板
6. `cpp11/09+10` 并发入门 (thread / async)
7. `cpp20/07` jthread（接并发话题, 前置阅读无碍）
8. `cpp11/11` chrono 时间库
9. `cpp11/12` random 随机库
10. `cpp11/13` std::array
11. `cpp11/14` Rule of Zero（回头印证 4 的意义）
12. `cpp14/*` 四个增强小件
13. `cpp17/01+02` 结构化绑定与三件套
14. `cpp17/03` string_view
15. `cpp17/06` 折叠（对照 cpp11/08 递归版）
16. `cpp17/07` if constexpr
17. `cpp17/08` CTAD / inline 变量
18. `cpp17/04+05` 文件系统与并行
19. `cpp20/01` Concepts
20. `cpp20/02` Ranges
21. `cpp20/08` 日常小件（erase / 指定初始化 / 模板化 Lambda）
22. `cpp20/03` 三路比较 `<=>`
23. `cpp20/04+05` span / constexpr 增强
24. `cpp20/06` 协程（手写 Generator 讲原理）
25. `cpp23/06` std::generator（生产版, 与 24 对照）
26. `cpp23/01+02` optional / expected monadic（生产高频）
27. `cpp23/03` views::zip
28. `cpp23/07` 新工具三件（move_only_function / ranges::to / enumerate）
29. `cpp23/04+05` if consteval / print

读完之后的下一步（未覆盖, 可按需向 Claude 要）：`std::mdspan`（多维数组）、`deducing this`、
C++20 chrono 的日历与时区、`std::format` 复杂格式、`char8_t` 与文本编码、`co_await` 网络/IO
协程框架、无锁并发与内存序、`std::execution`（C++26 方向）。

进阶方法：每读完一个文件，拿视频课程里的旧项目代码用对应新写法重构一遍，比读十遍有效。

## 验证与问题记录

**验证方法**: 每个文件用 `g++ -std=<版本> -Wall -Wextra [-static] -pthread -O1` 编译（零警告）→
运行 → 人工核对输出数值与语义（不只"能跑"）。

**关键输出核对清单**（2026-09-04, g++ 15.2.0 MinGW-W64）:

| 示例 | 核对点 | 结果 |
| --- | --- | --- |
| cpp11/04 | 循环引用节点是否泄漏 | 两个 ~Node 析构均打印 |
| cpp11/09 | 8 线程 × 10 万次计数 / 求和 | 加锁与原子计数均 = 800000；1..999999 和 = 499999500000 |
| cpp11/10 | fib(30) / fib(33) / 异常传播 | 832040 / 3524578；子线程异常在主线程捕获 |
| cpp11/11 | chrono 单位换算 / 睡眠 | 5500 ms；sleep_for(20ms) 实测 ~35ms（平台定时器粒度） |
| cpp11/12 | 固定种子可复现 | 同种子同序列 |
| cpp17/05 | seq 与 par 排序一致性 | 相等性校验通过 |
| cpp20/02 | Ranges 管道数值 | 6 12 18 24；1 9 25 49 81 |
| cpp20/06 | 协程生成器输出 | 1 2 3 4 5；斐波那契 1..144 |
| cpp20/07 | jthread 协作取消 | worker 1.69 亿圈后收到停止；watcher 观察到 stop_source 信号 |
| cpp23/02 | expected 成功链 / 错误链 | 成功 210；解析失败与除零错误逐级传导 |
| cpp23/03 | zip 引用写回 | bob 85 → 90 写回原 vector 生效 |
| cpp23/06 | std::generator | 与手写版输出一致（2 4 6 8 10 12 / 斐波那契到 144） |

**发现问题清单**（测试期内全部处理完毕）:

| 问题 | 现象 / 根因 | 处理 | 状态 |
| --- | --- | --- | --- |
| cpp17/03 版本越界 | C++17 文件误用 C++20 的 starts_with | 改写为 C++17 等效 substr 写法 | 已修复 |
| cpp17/06 符号可见性 | 折叠表达式里的函数定义在模板之后, 展开时找不到 | 调整定义顺序, 改用逗号折叠 | 已修复 |
| std::print 链接失败 | 本机 libstdc++ 缺终端直写符号（`__open_terminal` / `__write_to_terminal`）, 属该 MinGW 发行版构建缺陷 | 文件内用 std::format + cout 兼容层, 注释给出标准写法 | 已绕行 |
| 动态链接启动即挂（3 个文件） | filesystem / chrono / jthread 的动态 exe 依赖本机缺失的 CRT 入口点（真实错误码 0xC0000139, STATUS_ENTRYPOINT_NOT_FOUND; bash 显示 127） | 这三个文件一律 `-static` 编译, 代码本身无误 | 已绕行 |
| 并行算法 -ltbb 反而失败 | 本发行版不带 TBB 库; 但不加 -ltbb 时 par 策略可直接链接运行 | 编译命令一律不加 -ltbb | 无需处理 |

**工具链探测结论**: g++ 15.2 完整支持本套用到的全部 C++20/23 特性——协程、Concepts、
Ranges、`views::zip`/`enumerate`、`ranges::to`、`std::expected`、optional monadic、
if consteval、`std::move_only_function`、`std::format`、`std::generator`（后两者需 g++ 14+/15+）。

**其它说明**: bilibili 课程页面无法抓取（网络策略拦截），"视频教了 C++98" 的知识衔接按该
BV 号主流入门课内容推断，如有出入以实际课程为准。

**批次统计**:

| 批次 | 内容 | 结果 |
| --- | --- | --- |
| 批次1 | cpp11 (01-10) + cpp14, 14 文件 | PASS=14 |
| 批次2+3 | cpp17/20/23, 17 文件 | 首轮 16/17；filesystem 改 -static 后全过 |
| 补充批次 | 待补强烈推荐特性, 10 文件 | 首轮 8/10；chrono/jthread 改 -static 后全过 |
| **累计** | **41 个文件** | **编译零警告, 全部运行验证 PASS** |
