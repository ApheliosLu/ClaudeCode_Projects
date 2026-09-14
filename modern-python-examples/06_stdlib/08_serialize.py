# ============================================================================
# 08_serialize.py  现代 Python 示例集 · 06_stdlib 标准库工具箱
# 主题: 序列化与安全 —— json 交换 / pickle 红线 / copy 深浅 / shelve
# 解决的问题(基础课):
#   程序 A 要把数据交给程序 B(或存盘、或发给 HTTP 接口), 内存里的
#   dict/list 是"活对象", 别的程序看不懂 —— 得先变成纯文本/字节(序列化),
#   对方再还原(反序列化)。最通用的是 JSON(前后端交换事实标准)。
#   另外两个容易混的"拷贝": copy 浅拷贝与 deepcopy 深拷贝。
# 运行: python 08_serialize.py
# ============================================================================

import copy
import json
import pickle

# ---- 1. json 基本 round-trip: dict/list ↔ 字符串 ----
# 这是什么: json —— 把对象转成 JSON 文本(几乎所有语言都能解析的格式)。
#           json.dumps(对象) 序列化; json.loads(文本) 反序列化(round-trip)。
#           能直接转的只有 dict/list/str/int/float/bool/None —— 正适合 API。
user = {"name": "阿黎", "age": 23, "tags": ["python", "vue"], "vip": True}
text = json.dumps(user)
print("1) json round-trip:")  # → 1) json round-trip:
print("   dumps 文本:", text)
# 输出:    dumps 文本: {"name": "\u963f\u9ece", "age": 23, "tags": ["python", "vue"], "vip": true}
back = json.loads(text)
print("   loads 还原:", back, " # 类型/嵌套结构原样回来")
# 输出:    loads 还原: {'name': '阿黎', 'age': 23, 'tags': ['python', 'vue'], 'vip': True}  # 类型/嵌套结构原样回来
print("   两边相等:", user == back)  # →    两边相等: True

# ---- 2. 中文可读 + 美化输出: ensure_ascii / indent / sort_keys ----
# 这是什么: ensure_ascii=False —— 不把中文转成 \uXXXX 转义(默认 True 是为兼容
#           老系统); indent=2 —— 带缩进美化(存配置文件/给人读用);
#           sort_keys=True —— 键排序(输出稳定, 利于 diff 与缓存命中)。
print("\n2) 中文可读与美化(对比上面默认的 \\u 转义):")  # → 2) 中文可读与美化(对比上面默认的 \u 转义):
pretty = json.dumps(user, ensure_ascii=False, indent=2, sort_keys=True)
print(pretty)
# 美化后的整段 JSON(9 行):
# {
#   "age": 23,
#   "name": "阿黎",
#   "tags": [
#     "python",
#     "vue"
#   ],
#   "vip": true
# }
print("   ↑ 中文原样输出, 键按字母序, 缩进两级 —— 适合存配置文件")  # →    ↑ 中文原样输出, 键按字母序, 缩进两级 —— 适合存配置文件

# ---- 3. 自定义对象: default 钩子把任意对象变成 dict ----
# 这是什么: json 不认识自定义类实例(直接 dumps 报 TypeError) →
#           default=函数: 遇到不认识的对象时调用它, 返回可序列化的替代
#           (惯例返回 o.__dict__); 读回时再手动恢复成对象(单向转换,
#           JSON 不记你是什么类)。
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

s = Student("阿黎", 92)
s_json = json.dumps(s, default=lambda o: o.__dict__, ensure_ascii=False)
print("\n3) 自定义对象序列化(default 钩子):")  # → 3) 自定义对象序列化(default 钩子):
print("   dumps 结果:", s_json)  # →    dumps 结果: {"name": "阿黎", "score": 92}
raw = json.loads(s_json)
print("   还原后是普通 dict:", raw, "→ 需要对象再 Student(**raw) 手动恢复")
# 输出:    还原后是普通 dict: {'name': '阿黎', 'score': 92} → 需要对象再 Student(**raw) 手动恢复

