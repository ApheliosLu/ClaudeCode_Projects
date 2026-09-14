# ============================================================================
# 01_unittest_mock.py  现代 Python 示例集 · 09_tools 工程工具
# 主题: unittest + mock —— 标准库测试框架与"假对象"隔离
# 解决的问题(基础课):
#   写完函数靠"眼睛看输出"验证, 改了一处不知道哪又坏了 —— 工程上把
#   验证写成自动化测试: 每次改动跑一遍全量测试。unittest 是标准库测试
#   框架(不装第三方); 被测函数要调外部服务/网络时, 用 mock 造"假对象"
#   替身, 让测试不依赖真实环境。
# 本文件身份特殊: 它同时是"测试写法演示"和"自检测试" ——
#   运行 `python 01_unittest_mock.py` 就是跑它自己身上的测试。
# 运行: python 01_unittest_mock.py      (等价的: python -m unittest 01_unittest_mock.py)
# ============================================================================

import unittest
from unittest.mock import MagicMock, patch

# ===== 被测代码(实际工程里在别的模块, 这里同文件便于演示) =====

def calc_total(prices):
    """订单合计: 非负数求和, 负数/非数字视为数据错误"""
    total = 0
    for p in prices:
        if not isinstance(p, (int, float)) or p < 0:
            raise ValueError(f"价格非法: {p!r}")
        total += p
    return total


def send_alert(level, msg, notifier):
    """给运维发告警 —— notifier 是外部依赖(短信/邮件网关)"""
    notifier.deliver(f"[{level}] {msg}")
    return "已发送"


def fetch_price(item_id):
    """真实实现会请求外部价格服务 —— 测试时不希望真发请求"""
    import urllib.request
    with urllib.request.urlopen(f"https://prices.example/api/{item_id}") as r:
        return float(r.read())


# ===== 测试(每个 TestCase 类 = 一组相关用例, 每个 test_ 方法 = 一条用例) =====
# 这是什么: unittest.TestCase —— 测试类: 继承它后, 内部所有 test_ 开头的方法
#           都会被框架自动发现并按顺序运行; 断言失败即该条用例失败。
# 这是什么: setUp/tearDown —— 每条用例运行前/后自动调用: 造公共夹具
#           (setUp)与打扫战场(tearDown), 保证用例之间互不污染。
class TestCalcTotal(unittest.TestCase):
    def setUp(self):                                # 每条用例前自动跑
        self.prices = [10.5, 20, 5.5]               # 公共数据

    def test_normal_sum(self):
        self.assertEqual(calc_total(self.prices), 36.0)

    def test_empty_is_zero(self):
        self.assertTrue(calc_total([]) == 0)        # assertTrue: 布尔断言

    def test_bad_price_raises(self):
        # assertRaises: 断言"调用会抛指定异常"(with 语法把断言范围收紧)
        with self.assertRaises(ValueError):
            calc_total([1, -2])
        with self.assertRaises(ValueError):
            calc_total([1, "abc"])


class TestSendAlert(unittest.TestCase):
    # 这是什么: unittest.mock.MagicMock —— 万能"假对象": 任何属性/方法随取随有,
    #           调用即记录(记了 call_count/调用参数), 不会真发短信。
    #           测试的依赖替身就靠它 —— 被测函数以为自己调了真网关。
    def setUp(self):
        self.fake_notifier = MagicMock()            # 假告警网关

    def test_deliver_called_once(self):
        send_alert("ERROR", "磁盘满", self.fake_notifier)
        # assert_called_once_with: 断言"被调用过一次且参数正是这些"
        self.fake_notifier.deliver.assert_called_once_with("[ERROR] 磁盘满")
        self.assertEqual(self.fake_notifier.deliver.call_count, 1)

    def test_returns_sent(self):
        self.fake_notifier.deliver.return_value = "ok"   # 设定假对象返回值
        self.assertEqual(send_alert("INFO", "例行", self.fake_notifier), "已发送")

    # 这是什么: unittest.mock.patch —— 测试期间的"全局替换开关": with 块内
    #           把指定路径的对象换成替身(MagicMock), 退出 with 自动还原 ——
    #           被测代码里的 fetch_price 在测试中被假函数顶替, 不发真请求。
    def test_price_uses_patch(self):
        with patch("urllib.request.urlopen") as fake_open:
            fake_resp = MagicMock()
            fake_resp.__enter__.return_value.read.return_value = b"42.5"
            fake_open.return_value = fake_resp
            self.assertEqual(fetch_price(7), 42.5)
            fake_open.assert_called_once()          # 确认"请求确实被发出"过一次
            print("   [patch 生效] fetch_price 没发真实请求, 拿到替身数据 42.5")
            # 输出: ....   [patch 生效] fetch_price 没发真实请求, 拿到替身数据 42.5


# 这是什么: unittest.main() —— 命令行入口: 运行本文件即自动发现并跑全部
#           用例, 汇总输出. / OK / FAILED。等价命令 python -m unittest 文件名。
if __name__ == "__main__":
    unittest.main()
    # 运行本文件的完整输出(unittest 汇总走 stderr): 6 个点 = 6 条用例通过; 用时随机器浮动:
    # ....   [patch 生效] fetch_price 没发真实请求, 拿到替身数据 42.5
    # ..
    # ----------------------------------------------------------------------
    # Ran 6 tests in 0.012s
    # 
    # OK
