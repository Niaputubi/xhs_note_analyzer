"""
ai_analyzer.py — AI 分析模块

当前实现：本地规则版分析。
TODO: 后续可接入大模型 API（通义千问 / DeepSeek / OpenAI 等）。

本项目仅供个人学习和内容分析使用。
"""

import os
from datetime import datetime


def analyze_note(note):
    """对单篇笔记进行 AI 分析（规则版）

    输出字段：
    - popularity_reason: 为什么可能受欢迎
    - title_highlight: 标题亮点
    - content_structure: 内容结构
    - value_type: 情绪价值 / 实用价值
    - how_to_learn: 如何借鉴
    - extend_topics: 可延展的选题方向

    TODO: 接入大模型后替换此函数为 API 调用
    """
    if not note:
        return {}

    title = note.get("title", "")
    content = note.get("content", "")
    like_count = int(note.get("like_count", 0))
    collect_count = int(note.get("collect_count", 0))
    comment_count = int(note.get("comment_count", 0))

    engagement = like_count + collect_count + comment_count

    analysis = {
        "popularity_reason": _analyze_popularity(title, content, like_count, collect_count, comment_count),
        "title_highlight": _analyze_title(title),
        "content_structure": _analyze_structure(content),
        "value_type": _analyze_value_type(title, content),
        "how_to_learn": _generate_suggestions(title, content, engagement),
        "extend_topics": _generate_extend_topics(title, content),
    }

    return analysis


def _analyze_popularity(title, content, likes, collects, comments):
    """分析笔记受欢迎的原因"""
    reasons = []
    total = likes + collects + comments

    if total == 0:
        return "暂无互动数据，无法分析。"

    # 基于互动比例分析
    if collects > 0 and likes > 0 and collects / likes > 0.8:
        reasons.append("收藏量接近点赞量，说明内容具有很高的实用保存价值，很可能是攻略/清单类内容。")

    if comments > 50:
        reasons.append("评论互动活跃，说明内容引发了用户的讨论或共鸣。")

    if likes > 1000:
        reasons.append("点赞量超过 1000，属于高曝光内容，说明标题/封面吸引力强。")

    if collects > 500:
        reasons.append("收藏量超过 500，内容被大量用户保存，干货属性明显。")

    # 基于标题内容分析
    title_lower = title.lower()
    if any(w in title_lower for w in ["必看", "必买", "必备", "推荐", "清单", "合集"]):
        reasons.append("标题使用了"清单/推荐"类关键词，精准命中用户搜索意图。")

    if any(w in title_lower for w in ["后悔", "别买", "避雷", "踩雷", "别花"]):
        reasons.append("标题使用"避雷/省钱"类关键词，利用了用户的损失厌恶心理。")

    if any(w in title_lower for w in ["绝了", "绝绝子", "封神", "天花板", "太", "很", "超"]):
        reasons.append("标题使用了强情绪词汇，增强吸引力和点击欲望。")

    if any(w in title_lower for w in ["数字", "方法", "步骤", "教程", "教你"]):
        reasons.append("标题包含"教程/方法"类词，用户愿意保存以便后续参考。")

    if not reasons:
        reasons.append("该笔记的互动数据表现平稳，建议优化标题和封面。")

    return " ".join(reasons)


def _analyze_title(title):
    """分析标题亮点"""
    if not title:
        return "标题为空，建议添加有吸引力的标题。"

    highlights = []
    title_len = len(title)

    # 标题长度
    if 15 <= title_len <= 30:
        highlights.append(f"标题长度适中（{title_len}字），在搜索结果中能完整显示。")
    elif title_len < 15:
        highlights.append(f"标题较短（{title_len}字），建议适当增加关键词。")
    else:
        highlights.append(f"标题较长（{title_len}字），要注意核心信息前置。")

    # 是否包含数字
    if any(c.isdigit() for c in title):
        highlights.append("包含数字，能增强具体感和可信度。")
    else:
        highlights.append("建议加入数字（如数量、年份、价格等）增强说服力。")

    # 是否包含情绪词
    emotion_words = ["绝", "太", "超", "很", "超好", "无敌", "封神", "天花板", "yyds"]
    if any(w in title for w in emotion_words):
        highlights.append("包含情绪化表达，有助于激发点击欲望。")

    # 是否包含关键词
    if "推荐" in title or "必" in title:
        highlights.append("使用"推荐/必"类字眼，命中用户决策参考需求。")

    if "?" in title or "?" in title or "怎么" in title or "如何" in title:
        highlights.append("采用疑问句句式，激发用户好奇心，提高点击率。")

    return " ".join(highlights)


def _analyze_structure(content):
    """分析内容结构"""
    if not content:
        return "正文内容为空。"

    lines = content.strip().split("\n")
    lines = [l.strip() for l in lines if l.strip()]

    if len(lines) <= 3:
        return f"正文简短（共{len(lines)}段），适合快速阅读，但信息量可能不足。"

    # 检查是否有数字列表
    has_numbered = any(l[0].isdigit() for l in lines if l)
    has_dash = any(l.startswith("-") for l in lines)
    has_emoji = any("" in l for l in lines)

    parts = []
    parts.append(f"正文共 {len(lines)} 段，信息量充足。")

    if has_numbered:
        parts.append("使用了数字列表结构，层次清晰，便于读者快速定位信息。")
    if has_dash:
        parts.append("使用了列表符号，信息组织有序。")
    if has_emoji:
        parts.append("使用了 emoji 分隔/装饰，增强可读性和视觉层次。")

    # 估算字数
    total_chars = sum(len(l) for l in lines)
    if total_chars > 500:
        parts.append(f"正文字数约 {total_chars}，属于详细攻略型内容。")
    else:
        parts.append(f"正文字数约 {total_chars}，属于轻量快速阅读内容。")

    return " ".join(parts)


