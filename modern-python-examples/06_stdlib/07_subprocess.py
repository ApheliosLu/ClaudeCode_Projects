# ============================================================================
# 07_subprocess.py  现代 Python 示例集 · 06_stdlib 标准库工具箱
# 主题: subprocess —— 在 Python 里启动外部命令并拿回输出
# 解决的问题(基础课):
#   写工具脚本时早晚要调外部程序: 跑 ffmpeg 转码、git 提交、npm 构建……
#   基础课时代唯一的办法 os.system("命令") —— 只能看终端输出, 拿不到
#   输出内容(想解析结果得重定向到文件), 命令里带特殊字符还容易注入。
#   subprocess 把"跑命令"做成了带完整 API 的操作: 捕获输出/判退出码/传输入。
# 运行: python 07_subprocess.py
# ============================================================================

import os
import subprocess
import sys

# 教学统一约定: 用 sys.executable 调"当前这个解释器", 免得 PATH 里是别的 python
PY = sys.executable

# ---- 1. run + capture_output: 跑命令并把 stdout/stderr 抓回来 ----
# 这是什么: subprocess.run(命令列表, capture_output=True, text=True) ——
#           命令写成列表(每段一个元素, 不是一长串字符串); capture_output
#           把 stdout/stderr 收进内存; text=True 按文本解码(不设则返回字节)。
#           返回值是 CompletedProcess: .returncode/.stdout/.stderr。
r = subprocess.run([PY, "-c", "print(42)"], capture_output=True, text=True)
print("1) run 捕获输出:")  # → 1) run 捕获输出:
print("   returncode:", r.returncode, "  # 0 = 成功")  # →    returncode: 0   # 0 = 成功
print("   stdout    :", repr(r.stdout), " # print 自带换行")  # →    stdout    : '42\n'  # print 自带换行
print("   去除换行  :", r.stdout.strip())  # →    去除换行  : 42

# ---- 2. 失败的命令: 看 stderr 与退出码; check=True 直接抛异常 ----
print("\n2) 命令失败时的两种处理:")  # → 2) 命令失败时的两种处理:
bad = subprocess.run([PY, "-c", "1/0"], capture_output=True, text=True)
print("   不抛异常跑完: returncode =", bad.returncode)  # →    不抛异常跑完: returncode = 1
print("   stderr 尾行 :", bad.stderr.strip().splitlines()[-1])
# 输出:    stderr 尾行 : ZeroDivisionError: division by zero
# 这是什么: check=True —— run 的参数: 子进程退出码非 0 就直接抛
#           CalledProcessError(脚本默认"失败就该让上层知道", 不会悄悄继续)。
try:
    subprocess.run([PY, "-c", "1/0"], capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as e:
    print("   check=True: 捕获 CalledProcessError, returncode =", e.returncode)
    # 输出:    check=True: 捕获 CalledProcessError, returncode = 1

# ---- 3. Popen + communicate: 手动接管, 边跑边喂输入 ----
# 这是什么: subprocess.Popen —— run 的"低配手动档": run 等于 Popen +
#           communicate 一把梭。需要交互(先写 stdin 再读输出)、长进程
#           (想随时 poll 状态)时才用 Popen; 平常一律 run。
# 这是什么: communicate(input=...) —— 把数据写进子进程的 stdin 并等它结束,
#           一次性拿回 stdout/stderr。子进程这边: input() 从 stdin 读一行。
child = subprocess.Popen(
    [PY, "-c", "name = input('名字? '); print(f'你好, {name}')"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
)
out, err = child.communicate(input="阿黎\n")   # 喂一行输入, 等结束
print("\n3) Popen + communicate 喂输入:")  # → 3) Popen + communicate 喂输入:
print("   子进程输出:", out.strip(), "  # input() 的提示语不换行, 故与下一行拼接")
# 输出:    子进程输出: 名字? 你好, 阿黎   # input() 的提示语不换行, 故与下一行拼接

# ---- 4. env: 给子进程注入配置(项目配置传递的标准姿势) ----
# 这是什么: env={...} —— 指定子进程的环境变量。注意: 不传则继承父进程环境;
#           传了就是"只给这些"。常规做法 = 复制 os.environ 再改几个键
#           (否则子进程会丢 PATH 等基础变量, 连 python 都找不到)。
child_env = os.environ.copy()                 # 先复制整套环境
child_env["APP_MODE"] = "production"          # 再注入我们的配置
child_env["PYTHONUTF8"] = "1"                 # 顺带: 保证子进程中文输出按 UTF-8
r = subprocess.run(
    [PY, "-c",
     "import os; print('模式 =', os.environ.get('APP_MODE', '(没注入)'))"],
    capture_output=True, text=True, encoding="utf-8", env=child_env,
)
print("\n4) env 注入子进程:")  # → 4) env 注入子进程:
print("   APP_MODE 到达子进程:", r.stdout.strip())  # →    APP_MODE 到达子进程: 模式 = production

# ---- 5. 安全红线: shell=True 与 os.system ----
# 这是什么: shell=True —— 让系统 shell 去解释命令字符串(可写管道/通配符/&&),
#           代价: 字符串里的内容会被 shell 当命令执行 → 参数含用户输入就是
#           注入漏洞(等同 SQL 注入)。官方建议: 需要 shell 特性时逐条想清楚,
#           能不用就不用 —— 命令写成列表 + shell=False 最安全。
# 对照: os.system("命令") 就是"隐式 shell=True" + 输出全丢, 两宗罪占全,
#       新代码一律 subprocess。
user_input = "demo; echo 这里被 shell 执行了!"      # 恶意输入长这样
print("\n5) shell 注入红线(演示, 不真执行):")  # → 5) shell 注入红线(演示, 不真执行):
print("   列表形式 [PY, '-c', user_input] → 当作纯参数, 无注入风险 ✔")  # →    列表形式 [PY, '-c', user_input] → 当作纯参数, 无注入风险 ✔
print("   shell=True 时 ';' 会被当作命令分隔符 → 注入 ✗ (仅注释说明, 不演示)")  # →    shell=True 时 ';' 会被当作命令分隔符 → 注入 ✗ (仅注释说明, 不演示)
print("   os.system 旧写法 = 隐式 shell + 拿不到输出, 弃用")  # →    os.system 旧写法 = 隐式 shell + 拿不到输出, 弃用
