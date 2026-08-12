"""SQLite 数据库操作：建表、增删查、统计。

所有函数接收连接对象 conn，由界面层（web.py）负责建立连接。
"""
import sqlite3

from .models import Record

# 建表语句：表已存在时跳过（幂等）
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    note TEXT DEFAULT ''
)
"""


def init_db(conn: sqlite3.Connection) -> None:
    """初始化数据库：建表（已存在则跳过）。"""
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()


def _build_filters(month: str | None, categories: list[str] | None) -> tuple[list[str], list]:
    """把筛选条件拼成 SQL 片段和参数，供列表与统计共用。"""
    conditions: list[str] = []
    params: list = []
    if month:
        conditions.append("substr(date, 1, 7) = ?")
        params.append(month)
    if categories:
        placeholders = ", ".join("?" * len(categories))
        conditions.append(f"category IN ({placeholders})")
        params.extend(categories)
    return conditions, params


def add_record(conn: sqlite3.Connection, record: Record) -> int:
    """新增一条记录，返回新记录的 ID。"""
    cursor = conn.execute(
        "INSERT INTO records (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (record.amount, record.category, record.date, record.note),
    )
    conn.commit()
    return cursor.lastrowid


def list_records(
    conn: sqlite3.Connection,
    month: str | None = None,
    categories: list[str] | None = None,
) -> list[Record]:
    """按月份和分类筛选记录；不传筛选条件则返回全部。"""
    conditions, params = _build_filters(month, categories)
    sql = "SELECT id, amount, category, date, note FROM records"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY date DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    return [
        Record(id=row[0], amount=row[1], category=row[2], date=row[3], note=row[4])
        for row in rows
    ]


def delete_record(conn: sqlite3.Connection, record_id: int) -> bool:
    """按 ID 删除记录；ID 不存在时返回 False。"""
    cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_months(conn: sqlite3.Connection) -> list[str]:
    """返回数据库中出现过的所有月份（YYYY-MM），新的在前。"""
    rows = conn.execute(
        "SELECT DISTINCT substr(date, 1, 7) FROM records ORDER BY 1 DESC"
    ).fetchall()
    return [row[0] for row in rows]


def get_category_stats(
    conn: sqlite3.Connection,
    month: str | None = None,
    categories: list[str] | None = None,
) -> list[dict]:
    """按分类统计笔数和总金额，金额高的在前。"""
    conditions, params = _build_filters(month, categories)
    sql = "SELECT category, COUNT(*) AS count, SUM(amount) AS total FROM records"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " GROUP BY category ORDER BY total DESC"
    rows = conn.execute(sql, params).fetchall()
    return [
        {"category": row[0], "count": row[1], "total": row[2]}
        for row in rows
    ]
