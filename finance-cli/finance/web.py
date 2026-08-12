"""Streamlit 记账工具界面入口。

运行：streamlit run finance/web.py
"""
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from finance.database import (
    add_record,
    delete_record,
    get_category_stats,
    get_months,
    init_db,
    list_records,
)
from finance.models import Record

# 6 个预设分类
CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "居住", "其他"]

# 数据库文件放在项目根目录（finance-cli/expenses.db）
DB_PATH = Path(__file__).resolve().parent.parent / "expenses.db"


def get_conn() -> sqlite3.Connection:
    """新建数据库连接。

    不用缓存：Streamlit 每次交互都在新线程重跑脚本，
    缓存连接会触发 "SQLite objects created in a thread..." 错误。
    """
    return sqlite3.connect(DB_PATH)


def main() -> None:
    st.set_page_config(page_title="记账工具", page_icon="💰")
    st.title("记账工具")

    conn = get_conn()
    try:
        init_db(conn)

        # 月份筛选：当前月排最前，其余来自数据库已有的月份
        this_month = date.today().strftime("%Y-%m")
        month_options = [this_month] + [m for m in get_months(conn) if m != this_month]
        selected_month = st.selectbox("月份", month_options)
        selected_categories = st.multiselect("分类", CATEGORIES, default=CATEGORIES)

        records = list_records(conn, month=selected_month, categories=selected_categories)

        tab_detail, tab_stats = st.tabs(["明细", "统计"])
        with tab_detail:
            render_add_form(conn)
            render_list(conn, records)
        with tab_stats:
            render_stats(conn, selected_month, selected_categories)
    finally:
        conn.close()


def render_add_form(conn: sqlite3.Connection) -> None:
    st.subheader("添加账目")
    # 用 st.form 包起来：点击提交前不会触发页面重跑
    with st.form("add_form"):
        col_amount, col_date = st.columns(2)
        with col_amount:
            amount = st.number_input("金额（元）", min_value=0.01, step=0.01, format="%.2f")
        with col_date:
            expense_date = st.date_input("日期", value=date.today())
        col_category, col_note = st.columns(2)
        with col_category:
            category = st.selectbox("分类", CATEGORIES)
        with col_note:
            note = st.text_input("备注")
        submitted = st.form_submit_button("添加")

    if submitted:
        record = Record(
            id=None,
            amount=amount,
            category=category,
            date=expense_date.isoformat(),  # 转成 YYYY-MM-DD 文本存储
            note=note,
        )
        new_id = add_record(conn, record)
        st.success(f"已添加：{category} ¥{amount:.2f}（ID = {new_id}）")


def render_list(conn: sqlite3.Connection, records: list[Record]) -> None:
    st.subheader("账目列表")
    if not records:
        st.info("当前筛选下暂无记录")
        return

    total = sum(record.amount for record in records)
    col_metric1, col_metric2 = st.columns(2)
    col_metric1.metric("总笔数", len(records))
    col_metric2.metric("总金额", f"¥{total:.2f}")

    df = pd.DataFrame(records).rename(
        columns={"id": "编号", "amount": "金额", "category": "分类", "date": "日期", "note": "备注"}
    )
    df["金额"] = df["金额"].map(lambda x: f"¥{x:.2f}")
    st.dataframe(df, width="stretch", hide_index=True)

    st.subheader("删除账目")
    col_id, col_btn = st.columns([3, 1])
    with col_id:
        delete_id = st.number_input("输入要删除的账目编号", min_value=1, step=1)
    with col_btn:
        st.write("")
        clicked = st.button("删除", type="primary")
    if clicked:
        if delete_record(conn, delete_id):
            st.success(f"已删除编号 {delete_id}")
        else:
            st.warning(f"编号 {delete_id} 不存在")


def render_stats(conn: sqlite3.Connection, month: str, categories: list[str]) -> None:
    st.subheader("分类统计")
    stats = get_category_stats(conn, month=month, categories=categories)
    if not stats:
        st.info("当前筛选下暂无数据")
        return

    df = pd.DataFrame(stats).rename(
        columns={"category": "分类", "count": "笔数", "total": "总金额"}
    )
    df["占比"] = (df["总金额"] / df["总金额"].sum() * 100).round(1).astype(str) + "%"

    st.bar_chart(df, x="分类", y="总金额")

    # 追加合计行后展示（图表用的是合计前的数据）
    total_row = pd.DataFrame([{
        "分类": "合计",
        "笔数": df["笔数"].sum(),
        "总金额": df["总金额"].sum(),
        "占比": "100%",
    }])
    df_with_total = pd.concat([df, total_row], ignore_index=True)
    df_with_total["总金额"] = df_with_total["总金额"].map(lambda x: f"¥{x:.2f}")
    st.dataframe(df_with_total, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
