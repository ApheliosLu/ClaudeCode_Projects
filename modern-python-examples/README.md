# 现代 Python 示例集 (Modern Python Examples)

面向**已学完 Python 基础课(按 3.12 教学)、想进阶到工程实践的读者**。
34 个文件全部**可独立运行、纯标准库零依赖**,头部注释写明"解决什么基础课没讲的问题 / 旧写法对照"。

学习背景衔接:基础课主线是语法、面向对象与简单脚本。本套示例补齐:
数据模型与元编程(01)、迭代与惰性求值(02)、类型注解体系(03)、并发与异步(04/05)、
标准库工具箱(06)、异常进阶(07)、3.12 → 3.14 新特性(08)、工程工具(09)。

## 版本现状 (2026-09 视角, 本机 Python 3.14.3 实测)

| 版本 | 状态 | 本套示例的建议 |
| --- | --- | --- |
| 3.12 | 稳定主流, 基础课教学版 | 代码基线: 所有文件保证 3.12+ 可跑 |
| 3.13 | 稳定, 性能与类型系统增强 | 特性总览见 `08_new/02_py313.py` |
| 3.14 | **当前最新稳定**, 模板字符串/惰性注解落地 | 特性总览见 `08_new/03_py314.py`, 新增处均有 `(3.12 及之前: …)` 对照注释 |

3.12 与 3.14 的写法差异速查见文末对照表。本机实测 `3.14.3`(Miniforge py314 环境)。

## 目录结构 (34 个文件全部完成并逐文件运行验证 ✅)

```text
modern-python-examples/
├── README.md
├── .vscode/         # VSCode 配置: tasks/launch/settings 三件(见"运行方式")
├── 01_lang/         # 6 个 —— 语言核心: 数据模型/装饰器/上下文管理器/描述符/元类/闭包
├── 02_generator/    # 3 个 —— 迭代协议/生成器/itertools
├── 03_typing/       # 3 个 —— 注解/泛型与 Protocol/数据建模(dataclass+TypedDict+Enum)
├── 04_concurrency/  # 3 个 —— GIL 与线程/多进程/futures
├── 05_async/        # 3 个 —— 协程与事件循环/任务编排/何时用异步决策指南
├── 06_stdlib/       # 8 个 —— pathlib/logging/collections/functools/datetime/字符串与正则/subprocess/序列化
├── 07_errors/       # 2 个 —— 异常链与自定义体系/ExceptionGroup
├── 08_new/          # 3 个 —— 3.12 特性/3.13 特性/3.14 特性(逐条实测)
└── 09_tools/        # 3 个 —— unittest 与 mock/包与 venv/调试与性能
    └── demo_pkg/    # 教学脚手架(2 个支持文件, 不属于 34 个交付示例): 02 的包导入演示对象
```

## 注释里的"运行输出"约定

每个示例文件的 print 语句旁都写着**实际运行输出**: 行尾 `# → 输出内容` 即该行打印的结果;
输出较长或一次输出多行时, 改用紧随其后的块注释(`# 输出:` 起头):

```python
print("1) str(p)  =", str(p))          # 走 __str__  → 1) str(p)  = 点(1, 2)

for word in Words("hello python world"):
    print("   -", word)
    # 输出:
    #    - hello
    #    - python
    #    - world
```

说明: 计时/随机数/时间戳/绝对路径这类每次都会变的值, 取的是本机某次运行的实测值,
并在注释里标明"随机器浮动"之类; traceback 的行号会随注释增删而变化。
全部输出在 Python 3.14.3 + `PYTHONUTF8=1` 下采集(见"中文乱码怎么办")。

## 交付一览 (34 文件: 主题与演示要点)

