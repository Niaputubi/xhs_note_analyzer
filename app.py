"""
app.py — Streamlit 多页面主入口

本项目仅供个人学习和内容分析使用。
- 不涉及任何自动化数据采集
- 不破解任何反爬机制
- 不使用任何方式登录小红书平台
- 所有数据通过手动录入方式获得
- 禁止用于商业用途或批量采集

运行方式：streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database import (
    init_database, add_note, get_all_notes, get_note_by_id,
    search_notes, get_note_types, get_statistics,
)
from analysis import (
    extract_keywords, classify_note_type, get_type_distribution,
    get_engagement_ranking, summarize_viral_patterns,
    generate_topic_recommendations,
)
from ai_analyzer import analyze_note

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="xhs 笔记分析工具",
    page_icon="📒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 加载自定义样式 ────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── 初始化数据库 ──────────────────────────────────────────
init_database()

# ── 导航 ──────────────────────────────────────────────────
st.sidebar.markdown("# 📒 xhs 笔记分析")
st.sidebar.markdown("*个人学习·选题参考工具*")
st.sidebar.divider()

page = st.sidebar.radio(
    "导航",
    ["📊 首页概览", "✏️ 新增笔记", "📋 笔记列表", "📈 内容分析"],
)

st.sidebar.divider()
st.sidebar.caption(
    "⚠️ 本项目仅供个人学习\n"
    "不涉及自动化采集\n"
    "不破解反爬机制\n"
    "所有数据手动录入"
)


# ══════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════

def render_stat_card(value, label, css_class="stat-card"):
    """渲染统计卡片"""
    st.markdown(
        f'<div class="{css_class}">'
        f'  <div class="stat-value">{value}</div>'
        f'  <div class="stat-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_note_card(note):
    """渲染单篇笔记卡片"""
    tags_html = "".join(
        f'<span class="tag">{tag.strip()}</span>'
        for tag in note.get("tags", "").split(",")
        if tag.strip()
    )
    st.markdown(
        f'<div class="note-card">'
        f'  <h3>{note["title"]}</h3>'
        f'  <div class="meta">👤 {note["author_name"]}　📅 {note["publish_time"]}</div>'
        f'  {tags_html}'
        f'  <div class="stats">'
        f'    <span>❤️ {note["like_count"]}</span>'
        f'    <span>⭐ {note["collect_count"]}</span>'
        f'    <span>💬 {note["comment_count"]}</span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════
# 页面 1：首页概览
# ══════════════════════════════════════════════════════════
if page == "📊 首页概览":
    st.title("📊 数据概览")

    stats = get_statistics()

    # ── 统计卡片行 ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_stat_card(stats["total_notes"], "已录入笔记", "stat-card stat-card-green")
    with col2:
        render_stat_card(f'{stats["total_likes"]:,}', "总点赞", "stat-card stat-card-orange")
    with col3:
        render_stat_card(f'{stats["total_collects"]:,}', "总收藏", "stat-card stat-card-blue")
    with col4:
        render_stat_card(stats["avg_engagement"], "平均互动", "stat-card")

    # ── Top 5 ──
    st.subheader("🏆 互动量 TOP 5")
    if stats["top_notes"]:
        for note in stats["top_notes"]:
            render_note_card(note)
    else:
        st.info("暂无笔记数据，请在「新增笔记」页录入。")

    # ── 快速操作 ──
    st.subheader("🚀 快速操作")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✏️ 新增一篇笔记", use_container_width=True):
            st.switch_page("app.py?page=新增笔记")
    with c2:
        if st.button("📈 查看分析报告", use_container_width=True):
            st.switch_page("app.py?page=内容分析")


# ══════════════════════════════════════════════════════════
# 页面 2：新增笔记
# ══════════════════════════════════════════════════════════
elif page == "✏️ 新增笔记":
    st.title("✏️ 新增笔记")
    st.caption("手动录入一篇小红书公开笔记的信息。所有数据来自你阅读公开页面后手动填写。")

    with st.form("note_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            url = st.text_input("🔗 笔记链接", placeholder="https://www.xiaohongshu.com/...")
            title = st.text_input("📌 标题 *", placeholder="笔记标题")
            author_name = st.text_input("👤 作者昵称", placeholder="作者昵称")
            publish_time = st.date_input("📅 发布时间")
            note_type = st.selectbox(
                "🏷️ 内容类型",
                ["", "618攻略", "好物推荐", "测评", "攻略教程", "省钱",
                 "穿搭", "美妆", "美食", "家居", "读书学习", "旅行",
                 "情感", "职场", "李佳琦直播间", "淘宝购物", "其他"],
            )

        with col2:
            like_count = st.number_input("❤️ 点赞数", min_value=0, value=0, step=1)
            collect_count = st.number_input("⭐ 收藏数", min_value=0, value=0, step=1)
            comment_count = st.number_input("💬 评论数", min_value=0, value=0, step=1)
            tags = st.text_input("🏷️ 标签（逗号分隔）", placeholder="标签1, 标签2, 标签3")

        content = st.text_area("📝 正文", placeholder="粘贴或输入笔记正文内容...", height=200)
        my_notes = st.text_area("📎 我的备注", placeholder="记下你的想法、灵感、可借鉴的点...", height=100)

        submitted = st.form_submit_button("💾 保存笔记", use_container_width=True, type="primary")

        if submitted:
            if not title.strip():
                st.error("标题不能为空！")
            else:
                data = {
                    "url": url,
                    "title": title,
                    "content": content,
                    "author_name": author_name,
                    "like_count": like_count,
                    "collect_count": collect_count,
                    "comment_count": comment_count,
                    "publish_time": publish_time.strftime("%Y-%m-%d"),
                    "tags": tags,
                    "note_type": note_type or classify_note_type(title, content),
                    "my_notes": my_notes,
                }
                note_id = add_note(data)
                st.success(f"✅ 笔记「{title}」已保存（ID: {note_id}）")

    # ── 最近添加 ──
    st.divider()
    st.subheader("📄 最近录入")
    all_notes = get_all_notes()
    if all_notes:
        recent = all_notes[:5]
        for note in recent:
            render_note_card(note)
    else:
        st.info("还没有笔记，在上方表单录入第一篇吧！")


# ══════════════════════════════════════════════════════════
# 页面 3：笔记列表
# ══════════════════════════════════════════════════════════
elif page == "📋 笔记列表":
    st.title("📋 笔记列表")

    # ── 搜索与筛选 ──
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        keyword = st.text_input("🔍 搜索标题/正文", placeholder="输入关键词...")
    with col2:
        sort_options = {
            "like_count": "按点赞数",
            "collect_count": "按收藏数",
            "comment_count": "按评论数",
            "like_count + collect_count + comment_count": "按总互动量",
        }
        sort_by = st.selectbox("排序", options=list(sort_options.keys()), format_func=lambda x: sort_options[x])
    with col3:
        types_options = [""] + get_note_types()
        type_filter = st.selectbox("内容类型", options=types_options, format_func=lambda x: x if x else "全部")

    # ── 获取数据 ──
    notes = search_notes(keyword or "", sort_by=sort_by, note_type=type_filter or None)

    st.caption(f"共 {len(notes)} 条笔记")

    if notes:
        for note in notes:
            with st.container():
                cols = st.columns([4, 1])
                with cols[0]:
                    render_note_card(note)
                with cols[1]:
                    if st.button("查看详情 →", key=f"detail_{note['id']}"):
                        st.session_state["detail_note_id"] = note["id"]
                        st.switch_page("app.py?page=detail")
    else:
        st.info("未找到匹配的笔记。")

    # ── 详情弹窗（利用 session_state） ──
    if "detail_note_id" in st.session_state and st.session_state["detail_note_id"]:
        note_id = st.session_state["detail_note_id"]
        note = get_note_by_id(note_id)
        if note:
            with st.expander("📖 笔记详情", expanded=True):
                render_note_detail(note)
                if st.button("关闭详情"):
                    st.session_state["detail_note_id"] = None
                    st.rerun()


# ══════════════════════════════════════════════════════════
# 页面 4：内容分析
# ══════════════════════════════════════════════════════════
elif page == "📈 内容分析":
    st.title("📈 内容分析")

    all_notes = get_all_notes()
    if not all_notes:
        st.info("暂无数据，请先录入笔记。")
        st.stop()

    df = pd.DataFrame(all_notes)

    # ── Tab 布局 ──
    tab1, tab2, tab3, tab4 = st.tabs(["🔤 关键词分析", "📊 内容类型", "🏆 互动排行", "💡 AI 总结"])

    # ── Tab 1：关键词分析 ──
    with tab1:
        st.subheader("高频关键词 Top 20")
        keywords = extract_keywords(df, top_n=20)
        if keywords:
            kw_df = pd.DataFrame(keywords, columns=["关键词", "出现次数"])
            fig = px.bar(
                kw_df.sort_values("出现次数"),
                x="出现次数",
                y="关键词",
                orientation="h",
                height=500,
                color="出现次数",
                color_continuous_scale="Viridis",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 关键词列表"):
                st.dataframe(kw_df, use_container_width=True, hide_index=True)
        else:
            st.info("词数不足，无法提取关键词。")

    # ── Tab 2：内容类型分布 ──
    with tab2:
        st.subheader("内容类型分布")
        type_dist = get_type_distribution(df)
        if not type_dist.empty:
            type_df = type_dist.reset_index()
            type_df.columns = ["内容类型", "笔记数量"]

            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(type_df, values="笔记数量", names="内容类型", height=400)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.bar(
                    type_df.sort_values("笔记数量"),
                    x="笔记数量",
                    y="内容类型",
                    orientation="h",
                    height=400,
                    color="笔记数量",
                    color_continuous_scale="Blues",
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无分类数据。")

    # ── Tab 3：互动排行 ──
    with tab3:
        st.subheader("互动数据排行榜")
        ranked = get_engagement_ranking(df, top_n=10)
        if not ranked.empty:
            fig = px.bar(
                ranked,
                x="engagement",
                y="title",
                orientation="h",
                height=500,
                color="engagement",
                color_continuous_scale="Reds",
                labels={"engagement": "总互动量", "title": "笔记标题"},
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                ranked[["title", "like_count", "collect_count", "comment_count", "engagement"]]
                .rename(columns={
                    "title": "标题", "like_count": "点赞",
                    "collect_count": "收藏", "comment_count": "评论",
                    "engagement": "总互动",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("数据不足。")

    # ── Tab 4：AI 总结 ──
    with tab4:
        st.subheader("💡 爆款共性分析")

        viral_summary = summarize_viral_patterns(df)
        st.markdown(
            f'<div class="insight-box">{viral_summary}</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        st.subheader("选题建议")
        recommendations = generate_topic_recommendations(df)
        st.markdown(
            f'<div class="insight-box">{recommendations}</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════
# 笔记详情渲染（复用组件）
# ══════════════════════════════════════════════════════════
def render_note_detail(note):
    """渲染单篇笔记的完整详情 + AI 分析"""
    st.markdown(f'<div class="detail-label">标题</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detail-value">{note["title"]}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="detail-label">作者</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{note["author_name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-label">发布时间</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{note["publish_time"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-label">内容类型</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{note["note_type"]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="detail-label">互动数据</div>', unsafe_allow_html=True)
        total = int(note["like_count"]) + int(note["collect_count"]) + int(note["comment_count"])
        st.markdown(
            f'<div class="detail-value">'
            f'❤️ {note["like_count"]}　'
            f'⭐ {note["collect_count"]}　'
            f'💬 {note["comment_count"]}　'
            f'📊 总互动 {total}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="detail-label">链接</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{note["url"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-label">标签</div>', unsafe_allow_html=True)
        tags_html = "".join(
            f'<span class="tag">{tag.strip()}</span>'
            for tag in note.get("tags", "").split(",") if tag.strip()
        )
        st.markdown(f'<div class="detail-value">{tags_html}</div>', unsafe_allow_html=True)

    if note.get("content"):
        st.markdown(f'<div class="detail-label">正文</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{note["content"]}</div>', unsafe_allow_html=True)

    if note.get("my_notes"):
        st.markdown(f'<div class="detail-label">我的备注</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{note["my_notes"]}</div>', unsafe_allow_html=True)

    # ── AI 分析 ──
    st.divider()
    st.subheader("🤖 AI 分析")

    with st.spinner("正在分析..."):
        analysis = analyze_note(note)

    if analysis:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f'<div class="insight-box">'
                f'<h4>🔥 受欢迎原因</h4>'
                f'{analysis.get("popularity_reason", "暂无分析")}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="insight-box">'
                f'<h4>🎯 标题亮点</h4>'
                f'{analysis.get("title_highlight", "暂无分析")}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="insight-box">'
                f'<h4>📐 内容结构</h4>'
                f'{analysis.get("content_structure", "暂无分析")}'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="insight-box">'
                f'<h4>💎 价值类型</h4>'
                f'{analysis.get("value_type", "暂无分析")}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="insight-box">'
                f'<h4>📝 借鉴建议</h4>'
                f'{analysis.get("how_to_learn", "暂无分析")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        extend_topics = analysis.get("extend_topics", [])
        if extend_topics:
            st.markdown(
                f'<div class="insight-box">'
                f'<h4>🚀 可延展的选题方向</h4>'
                + "<br>".join(f"- {t}" for t in extend_topics[:8])
                + f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("分析数据不足。")

    # TODO: 接入大模型 API 后，在此添加切换开关
    with st.expander("⚙️ 关于 AI 分析"):
        st.caption(
            "当前分析基于本地规则引擎，分析维度包括：标题关键词、互动数据比例、内容长度和结构等。\n\n"
            "TODO: 后续可接入大模型 API（通义千问 / DeepSeek / OpenAI），"
            "在项目根目录配置 .env 文件即可启用。"
        )


# ── 处理从笔记列表跳转过来的详情 ──
if "detail_note_id" in st.session_state and st.session_state["detail_note_id"] and page != "📋 笔记列表":
    note_id = st.session_state["detail_note_id"]
    note = get_note_by_id(note_id)
    if note:
        st.title("📖 笔记详情")
        if st.button("← 返回列表"):
            st.session_state["detail_note_id"] = None
            st.rerun()
        render_note_detail(note)
