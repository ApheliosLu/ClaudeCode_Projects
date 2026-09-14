# ============================================================================
# 05_datetime.py  现代 Python 示例集 · 06_stdlib 标准库工具箱
# 主题: 时间处理 —— datetime + zoneinfo: 时刻/时区/格式化/运算
# 解决的问题(基础课):
#   基础课里处理时间只有 time.time() 秒数, 要"打印成人类日期"还得自己算;
#   涉及时区(服务器在 UTC、用户在中国)更是一笔糊涂账。
#   datetime 模块把"时间"分成三件套 + 时区支持, 是全套答案。
# 运行: python 05_datetime.py
# ============================================================================

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

# ---- 1. 三件套: date(日期) / time(时刻钟) / datetime(两者都有) ----
# 这是什么: datetime.date —— 只关心年月日(生日/节假日/报表日期);
#           datetime.time —— 只关心时分秒(打卡/营业时段);
#           datetime.datetime —— 两者合体, 绝大部分场景用这个。
print("1) 三件套基本构造:")  # → 1) 三件套基本构造:
d = date(2026, 9, 5)
t = time(14, 30, 0)
dt = datetime(2026, 9, 5, 14, 30, 0)
print("   date(2026,9,5)    =", d, "   #", type(d).__name__)  # →    date(2026,9,5)    = 2026-09-05    # date
print("   time(14,30,0)     =", t, "   #", type(t).__name__)  # →    time(14,30,0)     = 14:30:00    # time
print("   datetime(...)     =", dt, "   #", type(dt).__name__)
# 输出:    datetime(...)     = 2026-09-05 14:30:00    # datetime
print("   dt.date() 取日期部:", dt.date(), "  dt.time() 取时间部:", dt.time())
# 输出:    dt.date() 取日期部: 2026-09-05   dt.time() 取时间部: 14:30:00
print("   date 上做运算(加减天):", date(2026, 9, 5) + timedelta(days=10))  # →    date 上做运算(加减天): 2026-09-15

# ---- 2. 时区: 同一个瞬间, 在不同时区钟面不同 ----
# 这是什么: ZoneInfo("地区/城市") —— 3.9 起内置的 IANA 时区数据库(随系统),
#           (3.9 及之前: 没有标准库方案, 老项目普遍装第三方 pytz ——
#           新代码一律 zoneinfo, 别引 pytz)。datetime 带上 tzinfo 才是
#           "墙上时刻"明确的时刻; 不带 tzinfo 的 naive datetime 不能直接跨时区比。
print("\n2) 同一 UTC 时刻, 三个时区的钟面:")  # → 2) 同一 UTC 时刻, 三个时区的钟面:
utc = datetime.now(ZoneInfo("UTC"))
sh = utc.astimezone(ZoneInfo("Asia/Shanghai"))        # 中国标准时间 UTC+8
ur = utc.astimezone(ZoneInfo("Asia/Urumqi"))          # 新疆 实际 UTC+6
print("   UTC       :", utc.strftime("%H:%M"), " (偏移", utc.utcoffset(), ")")
# 钟面时刻随运行时间变化:
#    UTC       : 08:39  (偏移 0:00:00 )
print("   上海      :", sh.strftime("%H:%M"), " (偏移", sh.utcoffset(), ")")
# 钟面时刻随运行时间变化:
#    上海      : 16:39  (偏移 8:00:00 )
print("   乌鲁木齐  :", ur.strftime("%H:%M"), " (偏移", ur.utcoffset(), ")")
# 钟面时刻随运行时间变化:
#    乌鲁木齐  : 14:39  (偏移 6:00:00 )
print("   → 同一瞬间钟面差 2 小时, 偏移分别为 0 / +8 / +6 小时")  # →    → 同一瞬间钟面差 2 小时, 偏移分别为 0 / +8 / +6 小时
# 这是什么: 判断一个 datetime 带不带时区 —— 看 .tzinfo 是不是 None
#           (naive = 裸时间, 不知道自己在哪个时区, 跨时区换算前必须 aware)。
print("   带时区判断: utc.tzinfo:", utc.tzinfo, " | 裸的 datetime(2026,1,1).tzinfo:",
      datetime(2026, 1, 1).tzinfo)
      # 随运行时间变化:
      #    带时区判断: utc.tzinfo: UTC  | 裸的 datetime(2026,1,1).tzinfo: None