| 文件 | 主题 | 演示要点 |
| --- | --- | --- |
| `01_lang/01_data_model.py` | 数据模型协议 | `__repr__`/`__str__`、`__eq__` 后 `__hash__` 变 None 的坑、`__bool__`/`__len__`、`__getitem__`(切片)、`__iter__`、`__call__` |
| `01_lang/02_decorators.py` | 装饰器 | 裸语法 `f = deco(f)`、`wraps` 保 `__name__`、参数化装饰器、装饰类、`@staticmethod/@classmethod` 对照 |
| `01_lang/03_context_managers.py` | 上下文管理器 | `with` 协议、手写类、`@contextmanager`+yield、`ExitStack` 动态多资源 |
| `01_lang/04_descriptors_slots.py` | 描述符与 `__slots__` | property 即描述符、`__get__/__set__` 协议、`__slots__` 省内存对比、防越界校验描述符 |
| `01_lang/05_metaclass_abc.py` | 元类与抽象基类 | `type` 造类、元类拦截 `__new__`、`ABC`+`@abstractmethod`(类比 C++ 纯虚)、YAGNI 注释 |
| `01_lang/06_closures.py` | 闭包 | `nonlocal`、计数器/延迟求值、函数对象挂属性、循环闭包经典坑+默认参数规避 |
| `02_generator/01_iterators.py` | 迭代协议 | `for` = `iter()+next()`、手写迭代器、`iter(callable, sentinel)`、一次性消费、`reversed` |
| `02_generator/02_generators.py` | 生成器 | yield 暂停现场、生成器表达式、`send/throw/close`、`yield from`、无限生成器截取、内存对比 |
| `02_generator/03_itertools.py` | itertools 组合 | `count/cycle/repeat+islice`、`chain/tee/groupby`(先 sort)、`product/permutations/combinations`、`pairwise` |
| `03_typing/01_annotations.py` | 注解基础 | 注解只是元数据(运行时零强制)、`int \| None`(PEP 604)、`Literal/Any/TypeAlias`、`__annotations__` 读取 |
| `03_typing/02_generics_protocol.py` | 泛型与 Protocol | `TypeVar+Generic` 自定义容器、`Protocol` 结构化类型、`TypeGuard`、`ParamSpec` |
| `03_typing/03_models.py` | 数据建模四件套 | dataclass 全貌、可变默认值坑、`frozen/slots`、NamedTuple、TypedDict、Enum/StrEnum |
| `04_concurrency/01_gil_threads.py` | GIL 与线程 | `_is_gil_enabled()` 探测、无锁计数竞争(实测构造)、Lock/RLock/Event/Queue、IO 线程 CPU 进程 |
| `04_concurrency/02_multiprocessing.py` | 多进程 | Process/join、Pool 计时(实测 2.9x)、`Value/Array+Lock` 竞争实测、Queue、Windows spawn 保护 |
| `04_concurrency/03_futures.py` | concurrent.futures | Thread/Process PoolExecutor 同接口、`submit+Future`、`as_completed` 完成序、异常跨进程重抛 |
| `05_async/01_coroutines.py` | 协程与事件循环 | `async/await`、`gather` 并发(0.51s vs 1.01s)、`asyncio.sleep` vs `time.sleep`、never-awaited 警告 |
| `05_async/02_asyncio_tasks.py` | 任务编排 | `create_task/wait_for` 超时、`to_thread`、`asyncio.Queue`、`TaskGroup` 取消聚合 |
| `05_async/03_async_guide.py` | 何时用异步 | 决策表、阻塞库反模式、`asyncio.Lock` vs `threading.Lock` 死锁坑、伪异步 CPU 演示 |
| `06_stdlib/01_pathlib.py` | pathlib | Path 对象与 os.path 对照表、`/` 拼接、`glob/rglob/walk`、`mkdir(parents=True)`、`__file__` 定位 |
| `06_stdlib/02_logging.py` | logging | 五级别与过滤、`getLogger` 分类、RotatingFileHandler 轮转(实测 .1/.2/.3)、`exception` 记栈 |
| `06_stdlib/03_collections.py` | collections | Counter 词频、defaultdict 免 if、deque 环形缓冲、namedtuple、ChainMap 配置覆盖零复制 |
| `06_stdlib/04_functools.py` | functools | partial、`@cache` 记忆化(fib(37) 实测 2.02s vs 0.047ms)、singledispatch、reduce、cmp_to_key、wraps |
| `06_stdlib/05_datetime.py` | 时间与时区 | date/time/datetime、zoneinfo 三时区同刻(实测 +0/+8/+6)、strftime/strptime、timedelta、fromisoformat |
| `06_stdlib/06_strings_re.py` | f-string 与正则 | 格式说明符、`{x=}`、PEP 701 同引号/折行、r 前缀 `\n` 对比、命名分组、sub 打码 |
| `06_stdlib/07_subprocess.py` | 子进程 | `run+capture_output`、check=True、Popen+communicate 喂 stdin、env 注入、shell 注入红线 |
| `06_stdlib/08_serialize.py` | 序列化与安全 | json round-trip、`ensure_ascii=False`、default 钩子、pickle 安全红线、copy 深浅对比、shelve |
| `07_errors/01_exception_chain.py` | 异常链与体系 | `raise from` 与 `__cause__`、`from None`、自定义 AppError 体系、`except (A, B)` |
| `07_errors/02_exceptiongroup.py` | 异常组 | ExceptionGroup 构造、`except*` 分治、嵌套自动穿透(实测返回子组)、未接成员逃逸、TaskGroup 衔接 |
| `08_new/01_py312.py` | 3.12 特性 | `type` 语句/PEP 695 泛型、`@override`、PEP 701、Path.walk、**match-case**(3.10) |
| `08_new/02_py313.py` | 3.13 特性 | GIL 探测、错误消息拼写建议(实测在 traceback 层)、TypeIs/ReadOnly、dbm.sqlite3/JIT 背景 |
| `08_new/03_py314.py` | 3.14 特性 | t-strings 结构(实测 API)、PEP 649 惰性注解、PEP 758 except 无括号、PEP 765 finally 警告 |
| `09_tools/01_unittest_mock.py` | 标准库测试 | TestCase/setUp、assertRaises、MagicMock 断言、patch 顶替外部调用(自检测试 6 用例 OK) |
| `09_tools/02_packages_venv.py` | 包与 venv | demo_pkg 导入、`__package__`/`-m` 机制、sys.prefix 判 venv、操作序列注释 |
| `09_tools/03_debug_perf.py` | 调试与性能 | timeit、join vs `+=`(实测 118x)、推导 vs for(实测 ~1.1x)、cProfile 热点表 |

