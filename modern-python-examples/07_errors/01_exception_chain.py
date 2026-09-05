# ============================================================================
# 01_exception_chain.py  现代 Python 示例集 · 07_errors 异常进阶
# 主题: 异常链(raise from)与自定义异常体系 —— 让"哪里炸了"层层可追溯
# 解决的问题(基础课):
#   基础课只学了 try/except/finally 的基本用法。真实工程里异常问题有三个:
#   ① 底层报错被上层"二次包装"后, 原始原因丢了(只见表面不见病根);
#   ② 每个模块都 try: raise Exception("出错了") —— 一堆裸 Exception,
#      无法按错误类型分类处理;
#   ③ assert 和 raise 混用, 分不清各自职责。
# 运行: python 01_exception_chain.py
# ============================================================================

import logging
import sys

# stdout 行缓冲 + 日志走 stdout: 保证教学 print 与日志输出顺序对位(同 06/02)
sys.stdout.reconfigure(line_buffering=True)
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(levelname)s:%(name)s:%(message)s")

# ---- 1. 隐式异常上下文 vs 显式 raise ... from ... ----
# 这是什么: 异常链 —— 一个异常在另一个异常的处理过程中产生时, Python 自动
#           把它们串成链(打印时显示 "During handling of ... another exception")。
#           显式写法 raise 新异常 from 旧异常 则显示 "The above exception was
#           the direct cause" —— 语义更明确: 新异常是旧异常的"直接后果"。
def fetch_user(user_id):
    # 模拟: 数据库层抛 KeyError(底层细节)
    raise KeyError(f"user {user_id} 不存在于缓存")

def get_profile(user_id):
    try:
        fetch_user(user_id)
    except KeyError as e:
        # 业务层不适合让 KeyError 裸奔出去 —— 包装成业务异常并串上原因
        raise ValueError(f"获取用户 {user_id} 资料失败") from e

print("1) raise ... from ... 显式链(原因可见):")
try:
    get_profile(7)
except ValueError as e:
    print("   捕获到包装层 ValueError:", e)
    # 这是什么: 异常对象.__cause__ —— 链的编程入口: 拿到 from 指定的原始异常
    #           (日志/监控系统靠它归档"根本原因"; traceback 也会显示
    #           "The above exception was the direct cause")。
    print("   e.__cause__ 原始原因:", e.__cause__)
print("   → __cause__ 串起病根; 完整链式 traceback 见第 5 节输出")

# ---- 2. from None: 主动剪断上下文 ----
# 这是什么: raise ... from None —— 抑制隐式上下文: 有些"包装"是纯粹的策略
#           (例如把第三方库的细节错误换成对用户友好的提示), 不打算展示原始
#           异常 —— from None 明确告诉解释器"别自动接上下文", 输出干净。
def parse_conf(text):
    try:
        return int(text)
    except ValueError as e:
        # 配置解析失败对用户只需要一句话, 细节(ValueError)不必外泄
        raise RuntimeError(f"配置文件第 3 行不是数字: {text!r}") from None

print("\n2) from None 剪断上下文:")
try:
    parse_conf("abc")
except RuntimeError as e:
    print("   只显示包装后的异常:", e)
print("   ↑ traceback 只有 RuntimeError 一层(ValueError 被抑制), 输出干净")

# ---- 3. 自定义异常体系: 业务按类型分类处理 ----
# 这是什么: 自定义异常 —— 从 Exception 派生自己的异常类(惯例后缀 Error)。
#           业务层惯例是建"自己的基类"(AppError), 再子类化细分 ——
#           捕获时只需 except AppError 就能一把接住所有业务错误;
#           而每个具体类型(NotFoundError 等)还能单独处理/单独给 HTTP 状态码。
class AppError(Exception):
    """本应用所有业务错误的共同祖先: 捕获它 = 捕获全部业务错误"""

class NotFoundError(AppError):
    """资源不存在(对应 HTTP 404)"""

class PermissionDeniedError(AppError):
    """没有权限(对应 HTTP 403)"""

def load_doc(doc_id, user):
    if user != "admin":
        raise PermissionDeniedError(f"{user} 无权限读取文档 {doc_id}")
    if doc_id > 100:
        raise NotFoundError(f"文档 {doc_id} 不存在")
    return f"文档{doc_id}内容"

print("\n3) 自定义异常体系(按类型分诊):")
for user, doc_id in [("admin", 5), ("访客", 5), ("admin", 999)]:
    try:
        body = load_doc(doc_id, user)
        print(f"   {user} 读 {doc_id}: 成功 → {body}")
    except AppError as e:                  # 一个 except 接住全部业务错误
        kind = type(e).__name__
        status = 403 if isinstance(e, PermissionDeniedError) else 404
        print(f"   {user} 读 {doc_id}: [{kind}] {e}  (映射 HTTP {status})")
print("   ↑ 只写一个 except AppError, 各子类型可再单独判断/再细分 except")

# ---- 4. except (A, B): 一次捕获多种类型 + assert 与 raise 的分工 ----
print("\n4) except 多类型 + assert 与 raise 的分工:")
try:
    int("不是数字")                       # 触发 ValueError
    int(None)                             # 若走到这行则触发 TypeError(同类处理)
except (ValueError, TypeError) as e:      # 括号里列多种异常, 统一处理
    print(f"   捕获 (ValueError, TypeError): {type(e).__name__}")
print("   ↑ 两种异常都归这一个 except 块 —— 处理逻辑相同时不必写两遍")
# 这是什么: assert —— 调试期断言"前置条件成立"(条件假直接抛 AssertionError),
#           属于"开发期自检, 关不掉也在"; 而 raise 才是"运行期正式错误通道",
#           给用户/上层处理。程序逻辑靠 raise 表达错误, assert 只做内部假设检查
#           (可被 python -O 关闭, 不能当校验用)。

# ---- 5. logging.exception 与链的配合(复习 06/02) ----
print("\n5) 记录链式异常(完整栈进日志):")
try:
    get_profile(3)
except ValueError:
    logging.exception("查询资料接口失败(链路: ValueError ← KeyError)")
print("   ↑ 日志里两层异常都在, 排错不用猜")
