# mini_mall E2E 全流程测试 v2（Playwright + Edge，显式等待加固）
import sys
sys.stdout.reconfigure(encoding="utf-8")

import random
import sqlite3
import sys

from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
DB = "d:/1/CCC/ClaudeCode_Projects/mini_mall/dev.db"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = ""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'} | {name} {detail}")


def db_exec(sql: str):
    conn = sqlite3.connect(DB)
    conn.execute(sql)
    conn.commit()
    conn.close()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page()

    # ---------- 1. 买家浏览 ----------
    page.goto(BASE, wait_until="networkidle")
    check("首页加载", page.locator("text=精选商品").count() > 0)

    page.goto(f"{BASE}/products", wait_until="networkidle")
    cards = page.locator("a[href*='/products/']").count()
    check("商品列表渲染", cards > 5, f"商品链接 {cards} 个")

    page.fill('input[name="q"]', "手机")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("text=智能手机", timeout=8000)
    check("搜索'手机'", True)

    page.goto(f"{BASE}/products/phone-pro-2026", wait_until="networkidle")
    check("商品详情", page.locator("text=加入购物车").count() > 0)

    # ---------- 2. 注册新用户（等 header 显示用户名确认 session） ----------
    email = f"e2e{random.randint(1000, 9999)}@test.dev"
    page.goto(f"{BASE}/register", wait_until="networkidle")
    page.fill("#name", "E2E测试用户")
    page.fill("#email", email)
    page.fill("#password", "Test@123456")
    page.fill("#confirm", "Test@123456")
    page.click('button[type="submit"]')
    page.wait_for_selector("header >> text=E2E测试用户", timeout=10000)
    check("注册成功(header有用户名)", True, email)

    # ---------- 3. 加购 → 下单 → 支付 ----------
    page.goto(f"{BASE}/products/thermos-cup-500", wait_until="networkidle")
    page.click("text=加入购物车")
    page.wait_for_timeout(500)
    page.goto(f"{BASE}/cart", wait_until="networkidle")
    page.wait_for_selector("text=保温水杯", timeout=8000)
    check("购物车有商品", True)

    page.click("text=去结算")
    page.wait_for_load_state("networkidle")
    page.fill("#name", "张三")
    page.fill("#phone", "13800138000")
    page.fill("#address", "北京市海淀区中关村大街1号")
    page.click('button[type="submit"]:has-text("提交订单")')
    page.wait_for_url("**/pay/**", timeout=10000)
    check("下单成功跳转收银台", True)

    page.wait_for_load_state("networkidle")
    order_no = page.url.split("/pay/")[1]
    check("收银台订单号", len(order_no) > 10, order_no)

    page.click("text=确认支付")
    page.wait_for_url(f"**/orders/{order_no}*", timeout=10000)
    page.wait_for_selector("text=已支付", timeout=10000)
    check("支付成功", True, order_no)

    # ---------- 4. 订单列表 + 会员中心 ----------
    page.goto(f"{BASE}/orders", wait_until="networkidle")
    page.wait_for_selector(f"text={order_no}", timeout=8000)
    check("订单列表", True)
    page.goto(f"{BASE}/membership", wait_until="networkidle")
    check("会员中心(普通会员)", "普通会员" in page.content())

    # ---------- 5. vip 会员折扣验证（9.5 折：89 元 → 84.55） ----------
    page.context.clear_cookies()
    page.goto(f"{BASE}/login", wait_until="networkidle")
    page.fill("#email", "vip@minimall.dev")
    page.fill("#password", "Demo@123456")
    page.click('button[type="submit"]')
    page.wait_for_selector("header >> text=会员演示", timeout=10000)

    page.goto(f"{BASE}/products/thermos-cup-500", wait_until="networkidle")
    page.click("text=加入购物车")
    page.wait_for_timeout(500)
    page.goto(f"{BASE}/cart", wait_until="networkidle")
    page.wait_for_selector("text=去结算", timeout=8000)
    page.click("text=去结算")
    page.wait_for_load_state("networkidle")
    page.fill("#name", "会员用户")
    page.fill("#phone", "13900139000")
    page.fill("#address", "上海市浦东新区世纪大道100号")
    page.click('button[type="submit"]:has-text("提交订单")')
    page.wait_for_url("**/pay/**", timeout=10000)
    page.wait_for_load_state("networkidle")
    check("vip 9.5折金额¥84.55", "¥84.55" in page.content())
    page.click("text=确认支付")
    page.wait_for_selector("text=已支付", timeout=12000)
    check("vip支付成功", True)

    # ---------- 6. 会员升级验证（demo 预置 7999 元 → 买 798 元跨过 8000 阈值） ----------
    db_exec("UPDATE user SET accumulatedSpentCents = 799900 WHERE email = 'demo@minimall.dev'")
    page.context.clear_cookies()
    page.goto(f"{BASE}/login", wait_until="networkidle")
    page.fill("#email", "demo@minimall.dev")
    page.fill("#password", "Demo@123456")
    page.click('button[type="submit"]')
    page.wait_for_selector("header >> text=演示买家", timeout=10000)

    page.goto(f"{BASE}/products/mech-keyboard-k87", wait_until="networkidle")
    page.click("text=加入购物车")
    page.wait_for_timeout(500)
    page.goto(f"{BASE}/cart", wait_until="networkidle")
    page.wait_for_selector("text=去结算", timeout=8000)
    page.click("text=去结算")
    page.wait_for_load_state("networkidle")
    page.fill("#name", "升级测试")
    page.fill("#phone", "13700137000")
    page.fill("#address", "广州市天河区体育西路100号")
    page.click('button[type="submit"]:has-text("提交订单")')
    page.wait_for_url("**/pay/**", timeout=10000)
    page.wait_for_load_state("networkidle")
    page.click("text=确认支付")
    page.wait_for_selector("text=已支付", timeout=12000)
    page.goto(f"{BASE}/membership", wait_until="networkidle")
    page.wait_for_selector("text=心悦1级", timeout=8000)
    check("demo升级为心悦1", True)

    # ---------- 7. 管理端 ----------
    page.context.clear_cookies()
    page.goto(f"{BASE}/login", wait_until="networkidle")
    page.fill("#email", "admin@minimall.dev")
    page.fill("#password", "Admin@123456")
    page.click('button[type="submit"]')
    page.wait_for_selector("header >> text=管理员", timeout=10000)
    page.goto(f"{BASE}/admin", wait_until="networkidle")
    check("管理端仪表盘", "仪表盘" in page.content())

    page.goto(f"{BASE}/admin/products", wait_until="networkidle")
    page.wait_for_selector("text=智能手机", timeout=8000)
    check("商品管理列表", True)

    page.goto(f"{BASE}/admin/products/new", wait_until="networkidle")
    page.fill("#name", "E2E测试商品")
    page.fill("#slug", "e2e-test-product")
    page.fill("#price", "66.00")
    page.fill("#stock", "10")
    page.select_option("#category", label="数码电子")
    page.click('button[type="submit"]:has-text("保存")')
    page.wait_for_url("**/admin/products", timeout=10000)
    page.wait_for_selector("text=E2E测试商品", timeout=8000)
    check("新建商品", True)

    page.goto(f"{BASE}/admin/products/e2e-test-product/edit", wait_until="networkidle")
    page.wait_for_selector("#price", timeout=8000)
    page.fill("#price", "55.00")
    page.click('button[type="submit"]:has-text("保存")')
    page.wait_for_url("**/admin/products", timeout=10000)
    page.wait_for_selector("text=¥55.00", timeout=8000)
    check("编辑商品", True)

    page.goto(f"{BASE}/admin/orders", wait_until="networkidle")
    page.wait_for_selector("text=订单管理", timeout=8000)
    check("订单管理列表", True)
    page.click("text=发货")
    page.wait_for_selector("text=已发货", timeout=8000)
    check("订单发货流转", True)

    page.goto(f"{BASE}/admin/categories", wait_until="networkidle")
    page.fill("#cat-name", "E2E测试分类")
    page.fill("#cat-slug", "e2e-cat")
    page.click('button[type="submit"]:has-text("创建分类")')
    page.wait_for_selector("text=E2E测试分类", timeout=8000)
    check("新建分类", True)

    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n===== 汇总: {len(results) - len(failed)}/{len(results)} 通过 =====")
for name, ok, detail in results:
    if not ok:
        print(f"  FAIL: {name} {detail}")
sys.exit(1 if failed else 0)