## 学习路线

按域顺序学习, 前域是后域的地基:

```text
01_lang(对象机制) → 02_generator(迭代/惰性) → 03_typing(注解体系)
→ 04_concurrency(线程/进程) → 05_async(异步) → 06_stdlib(工具箱)
→ 07_errors(异常进阶) → 08_new(版本特性收尾) → 09_tools(工程化)
```

- **01 → 02**:02 依赖 01 的 `__iter__` 数据模型理解迭代协议。
- **01/02 → 03**:`Generic[T]` 等注解语法基于已学的容器概念。
- **03 → 04 → 05**:类型标注让并发代码自文档化;04 的"IO 多线程"为 05 的
  asyncio 铺垫(何时该用异步见 `05_async/03` 决策表)。
- **05 → 07**:TaskGroup 抛的正是 07 的 ExceptionGroup。
- **06/07 → 09**:unittest/patch 常配 logging 与异常体系做测试;性能工具
  回头量化 04 的并发收益。
- 每域目录内按文件编号顺序读;每个文件可独立运行, 输出即演示结论。
- 基础课未覆盖的现代语法 **match-case**(3.10 起, 3.12 完全可用)并入
  `08_new/01_py312.py` 第 5 节, 读 08 时一并掌握。

## 运行方式

零第三方依赖 -- 不用建虚拟环境, 不用 `pip install`。
本机实测环境: **Miniforge py314 -> Python 3.14.3** (即 PATH 上的 `python`)。

### 命令行 (任何终端)

```bash
# 任意单文件(在 modern-python-examples/ 下, Windows Git Bash)
python 01_lang/01_data_model.py

# 整域核验
cd 06_stdlib && for f in *.py; do python "$f"; done
```

示例文件可能写临时目录, 均用完自动清理。

### VSCode 里 (配置已就绪)

`.vscode/` 下三个文件已配好, 键位跟 C++ 示例集保持一致:

| 操作 | 效果 |
| --- | --- |
| **`Ctrl+Shift+B`** | 运行当前 `.py` (★ 日常只记这一个) |
| **F5** | 断点调试当前 `.py` |
| 右上角 **▶** | 运行, 等价于 Ctrl+Shift+B |

> ⚠️ 跟 C++ 一样: 任务作用于**当前焦点所在的编辑器**。焦点停在 `README.md` 上按快捷键,
> 它会去跑 README.md。按之前先点一下 `.py` 的编辑区。

三个文件各管什么:

| 文件 | 作用 |
| --- | --- |
| `tasks.json` | 定义"运行当前文件"任务, 被 `Ctrl+Shift+B` 触发 |
| `launch.json` | F5 调试配置。`console` 特意设成 `integratedTerminal`, 默认的调试控制台里 `input()` 不可用、中文也容易乱码 |
| `settings.json` | 锁定解释器为 py314 + 集成终端里带上 `PYTHONUTF8=1` |

### 为什么 Python 不需要 C++ 那么复杂的配置

