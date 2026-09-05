# ============================================================================
# 02_exceptiongroup.py  现代 Python 示例集 · 07_errors 异常进阶
# 主题: ExceptionGroup —— 一次抛出一组异常, except* 按类型分治
# 解决的问题(基础课):
#   基础课的 except 一次只能接一个异常。但并发时代(见 04/05)一个任务
#   同时跑 100 个请求, 挂了 5 个 —— 只抛第一个失败, 其余 4 个的排查信息
#   就丢了。ExceptionGroup 让你"把一组异常打包抛", 处理端还能按类型
#   分批接走。
# 这是什么: ExceptionGroup —— 3.11 新增((3.11 新增, 3.12 已有)): 一个容器
#           异常, 里面装着多个异常(可嵌套)。配套语法 except*(带星号):
#           像 except 一样按类型匹配, 但一次处理组里"所有同类成员"。
# 运行: python 02_exceptiongroup.py
# ============================================================================

# ---- 1. 构造异常组 + except* 按类型分治 ----
# 这是什么: ExceptionGroup("说明文字", [异常列表]) —— 组名是给人看的总述;
#           成员可以是任何异常(也可再套 ExceptionGroup)。
eg = ExceptionGroup("批量导入失败", [
    ValueError("第 2 行: 价格不是数字"),
    TypeError("第 5 行: 缺少必填字段"),
    ValueError("第 8 行: 数量为负"),
])
print("1) except* 按类型分治:")
try:
    raise eg
except* ValueError as vg:                       # 星号: 接走"所有 ValueError 成员"
    print(f"   [ValueError 组] 共 {len(vg.exceptions)} 个:")
    for e in vg.exceptions:
        print(f"     - {e}")
except* TypeError as tg:
    print(f"   [TypeError 组] 共 {len(tg.exceptions)} 个:",
          [str(e) for e in tg.exceptions])
print("   → 三类成员各归各家处理; 组内每类都有人接, 整体才算处理完")

# ---- 2. 嵌套组: 自动穿透外壳, 返回的是"保留壳的子组" ----
# 这是什么: except* 面对嵌套组会自动"穿透": 匹配叶子异常时把内层挑出来,
#           但返回给你的仍是"保留了外层壳结构的子组"(壳名会带上
#           (N sub-exception)); 想拿到平铺的叶子, 得自己递归拆一层。
nested = ExceptionGroup("任务组", [
    ExceptionGroup("下载阶段", [ValueError("图 1 下载超时"), ValueError("图 2 超时")]),
    ExceptionGroup("校验阶段", [TypeError("格式不合法")]),
])

def flatten(g):
    """递归把异常组拆成叶子异常列表(教学小工具)"""
    for e in g.exceptions:
        yield from flatten(e) if isinstance(e, ExceptionGroup) else (e,)

print("\n2) 嵌套组自动穿透(返回子组, 叶子需自拆):")
try:
    raise nested
except* ValueError as vg:
    print("   ValueError 子组:", vg)                       # 还是带壳的组
    print("   递归拆出叶子     :", [str(e) for e in flatten(vg)])
except* TypeError as tg:
    print("   TypeError 子组  :", [str(e) for e in flatten(tg)])

# ---- 3. 没人接的成员会怎样: 逃逸! ----
# 这是什么: 若组里某种类型没有对应 except* 接 —— 处理完后剩下的成员会
#           "原样抛出"(组名自动改成"未处理子异常")。所以要么把所有类型
#           都 except* 到, 要么最后留一个 except Exception 兜底整组。
print("\n3) 未接走的成员会继续抛(演示后接住):")
leftover = ExceptionGroup("混合", [ValueError("有人接"), RuntimeError("没人接")])
try:
    try:
        raise leftover
    except* ValueError as vg:
        print("   只接了 ValueError:", [str(e) for e in vg.exceptions])
    # RuntimeError 没人接 → 这里会重新抛出(注意没走 except*, 是普通 try 的 except)
except Exception as whole:
    print(f"   RuntimeError 逃逸, 被外层普通 except 接住: {whole}")
    print("   (组名自动变成 '(1 sub-exception)')—— 提醒你还有异常未分诊")

# ---- 4. 实战视角: asyncio.TaskGroup 与它什么关系 ----
# 这是什么: asyncio.TaskGroup(3.11+, 见 05_async/02) —— 组里任何一个任务
#           异常, 会先取消其余任务, 然后把所有失败聚合成一个
#           ExceptionGroup 抛给你 —— 你在 except* 里按类型分诊即可。
#           所以"并发任务批量失败"现在有标准答案:
#           收集端 = TaskGroup, 报错端 = ExceptionGroup, 处理端 = except*。
print("\n4) 实战衔接:")
print("   asyncio.TaskGroup 抛出的就是 ExceptionGroup —— 处理写法同本文件")
print("   (完整演示见 05_async/02_asyncio_tasks.py 的 TaskGroup 小节)")
