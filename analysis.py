"""
analysis.py — 关键词提取、内容分类、统计分析

本项目仅供个人学习和内容分析使用。
"""

import re
from collections import Counter
import jieba.analyse
import pandas as pd


# 停用词列表（基础版）
_STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "可以", "这个", "那个", "什么", "怎么", "因为", "所以", "但是", "如果",
    "虽然", "还是", "只是", "不过", "而且", "或者", "然后", "这样", "那样",
    "不是", "就是", "还是", "真的", "非常", "特别", "比较", "有点", "因为",
    "所以", "但是", "可以", "没有", "已经", "通过", "进行", "以及", "因此",
    "其中", "之后", "之前", "目前", "目前", "可能", "能够", "使用", "需要",
    "应该", "这个", "那个", "这些", "那些", "这里", "那里", "时候", "现在",
    "今天", "昨天", "明天", "刚刚", "已经", "一直", "一起", "一样", "一些",
    "每", "年", "月", "日", "还有", "还有", "就是", "不是",
])


def extract_keywords(notes_df, top_n=20):
    """从笔记标题和正文中提取高频关键词

    Args:
        notes_df: 包含 title 和 content 列的 DataFrame
        top_n: 返回前 N 个关键词

    Returns:
        list of (keyword, count) 元组
    """
    texts = []
    for _, row in notes_df.iterrows():
        parts = []
        if row.get("title"):
            parts.append(str(row["title"]))
        if row.get("content"):
            parts.append(str(row["content"]))
        texts.append(" ".join(parts))

    all_text = " ".join(texts)
    if not all_text.strip():
        return []

    # jieba TF-IDF 关键词提取
    keywords_tfidf = jieba.analyse.extract_tags(all_text, topK=top_n * 2, withWeight=True)

    # 词频统计补充
    words = jieba.lcut(all_text)
    words = [w.strip() for w in words if len(w.strip()) >= 2 and w.strip() not in _STOP_WORDS]
    word_freq = Counter(words)

    # 合并两种方法的结果
    result = []
    seen = set()
    for kw, weight in keywords_tfidf:
        if kw not in seen and kw in word_freq:
            result.append((kw, word_freq[kw]))
            seen.add(kw)
        elif kw not in seen:
            result.append((kw, int(weight * 100)))
            seen.add(kw)

    # 补充词频高但 TF-IDF 未覆盖的词
    for word, count in word_freq.most_common(top_n * 3):
        if word not in seen and len(result) < top_n:
            result.append((word, count))
            seen.add(word)

    return result[:top_n]


def classify_note_type(title, content):
    """基于关键词规则对笔记内容类型进行分类

    TODO: 这个规则列表可以通过 UI 自定义扩展
    """
    text = f"{title} {content}".lower()

    rules = [
        ("618攻略", ["618", "618攻略", "618必买", "618清单", "618好物"]),
        ("好物推荐", ["好物", "推荐", "安利", "种草", "值得买", "入手"]),
        ("测评", ["测评", "评测", "实测", "试用", "体验", "使用感受"]),
        ("攻略教程", ["教程", "攻略", "步骤", "方法", "技巧", "怎么", "如何", "指南"]),
        ("省钱", ["省钱", "优惠", "折扣", "满减", "券", "红包", "划算", "性价比"]),
        ("穿搭", ["穿搭", "搭配", "穿衣", "OOTD", "上身", "试穿"]),
        ("美妆", ["化妆", "护肤", "妆容", "眼影", "口红", "粉底", "面膜", "精华"]),
        ("美食", ["美食", "食谱", "做饭", "做菜", "烘焙", "好吃", "零食", "厨房"]),
        ("家居", ["家居", "收纳", "装修", "租房", "改造", "布置", "好物"]),
        ("读书学习", ["书单", "读书", "阅读", "学习", "备考", "考研", "英语", "课程"]),
        ("旅行", ["旅行", "旅游", "攻略", "打卡", "景点", "酒店", "民宿"]),
        ("情感", ["情感", "恋爱", "结婚", "分手", "闺蜜", "朋友", "关系"]),
        ("职场", ["职场", "工作", "面试", "简历", "跳槽", "升职", "副业"]),
        ("李佳琦直播间", ["李佳琦", "佳琦", "直播间"]),
        ("淘宝购物", ["淘宝", "淘到", "购物", "买买买"]),
    ]

    for type_name, keywords in rules:
        for kw in keywords:
            if kw in text:
                return type_name

    return "其他"


def classify_all_notes(notes_df):
    """对 DataFrame 中所有笔记进行内容类型分类"""
    types = notes_df.apply(
        lambda row: classify_note_type(
            row.get("title", ""), row.get("content", "")
        ), axis=1
    )
    return types


