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

主流说法：存量项目 C++17/20 居多；2026 年开新项目默认 `-std=c++20`（稳妥）或 `-std=c++23`。C++11 的学习价值在于 C++14/17 都是它的增量——本目录先学 cpp11 的理由就在这。

> **本机工具链现状（2026-09-21，macOS 26.6 / Apple clang 21.0.0）**
>
> 42 个文件实测 **39 个编译通过**。3 个失败全部是 **Apple libc++ 的实现缺口**，不是代码问题：
>
> | 失败文件 | 缺失特性 |
> | --- | --- |
> | `cpp17/05_parallel_algorithms.cpp` | `std::execution::seq/par/par_unseq` |
> | `cpp23/06_std_generator.cpp` | `<generator>` |
> | `cpp23/07_tools.cpp` | `std::move_only_function` |
>
> 这三者在 GCC 15.2 上都能编过（原 Windows 机器即是 42/42 全过）。要补全需装 GCC；
> 是否值得装、以及各特性的替代方案，见文末「验证与问题记录 → 工具链差异」。

## 目录结构 (全部完成 ✅, 共 42 个文件)

```text
modern-cpp-examples/
├── README.md
├── cpp11/          # 15 个 —— 地基: 推导/智能指针/移动/转发/Lambda/变参/并发 + 补齐的时间/随机/array/资源规则/指针实战
│   01_auto_decltype.cpp                02_nullptr_enum_class_override_final.cpp
│   03_range_for_and_uniform_init.cpp   04_smart_pointers.cpp
│   05_move_semantics.cpp               06_perfect_forwarding.cpp
│   07_lambda.cpp                       08_variadic_templates.cpp
│   09_thread_and_mutex.cpp             10_async_future.cpp
│   11_chrono.cpp        [补] 时间库     12_random.cpp          [补] 随机库
│   13_std_array.cpp     [补] 现代数组   14_rule_of_zero.cpp    [补] =default/=delete
│   15_smart_pointers_in_practice.cpp    [补] 智能指针实战 (04 续篇: auto_ptr 反面教材 / 多态容器 / 反向指针)
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
| cpp11 | 15 | 移动语义/完美转发、Lambda、智能指针（API + 实战）、thread/async/future、auto/decltype、范围 for、nullptr/enum class/override/final、变参模板、`<chrono>` 时间、`<random>` 随机、std::array、Rule of Zero | weak_ptr 循环引用实测无泄漏；auto_ptr 掏空实测（抄作业勿学）；循环引用 vs 反向指针 A/B 对照（有无析构输出即有无泄漏）；多态容器 `vector<unique_ptr<Shape>>` 面积 3.14159+6=9.14159；并发计数 800000 精确；跨线程异常正常重抛；chrono 换算 5500ms、sleep 实测；随机固定种子可复现；array 越界 at() 抛异常 |
| cpp14 | 4 | 泛型 Lambda/初始化捕获、auto 返回类型、make_unique、二进制字面量/分隔符 | 同一泛型 lambda 跑通 int/double/string |
| cpp17 | 8 | 结构化绑定/if-switch 初始化、optional/variant/any、string_view、filesystem、并行算法、折叠、if constexpr、CTAD/inline 变量 | seq/par 排序一致性通过；filesystem 建写列查清全流程；if constexpr 丢弃分支不实例化 |
| cpp20 | 8 | Concepts、Ranges、`<=>`、span、constexpr/consteval/constinit、协程、jthread/stop_token、erase 系列/指定初始化/模板化 Lambda | 手写 Generator 输出自然数与斐波那契；jthread 协作取消实测（1.69 亿圈后收到停止）；consteval 双路径验证 |
| cpp23 | 7 | optional monadic、expected、views::zip、if consteval、print/format、std::generator、move_only_function/ranges::to/enumerate | expected 链路 210/错误传导；zip 写回生效 (bob 85→90)；std::generator 生产版与手写版对照 |

每文件的"解决什么 C++98 旧写法 / 替代为 X"见各 .cpp 头部注释；文件主题一览见上方目录树。

## 在 VSCode 里运行（日常用这个）

配置已经写好了，在 `.vscode/` 下的 `tasks.json` / `launch.json` / `c_cpp_properties.json` 里，不用自己配。

### 一次性准备

1. **打开的是本文件夹，不是父目录**：`File → Open Folder…` 选 `modern-cpp-examples` 本身。
   `.vscode/` 只在"工作区根目录"下生效——如果打开的是 `ClaudeCode_Projects`，
   任务列表里根本不会出现下面这些任务。这是新手最容易踩的一步。
2. 装 **C/C++ 扩展**（`ms-vscode.cpptools`，Microsoft 出的那个）：只编译运行不装也行，
   但 **F5 调试、代码跳转和补全需要它**。
3. 编译器不需要额外安装。macOS 用 **Apple clang**，随 Xcode Command Line Tools 一起提供。
   验证：终端里 `clang++ --version` 应输出 `Apple clang version 21.x`；F5 调试用的 `lldb` 同源同装。

> **`.vscode/c_cpp_properties.json` 是给这个扩展用的 IntelliSense 配置**（告诉它按 `c++23`
> 和系统头文件来"读"代码）。**它只影响编辑器的红波浪线/补全/跳转，不影响编译**——
> 没有它的话，`cpp17/` 及以后的文件会因为扩展默认标准太低而满屏假报错
> （如 `cpp23/05` 报"命名空间 std 没有成员 format"）。真正编译用的标准是
> `Ctrl+Shift+B` 弹出的那个下拉框，两者互不相干。
>
> ⚠️ 这个文件归 C/C++ 扩展管，**扩展重写它时会清掉里面的注释并重排缩进**，这是正常的，
> 不用手工去整理格式。`tasks.json` 也有同样的问题。

### 编译 + 运行

**日常只记一个键：`Ctrl+Shift+B`。**

| 步骤 | 操作 |
| --- | --- |
| 1 | **先点一下那个 `.cpp` 的编辑区**（让焦点在它身上，原因见下面的红字警告） |
| 2 | `Ctrl+Shift+B` → 弹下拉框，选该文件对应的标准（在 `cpp11/` 里就选 `c++11`） |
| 3 | 编译 + 运行一气呵成，输出打在下方终端面板 |

产物是**源文件旁边的同名可执行文件**，如 `cpp11/01_auto_decltype`（macOS 上不带扩展名），下次可以直接跑。
旁边还可能多出一个同名 `.dSYM/` 目录，那是调试符号（`-g` 的产物），两者都已被 `.gitignore` 忽略，不用管。

> ⚠️ **最容易踩的坑：`Ctrl+Shift+B` 作用于"当前焦点所在的编辑器"。**
> 如果你刚看完 README、焦点还停在 `README.md` 上就按快捷键，它会去"编译 README.md"然后失败，
> 而且**编译一失败，后面的运行就不会发生**——表现出来就是"按了没反应 / 没有执行"。
> 所以按之前先点一下 `.cpp` 的编辑区。同理，VSCode 窗口停在别的文件上也不行。

另外两个任务（`Ctrl+Shift+P` → `Tasks: Run Task` 里选）：

| 任务 | 什么时候用 |
| --- | --- |
| `C++: 只编译不运行` | 只想确认"改的代码能不能过编译"，不看输出 |
| `C++: 只运行 (不重新编译)` | 代码没改、只想再看一遍输出。**改了 `.cpp` 别用这个**，跑的是旧可执行文件 |

两个标签长得很像，选的时候看清结尾是"不运行"还是"不重新编译"。

比上面更顺手的两招：

**招数一：在终端里直接跑生成的可执行文件。** 路径是相对"终端当前所在目录"算的，不是相对
工作区根目录——VSCode 终端默认停在 `modern-cpp-examples/`，此时写 `./cpp11/01_auto_decltype`；
如果你已经 `cd cpp11` 进去了，就写 `./01_auto_decltype`。

```bash
# 情况 A: 终端在 modern-cpp-examples/ 下
./cpp11/01_auto_decltype

