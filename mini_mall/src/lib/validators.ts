// Zod 校验 schema（Server Action 输入校验；客户端可复用）
import { z } from "zod";

/** 下单：购物车项 + 收货信息 */
export const createOrderSchema = z.object({
  items: z
    .array(
      z.object({
        productId: z.string().min(1),
        qty: z.number().int().min(1).max(999),
      })
    )
    .min(1)
    .max(50),
  recipientName: z.string().min(1, "请填写收货人姓名").max(50),
  recipientPhone: z
    .string()
    .regex(/^1\d{10}$/, "手机号格式不正确（11 位，1 开头）"),
  shippingAddress: z.string().min(5, "请填写详细收货地址").max(200),
});

/** 商品创建/更新（金额以元字符串入参，服务端转分） */
export const productSchema = z.object({
  name: z.string().min(1, "商品名不能为空").max(100),
  slug: z
    .string()
    .min(1)
    .max(100)
    .regex(/^[a-z0-9-]+$/, "slug 只能包含小写字母、数字和连字符"),
  description: z.string().max(2000),
  priceYuan: z.string().regex(/^\d+(\.\d{1,2})?$/, "价格格式不正确"),
  stock: z.number().int().min(0).max(1_000_000),
  categoryId: z.string().min(1, "请选择分类"),
  images: z.string().max(2000), // 逗号分隔的图片 URL
  featured: z.boolean().optional(),
});

/** 模拟支付 */
export const mockPaySchema = z.object({
  orderNo: z.string().min(1),
  channel: z.enum(["alipay", "wechat", "unionpay"], {
    message: "请选择支付渠道",
  }),
});

/** 分类创建/更新 */
export const categorySchema = z.object({
  name: z.string().min(1, "分类名不能为空").max(50),
  slug: z
    .string()
    .min(1)
    .max(50)
    .regex(/^[a-z0-9-]+$/, "slug 只能包含小写字母、数字和连字符"),
  description: z.string().max(200).optional().or(z.literal("")),
});
