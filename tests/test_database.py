"""
test_database.py — 数据库模块单元测试

本项目仅供个人学习和内容分析使用。
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import (
    get_connection,
    init_database,
    add_note,
    get_all_notes,
    get_note_by_id,
    search_notes,
    get_note_types,
    get_statistics,
    update_note,
    delete_note,
)


# ── Fixtures ──────────────────────────────────────────────

@pytest.fixture(autouse=True)
def use_temp_db():
    """每个测试用例使用独立的临时数据库"""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_path = tmp.name
    tmp.close()

    import database as db_mod
    original_path = db_mod.DB_PATH
    db_mod.DB_PATH = tmp_path

    init_database()

    yield

    db_mod.DB_PATH = original_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def sample_note():
    """一条示例笔记数据"""
    return {
        "title": "618必买清单",
        "content": "今年618要买的东西总结",
        "author_name": "小美",
        "like_count": 100,
        "collect_count": 200,
        "comment_count": 30,
        "publish_time": "2026-05-20",
        "url": "https://example.com/note1",
        "tags": "618,好物推荐",
        "note_type": "618攻略",
        "my_notes": "收藏很高",
    }


@pytest.fixture
def populated_db(sample_note):
    """预填多条数据的数据库"""
    ids = []
    for i in range(5):
        note = sample_note.copy()
        note["title"] = f"测试笔记 {i + 1}"
        note["like_count"] = 100 * (i + 1)
        note["collect_count"] = 50 * (i + 1)
        note["comment_count"] = 10 * (i + 1)
        note["note_type"] = "日常" if i % 2 == 0 else "攻略"
        ids.append(add_note(note))
    return ids


# ── init_database 测试 ──────────────────────────────────

class TestInitDatabase:
    def test_init_creates_table(self):
        """init_database 应创建 notes 表"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_init_is_idempotent(self):
        """多次调用 init_database 应不报错"""
        init_database()
        init_database()
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM notes")
        assert cursor.fetchone()["cnt"] == 0
        conn.close()

    def test_table_has_correct_columns(self):
        """notes 表应包含所有必需的字段"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(notes)")
        columns = {row["name"] for row in cursor.fetchall()}
        conn.close()

        expected = {
            "id", "title", "content", "author_name",
            "like_count", "collect_count", "comment_count",
            "publish_time", "url", "tags", "note_type",
            "my_notes", "created_at",
        }
        assert expected.issubset(columns), f"缺少字段: {expected - columns}"


# ── add_note 测试 ───────────────────────────────────────

class TestAddNote:
    def test_add_note_returns_id(self, sample_note):
        """add_note 应返回新记录的自增 ID"""
        note_id = add_note(sample_note)
        assert isinstance(note_id, int)
        assert note_id > 0

    def test_add_note_increases_count(self, sample_note):
        """添加笔记后总数应增加"""
        count_before = len(get_all_notes())
        add_note(sample_note)
        count_after = len(get_all_notes())
        assert count_after == count_before + 1

    def test_add_note_with_minimal_fields(self):
        """只传必填字段应能正常添加"""
        note_id = add_note({"title": "测试"})
        assert note_id > 0
        note = get_note_by_id(note_id)
        assert note["title"] == "测试"
        assert note["content"] == ""
        assert note["like_count"] == 0

    def test_add_note_persists_all_fields(self, sample_note):
        """所有字段应正确持久化"""
        note_id = add_note(sample_note)
        note = get_note_by_id(note_id)
        for key in sample_note:
            assert note[key] == sample_note[key], f"字段 {key} 不匹配"

    def test_add_note_created_at_auto(self, sample_note):
        """created_at 应自动生成"""
        note_id = add_note(sample_note)
        note = get_note_by_id(note_id)
        assert note["created_at"] is not None
        assert len(note["created_at"]) > 0

    def test_add_note_string_to_int_conversion(self):
        """字符串数字应自动转为整数"""
        note_id = add_note({
            "title": "转换测试",
            "like_count": "500",
            "collect_count": "300",
            "comment_count": "50",
        })
        note = get_note_by_id(note_id)
        assert note["like_count"] == 500
        assert note["collect_count"] == 300
        assert note["comment_count"] == 50


# ── get_note_by_id 测试 ────────────────────────────────

class TestGetNoteById:
    def test_get_existing_note(self, sample_note):
        """应能通过 ID 获取已存在的笔记"""
        note_id = add_note(sample_note)
        note = get_note_by_id(note_id)
        assert note is not None
        assert note["title"] == sample_note["title"]

    def test_get_nonexistent_note(self):
        """不存在的 ID 应返回 None"""
        assert get_note_by_id(99999) is None

    def test_get_returns_dict(self, sample_note):
        """返回值应为 dict 类型"""
        note_id = add_note(sample_note)
        note = get_note_by_id(note_id)
        assert isinstance(note, dict)

    def test_get_note_has_all_fields(self, sample_note):
        """返回的笔记应包含所有字段"""
        note_id = add_note(sample_note)
        note = get_note_by_id(note_id)
        expected_keys = {
            "id", "title", "content", "author_name",
            "like_count", "collect_count", "comment_count",
            "publish_time", "url", "tags", "note_type",
            "my_notes", "created_at",
        }
        assert expected_keys.issubset(note.keys())


# ── get_all_notes 测试 ─────────────────────────────────

class TestGetAllNotes:
    def test_empty_database(self):
        """空数据库应返回空列表"""
        assert get_all_notes() == []

    def test_returns_list_of_dicts(self, populated_db):
        """应返回 dict 列表"""
        notes = get_all_notes()
        assert isinstance(notes, list)
        assert all(isinstance(n, dict) for n in notes)

    def test_returns_all_notes(self, populated_db):
        """应返回全部笔记"""
        notes = get_all_notes()
        assert len(notes) == 5

    def test_ordered_by_created_at_desc(self, populated_db):
        """默认按 created_at 降序排列"""
        notes = get_all_notes()
        timestamps = [n["created_at"] for n in notes]
        assert timestamps == sorted(timestamps, reverse=True)


# ── search_notes 测试 ──────────────────────────────────

class TestSearchNotes:
    def test_search_by_title_keyword(self, populated_db):
        """应能按标题关键词搜索"""
        results = search_notes("测试")
        assert len(results) == 5

    def test_search_by_content_keyword(self, populated_db):
        """应能按正文关键词搜索"""
        results = search_notes("今年618")
        assert len(results) == 5

    def test_search_no_match(self, populated_db):
        """无匹配关键词应返回空列表"""
        results = search_notes("不存在的内容xyz")
        assert results == []

    def test_search_empty_keyword_returns_all(self, populated_db):
        """空关键词应返回全部"""
        results = search_notes("")
        assert len(results) == 5

    def test_search_sort_by_likes(self, populated_db):
        """应支持按点赞数排序"""
        results = search_notes("", sort_by="like_count")
        likes = [r["like_count"] for r in results]
        assert likes == sorted(likes, reverse=True)

    def test_search_sort_ascending(self, populated_db):
        """应支持升序排列"""
        results = search_notes("", sort_by="like_count", sort_order="ASC")
        likes = [r["like_count"] for r in results]
        assert likes == sorted(likes)

    def test_search_sort_by_engagement(self, populated_db):
        """应支持按总互动量排序"""
        results = search_notes("", sort_by="like_count + collect_count + comment_count")
        engagement = [r["like_count"] + r["collect_count"] + r["comment_count"] for r in results]
        assert engagement == sorted(engagement, reverse=True)

    def test_search_filter_by_type(self, populated_db):
        """应支持按内容类型筛选"""
        results = search_notes("", note_type="日常")
        assert all(r["note_type"] == "日常" for r in results)

    def test_search_combined_filter(self, populated_db):
        """关键词 + 类型筛选应同时生效"""
        results = search_notes("测试", note_type="攻略")
        assert len(results) > 0
        assert all(r["note_type"] == "攻略" for r in results)
        assert all("测试" in r["title"] or "测试" in r["content"] for r in results)

    def test_search_partial_title_match(self, populated_db):
        """应支持标题部分匹配"""
        results = search_notes("笔记")
        assert len(results) == 5


# ── get_note_types 测试 ─────────────────────────────────

class TestGetNoteTypes:
    def test_empty_returns_empty_list(self):
        """空数据库应返回空列表"""
        assert get_note_types() == []

    def test_returns_unique_types(self, populated_db):
        """应返回去重后的内容类型"""
        types = get_note_types()
        assert set(types) == {"日常", "攻略"}

    def test_returns_sorted(self, populated_db):
        """返回值应有序"""
        types = get_note_types()
        assert types == sorted(types)


# ── get_statistics 测试 ────────────────────────────────

class TestGetStatistics:
    def test_empty_database(self):
        """空数据库应返回全零统计"""
        stats = get_statistics()
        assert stats["total_notes"] == 0
        assert stats["total_likes"] == 0
        assert stats["total_collects"] == 0
        assert stats["avg_engagement"] == 0.0
        assert stats["top_notes"] == []

    def test_total_counts(self, populated_db):
        """统计数应与实际数据一致"""
        stats = get_statistics()
        assert stats["total_notes"] == 5
        assert stats["total_likes"] == 100 + 200 + 300 + 400 + 500
        assert stats["total_collects"] == 50 + 100 + 150 + 200 + 250

    def test_avg_engagement(self, populated_db):
        """平均互动量应计算正确"""
        stats = get_statistics()
        total = 0
        for i in range(5):
            total += 100 * (i + 1) + 50 * (i + 1) + 10 * (i + 1)
        expected = round(total / 5, 1)
        assert stats["avg_engagement"] == expected

    def test_top_notes_limit(self, populated_db):
        """Top 笔记应只返回 5 条"""
        stats = get_statistics()
        assert len(stats["top_notes"]) == 5

    def test_top_notes_ordered(self, populated_db):
        """Top 笔记应按互动量降序"""
        stats = get_statistics()
        engagement = [n["engagement"] for n in stats["top_notes"]]
        assert engagement == sorted(engagement, reverse=True)

    def test_top_notes_include_engagement_field(self, populated_db):
        """Top 笔记应包含 engagement 字段"""
        stats = get_statistics()
        for note in stats["top_notes"]:
            assert "engagement" in note
            expected = note["like_count"] + note["collect_count"] + note["comment_count"]
            assert note["engagement"] == expected


# ── update_note 测试 ───────────────────────────────────

class TestUpdateNote:
    def test_update_single_field(self, sample_note):
        """应能更新单个字段"""
        note_id = add_note(sample_note)
        result = update_note(note_id, {"title": "更新后的标题"})
        assert result is True
        note = get_note_by_id(note_id)
        assert note["title"] == "更新后的标题"
        assert note["author_name"] == sample_note["author_name"]  # 未变

    def test_update_multiple_fields(self, sample_note):
        """应能同时更新多个字段"""
        note_id = add_note(sample_note)
        result = update_note(note_id, {
            "title": "新标题",
            "content": "新内容",
            "like_count": 999,
        })
        assert result is True
        note = get_note_by_id(note_id)
        assert note["title"] == "新标题"
        assert note["content"] == "新内容"
        assert note["like_count"] == 999

    def test_update_nonexistent_note(self):
        """更新不存在的笔记应返回 False"""
        result = update_note(99999, {"title": "xxx"})
        assert result is False

    def test_update_with_empty_data(self, sample_note):
        """不传更新字段应返回 False"""
        note_id = add_note(sample_note)
        result = update_note(note_id, {})
        assert result is False

    def test_update_partial_fields_unchanged(self, sample_note):
        """未传入的字段应保持不变"""
        note_id = add_note(sample_note)
        update_note(note_id, {"title": "新标题"})
        note = get_note_by_id(note_id)
        assert note["content"] == sample_note["content"]
        assert note["author_name"] == sample_note["author_name"]
        assert note["like_count"] == sample_note["like_count"]


# ── delete_note 测试 ───────────────────────────────────

class TestDeleteNote:
    def test_delete_existing_note(self, sample_note):
        """删除已存在的笔记应返回 True"""
        note_id = add_note(sample_note)
        assert get_note_by_id(note_id) is not None
        result = delete_note(note_id)
        assert result is True
        assert get_note_by_id(note_id) is None

    def test_delete_nonexistent_note(self):
        """删除不存在的笔记应返回 False"""
        result = delete_note(99999)
        assert result is False

    def test_delete_reduces_count(self, sample_note):
        """删除后总数应减少"""
        note_id = add_note(sample_note)
        count_before = len(get_all_notes())
        delete_note(note_id)
        count_after = len(get_all_notes())
        assert count_after == count_before - 1

    def test_delete_is_cascading(self, populated_db):
        """删除应只影响目标记录"""
        count_before = len(get_all_notes())
        delete_note(populated_db[0])
        assert len(get_all_notes()) == count_before - 1
        # 其余笔记应不受影响
        for note_id in populated_db[1:]:
            assert get_note_by_id(note_id) is not None
