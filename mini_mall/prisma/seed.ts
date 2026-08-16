// 种子数据：4 分类 × 16 商品（幂等，可重复执行）
// 用户账号（admin/demo/vip）在 Phase C 认证落地后补充
import "dotenv/config";
import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";

const adapter = new PrismaBetterSqlite3({ url: process.env.DATABASE_URL! });
const prisma = new PrismaClient({ adapter });

type SeedProduct = {
  name: string;
  slug: string;
  description: string;
  priceCents: number;
  stock: number;
  featured?: boolean;
};

const categories: { name: string; slug: string; description: string; products: SeedProduct[] }[] = [
  {
    name: "数码电子",
    slug: "digital",
    description: "手机、耳机、穿戴设备与桌面外设",
    products: [
      {
        name: "智能手机 Pro 2026",
        slug: "phone-pro-2026",
        description: "6.8 英寸 2K 屏，5000mAh 大电池，1 英寸主摄，性能旗舰首选。",
        priceCents: 499900,
        stock: 200,
        featured: true,
      },
      {
        name: "无线降噪耳机 Pro",
        slug: "wireless-nc-earbuds",
        description: "主动降噪 48dB，单次续航 8 小时，支持无线充电。",
        priceCents: 89900,
        stock: 500,
        featured: true,
      },
      {
        name: "智能手表 S2",
        slug: "smart-watch-s2",
        description: "血氧心率监测、100+ 运动模式、14 天续航。",
        priceCents: 129900,
        stock: 300,
      },
      {
        name: "机械键盘 K87",
        slug: "mech-keyboard-k87",
        description: "87 键三模连接，Gasket 结构，热插拔轴体。",
        priceCents: 39900,
        stock: 150,
      },
    ],
  },
  {
    name: "服饰鞋包",
    slug: "fashion",
    description: "日常穿搭与出行装备",
    products: [
      {
        name: "纯棉印花 T 恤",
        slug: "cotton-print-tee",
        description: "100% 新疆棉，宽松版型，多色可选。",
        priceCents: 7900,
        stock: 500,
      },
      {
        name: "加绒连帽卫衣",
        slug: "hoodie-fleece",
        description: "加厚抓绒内里，秋冬保暖，落肩设计。",
        priceCents: 19900,
        stock: 300,
        featured: true,
      },
      {
        name: "轻便跑步鞋",
        slug: "running-shoes-light",
        description: "回弹中底，透气网面，单只仅 230g。",
        priceCents: 35900,
        stock: 250,
      },
      {
        name: "通勤双肩包",
        slug: "commuter-backpack",
        description: "15.6 英寸电脑仓，防泼水面料，USB 外接充电口。",
        priceCents: 25900,
        stock: 200,
      },
    ],
  },
  {
    name: "家居生活",
    slug: "home",
    description: "让居家更舒适的小物",
    products: [
      {
        name: "护眼台灯 Pro",
        slug: "eye-care-lamp-pro",
        description: "全光谱无频闪，自动感光调光，三档色温。",
        priceCents: 16900,
        stock: 400,
      },
      {
        name: "保温水杯 500ml",
        slug: "thermos-cup-500",
        description: "316 不锈钢内胆，24 小时保温，一键弹盖。",
        priceCents: 8900,
        stock: 600,
      },
      {
        name: "香薰蜡烛礼盒",
        slug: "scented-candle-set",
        description: "大豆蜡手工灌装，三种香型，燃烧 40 小时。",
        priceCents: 12900,
        stock: 150,
        featured: true,
      },
      {
        name: "桌面收纳盒三件套",
        slug: "desk-organizer-set",
        description: "磨砂材质，自由组合，告别桌面杂乱。",
        priceCents: 5900,
        stock: 350,
      },
    ],
  },
  {
    name: "食品生鲜",
    slug: "food",
    description: "精选零食与茶饮",
    products: [
      {
        name: "精品咖啡豆 500g",
        slug: "coffee-beans-500g",
        description: "阿拉比卡中度烘焙，坚果可可风味，下单烘焙。",
        priceCents: 12800,
        stock: 200,
      },
      {
        name: "每日坚果 30 包",
        slug: "daily-nuts-30packs",
        description: "六种坚果科学配比，独立小包锁鲜。",
        priceCents: 9900,
        stock: 400,
      },
      {
        name: "明前龙井茶礼盒",
        slug: "longjing-tea-gift",
        description: "明前采摘一级龙井，礼盒装送礼佳品。",
        priceCents: 26800,
        stock: 120,
        featured: true,
      },
      {
        name: "黑巧克力 85% 礼盒",
        slug: "dark-choco-gift",
        description: "85% 可可含量，低糖配方，12 粒装。",
        priceCents: 6900,
        stock: 300,
      },
    ],
  },
];

async function main() {
  console.log("开始写入种子数据...");

  for (const cat of categories) {
    const category = await prisma.category.upsert({
      where: { slug: cat.slug },
      update: { name: cat.name, description: cat.description },
      create: { name: cat.name, slug: cat.slug, description: cat.description },
    });

    for (const p of cat.products) {
      const product = await prisma.product.upsert({
        where: { slug: p.slug },
        update: {
          name: p.name,
          description: p.description,
          priceCents: p.priceCents,
          stock: p.stock,
          featured: p.featured ?? false,
          categoryId: category.id,
        },
        create: {
          name: p.name,
          slug: p.slug,
          description: p.description,
          priceCents: p.priceCents,
          stock: p.stock,
          featured: p.featured ?? false,
          categoryId: category.id,
        },
      });

      // 每商品 2 张占位图（picsum.photos 按 slug 生成固定图）
      const imageUrls = [
        `https://picsum.photos/seed/${p.slug}/600/600`,
        `https://picsum.photos/seed/${p.slug}-2/600/400`,
      ];
      const existing = await prisma.productImage.count({ where: { productId: product.id } });
      if (existing === 0) {
        await prisma.productImage.createMany({
          data: imageUrls.map((url, i) => ({ url, sortOrder: i, productId: product.id })),
        });
      }
    }
    console.log(`  ✓ 分类「${cat.name}」${cat.products.length} 个商品`);
  }

  // TODO(Phase C)：用户账号 admin/demo/vip 在认证模块落地后补充（经 better-auth 注册以正确哈希密码）
  console.log("种子数据完成（商品与分类）。用户账号待 Phase C 补充后重跑本脚本。");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
