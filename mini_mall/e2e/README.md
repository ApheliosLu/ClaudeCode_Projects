# E2E 测试

完整买家/管理端/会员流程测试（Playwright + 系统 Edge）。

## 前置条件

```bash
# Python 环境安装 playwright（已装则跳过）
pip install playwright          # 不下载浏览器，用系统 Edge

# 构建并启动生产服务器（或 npm run dev）
npm run build && npm start      # 默认 3000 端口
```

## 运行

```bash
# 注意：测试会写数据库（测试用户/订单/会员改动）
# 运行前备份 dev.db，测试后恢复：
cp dev.db /tmp/dev-backup.db
python e2e/full-flow-test.py
cp /tmp/dev-backup.db dev.db
```

## 覆盖范围（21 项断言）

- 买家：首页 / 列表 / 搜索 / 详情 / 注册 / 加购 / 下单 / 收银台 / 支付 / 订单列表 / 会员中心
- 会员：vip 9.5 折金额（¥89 → ¥84.55）、demo 累计跨 8000 元升级心悦1
- 管理端：仪表盘 / 商品列表 / 新建 / 编辑 / 订单发货流转 / 新建分类

## 注意

- 使用 `channel="msedge"` 驱动系统 Edge，无需下载 Chromium
- 数据库恢复以 `cp` 恢复备份（最简单可靠）