def get_type_distribution(notes_df):
    """统计内容类型分布"""
    if "note_type" not in notes_df.columns or notes_df.empty:
        return pd.Series()
    return notes_df["note_type"].value_counts()


def get_engagement_ranking(notes_df, top_n=10):
    """按互动量（点赞+收藏+评论）排序"""
    if notes_df.empty:
        return pd.DataFrame()
    df = notes_df.copy()
    df["engagement"] = df["like_count"] + df["collect_count"] + df["comment_count"]
    return df.sort_values("engagement", ascending=False).head(top_n)


def summarize_viral_patterns(notes_df):
    """分析爆款笔记共性（基于互动量 Top N 笔记）

    这是一个简单的规则版分析，TODO: 后续可以接入 LLM 做更深入的分析
    """
    if notes_df.empty:
        return "暂无数据，请先录入笔记。"

    df = notes_df.copy()
    df["engagement"] = df["like_count"] + df["collect_count"] + df["comment_count"]
    top = df.nlargest(min(5, len(df)), "engagement")

    if len(top) == 0:
        return "暂无足够数据进行分析。"

    insights = ["## 📊 爆款笔记共性分析\n"]

    # 1. 标题分析
    titles = top["title"].tolist()
    title_words = []
    for t in titles:
        if t:
            title_words.extend([w for w in jieba.lcut(t) if len(w) >= 2 and w not in _STOP_WORDS])
    if title_words:
        common_words = Counter(title_words).most_common(5)
        words_str = "、".join([f"「{w}」" for w, _ in common_words])
        insights.append(f"### 标题高频词\nTop 笔记标题中反复出现的词：{words_str}\n")

    # 2. 内容类型分析
    types = top["note_type"].value_counts()
    if not types.empty:
        type_str = "、".join([f"「{t}」({c}篇)" for t, c in types.items()])
        insights.append(f"### 热门内容类型\n爆款笔记主要类型：{type_str}\n")

    # 3. 互动特征
    avg_likes = int(top["like_count"].mean())
    avg_collects = int(top["collect_count"].mean())
    avg_comments = int(top["comment_count"].mean())
    insights.append(f"### 平均互动数据\n")
    insights.append(f"- 平均点赞：{avg_likes}")
    insights.append(f"- 平均收藏：{avg_collects}")
    insights.append(f"- 平均评论：{avg_comments}")
    insights.append(f"- 平均互动总量：{avg_likes + avg_collects + avg_comments}\n")

    # 4. 共性总结
    insights.append("### 共性总结\n")
    if avg_collects > avg_likes * 0.5:
        insights.append("- 📌 **收藏价值高**：收藏量相对于点赞量较高，说明笔记的实用性强，用户愿意保存")
    if avg_comments > 50:
        insights.append("- 💬 **讨论热度高**：评论互动活跃，笔记引发了用户讨论")
    if len(top[top["collect_count"] > avg_collects]) > 2:
        insights.append("- 🏆 **收藏驱动型爆款**：多数爆款笔记以收藏量为主导，内容偏向干货/攻略类")

    insights.append("\n*以上分析基于互动量前 5 篇笔记，仅供参考。*")

    return "\n".join(insights)


def generate_topic_recommendations(notes_df):
    """基于已有笔记数据生成选题建议

    简单规则版，TODO: 接入大模型后可生成更精准的建议
    """
    if notes_df.empty:
        return "暂无数据，请先录入笔记。"

    df = notes_df.copy()
    df["engagement"] = df["like_count"] + df["collect_count"] + df["comment_count"]

    recommendations = ["## 💡 选题建议\n"]

    # 1. 基于高频关键词
    keywords = extract_keywords(df, top_n=10)
    if keywords:
        kw_str = "、".join([kw for kw, _ in keywords[:5]])
        recommendations.append(f"### 热门关键词方向\n")
        recommendations.append(f"以下关键词在你的笔记库中出现频率较高，可考虑围绕它们继续创作：\n")
        recommendations.append(f"**{kw_str}**\n")

    # 2. 基于高互动内容类型
    type_engagement = df.groupby("note_type")["engagement"].mean().sort_values(ascending=False)
    if not type_engagement.empty:
        top_type = type_engagement.index[0]
        recommendations.append(f"### 高互动内容类型\n")
        recommendations.append(f"内容类型「{top_type}」的平均互动量最高，值得继续深耕。\n")

    # 3. 基于组合建议
    recommendations.append("### 尝试方向\n")
    recommendations.append("- 结合热门关键词 + 高互动类型，创作交叉主题内容")
    recommendations.append("- 分析爆款笔记的标题句式，尝试类似结构")
    recommendations.append("- 关注评论区用户提问，挖掘用户的真实需求")

    recommendations.append("\n*以上建议基于已有数据统计生成，仅供参考。*")
    return "\n".join(recommendations)
