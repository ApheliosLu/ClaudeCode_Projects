# ============================================================================
# 01_py312.py  现代 Python 示例集 · 08_new 版本新特性
# 主题: Python 3.12 实装特性总览(type 语句/override/PEP 701/walk/match)
# 解决的问题(基础课):
#   基础课按 3.12 教学, 但 3.12 的"新语法糖"未必都覆盖到: 泛型要写
#   TypeVar、f-string 有引号限制、目录遍历要 os.walk 字符串……
#   本文件把 3.12 值得记的新写法集中过一遍(全部按本机 3.14.3 实测可跑)。
# 运行: python 01_py312.py
# ============================================================================

import sys

assert sys.version_info >= (3, 12), "本文件演示 3.12+ 特性, 请用 3.12 及以上运行"
# 这是什么: assert + sys.version_info —— 版本门槛断言: 在错误的解释器上
#           直接报错退出, 防止"拿 3.10 跑出莫名 SyntaxError"的迷惑现场。

# ---- 1. type 语句(PEP 695): 别名与泛型的新语法 ----
# 这是什么: type X = 类型 —— 3.12 起的类型别名语句: 给长类型起短名。
#           (3.12 及之前: 只能 TypeAlias 注解或直接复制长类型, 无专用语法。)
type IntList = list[int]                      # 别名: 之后 IntList ≡ list[int]
print("1) type 语句别名与泛型新语法:")
print("   type IntList = list[int] → 别名即类型本身:", IntList)

# 这是什么: 函数泛型 def f[T](x: T) -> T —— 3.12 起方括号内联声明类型变量。
#           (3.12 及之前: from typing import TypeVar; T = TypeVar("T") 两行
#           才能声明一个类型变量, 然后 def f(x: T) -> T。)
def first[T](items: list[T]) -> T:            # 3.12 泛型函数: 返回与入参同型
    return items[0]

class Box[T]:                                 # 3.12 泛型类: 类级类型变量
    def __init__(self, value: T):
        self.value = value

print("   first([10, 20, 30]) =", first([10, 20, 30]), type(first([10, 20, 30])).__name__)
print("   first(['a'])        =", first(["a"]), type(first(["a"])).__name__)
b = Box("hello")
print("   Box[str] 实例:", b.value, "   # 无需运行时类型检查, 语法层面标注")

# ---- 2. @override(typing): 声明"我在覆写父类" ----
from typing import override
# 这是什么: @override —— 给覆写方法打标: 告诉类型检查器"父类必须有同名方法",
#           父类方法被改名/删除时静态检查直接报错, 防止"以为覆写了其实没有"
#           的静默 bug。注意: 纯运行时无校验 —— 它只给 mypy/pyright 看。
class Base:
    def greet(self) -> str:
        return "Base 你好"

class Child(Base):
    @override                                # 若父类没有 greet, 检查器会标红
    def greet(self) -> str:
        return "Child 覆写: " + super().greet()

print("\n2) @override 覆写标注:")
print("   Child().greet():", Child().greet())
print("   (运行时无校验 —— 若父类没这方法, 只有静态检查器会报, 见注释)")

# ---- 3. PEP 701 多行/同引号 f-string(完整演示见 06_stdlib/06) ----
print("\n3) PEP 701 快速回顾(详见 06_stdlib/06_strings_re.py 第 3 节):")
d = {"a": 1}
print("   同引号嵌套 f\"{d[\"a\"]}\":", f"{d["a"]}")   # 3.12 前是 SyntaxError

# ---- 4. pathlib.Path.walk(对照 os.walk)——完整使用见 06_stdlib/01 ----
print("\n4) Path.walk(3.12+, 使用细节见 06_stdlib/01_pathlib.py):")
print("   在 3.12 前遍历目录只能 os.walk(字符串); 3.12 起 Path 自带 .walk():")
import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "src" / "mod").mkdir(parents=True)
    (root / "src" / "app.py").write_text("", encoding="utf-8")
    dirs = [d.relative_to(root) for d, _, _ in root.walk()]
    print("   遍历到的目录:", [str(x) for x in dirs])
print("   → 返回的是 Path 对象(旧 os.walk 只给字符串), 可直接继续链式调用")

# ---- 5. match-case 语句(PEP 634, 3.10 新增) ----
# 这是什么: match 值: case 模式: —— 结构模式匹配(3.10 新增, 3.12 完全可用):
#           比 if-elif 链更强的分支: 能按"结构/形状"匹配(解包、类型+变量绑定、
#           守卫条件), 解析命令/路由/JSON 形状的正规军。
def route(cmd: str) -> str:
    match cmd.split():                         # 对字符串分词结果做模式匹配
        case ["open", path]:                   # 恰好两个词, 且首词是 open
            return f"打开文件 {path}"
        case ["quit"] | ["exit"]:              # 或模式: 两种词都算退出
            return "再见!"
        case [action, *rest]:                  # 其余任意首词 + 尾巴
            return f"未知命令 {action}(剩余参数: {rest})"
        case _:                                # 兜底: 空输入等
            return "空命令"

print("\n5) match-case 结构模式匹配(3.10 新增):")
for cmd in ["open notes.md", "quit", "exit", "delete a b", ""]:
    print(f"   {cmd!r:16} → {route(cmd)}")
