# ============================================================================
# 03_py314.py  现代 Python 示例集 · 08_new 版本新特性
# 主题: Python 3.14 实装特性总览(t-strings/PEP 649/PEP 758/PEP 765)
# 解决的问题(基础课):
#   3.14 的玩法大变: 字符串多了个 t- 前缀、注解默认改成惰性求值、
#   两个老语法限制被解除。本文件按本机 3.14.3 逐条实测落笔。
#   ⚠ 运行本文件: 第一行输出是一条 SyntaxWarning —— 那是第 4 节演示,
#     它发生在"编译期", 天然先于一切运行输出(见第 4 节注释)。
# 运行: python 03_py314.py
# ============================================================================

import sys

assert sys.version_info >= (3, 14), "本文件演示 3.14 特性, 请用 3.14 及以上运行"
# stdout 行缓冲: 教学 print 与警告(stderr)顺序对位(同系列惯例)
sys.stdout.reconfigure(line_buffering=True)

# ---- 1. t-strings(PEP 750): 模板字符串, 得到的是"结构化模板" ----
# 这是什么: t"..." —— 3.14 新增的模板字符串前缀(类似 f-string 但更底层):
#           求值结果不是拼好的文本, 而是一个 Template 对象 —— 带着
#           文本骨架 .strings 和插值 .interpolations(每个插值含原表达式
#           文本与已求值的 .value)。适合做"先保存模板、稍后不同环境渲染"
#           /SQL 语句与参数分离/多语言文案这类场景。
#           (3.12 及之前: 没有 t-strings —— 同样需求只能 f-string 当场拼死,
#           或手写占位符模板再 replace, 拿不到结构化的插值清单。)
name, age = "阿黎", 23
tpl = t"用户 {name} 年龄 {age}"
print("1) t-strings(PEP 750): 结果是 Template 对象")
print("   tpl 类型:", type(tpl).__name__)
print("   文本骨架 strings  :", tpl.strings)
print("   插值清单(表达式+值):")
for iv in tpl.interpolations:
    print(f"     {iv.expression!r} → {iv.value!r}")
print("   .values 直接取值:", tpl.values)
# 实测注: 3.14.3 的 templatelib 尚在早期 —— str(tpl) 还未特殊化为合并文本
# (打印出来是构造样式)。自行渲染 = 骨架与值交错拼起来:
rendered = ""
for i, s in enumerate(tpl.strings):
    rendered += s
    if i < len(tpl.values):
        rendered += str(tpl.values[i])
print("   手写渲染结果:", rendered)

# ---- 2. PEP 649: 注解默认惰性求值(类前向引用不再需要 __future__) ----
# 这是什么: PEP 649 —— 3.14 起注解求值改为"访问 __annotations__ 时才算":
#           函数/类定义时不再立即求值注解。效果: "后定义先引用"直接合法,
#           且拿到的是真实类型对象(不是字符串)。
#           (3.12 及之前: 注解定义时立即求值 —— def g(x: Later) 在 Later
#           尚未定义时会 NameError; 绕法 = 把类定义提前, 或文件顶部
#           from __future__ import annotations 把注解"字符串化"(PEP 563),
#           代价是拿不到真实对象, isinstance 类检查要 eval 字符串。)
def build(x: Later) -> Later:      # Later 定义在下面 —— 3.14 直接合法
    return x

class Later:                       # 类定义在函数之后
    def __init__(self, v):
        self.v = v

print("\n2) PEP 649 惰性注解(类后置定义直接可用):")
ann = build.__annotations__
print("   build.__annotations__:", ann)
print("   'return' 是真实类型对象:", isinstance(ann["return"], type),
      "→", ann["return"].__name__)
print("   (PEP 563 字符串化方案下这里是字符串 'Later', 见注释对照)")

# ---- 3. PEP 758: except 不用括号也能列多类型 ----
# 这是什么: PEP 758 —— 3.14 恢复了"裸逗号"写法: except A, B: 与
#           except (A, B): 完全等价(早古 Python 曾有, 后被移除)。
#           新代码照旧写括号版也行 —— 只是语法枷锁少了一道。
print("\n3) PEP 758: except A, B(无括号, 3.14 实测可用):")
try:
    int("abc")
except ValueError, TypeError:                 # 无括号多类型 —— 3.14 起合法
    print("   捕获: except ValueError, TypeError 生效(与括号版等价)")

# ---- 4. PEP 765: finally 里 return/break/continue 不再被默许 ----
# 这是什么: PEP 765 —— finally 块里的 return/break/continue 会悄悄吞掉
#           try 里 pending 的 return/异常(控制流劫持), 极易出隐蔽 bug。
#           3.14 起发出 SyntaxWarning(实测 3.14.3 为 SyntaxWarning,
#           未来版本升级为 SyntaxError), 提醒你重构掉这种写法。
#   ⚠ 这条警告发生在编译期, 所以它排在文件所有输出之前 —— 你运行本文件
#     看到的第一行即它; 正因如此, 演示函数必须存在却不应被调用,
#     否则 finally 的 return 会把 try 的返回值吞掉。
def f_bad():
    try:
        return 1
    finally:
        return 2                      # 吞掉上面的 return 1(3.14 起警告)

print("\n4) PEP 765: finally 内 return 已被警告(见文件顶部第一条输出)")
print("   若调用 f_bad() 会得到", 2, "而不是 1 —— 控制流被 finally 劫持的现场")
print("   正确写法: 别在 finally 里 return; 清理代码用 try/finally 不加 return")