# 情况 B: 已经 cd 进 cpp11/ (路径从当前目录算起, 少一层)
./01_auto_decltype
```

> ⚠️ **macOS 上跑当前目录的程序必须带 `./` 前缀**，直接写 `01_auto_decltype` 会报
> `zsh: command not found: 01_auto_decltype`。这不是故障——Unix 出于安全考虑
> **默认不把当前目录放进 `PATH`**（否则你 cd 进一个陌生目录、里面有个叫 `ls` 的恶意文件，
> 一敲 `ls` 就被执行了）。写 `./` 等于明确声明"我就是要跑当前目录下这个文件"。

**中文输出不需要任何设置。** macOS 终端默认就是 UTF-8：程序吐 UTF-8 字节、终端按 UTF-8 解码，
两边天然对齐，中文直接正常显示。

> 这在 Windows 上是个大坑——PowerShell 会把子进程输出按 gb2312 **重解一遍**，而 `chcp 65001`
> 治不了它（因为真正解码的是 PowerShell 自己缓存的属性，不是控制台代码页）。当年花了一整节
> 才排查清楚。**macOS 上这一整类问题不存在**，因为整条链路上只有一个编码。
> 想看当年怎么解的，见文末「附录：Windows 时期历史记录」。

**别在 Finder 里双击可执行文件。** 命令行程序打印完就退出，而 macOS 会为它开一个终端窗口、
跑完立刻关闭，所以你只会看到窗口一闪而过。这是正常现象不是报错。
必须在终端里跑（或按 F5 调试）才看得到输出。

**招数二（已配好）：`Ctrl+Alt+R` 直接弹出任务列表**，上面那三个任务点一下就跑，
不用再走 `Ctrl+Shift+P`。

> ⚠️ **VSCode 的硬限制：快捷键不支持项目级配置。** `tasks.json` / `launch.json` 能放在 `.vscode/`
> 里跟着项目走，但快捷键只能写进**全局**的 `~/Library/Application Support/Code/User/keybindings.json`
> （macOS 路径；Windows 是 `%APPDATA%\Code\User\keybindings.json`）——
> 也就是说这条绑定对你所有项目生效，换台机器/重装 VSCode 都不会跟着仓库走。

已写入的内容：

```jsonc
// ~/Library/Application Support/Code/User/keybindings.json   (macOS)
// %APPDATA%\Code\User\keybindings.json                       (Windows)
{
  "key": "ctrl+alt+r",
  // 不写 args = 打开任务选择器(列全部任务)
  // 写了 args = 直接跑指定任务, 例如 "args": "C++: 只运行 (不重新编译)"
  "command": "workbench.action.tasks.runTask"
}
```

选"任务选择器"而不是"一个任务一个键"的原因：以后往 `tasks.json` 里加任务时，这个键不用跟着改。

### F5 调试（可选）

行号左边点一下打个红点（断点）→ `F5` → 再选一次标准 → 程序停在断点处，
左栏看变量/调用栈，顶部单步。讲语义的文件（`cpp11/01` 的 auto 推导、`cpp11/05` 的移动语义）
单步跟一遍比读十遍注释管用。

### 任务背后的命令

两个 json 不是黑魔法，等价于下面这一行（`{std}` 是下拉框选的，`{file}` 是当前文件）：

```bash
clang++ -std={std} -Wall -Wextra -O1 -g -pthread {file} -o {同名可执行文件}
```

就这一条，没有别的包装——macOS 上不需要切代码页，也不需要强制走某个 shell。

各参数为什么这么定：

| 参数 | 作用 |
| --- | --- |
| `-Wall -Wextra` | 开警告，提前发现手误。见下方"验证与问题记录" |
| `-O1` | 轻微优化。`-O0` 时部分警告（如使用未初始化变量）不触发；`-O2` 编译慢且没必要 |
| `-g` | 生成调试信息，F5 必需 |
| `-pthread` | 并发/并行示例需要（`cpp11/09`、`cpp11/10`、`cpp17/05`、`cpp20/07`） |

> **Windows 版比这多两个参数，macOS 上都不需要：**
>
> | 参数 | 为什么 Windows 需要 | 为什么 macOS 不需要 |
> | --- | --- | --- |
> | `-static` | 绕开 MinGW 动态链接缺 CRT 入口点的坑（`filesystem` / `chrono` / `jthread` 三个文件启动即挂） | macOS **不支持完全静态链接**（会报 `ld: library not found for -lcrt0.o`），加了反而编不过。而 macOS 系统库始终存在，本来就不会缺库 |
> | `-lstdc++exp` | GCC 把 `std::println` 的"终端直写"符号单独放在实验库 `libstdc++exp.a` 里，不显式链接就 undefined reference | 那是 **GCC 特有的库**，clang / libc++ 根本没有。Apple clang 由 libc++ 直接提供 `std::print`，无需额外链接 |

### 自己写的练习文件怎么办

任务用的是 `${file}`（当前焦点文件），所以**任何位置、任何名字的 `.cpp` 都能直接编**，
不需要登记到什么地方：

| 问题 | 答案 |
| --- | --- |
| 放哪 | 随便。放在 `cpp17/` 下表示"C++17 的练习"，放别处也行 |
| 标准怎么定 | 任务**不看文件放在哪**，只看下拉框里你选了什么。建议跟着所在目录选 |
| 产物叫什么 | 跟源文件同名、同目录。`my_test.cpp` → `my_test`（macOS 无扩展名，旁边还有个 `my_test.dSYM/`，同样被 git 忽略） |
| 文件名建议 | 用英文 + 数字 + 下划线，别用空格和中文（`-o` 那行的路径不一定会被自动加引号） |
| 一次编多个文件 | 不支持。本套是"一个文件一个程序"的设计；真要多文件就去写 `Makefile`（见 FAQ Q5 的升级路径） |

> **`.vscode/` 里的 `tasks.json` / `launch.json` / `c_cpp_properties.json` 是项目的一部分，要跟着 git 提交**，
> 否则换台电脑或重新 clone 就没有这些任务了。（`keybindings.json` 是例外——它在全局，
> 跟仓库无关，换机器要手动补。）

### 常见问题

| 现象 | 原因 / 处理 |
| --- | --- |
| **按了 `Ctrl+Shift+B`，它去编译别的文件 / 报错 / 只编译不运行** | 焦点不在 `.cpp` 上（比如停在 `README.md`）。任务作用于 `${file}`＝当前焦点编辑器；**编译失败时后面的运行会被跳过**，所以看着像"没执行"。先点一下 `.cpp` 编辑区再按 |
| **选了"编译并运行"，它又编译了一遍** | 设计如此：该任务永远是"先编译、成功后运行"。不想重编就用 `C++: 只运行 (不重新编译)` |
| `Ctrl+Shift+B` 没反应，或任务列表里没有 `C++:` 开头的项 | 打开的是父目录。`File → Open Folder` 换成 `modern-cpp-examples` |
| 报 `clang++: command not found` | 没装 Xcode Command Line Tools。终端执行 `xcode-select --install`，装完 `clang++ --version` 应能输出 `Apple clang version 21.x` |
| 编译报一堆 `'xxx' is not a member of 'std'` | 下拉框标准选低了。`cpp17/` 的文件按 `c++11` 编，自然找不到 `std::optional` |
| F5 报"无法启动程序，文件不存在" | F5 的 `preLaunchTask` 会先编译；它会弹标准选择框，选对即可。若确实没编译成功，先单独 `Ctrl+Shift+B` 一次 |
| **在 Finder 里双击产物只闪一下窗口** | 正常现象，不是报错。命令行程序打印完就退出，macOS 开着终端窗口跑完立刻关闭。必须在终端里跑才看得到输出（见上面"招数一"） |
| 改了 `.cpp` 再跑，输出没变 | 产物是**编译那一刻的代码快照**，改源码不会自动更新。每次改完都要重新 `Ctrl+Shift+B` |
| **编译产物越攒越多** | 每个可执行文件约 40 KB，42 个全编一遍也才几 MB（macOS 没有 `-static`，所以没有 Windows 上单文件 3 MB 的膨胀）。产物散落在各 `cppXX/` 目录里，但已被 `modern-cpp-examples/.gitignore` 忽略。想清理：在 `modern-cpp-examples/` 下执行 `find . -type f ! -name '*.cpp' ! -name '*.md' ! -path './.vscode/*' -delete && find . -name '*.dSYM' -exec rm -r {} +`。删了不影响仓库，用的时候 `Ctrl+Shift+B` 重建即可 |
| 终端报 `zsh: command not found: 01_auto_decltype` | 路径少了 `./`。macOS 默认不把当前目录放进 `PATH`，跑当前目录下的程序必须写 `./01_auto_decltype` |
| 终端报 `zsh: permission denied: ./01_auto_decltype` | 产物没有可执行位。正常由编译器生成时一定有；如果是从别处拷来的，`chmod +x 文件名` |
| 改了 `.vscode/*.json` 不生效 | `Ctrl+Shift+P` → `Developer: Reload Window` |
| **`Ctrl+Alt+R` 按了没反应** | 这条绑定在**全局** `keybindings.json` 里，不跟着仓库走。换机器、重装 VSCode、或用了另一套 Profile 就没了，按「招数二」重新加一次即可 |
| 生成的产物会不会被 git 提交 | 不会，`modern-cpp-examples/.gitignore` 已把各 `cppXX/` 目录下除 `.cpp` 外的一切忽略（含 `.dSYM/`） |

## 编译与运行（命令行 / 参考）

日常读代码用上面那节就够了，这节是没有 VSCode 或想手动指定参数时的写法。

本机实测编译器：**Apple clang 21.0.0 (arm64-apple-darwin25)**，随 Xcode Command Line Tools 提供。
**39 / 42 个文件**编译并运行通过；3 个失败全部是 Apple libc++ 的实现缺口，不是代码问题
（详见"验证与问题记录"）。Windows 版用 GCC 15.2 时是 42/42 全过。

```bash
# 通用单文件命令（替换 {std} 与文件名；并发/并行示例保留 -pthread）
clang++ -std={c++11|c++14|c++17|c++20|c++23} -Wall -Wextra -O1 -pthread 路径/文件.cpp -o demo && ./demo
```

**macOS 上没有"工具链特例"。** 所有文件一条通用命令即可——不需要 `-static`，
不需要补链接库。（对照：Windows/MinGW 版本有三处特例——动态链接启动即挂、
`std::println` 缺实验库、静态链接参数顺序，全部源于 MinGW 的运行时管理方式，见文末附录。）

3 个编不过的文件及当下可用的替代路径：

| 文件 | 缺失特性 | 现在能怎么办 |
| --- | --- | --- |
| `cpp17/05_parallel_algorithms.cpp` | `std::execution::par` | 用 `std::thread` / 线程池手动并行。⚠️ **Apple clang 不支持 `-fopenmp`**（实测报 `unsupported option`），要走 OpenMP 得先 `brew install libomp`。或装 GCC |
| `cpp23/06_std_generator.cpp` | `<generator>` | 直接读 `cpp20/06_coroutine_generator.cpp`——那是同一件事的手写协程实现，原理讲得更透。或装 GCC |
| `cpp23/07_tools.cpp` | `std::move_only_function` | 用 `std::function` 顶替（仅限可拷贝的回调）；或装 GCC |

编译器需求速查：

| 标准 | g++ (libstdc++) | clang (libc++) | MSVC (Visual Studio) |
| --- | --- | --- | --- |
| C++11 | 4.9+ | 3.4+ | VS 2015+ |
| C++14 | 5+ | 3.4+ | VS 2015+ |
| C++17 | 8+ | 6+ | VS 2017 15.7+ |
| C++20 | 10+ (较全 12+) | 13+ (较全 16+) | VS 2022 17.0+ |
| C++23 | 13+ 部分 / 14+ 大部分 / **15+ 含 std::generator** | 17+ / 18+ 较多 | VS 2022 17.8+ 逐步覆盖 |

## 学习疑问 FAQ

读这套示例时自己冒出来的问题，连同答案记在这，省得以后重新查一遍。（2026-09 记录）

### Q1. `-Wall` 是干嘛的？

打开一组编译器认为"普遍有用"的警告。名字里 W 是 warning（`-W` 是所有警告开关的前缀），
但 `all` 是历史遗留的营销词——**它不是真的全部**，只是一份精选清单。

写段故意有毛病的代码实测：

| 编译参数 | 输出 |
| --- | --- |
| 不加 `-Wall` | 干净通过，一个警告都不报 |
| 加 `-Wall` | 4 条警告：未使用变量、疑似 `=` 写成 `==`、有符号/无符号比较、printf 格式串类型不匹配 |

要点：

- **警告 ≠ 错误**。加了 `-Wall` 照样编译成功、照样能跑，只是多打印出可疑之处。要让警告中止编译得再加 `-Werror`。
- 默认不开是为了向后兼容：几十年的老代码一开就满屏警告，厂商怕吓到用户。所以新项目应该自己主动开。
- `-Wall` 抓的是"大概率是 bug"（未使用变量、漏 `return`、括号歧义、变量遮蔽……），
  **抓不了逻辑错误**——能通过 `-Wall` 的代码完全可能算错。
- `-Wextra` 是比 `-Wall` 更啰嗦的另一组。`-Wall -Wextra -Werror -pedantic` 是很多严肃项目的标配。
- 可以单独开关某一项：`-Wno-unused-variable`。

### Q2. 示例里的 `(void)y;` 这种句子有什么用？

抑制 `-Wall` 里的 `-Wunused-variable` 警告。

`y` 只在 `decltype(y)` 里出现，而 `decltype` 是**不求值上下文**——编译期取类型，运行时不读这个变量，
于是编译器认为它"声明了但从没被使用"。`(void)y;` 就是惯用的"我故意的，别警告"标记。

实测（原 Windows 机器，g++ 15.2）：

| 情况 | 结果 |
| --- | --- |
| 保留 `static_assert`，删掉 `(void)` | 无警告 |
| 连 `static_assert` 一起删掉 | `warning: unused variable 'y' / 'z' [-Wunused-variable]` |

也就是说**在原 Windows 机器的 g++ 15.2 下 `cpp11/01` 里那两行其实是冗余的**——它上面的 `decltype` 已经足够让 GCC
认为变量被用过了。写 `(void)` 是为了跨编译器/跨版本稳妥（历史上 GCC/Clang 某些版本确实会把 decltype
中的出现算作"未使用"）。另外 C++11 文件用不了 C++17 的 `[[maybe_unused]]`，所以只能用 `(void)` 转换；
现代代码里 `[[maybe_unused]]` 更推荐。同文件 `cpp11/01` 靠后的 `(void)b; (void)c;` 是一回事。

### Q3. `Ctrl+Shift+B` 和 `Ctrl+Shift+P` 分别是什么？

| 快捷键 | 官方名字 | 本质 | 用途 |
| --- | --- | --- | --- |
| `Ctrl+Shift+B` | Run Build Task | **"构建"专用快捷键**，只认 `tasks.json` 里 `isDefault: true` 的那一个任务 | 编译并运行当前文件（一条龙） |
| `Ctrl+Shift+P` | Show All Commands（命令面板） | VSCode 的**总入口**，一个搜所有命令的输入框，跟 C++ 毫无关系 | 搜 `Tasks: Run Task` 去跑另外两个非默认任务 |

关键区别：`Ctrl+Shift+B` **只跑默认任务，一个**。VSCode 没给"运行任意任务"配内置快捷键，
所以另外两个任务走 `Ctrl+Alt+R` 任务选择器（见上一节「招数二」，已配好），或者
`Ctrl+Shift+P` → `Tasks: Run Task`。

`Ctrl+Shift+P` 还能搜到 `Developer: Reload Window`、`Preferences: Open Settings` 等等一切命令——
记住它是 VSCode 的万能搜索框就够了。

### Q4. 不需要 CMake 之类的来构建吗？

不需要，因为这里没有"工程"可构建。

CMake 解决的是**多文件的依赖图问题**：A.cpp 用了 B.cpp 的函数、要链第三方库、
要生成 VS 工程给同事、要在 Linux 和 Windows 上都编。
而这 42 个文件是 **42 个各自独立的单文件程序**——每个自带 `main`，互相不 `#include`。
这种情况「直接编那一个文件」就是正解，套 CMake 只会多出 `CMakeLists.txt`、`build/` 目录、
改一行代码要先"重新配置"的仪式感，收益是零。

一句话：**CMake 管的是"工程"，`clang++` 直接编管的是"一个文件"。**

（本机 `CMake 4.4.3`（Homebrew 装，2026-09-19）、`GNU Make 3.81`（Apple 自带）都就绪，随时能用，
只是这里用不上。`Ninja` 未装，真需要时 `brew install ninja` 即可。）

### Q5. 几个配置文件各管什么？只靠它们够吗？

够。但要分清**四层**——很多困惑都来自把它们混在一起看：

```text
① 键位层   Ctrl+Shift+B  /  Ctrl+Alt+R        ← VSCode 内置 / 全局 keybindings.json
                 │ 触发
② 命令层   workbench.action.tasks.runTask      ← VSCode 内置命令, 本身不认识任何具体任务
                 │ 运行时才去问"当前工作区有哪些任务"
③ 任务层   .vscode/tasks.json                  ← 真正的命令(clang++ / 产物) + 依赖关系
                 │ 调用
④ 构建层   clang++ ...                         ← 换成 make / CMake / MSBuild 也行
```

**②③ 的关系是最容易搞错的地方**：

| 绑定写法 | 效果 |
| --- | --- |
| `"command": "workbench.action.tasks.runTask"`（**没有** `args`） | 打开**任务选择器**，列出当前工作区所有任务 |
| 再加上 `"args": "任务名"` | 不弹列表，**直接跑那一个任务** |

所以 `Ctrl+Alt+R` 跟具体任务之间**没有写死的对应关系**——它绑的是"选择器"这个命令，
任务列表是运行时才从 `tasks.json` 里读的。这正是它比"一个任务一个键"好用的原因：
以后往 `tasks.json` 里加新任务，快捷键一个字都不用改。

**③ 内部还能再套一层**：一个任务可以用 `dependsOn` 串起别的任务，形成"先跑依赖、再跑自己的命令"的链。
`Ctrl+Shift+B` 之所以能一键完成编译 + 运行，就是因为它指向的默认构建任务长这样：

```text
Ctrl+Shift+B
  └─> 任务「C++: 编译并运行当前文件」
        ├─ dependsOn → 任务「C++: 只编译不运行」  →  clang++ ...   ← 先跑
        └─ 自己的 command                        →  01_xxx      ← 后跑
```

编译失败时链上第一环就断了，第二环不会发生——所以"按了没反应"要先去面板看编译报了什么错。

**`Ctrl+Shift+B` 本身是 VSCode 内置快捷键**，行为写死为"跑当前工作区的**默认构建任务**"，
也就是 `tasks.json` 里标了 `"group": {"kind": "build", "isDefault": true}` 的那一条。
把标记挪到别的任务上，它就跑别的——**改的是任务，不是键位。**

**`tasks.json` 也不是构建系统**，它只是一张"点一下就跑这条命令"的便利贴，
真正编译的是它背后那个 `clang++`。所以"够不够"取决于构建层——单文件场景 `clang++` 完全够，集成层也就够。

项目长大后的升级路径：

| 场景 | 该用什么 |
| --- | --- |
| 1 个文件（现在） | `clang++` + `tasks.json` |
| 十几个文件、互相依赖、想增量编译 | 写个 `Makefile`（本机 `make` 已装），`tasks.json` 改成调 `make` |
| 要链 OpenCV/Qt/Boost、跨平台、给别人用 | 上 CMake + 装 **CMake Tools 扩展**；那时构建按钮归扩展管，`tasks.json` 基本就不需要了 |

`launch.json` 的定位与这三档都无关——它只负责"按 F5 时怎么调试"，用什么构建系统都用得上。

`.vscode/c_cpp_properties.json` **根本不在这条链上**：它不参与构建，只是喂给 C/C++ 扩展做
IntelliSense（跳转、补全、红波浪线）。所以它"管不管用"和能不能编译完全无关——删了它照样能
`Ctrl+Shift+B`，只是编辑器看 `cpp17/` 以后的代码会满屏假错误。

## 对照速查: C++98 旧写法 → 现代写法

| C++98/03 时代写法 | 现代推荐写法 | 示例文件 |
| --- | --- | --- |
| `NULL` / `0` 当空指针 | `nullptr` | cpp11/02 |
| `enum { ... }` 泄漏作用域 | `enum class` | cpp11/02 |
| 手写迭代器 for 循环 | 范围 for / STL 算法 / Ranges 管道 | cpp11/03,07 cpp20/02 |
| `new`/`delete`、`new[]`/`delete[]` 手动管理 | `unique_ptr` / `shared_ptr` / `vector` | cpp11/04 cpp11/15 cpp14/03 |
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
4. `cpp11/04+05+06` 智能指针 / 移动 / 转发（最核心, 连读）；`cpp11/15` 智能指针实战（04 的续篇: 来源 / 判断 / 多态容器 / 反向指针）
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
协程框架、`std::execution`（C++26 方向）；**并发相关的缺口单独盘点在下一节**。

进阶方法：每读完一个文件，拿视频课程里的旧项目代码用对应新写法重构一遍，比读十遍有效。

## 并发 / 多线程：已覆盖与缺口 (2026-09-12 盘点)

已覆盖 4 个文件（另有 `cpp20/06`、`cpp23/06` 两个**协程**文件 —— 协程是单线程的协作式调度, 与多线程无关, 别混）：

| 文件 | 覆盖内容 | 实测验证 |
| --- | --- | --- |
| `cpp11/09` | `std::thread` + `join`、`std::mutex` + `lock_guard`(RAII 锁)、`std::atomic` 无锁计数、按线程拆分任务最后汇总 | 8 线程 × 10 万次, 加锁/原子计数均精确 800000；1..999999 求和 499999500000 |
| `cpp11/10` | `std::async` + `std::future`、显式 `launch::async`、`get()` 阻塞取值、**异常跨线程传播** | fib(30)=832040、fib(33)=3524578；子线程的 `invalid_argument` 在主线程捕获 |
| `cpp17/05` | 并行算法执行策略 `seq` / `par` / `par_unseq`（不用自己管线程, 标准库帮你并行） | seq 与 par 排序结果一致 |
| `cpp20/07` | `std::jthread` 析构自动 join（RAII）、`stop_token` / `stop_source` 协作式取消 | 忘写 join 不会 terminate；worker 收到停止信号后退出 |

**缺口清单**（按学习价值排序, 需要时按此顺序补）：

| # | 缺口 | 说明 |
| --- | --- | --- |
| 1 | `std::condition_variable` + `std::unique_lock` | 生产者/消费者队列 —— 线程间协作最常用的模式。`condition_variable` 必须配 `unique_lock`：`wait()` 内部要先解锁、醒来再重新加锁, `lock_guard` 做不到（现有例子只有 `lock_guard`） |
| 2 | 死锁与 `std::lock` / `std::scoped_lock` | "两个 mutex 反序加锁"的经典死锁现场（跑一次卡住才记得住）；C++17 `scoped_lock` 一次锁多个 mutex, 内部含死锁避免算法 |
| 3 | `std::promise` / `std::packaged_task` | `future` 有**三个**来源, 目前只演示了 `async`；这两种是"先把 future 交出去、由别人填值"的常见写法 |
| 4 | `std::memory_order` | 目前一律用默认 `seq_cst`（最安全也最慢）；`relaxed` / `acquire` / `release` 是无锁编程的基础 |
| 5 | `std::thread` 日常细节 | `detach`、传引用要包 `std::ref`、`thread_local`、`hardware_concurrency()`、`this_thread::sleep_for/yield/get_id` |
| 6 | C++20 同步原语 | `std::counting_semaphore` / `std::latch` / `std::barrier` / `atomic<shared_ptr>` |
| 7 | 线程池 | 标准库至今没有（C++26 的 `std::execution` 还在路上）, 实战需自写或用第三方 |
| 8 | `std::async` 默认策略的坑 | 不传策略时任务可能**同步执行**(deferred) —— `cpp11/10` 的头部注释提到过, 但没有实际演示出来 |

> 以后要补的话, 建议这样合并成文件：①+② 一个文件（条件变量 + `unique_lock` + 死锁现场 + `scoped_lock` 对比）,
> ③+⑧ 一个文件（future 三来源 + async 策略陷阱）；内存序(④)配一个无锁队列的例子才讲得透。

## 验证与问题记录

### macOS 环境实测（2026-09-21）

**本机工具链**：Apple clang 21.0.0（`clang-2100.3.34.2`），链接器 `ld-27037.1`，
Target `arm64-apple-darwin25.6.0`，macOS 26.6。随 Xcode Command Line Tools 提供，无需额外安装。

**验证方法**：`clang++ -std=<版本> -Wall -Wextra -O1 -g -pthread 文件.cpp -o 同名产物` 逐个编译。

| 目录 | 标准 | 文件数 | 通过 | 失败 |
| --- | --- | --- | --- | --- |
| cpp11 | `-std=c++11` | 15 | 15 | 0 |
| cpp14 | `-std=c++14` | 4 | 4 | 0 |
| cpp17 | `-std=c++17` | 8 | 7 | 1（`05_parallel_algorithms`） |
| cpp20 | `-std=c++20` | 8 | 8 | 0 |
| cpp23 | `-std=c++23` | 7 | 5 | 2（`06_std_generator`、`07_tools`） |
| **合计** | | **42** | **39** | **3** |

**工具链差异**：3 个失败是 Apple libc++ 的实现缺口，不是代码问题——同样的文件在
GCC 15.2 上一个不少地全过。C++23 关键特性的逐项实测结果：

| 特性 | Apple libc++ 21 | 说明 |
| --- | --- | --- |
| `std::print` / `std::println` | ✅ | 无需任何额外链接参数（对比 GCC 那边要 `-lstdc++exp`） |
| `std::format` | ✅ | |
| ranges / views | ✅ | 含 `views::zip`、`views::enumerate` |
| concepts | ✅ | |
| `std::expected` | ✅ | |
| `std::span` / `std::mdspan` | ✅ | |
| `std::flat_map` | ✅ | |
| `std::to_chars`（浮点） | ✅ | |
| `std::generator` | ❌ | |
| `std::move_only_function` | ❌ | |
| `std::stacktrace` | ❌ | 示例集未用到 |
| `std::execution::par` | ❌ | 且 **Apple clang 不支持 `-fopenmp`**，要 OpenMP 须先装 `libomp` |

**要不要装 GCC 补全 42/42**：不是必须。39/42 已覆盖 C++11→23 的学习主线，
缺的三个特性各自都有替代路径（见上方"编译与运行（命令行 / 参考）"）。
装 GCC 的成本不高（约 90 MB 下载、装后约 2 GB），但会引入"两个编译器行为不一致"的困扰。
**建议等真正写代码撞上时再装。**

> ⚠️ **迁移期间踩过的一个坑（已解决，记录备查）**：更新 CLT **之前**，链接器是 `ld-1267`，
> 它看不懂 macOS 27.0 SDK 的 `.tbd` 文件里新增的 `arm64e.x1` 架构，导致**所有** C/C++
> 程序链接失败（`tapi error: unknown architecture`）——注意只编译不链接（`-c`）是成功的，
> 所以很容易误判成环境没问题。更新 Command Line Tools 后链接器升到 `ld-27037.1`，问题消失，
> **不需要任何环境变量或配置改动**。

**关键输出核对**（macOS / Apple clang，39 个通过的文件全部实际运行并核对）：

已逐文件运行验证，输出与下方 Windows 记录一致——示例本身是纯标准库代码，跨平台输出不变。

---

### Windows 环境实测（2026-09-04，g++ 15.2.0 MinGW-W64）

> 以下为原 Windows 机器上的验证记录，保留备查。对照上方的 macOS 结果阅读。

**验证方法**: 每个文件用 `g++ -std=<版本> -Wall -Wextra [-static] -pthread -O1` 编译 →
运行 → 人工核对输出数值与语义（不只"能跑"）。

**关键输出核对清单**（2026-09-04, g++ 15.2.0 MinGW-W64）:

| 示例 | 核对点 | 结果 |
| --- | --- | --- |
| cpp11/04 | 循环引用节点是否泄漏 | 两个 ~Node 析构均打印 |
| cpp11/15 | auto_ptr 掏空 / 多态容器 / 循环引用 vs 反向指针 | 拷贝后 a 被掏空(nullptr)、传参后 c 被掏空；面积 3.14159+6=9.14159；A 组零析构输出(泄漏)、B 组 ~Parent+~Child 均打印 |
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
| std::print 链接失败 | 终端直写符号（`__open_terminal` / `__write_to_terminal`）被 libstdc++ 放在**实验库** `libstdc++exp.a` 里，不显式链接就报 undefined reference。⚠️ **原记录误判为"该 MinGW 发行版的构建缺陷"，2026-09-12 查明并修正** | 链接时加 `-lstdc++exp` 即可（g++ 15.2.0 实测通过，配 `-static` 也可以）。**2026-09-12 已把 `cpp23/05` 改回官方 `std::println`/`std::print` 写法**（原先的 format+cout 兼容层已删除），tasks.json 编译参数补上该库；全量复测 **41/41 通过，警告数仍为 4** | **已修复** |
| 动态链接启动即挂（3 个文件） | filesystem / chrono / jthread 的动态 exe 依赖本机缺失的 CRT 入口点（真实错误码 0xC0000139, STATUS_ENTRYPOINT_NOT_FOUND; bash 显示 127） | 这三个文件一律 `-static` 编译, 代码本身无误 | 已绕行 |
| 并行算法 -ltbb 反而失败 | 本发行版不带 TBB 库; 但不加 -ltbb 时 par 策略可直接链接运行 | 编译命令一律不加 -ltbb | 无需处理 |
| **4 个文件有警告**（2026-09-12 复查发现, 原记录"零警告"有误） | `-Wall -Wextra` 下: cpp14/02 与 cpp17/01 是 `-Wunused-but-set-variable`; cpp20/08 是 `-Wmissing-field-initializers`（故意不初始化 Point3D::y 的演示）; cpp23/06 是 libstdc++ `std::generator` 头文件内的 `-Wmismatched-new-delete` 编译器误报 | 前两个可加 `[[maybe_unused]]` 修; 第三个是刻意演示, 应保留; 第四个改不了我们的代码 | **待定** |

**工具链探测结论**: g++ 15.2 完整支持本套用到的全部 C++20/23 特性——协程、Concepts、
Ranges、`views::zip`/`enumerate`、`ranges::to`、`std::expected`、optional monadic、
if consteval、`std::move_only_function`、`std::format`、`std::generator`（后两者需 g++ 14+/15+）。

**其它说明**: bilibili 课程页面无法抓取（网络策略拦截），"视频教了 C++98" 的知识衔接按该
BV 号主流入门课内容推断，如有出入以实际课程为准。

## 附录：Windows 时期历史记录（中文乱码排查完整档案）

> ⚠️ **以下内容全部来自原 Windows 机器，在 macOS 上不适用**，仅作历史存档保留。
> 记录的是 2026-09 那台 Windows 设备上的一个编码问题的完整排查过程。
> **日常使用（macOS）不需要读**——macOS 上整条链路只有一个 UTF-8，这一整类问题不存在。
>
> 保留的理由有两个：① 记录"当年为什么那样配"，以后看到历史提交或旧笔记时不至于困惑；
> ② 万一以后回到 Windows 环境，这些结论可以直接复用，不用重新踩一遍。
>
> 当年为了这件事改动了 `.vscode/tasks.json`（加了 `chcp 65001` + 强制走 `cmd.exe`）
> 和两个 PowerShell profile（加了 `[Console]::OutputEncoding`）。**这些改动在迁移到
> macOS 时已全部移除**——现在的 `tasks.json` 里没有任何代码页相关的内容。

### 现象

```text
$ .\cpp11\02_nullptr_enum_class_override_final.exe
Color::Red 鐨勫簳灞傚€?= 0        ← 乱码
Color::Red 的底层值 = 0           ← 应该是这样
```

### 根因：一条链路上有 4 层编码，它们没对齐

| 层 | 是什么 | 本机取值 | 谁决定 |
| --- | --- | --- | --- |
| ① 系统代码页 | ANSI / OEM | **936** | 系统区域设置（LCID 2052 = zh-CN） |
| ② 控制台代码页 | conhost 给控制台程序的 | **936** | 从 ① 派生 |
| ③ Shell 的解码器 | PowerShell 的 `[Console]::OutputEncoding` | **gb2312** | PS **启动那一刻**从 ② 取一次，之后**永不更新** |
| ④ 终端渲染层 | VSCode / Windows Terminal / mintty | **UTF-8** | 各自实现，与 ①②③ 无关 |

g++ 编出的程序吐的是 **UTF-8 字节**（`的` = `E7 9A 84`，`od -An -tx1` 一查便知），
按 ①②③ 的 936/gb2312 去解就是乱码。**错的不是示例代码，是解码端。**

### 为什么 `Ctrl+Shift+B` 不乱、手工在终端里就乱

| 路径 | 链路 | 结果 |
| --- | --- | --- |
| `Ctrl+Shift+B` | `VSCode → cmd /c "chcp 65001 & exe"`，exe 的字节**直落**控制台 | ✅ cmd 是**哑管道**，字节原样透传；控制台被切成 65001，正好对得上 |
| 手工在 PowerShell 里跑 | `PowerShell → exe`，PS **把输出读进管道**，用 `[Console]::OutputEncoding`(gb2312) **重解一遍** | ❌ 解错 → 再按 GBK 写出去 → 渲染层按 UTF-8 读 → **错两层** |
| 手工在 Git Bash 里跑 | mintty，locale = `C.UTF-8` | ✅ 天然 UTF-8，一直就是好的 |

**要点：区别不在 exe，在中间有没有一个"会转码的中间人"。** cmd 是哑管道；
PowerShell 是带翻译的中间人——它必须读子进程输出（否则 `$r = & xxx.exe` 没法实现），
而它那个翻译设置启动时就锁死了。

顺带解释了**为什么 Python 一直没事**：管道里 Python 的 `sys.stdout.encoding` = `cp936`
（取自 `locale.getpreferredencoding()`），吐的是 GBK 字节，和 PS 的 gb2312 恰好对得上。
不是 Python 更正确，是它说的方言正好一致。

### 做了哪些改动 / 怎么撤销

**改动 1 — `.vscode/tasks.json` 的两个运行任务**（让任务走 cmd 并切代码页，绕开 PowerShell）：

```jsonc
"command": "chcp 65001 >nul & ${fileDirname}/${fileBasenameNoExtension}.exe",
"options": { "shell": { "executable": "cmd.exe", "args": ["/d", "/c"] } }
```

- **撤销**：把这两处改回 `"command": "${fileDirname}/${fileBasenameNoExtension}.exe"`，删掉 `options.shell`
- ⚠️ `chcp 65001 >nul &` 这句**只在 cmd 里成立**（PowerShell 里 `&` 是调用运算符），所以强制走 cmd
- ⚠️ C/C++ 扩展会自动加一个 `C/C++: g++.exe 生成活动文件` 任务并抢走 `isDefault`。
  它没带 `-std=` 和 `-static`，编 `cpp17/` 及以后会失败、编出来也跑不起来。
  已把它设为 `isDefault: false`（保留任务本身，免得扩展反复生成）

**改动 2 — 两个 PowerShell profile**（**全局配置，不在仓库里**）：

| Shell | 路径 |
| --- | --- |
| Windows PowerShell 5.1 | `C:\Users\q1209\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` |
| PowerShell 7 | `C:\Users\q1209\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` |

两个文件内容相同，最后一行：

```powershell
[Console]::OutputEncoding = [Text.Encoding]::UTF8
```

- **撤销**：删掉那两个文件（2026-09-12 之前都不存在），或把那行注释掉
- ⚠️ **改完必须新开终端才生效** —— profile 只在 PowerShell 启动时执行一次
- ⚠️ 副作用：外部程序的输出一律按 UTF-8 解码。Windows 自带工具会回退成**英文**而不是乱码
  （`ipconfig` 的 `Windows IP 配置` → `Windows IP Configuration`；控制台代码页仍是 936，
  `chcp` 查得到，所以是语言回退不是编码错乱）；极少数只吐 GBK 的老工具反而可能乱

**42 个 `.cpp` 源码：一行都没改。**

### 自己诊断的三步

```bash
# 1) 看程序吐的字节对不对（"的" = E7 9A 84 就是正确的 UTF-8）
./xxx.exe | od -An -tx1

# 2) 看 PowerShell 的解码器设置（PowerShell 里敲）
[Console]::OutputEncoding.WebName        # gb2312 = 有问题   utf-8 = 已修好

# 3) 看控制台代码页
chcp                                     # 默认 936; 任务里 chcp 后会变 65001
```

判断口径：**字节本身是正确的 UTF-8 而显示是花的 → 解码端问题，不要去改程序代码。**

### 试过但没用的（别再走一遍）

| 做法 | 为什么没用 |
| --- | --- |
| `chcp 65001` 后再手工跑 exe | 改的是**控制台代码页**，改不动 PS 启动时缓存的解码器属性。实测 chcp 前后 PS 解出的码点一模一样；反而因为控制台变了、PS 仍按 GBK 写出去，乱码**多套一层** |
| 给 41 个 `.cpp` 加 `SetConsoleOutputCP(CP_UTF8)` | 同样是改控制台代码页，PS 的缓存属性照样不动，**修不好手工路径** |
| 编译加 `-fexec-charset=GBK`（让程序吐 GBK 去迎合终端） | 在 PowerShell/cmd 里有效（实测 41/41 编译通过，字节与 Python 一致），但 **Git Bash 是 UTF-8，会反过来弄坏**。没有一种编码能同时满足两边 |
| 把 profile 只写到 PS 5.1 的路径 | 本机 PS 5.1 和 PS 7.6.6 都装着，VSCode 启动哪个不确定。**两个都写**才盖得住 |

### 追加：「改用 `std::print` 不就行了？」——只对一半

C++23 的 `std::print` 确实是标准给的解法，但它**只覆盖"程序直接对终端说话"这一种情况**。
本机 g++ 15.2.0 的 `<print>` 头文件原文（`include/c++/15.2.0/print`）写得很清楚：

```cpp
// If stream refers to a terminal, write a native Unicode string to it.
if (auto __term = __open_terminal(__stream))
  { ... __write_to_terminal(__term, __out); ... }

// Otherwise just write the string to the file as vprint_nonunicode does.
if (std::fwrite(__out.data(), 1, __out.size(), __stream) != __out.size())
```

| 场景 | 走哪条路 | 结果 |
| --- | --- | --- |
| 双击 / cmd 窗口 / VSCode 任务（直连控制台） | `__write_to_terminal` → UTF-16 → `WriteConsoleW` | ✅ 不挑代码页 |
| **在 PowerShell 里跑**（PS 把 stdout 接进管道，此时 exe 看到的**不是终端**） | 退化成 `fwrite` 写原始 UTF-8 字节 | ❌ **照样被 PS 的 gb2312 搞乱** |
| 重定向到文件 | `fwrite` UTF-8 字节 | ✅ 文件是正确的 UTF-8 |

也就是说 `std::print` 修的是 `exe → 控制台` 这一段，**修不了 `PowerShell` 那一层**（而"中间隔着东西"恰恰是日常最常见的情况）：

```text
   exe                    PowerShell                   终端渲染层
    │                          │                             │
    │ ① 怎么写出去              │ ② 怎么重解、再写出去         │ ③ 怎么画
    │ std::print 管这段         │ profile 管这段               │ UTF-8, 改不了
```

**本机链接失败是缺一个参数，不是工具链缺陷**（2026-09-12 查明，修正了原记录的误判）：

```text
undefined reference to `std::__open_terminal(_iobuf*)'
undefined reference to `std::__write_to_terminal(void*, std::span<char, ...>)'
```

这两个符号在 **`D:/mingw64/lib/libstdc++exp.a`** 里（`nm` 查得到）。那是 libstdc++ 的
**实验库**，里面装着 `print.o` / `stacktrace.o` / `contract.o` / `text_encoding.o`，
以及旧的 `std::experimental::filesystem`。**链接时补上 `-lstdc++exp` 就好**：

```bash
g++ -std=c++23 -Wall -Wextra -O1 -g -pthread -static xxx.cpp -o xxx.exe -lstdc++exp
```

已实测：`std::println` 编译、链接、运行全部正常，配 `-static` 也可以。
**不需要更新 MinGW，也不需要换 MSVC/LLVM**；MSVC 17.8+ / LLVM 18+ 不用这个参数。

> 这条修正的意义：原记录写"属该 MinGW 发行版的构建缺陷"，会让人以为要换工具链。
> 实际上工具链是好的，只是 GCC 把 `<print>` 的终端支持放在了单独的库里。

顺带一个细节：该头文件开头就是 `#if !defined(_WIN32)` 分支，注释写着 *"For most targets we don't need to do anything special to write Unicode to a terminal"* —— **标准库自己把这件事标注成了 Windows 专属的麻烦**。

**批次统计**:

| 批次 | 内容 | 结果 |
| --- | --- | --- |
| 批次1 | cpp11 (01-10) + cpp14, 14 文件 | PASS=14 |
| 批次2+3 | cpp17/20/23, 17 文件 | 首轮 16/17；filesystem 改 -static 后全过 |
| 补充批次 | 待补强烈推荐特性, 10 文件 | 首轮 8/10；chrono/jthread 改 -static 后全过 |
| 增补 (2026-09-12) | cpp11/15 智能指针实战, 1 文件 | PASS，`-Wall -Wextra -O1` 下 0 警告（auto_ptr 段用 `#pragma GCC diagnostic` 屏蔽弃用警告） |
| **Windows 累计** | **42 个文件** | **全部编译通过并运行验证 PASS**（4 个文件有警告, 见上表） |
| **macOS 复测 (2026-09-21)** | **42 个文件** | **39 PASS / 3 编译失败**（缺失特性见上方「macOS 环境实测」）；通过的全部实际运行验证 |