# ---- 4. pickle: Python 专用序列化 —— 一条红线 ----
# 这是什么: pickle —— Python 对象 ↔ 字节流的一对一序列化(能存任意对象,
#           包括类实例/函数/生成器), 比 json 强得多 —— 但只限 Python 之间。
#   ⚠️ 安全红线: pickle.loads(不可信数据) = 执行任意代码!
#   恶意 pickle 字节流里可以打包"加载即执行"的 payload(反序列化攻击)。
#   json 只是纯文本数据、无执行能力, 所以"跨进程/跨语言/对外接收"一律 json;
#   pickle 只用于: 自己写的程序、存给自己读的缓存(且文件不被他人写入)。
print("\n4) pickle(仅演示机制, 红线在注释):")  # → 4) pickle(仅演示机制, 红线在注释):
data = {"cache": [1, 2, 3], "note": "自己程序内部缓存"}
blob = pickle.dumps(data)
print("   dumps 字节:", blob[:28], "...   # 二进制, 人类不可读")
# 输出:    dumps 字节: b'\x80\x05\x959\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x05cache\x94]\x94(K\x01K' ...   # 二进制, 人类不可读
print("   loads 还原:", pickle.loads(blob))  # →    loads 还原: {'cache': [1, 2, 3], 'note': '自己程序内部缓存'}
print("   ⚠️ 只反序列化自己信任来源的数据 —— 对不可信输入用 pickle 等同裸奔")  # →    ⚠️ 只反序列化自己信任来源的数据 —— 对不可信输入用 pickle 等同裸奔

# ---- 5. copy.copy 浅拷贝 vs copy.deepcopy 深拷贝 ----
# 这是什么: 浅拷贝 copy.copy(x) —— 只复制"最外层容器", 里面的子对象仍是
#           同一个(改子对象两边一起变); 深拷贝 copy.deepcopy(x) —— 递归
#           复制到底, 子对象也全新一份(互不影响)。基础课的赋值 b = a 连
#           外层都不复制(两名字同一对象)。
print("\n5) 浅拷贝 vs 深拷贝:")  # → 5) 浅拷贝 vs 深拷贝:
a = {"items": [1, 2, 3], "tag": "原"}
b = a                                  # 赋值: 同一对象
c = copy.copy(a)                       # 浅拷贝: 新外层, 共享内部 list
d = copy.deepcopy(a)                   # 深拷贝: 全部全新
print("   是否同一对象  a is b:", a is b, "| a is c:", a is c, "| a is d:", a is d)
# 输出:    是否同一对象  a is b: True | a is c: False | a is d: False
c["items"].append(4)                   # 改浅拷贝的内层 list
print("   c 的 list 加 4 后:")  # →    c 的 list 加 4 后:
print("   a['items']:", a["items"], "  # 跟着变了(共享内层)")  # →    a['items']: [1, 2, 3, 4]   # 跟着变了(共享内层)
print("   d['items']:", d["items"], "  # 不受影响(深拷贝独立)")  # →    d['items']: [1, 2, 3]   # 不受影响(深拷贝独立)
d["items"].append(5)
print("   d 再加 5 → a 仍是:", a["items"], "  # 彻底互不干扰")  # →    d 再加 5 → a 仍是: [1, 2, 3, 4]   # 彻底互不干扰

# ---- 6. shelve: 一个按键存取的持久化 dict(一句带过) ----
# 这是什么: shelve —— 把 dict 的键值"存进本地文件"(背后是 dbm/pickle):
#           程序重启后数据还在, 像数据库的迷你版。小工具存配置/缓存够用;
#           数据量大/要并发/要查询就上真数据库。用法与 dict 几乎一致,
#           此处不展开(纯标准库, 需要时查文档即会)。
print("\n6) shelve: 迷你持久化 dict(注释已述, 不展开演示)")  # → 6) shelve: 迷你持久化 dict(注释已述, 不展开演示)
print("\n全部演示完成 ✔")  # → 全部演示完成 ✔