C++ 那边有三个任务(只编译 / 编译并运行 / 只运行), Python 只有一个, 差别在**构建步骤**:

| | C++ | Python |
| --- | --- | --- |
| 源文件是 | 给编译器读的 | 给解释器读的 |
| 到能跑需要 | ① `g++` 编译链接 -> ② 运行 exe, **两步** | `python f.py` **一步到位** |
| 中间产物 | `.exe`(得管它在哪、是不是最新的) | 无 |
| 需要用户拍板的自由参数 | 编译器、`-std=` 版本、`-O` 级别、链接哪些库、输出名……**不写下来 VSCode 猜不到** | 几乎只有"用哪个解释器", 而 Python 扩展已经管了 |

一句话: **`tasks.json` 的存在前提是"从源码到可执行有需要用户拍板的参数"。** C++ 有, 所以必须有;
Python 没有 -- `python 文件名` 已经短到不需要再包一层。同理, VSCode 的 Python 扩展能自动提供
运行按钮和 `Python File` 调试配置, 而 C/C++ 扩展给不了(它没法猜你怎么编译)。

### 中文乱码怎么办

只有一种情况会乱码: **输出被重定向或走管道**时, Python 检测到 stdout 不是真控制台,
会退回系统区域编码 `cp936`(GBK), 中文就糊了。

| 场景 | 结果 |
| --- | --- |
| VSCode 集成终端里手动 `python f.py` | ✅ 真控制台, 走 UTF-8 通道, 正常显示 |
| `python f.py > out.txt`、`\| head`、被别的工具抓输出 | ⚠️ 走 GBK, 乱码 |

遇到就加环境变量: `PYTHONUTF8=1 python 文件.py`(上面 `settings.json` 里已经给集成终端配好了)。

## 对照速查: 3.12 → 3.14 关键差异 (本机 3.14.3 实测)

| 特性 | 版本 | 3.12 及之前 | 3.14 实测行为(差异) | 示例文件 |
| --- | --- | --- | --- | --- |
| `type` 语句 (PEP 695) | 3.12 | 无别名语法, 泛型要 `TypeVar` 两行 | `type A = list[int]`、`def f[T]` 内联泛型 | 08_new/01 |
| f-string 引号/折行 (PEP 701) | 3.12 | `f"{d['k']}"` 被迫错开引号; 表达式不能折行 | 同引号嵌套与跨行表达式合法 | 06_stdlib/06, 08_new/01 |
| `typing.override` | 3.12 | 无(写注释提醒) | 覆写标注, 检查器校验父类存在 | 08_new/01 |
| `Path.walk()` | 3.12 | 只有 `os.walk`(返回字符串) | Path 自带遍历, 产出 Path 对象 | 06_stdlib/01, 08_new/01 |
| match-case (PEP 634) | 3.10 | if-elif 链 | 结构模式匹配(解包/或/守卫) | 08_new/01 |
| `zip(strict=)` | 3.10 | 不等长静默截断 | 严格模式抛 ValueError | 一句话收录, 未单列文件 |
| `itertools.pairwise` | 3.10 | 手写 zip(x, x[1:]) | 相邻对一步到位 | 02_generator/03 |
| StrEnum | 3.11 | str + Enum 双继承绕行 | `class X(StrEnum)` 自带 str 行为 | 03_typing/03 |
| `ExceptionGroup` + `except*` | 3.11 | 一次只能抛/接一个异常 | 一组异常按类型分治; 嵌套自动穿透 | 07_errors/02 |
| `asyncio.TaskGroup` | 3.11 | `ensure_future + gather` | 组内失败取消其余并聚合成 ExceptionGroup | 05_async/02 |
| `tomllib` | 3.11 | 无标准库 TOML 解析 | `tomllib.load` 读配置文件 | 一句话收录, 未单列文件 |
| `sys._is_gil_enabled()` | 3.13 | 无(自由线程不存在) | True=默认 GIL 构建, False=自由线程 | 04/01, 08_new/02 |
| `typing.TypeIs` | 3.13 | 只有 TypeGuard(窄化粗) | 精确到子类型的窄化断言 | 08_new/02 |
| `TypedDict` 只读字段 | 3.13 | 无只读概念 | `ReadOnly[...]` 标注禁写 | 08_new/02 |
| 错误消息增强 | 3.10-3.13 | 简单文本 | NameError 等带拼写建议(实测: traceback 层附加) | 08_new/02 |
| t-strings (PEP 750) | 3.14 | 只能 f-string 当场拼死 | `t"..."` 得结构化 Template(strings+interpolations); 实测 3.14.3 `str()` 未特殊化, 需自行渲染 | 08_new/03 |
| PEP 649 惰性注解 | 3.14 | 立即求值需 `__future__` 字符串化 (PEP 563) | 默认惰性, 类后置定义合法且注解为真实类型对象 | 08_new/03 |
| `except A, B:` (PEP 758) | 3.14 | 必须括号 | 无括号多类型恢复合法 | 08_new/03 |
| `finally` 内 `return/break/continue` (PEP 765) | 3.14 | 静默放行(吞返回值) | 编译期 SyntaxWarning(实测), 未来转错误 | 08_new/03 |

