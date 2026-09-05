# ============================================================================
# 01_pathlib.py  现代 Python 示例集 · 06_stdlib 标准库工具箱
# 主题: pathlib —— 用 Path 对象操作路径, 告别字符串拼路径
# 解决的问题(基础课):
#   基础课里拼路径用的是 os.path.join(dir, "a", "b") + 字符串;
#   Windows 用反斜杠 \、Linux/mac 用正斜杠 /, 字符串拼起来又长又易错。
#   pathlib 把路径做成"对象", 用 / 运算符拼接, 天然跨平台。
# 这是什么: pathlib.Path —— 一个"路径对象": 既是字符串、又能当文件系统
#           的句柄用(可以 .exists()/.mkdir()/.read_text())。3.4 起标准库,
#           官方现在推荐一律用它(替代 os.path 字符串函数)。
# 运行: python 01_pathlib.py
# ============================================================================

import tempfile
from pathlib import Path

# ---- 1. 构造路径对象: 对照表, 以后见 os.path 就换成这行 ----
# 这是什么: Path("a") / "b" —— / 运算符拼接路径段(自动按当前系统补分隔符),
#           os.path.join 的现代替代品, 一次能接多个段。
print("1) 路径对象与 os.path 对照表:")
p = Path("docs") / "report" / "2026.md"
print("   拼接结果      :", p, "   # Windows 下自动用反斜杠显示")
print("   os.path 旧写法: os.path.join('docs', 'report', '2026.md')")
print("   文件后缀 suffix:", p.suffix, "    # .md; 等价旧写法 os.path.splitext()[1]")
print("   文件名 name    :", p.name)          # 最后一段: 2026.md
print("   主名 stem      :", p.stem)          # 去掉后缀: 2026
print("   父目录 parent  :", p.parent)

# ---- 2. cwd / home / 绝对化 ----
print("\n2) 常用起点路径:")
print("   当前工作目录  :", Path.cwd())
print("   用户主目录    :", Path.home())
print("   相对转绝对    :", p.resolve())

# ---- 3. 实战: 临时目录里建一棵树, 再遍历它 ----
# 这是什么: tempfile.TemporaryDirectory —— 用完自动删除的临时目录
#           (上下文管理器, 退出 with 即清理; 免去手动 rm -rf 的残留烦恼)。
print("\n3) 在临时目录里建目录树并用 Path 遍历:")
with tempfile.TemporaryDirectory(prefix="pathlib_demo_") as tmp:
    root = Path(tmp)                      # 临时目录的 Path 形式
    (root / "src" / "utils").mkdir(parents=True, exist_ok=True)   # 递归建目录
    (root / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (root / "src" / "utils" / "helper.py").write_text("x = 1\n", encoding="utf-8")
    (root / "README.md").write_text("# demo\n", encoding="utf-8")
    # 这是什么: mkdir(parents=True, exist_ok=True) —— parents 递归创建中间层,
    #           exist_ok 目录已存在时不报错(否则 FileExistsError)。
    # 这是什么: write_text/read_text —— 一步读写文本文件, 替代
    #           open()+write()+close() 三连(带 encoding 参数写清楚编码)。

    print("   --- glob('*.py') 只找本层 .py ---")
    for f in sorted(root.glob("*.py")):
        print("   ", f.name)                        # src 下的 main.py 不会被 glob 到
    print("   --- rglob('*.py') 递归找全部 .py ---")
    for f in sorted(root.rglob("*.py")):
        print("   ", f.relative_to(root))           # relative_to: 显示相对路径
    # 这是什么: glob("模式") 按模式找"这一层"的文件(类似 shell 通配);
    #           rglob 递归子目录找全部; 都返回 Path, 不是裸字符串。

    print("   --- Path.walk() (3.12+) ---")
    for dirpath, dirnames, filenames in root.walk():
        rel = dirpath.relative_to(root)
        print(f"   目录 {'.' if str(rel)=='.' else rel}: {sorted(filenames)}")
    # 这是什么: Path.walk() —— 3.12 新增, 递归遍历生成 (目录, 子目录名列表, 文件名列表)
    #           三元组, 逐个目录往下走; (3.12 及之前: 用 os.walk(root) 得到的是
    #           字符串路径, 还要自己再包 Path)。

    print("   --- stat / is_file / exists ---")
    main = root / "src" / "main.py"
    print("   is_file():", main.is_file(), "  exists():", main.exists())
    print("   文件大小    :", main.stat().st_size, "字节")
    # 这是什么: stat() —— 文件系统元信息(大小/修改时间/权限), 类似 shell 的 ls -l。

# 退出 with: 临时目录已自动删除
print("\n   临时目录已自动清理 ✔")

# ---- 4. __file__: 定位"脚本自己"的路径 ----
# 这是什么: __file__ —— Python 为每个模块内置的变量, 存模块自身文件路径
#           (命令行直接跑脚本时它就是脚本 .py 的路径)。包里的代码常用它
#           定位"资源文件与代码的相对位置", 比依赖 cwd 稳。
here = Path(__file__).resolve()
print("\n4) 本脚本 __file__ 定位自身:")
print("   绝对路径  :", here)
print("   文件名    :", here.name, "   # 带 .py 后缀 —— 演示点")
print("   所在目录  :", here.parent)