def _analyze_value_type(title, content):
    """判断内容的价值类型（情绪价值 / 实用价值）"""
    text = f"{title} {content}"

    # 实用价值关键词
    practical_words = ["方法", "教程", "步骤", "攻略", "清单", "推荐",
                       "测评", "对比", "价格", "省钱", "优惠", "技巧"]
    # 情绪价值关键词
    emotional_words = ["绝了", "哭了", "感动", "温暖", "治愈", "焦虑",
                       "纠结", "后悔", "开心", "快乐", "心情", "分享"]

    text_lower = text.lower()
    practical_score = sum(1 for w in practical_words if w in text_lower)
    emotional_score = sum(1 for w in emotional_words if w in text_lower)

    if practical_score > emotional_score:
        return "📌 **实用价值型** — 以提供具体方法/攻略/推荐为主，读者主要为了获取有用信息而阅读。"
    elif emotional_score > practical_score:
        return "💖 **情绪价值型** — 以引发情感共鸣为主，读者主要为获得情感体验或认同感而阅读。"
    else:
        return "📌 **综合型** — 兼具实用价值和情绪价值，是最常见的内容类型。"


def _generate_suggestions(title, content, engagement):
    """生成借鉴建议"""
    suggestions = []

    if not title:
        suggestions.append("建议撰写一个包含关键词的标题，长度在 15-30 字之间。")
    else:
        suggestions.append("保持标题的结构风格，尝试在不同主题上复用类似的标题句式。")

    if engagement > 500:
        suggestions.append("该笔记表现优秀，可以形成系列内容，持续输出相似主题。")
    elif engagement > 100:
        suggestions.append("该笔记有一定潜力，可以在此基础上增加更多实用信息，提升收藏量。")
    else:
        suggestions.append("可以尝试调整标题句式、增加关键词密度，或参考爆款笔记的选题方向。")

    suggestions.append("关注评论区中读者的提问，这些是下一期内容的天然选题来源。")

    return " ".join(suggestions)


def _generate_extend_topics(title, content):
    """生成可延展的选题方向"""
    text = f"{title} {content}"

    topics = []
    text_lower = text.lower()

    # 基于关键词生成延展方向
    kw_topic_map = [
        ("618", ["双11攻略", "双12必买", "年终购物清单", "大促囤货指南"]),
        ("测评", ["长期使用反馈", "同类产品横向对比", "平替推荐", "避雷合集"]),
        ("护肤", ["成分解析", "不同肤质方案", "平价/贵妇对比", "换季护肤"]),
        ("美妆", ["新手化妆教程", "通勤妆", "约会妆", "化妆品铁皮分享"]),
        ("穿搭", ["胶囊衣橱", "一衣多穿", "通勤穿搭", "季节穿搭合集"]),
        ("美食", ["一周食谱", "懒人快手菜", "减脂餐", "零食测评"]),
        ("家居", ["租房改造", "收纳技巧", "好物分享", "DIY改造"]),
        ("学习", ["学习计划表", "工具推荐", "经验分享", "书单合集"]),
        ("省钱", ["攒钱方法", "记账技巧", "优惠攻略", "二手好物"]),
        ("攻略", ["新手入门指南", "进阶技巧", "常见问题解答", "资源合集"]),
    ]

    for kw, suggestions in kw_topic_map:
        if kw in text_lower:
            topics.extend(suggestions)

    if not topics:
        topics = ["同主题系列化内容", "读者问答/互动内容", "不同场景下的应用",
                  "与其他品牌/产品对比", "使用心得长期更新"]

    return topics


# ============================================================
# 大模型 API 预留接口
# ============================================================

# TODO: 接入大模型 API
# 本模块当前为纯规则实现，后续可以通过配置环境变量来启用 LLM 分析。
#
# 使用方式（以通义千问为例）：
#   1. 在项目根目录创建 .env 文件，添加：
#      LLM_API_KEY=your_api_key
#      LLM_MODEL=qwen-plus  # 或其他模型
#      LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
#
#   2. 安装 openai 库：pip install openai
#
#   3. 取消下面代码的注释，并在 analyze_note 中添加 LLM 分支


def analyze_note_with_llm(note):
    """使用大模型分析笔记（预留接口）

    使用前需要：
    - pip install openai python-dotenv
    - 在 .env 中配置 LLM_API_KEY
    """
    try:
        from openai import OpenAI
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        if not api_key:
            return None  # 未配置 API key，回退到规则版

        client = OpenAI(api_key=api_key, base_url=api_base)

        prompt = f"""请分析以下小红书笔记，输出 JSON 格式的分析结果。

笔记标题：{note.get('title', '')}
笔记正文：{note.get('content', '')}
点赞数：{note.get('like_count', 0)}
收藏数：{note.get('collect_count', 0)}
评论数：{note.get('comment_count', 0)}

请输出包含以下字段的 JSON：
{{
    "popularity_reason": "这篇笔记受欢迎/不温不火的原因分析",
    "title_highlight": "标题的亮点分析和优化建议",
    "content_structure": "内容结构分析",
    "value_type": "情绪价值/实用价值判断及理由",
    "how_to_learn": "我可以如何借鉴",
    "extend_topics": ["延展选题1", "延展选题2", "延展选题3", "延展选题4", "延展选题5"]
}}
"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        import json
        result = json.loads(response.choices[0].message.content)
        return result

    except ImportError:
        return None  # 依赖未安装，回退到规则版
    except Exception as e:
        return {"error": f"LLM API 调用失败: {str(e)}"}
