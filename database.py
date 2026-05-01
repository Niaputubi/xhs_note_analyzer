"""
database.py — SQLite 数据库初始化与 CRUD 操作

本项目仅供个人学习和内容分析使用。
不涉及任何自动化数据采集，不破解反爬机制。
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "xhs_notes.db")


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库，创建 notes 表（如果不存在）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT '',
            content TEXT DEFAULT '',
            author_name TEXT DEFAULT '',
            like_count INTEGER DEFAULT 0,
            collect_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            publish_time TEXT DEFAULT '',
            url TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            note_type TEXT DEFAULT '',
            my_notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()


def add_note(data):
    """添加一条笔记记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notes (title, content, author_name, like_count,
                           collect_count, comment_count, publish_time,
                           url, tags, note_type, my_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("title", ""),
        data.get("content", ""),
        data.get("author_name", ""),
        int(data.get("like_count", 0)),
        int(data.get("collect_count", 0)),
        int(data.get("comment_count", 0)),
        data.get("publish_time", ""),
        data.get("url", ""),
        data.get("tags", ""),
        data.get("note_type", ""),
        data.get("my_notes", ""),
    ))
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id


def get_all_notes():
    """获取所有笔记，按创建时间倒序"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_note_by_id(note_id):
    """根据 ID 获取单条笔记"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def search_notes(keyword, sort_by="like_count", sort_order="DESC", note_type=None):
    """搜索笔记，支持关键字匹配和排序

    Args:
        keyword: 搜索关键词（匹配标题和正文）
        sort_by: 排序字段
        sort_order: 排序方向 (DESC/ASC)
        note_type: 内容类型筛选
    """
    conn = get_connection()
    cursor = conn.cursor()

    valid_sort_fields = ["like_count", "collect_count", "comment_count",
                         "like_count + collect_count + comment_count", "created_at"]
    sort_field = sort_by if sort_by in valid_sort_fields else "like_count"
    order = "DESC" if sort_order.upper() == "DESC" else "ASC"

    sql = "SELECT * FROM notes WHERE (title LIKE ? OR content LIKE ?)"
    params = [f"%{keyword}%", f"%{keyword}%"]

    if note_type:
        sql += " AND note_type = ?"
        params.append(note_type)

    sql += f" ORDER BY {sort_field} {order}"

    cursor.execute(sql, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_note_types():
    """获取所有已使用的内容类型"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT note_type FROM notes WHERE note_type != '' ORDER BY note_type")
    types = [row["note_type"] for row in cursor.fetchall()]
    conn.close()
    return types


def get_statistics():
    """获取基本统计数据"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM notes")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(like_count), 0) as total_likes FROM notes")
    total_likes = cursor.fetchone()["total_likes"]

    cursor.execute("SELECT COALESCE(SUM(collect_count), 0) as total_collects FROM notes")
    total_collects = cursor.fetchone()["total_collects"]

    cursor.execute("""
        SELECT COALESCE(AVG(like_count + collect_count + comment_count), 0) as avg_engagement
        FROM notes
    """)
    avg_engagement = round(cursor.fetchone()["avg_engagement"], 1)

    cursor.execute("""
        SELECT *, (like_count + collect_count + comment_count) as engagement
        FROM notes ORDER BY engagement DESC LIMIT 5
    """)
    top_notes = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "total_notes": total,
        "total_likes": total_likes,
        "total_collects": total_collects,
        "avg_engagement": avg_engagement,
        "top_notes": top_notes,
    }
