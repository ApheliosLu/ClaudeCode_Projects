"""数据结构定义。"""
from dataclasses import dataclass


@dataclass
class Record:
    """一条账目记录，字段顺序与数据库表 records 一致。"""

    id: int | None  # 数据库自动编号；新增时还没有 ID，为 None
    amount: float   # 金额（元）
    category: str   # 6 个预设分类之一
    date: str       # 日期，YYYY-MM-DD
    note: str       # 备注