# ---- 3. astimezone 不传参 = 转成本机时区; now() 的机器时区 ----
print("\n3) 本地时间与 UTC 的换算:")  # → 3) 本地时间与 UTC 的换算:
local_now = datetime.now()                            # 本机时区(不带 tzinfo)
print("   datetime.now() 本地:", local_now.strftime("%Y-%m-%d %H:%M:%S"),
      "  # 不带时区信息")
      # 随运行时间变化:
      #    datetime.now() 本地: 2026-09-12 16:39:55   # 不带时区信息
utc_aware = datetime.now(ZoneInfo("UTC"))
print("   .astimezone() 无参 → 机器时区:", utc_aware.astimezone().strftime("%H:%M %z"))
# 随运行时间与机器时区变化:
#    .astimezone() 无参 → 机器时区: 16:39 +0800
# %z = 时区偏移形如 +0800; 机器在中国就是 UTC+8

# ---- 4. strftime 格式化 与 strptime 解析: 双向 ----
# 这是什么: 时刻.strftime("格式") —— 时刻 → 字符串(输出给人看/写日志);
#           字符串.strptime(s, "格式") —— 字符串 → 时刻(解析用户输入/外部数据)。
#           常用格式符: %Y 年 %m 月 %d 日 %H 时 %M 分 %S 秒 %A 星期几 %z 时区偏移。
print("\n4) strftime(时刻→文本) / strptime(文本→时刻):")  # → 4) strftime(时刻→文本) / strptime(文本→时刻):
fmt = "%Y-%m-%d %H:%M:%S"
s = local_now.strftime(fmt)
print("   格式化输出   :", s)
# 随运行时间变化:
#    格式化输出   : 2026-09-12 16:39:55
parsed = datetime.strptime("2026-09-05 08:30:00", fmt)
print("   解析输入     :", parsed, "  # strptime 反着来")  # →    解析输入     : 2026-09-05 08:30:00   # strptime 反着来
print("   星期几 %A    :", local_now.strftime("%A"))   # 英文星期(机器语言环境而定)
# 星期名随系统语言环境:
#    星期几 %A    : Saturday
print("   isoformat()  :", local_now.isoformat(sep=" ", timespec="seconds"),
      "  # ISO 8601 通用交换格式")
      # 随运行时间变化:
      #    isoformat()  : 2026-09-12 16:39:55   # ISO 8601 通用交换格式

# ---- 5. timedelta 运算: 时间加减与差值 ----
# 这是什么: timedelta —— "时长"对象(天/秒/微秒): 时刻 ± timedelta = 新时刻;
#           时刻 - 时刻 = timedelta。查"距某个截止还有多久"全靠它。
print("\n5) timedelta 运算:")  # → 5) timedelta 运算:
deadline = datetime(2026, 12, 31, 23, 59, 59)
remain = deadline - local_now.replace(microsecond=0)
print("   现在距离 2026-12-31 23:59:59:", remain, "  # timedelta 显示为 天, 时:分:秒")
# 随运行时间变化:
#    现在距离 2026-12-31 23:59:59: 110 days, 7:20:04   # timedelta 显示为 天, 时:分:秒
print("   再加一周                   :", (deadline + timedelta(weeks=1)).date())
# 输出:    再加一周                   : 2027-01-07

# ---- 6. fromisoformat: 解析标准格式字符串(数据库/API 常见) ----
# 这是什么: datetime.fromisoformat("...") —— 直接解析 ISO 8601 字符串,
#           不用手写格式串(strptime 的便捷版, 处理机器间交换的时间文本)。
print("\n6) fromisoformat 解析 API 返回的时间文本:")  # → 6) fromisoformat 解析 API 返回的时间文本:
msg_time = datetime.fromisoformat("2026-09-04T10:00:00")   # 无时区
print("   '2026-09-04T10:00:00' →", msg_time)  # →    '2026-09-04T10:00:00' → 2026-09-04 10:00:00
msg_tz = datetime.fromisoformat("2026-09-04T10:00:00+08:00")  # 带 +08:00 偏移
print("   带偏移的版本        →", msg_tz, "  # 解析后自动带 tzinfo")
# 输出:    带偏移的版本        → 2026-09-04 10:00:00+08:00   # 解析后自动带 tzinfo
print("   换算成 UTC         →", msg_tz.astimezone(ZoneInfo("UTC")), "  # 10:00+8 就是 02:00 UTC")
# 输出:    换算成 UTC         → 2026-09-04 02:00:00+00:00   # 10:00+8 就是 02:00 UTC

# ---- 7. 耗时测量 timeit 去哪儿了 ----
# 一句话: 测量一小段代码耗时用 timeit(标准库), 完整演示见 09_tools/03_debug_perf.py,
# 这里不展开 —— 顺手记: datetime 负责"墙上时刻", 测量耗时用 timeit/time.perf_counter。
