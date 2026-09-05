# ============================================================================
# 02_logging.py  现代 Python 示例集 · 06_stdlib 标准库工具箱
# 主题: logging —— 工程日志体系(级别/时间戳/分类/文件), 替代 print 调试
# 解决的问题(基础课):
#   基础课里排查问题全靠 print —— 上线后没人盯着终端看, 你得让程序
#   自己"写日志": 带时间戳、分级别、按模块开关、能落文件还能自动轮转。
#   logging 就是干这个的标准库(运维排查的第一现场)。
# 这是什么: logging —— Python 标准日志库。核心模型三个词:
#           Logger(记日志的人, 带名字) → Handler(把日志送往终端/文件)
#           → Formatter(决定每行长什么样)。级别从上到下越来越严重:
#           DEBUG < INFO < WARNING < ERROR < CRITICAL, 过滤规则 =
#           "设了 WARNING 就只显示 WARNING 及更严重的"。
# 运行: python 02_logging.py
# ============================================================================

import logging
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

# stdout 行缓冲: 保证 print 教学标题与日志输出(见下, 统一走 stdout)顺序对位
sys.stdout.reconfigure(line_buffering=True)

# ---- 1. basicConfig 一次性配置全局格式, 五种级别逐个演示 ----
# 这是什么: logging.basicConfig() —— 一条命令配好 root logger 的级别与格式
#           (只在第一次调用生效, 之后调用被忽略)。format 里的 %(asctime)s/
#           %(levelname)s/%(name)s/%(message)s 是占位符, 每行日志会按它拼。
print("1) 五种级别(DEBUG → CRITICAL), basicConfig 配置后全部可见:")
logging.basicConfig(
    level=logging.DEBUG,                       # 门槛: DEBUG 及更严重都放行
    format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
    datefmt="%H:%M:%S",                        # 时间戳只要时分秒
    stream=sys.stdout,                         # 与 print 同流, 演示顺序直观
)
logging.debug("查变量细节用 DEBUG")
logging.info("正常流程节点用 INFO")
logging.warning("能跑但可疑用 WARNING")
logging.error("出错但程序没崩用 ERROR")
logging.critical("程序要完蛋了用 CRITICAL")
print("   ↑ 级别从左到右递增; setLevel 越低放行越多")

# ---- 2. getLogger(名字): 按模块分类, 各自独立设门槛 ----
# 这是什么: logging.getLogger("模块.部位") —— 拿一个"带名字的 logger"。
#           名字就是树形分类(点号分层, 如 "shop.cart" 是 "shop" 的子级);
#           好处: 每个模块有自己的 logger, 可以单独开/关级别,
#           线上排查时"只把订单模块调到 DEBUG, 其余保持 WARNING"。
cart = logging.getLogger("shop.cart")         # 分类 logger, 无自己的 handler
cart.setLevel(logging.WARNING)                # 只放行 WARNING 及以上
order = logging.getLogger("shop.order")       # 继承全局 DEBUG 门槛
print("\n2) 按模块分类与独立级别: cart 设 WARNING 门槛, order 保持 DEBUG")
cart.debug("cart 的 DEBUG 被门槛挡掉, 不显示")
cart.warning("cart 出 WARNING, 可见")
order.debug("order 的 DEBUG, 因全局 DEBUG 门槛而可见")
print("   对比上面 print 里的日志: name 列显示 shop.cart / shop.order")

# ---- 3. 落文件 + 自动轮转: RotatingFileHandler ----
# 这是什么: RotatingFileHandler —— 文件一超过 maxBytes 字节就"滚动"成
#           .1/.2/.3 备份并开新文件, 只留 backupCount 份, 防止日志无限膨胀
#           (生产上 24 小时在线的服务, 不轮转会把磁盘写满)。
print("\n3) 日志写文件 + 超过 maxBytes 自动轮转备份:")
with tempfile.TemporaryDirectory(prefix="log_demo_") as tmp:
    log_path = Path(tmp) / "app.log"
    rot = logging.getLogger("rotate.demo")
    rot.setLevel(logging.INFO)
    # 这是什么: logger.propagate —— 默认 True 表示日志会继续"冒泡"传给父级
    #           (这里就是 root, 会重复打到控制台)。关掉它, 日志只走自己的 handler。
    rot.propagate = False
    fh = RotatingFileHandler(log_path, maxBytes=200, backupCount=3,
                             encoding="utf-8")      # 200 字节即转一次(教学故意调小)
    rot.addHandler(fh)                              # 挂到 logger 上
    for i in range(25):                             # 25 条 × ~90 字节 → 轮转多次
        rot.info(f"第 {i} 条业务日志: 用户下单 #{i}")

    files = sorted(Path(tmp).iterdir())
    print("   临时目录里生成的文件:")
    for f in files:
        size = f.stat().st_size
        print(f"   {f.name:<12} {size} 字节")
    print(f"   → 现役 app.log + {len(files) - 1} 个备份(backupCount=3 只留 3 份)")
    print("   备份 .1 的内容头两行:")
    backup = Path(tmp) / "app.log.1"
    for line in backup.read_text(encoding="utf-8").splitlines()[:2]:
        print("   |", line)
    fh.close()                                      # 关 handler 释放文件句柄
    rot.removeHandler(fh)
# 退出 with: 文件已释放, 临时目录自动清理
print("   临时目录已自动清理 ✔")

# ---- 4. logging.exception: 在 except 里记完整调用栈 ----
# 这是什么: logger.exception("说明") —— 只能在 except 块里用: 等价于
#           logger.error(..., exc_info=True), 自动把当前异常的 traceback
#           完整写进日志 —— 线上排错最需要的就是"哪一行炸的"。
print("\n4) except 里用 exception 记下完整栈:")
try:
    total = 10 / 0
except ZeroDivisionError:
    logging.exception("计算平均价失败(故意的)")     # 输出 ERROR 行 + traceback
print("   ↑ traceback 完整记录了异常发生位置(运维排错第一现场)")