> 版本注释惯例: 各文件用 `(3.12 及之前: …)` 标注行为差异; `08_new` 三个
> 文件的探测结论均以本机 3.14.3 实测为准并写入文件头注释。

## 验证与问题记录 (2026-09-05, 全部实测)

| 域 | 文件数 | 运行核验 | 备注 |
| --- | --- | --- | --- |
| 01_lang | 6 | ✅ 全部通过(2026-09-04 审查) | 无 |
| 02_generator | 3 | ✅ 全部通过 | 组合数数学核对一致 |
| 03_typing | 3 | ✅ 全部通过 | 可变默认值坑输出符合预期 |
| 04_concurrency | 3 | ✅ 全过 | 竞争实测构造见 PLAN.md(勿回改注释) |
| 05_async | 3 | ✅ 全过(2026-09-05 收尾) | never-awaited 警告为故意演示 |
| 06_stdlib | 8 | ✅ 全过, 无残留文件 | 轮转 .1/.2/.3 正确 |
| 07_errors | 2 | ✅ 全过 | `except*` 返回子组实测 |
| 08_new | 3 | ✅ 全过 | 03 的 SyntaxWarning 为 PEP 765 演示(文件头有预告) |
| 09_tools | 3 | ✅ 全过(6 tests OK) | demo_pkg 脚手架保留; `__pycache__` 已清理 |

**探测结论(08_new 写文件前逐条 `python -c` 实测)**:PEP 695 `type` 可用;
`typing.override` 可用;`Path.walk` 存在;`_is_gil_enabled` True(默认 GIL 构建);
t-strings 得 `string.templatelib.Template`;PEP 649 注解为真实类型对象;
PEP 758 无括号 `except A, B` 可用;PEP 765 实测为 SyntaxWarning;TypeIs/ReadOnly 可导入。

**实测发现并已按实测修正的"文档预期偏差"**:

| 主题 | 文档/直觉预期 | 3.14.3 实测 | 处理 |
| --- | --- | --- | --- |
| datetime 判 aware | 有 `isaware()` 方法 | 无此方法 | 改用 `.tzinfo is not None` |
| NameError 拼写建议 | `str(e)` 含建议 | 建议由 traceback 打印时附加 | 演示用 `traceback.print_exc()` |
| `except*` 嵌套展平 | 拿到平铺叶子 | 返回保留壳的子组 | 文件内 flatten 工具递归拆 |
| t-string `str(Template)` | 得合并文本 | 3.14.3 未特殊化 | 手写渲染循环演示 |
| for+append vs 推导 | 差距明显 | 3.11+ 特化后仅 ~1.1 倍 | 注释改为可读性论点 |
| 线程竞争 `counter += 1` | 无锁必丢 | 3.13+ 切换点不在三步间, 零损失 | 04/01 用 sleep(0) 构造必现 |

## 读完之后的下一步 (一句话指引)

| 工具 | 一句话 |
| --- | --- |
| pytest | 把 09_tools 的 unittest 换成 pytest(更少的样板, 插件生态) |
| ruff | 现代 lint + format 一体, `pip install ruff` 后替代手写风格纠结 |
| mypy / pyright | 让 03_typing 的注解真正生效(CI 里把关类型) |
| uv | 替代 pip+venv 的现代包管理(锁文件/超快解析) |
| FastAPI | 把 async 学以致用: 用 `async def` 写接口, 数据库查询交 `to_thread` |
| Docker | 让"本机能跑"变成"哪都能跑": 镜像里固定 Python 版本与依赖 |

---

姊妹篇: 同仓库的 `modern-cpp-examples/`(现代 C++ 11→23 示例集)。
两套的设计意图一致 —— 把课程旧写法映射到业界现行推荐写法。
