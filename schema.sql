/*

本项目仅供个人学习和内容分析使用。

- 不涉及任何自动化数据采集
- 不破解任何反爬机制
- 不使用任何方式登录小红书平台
- 不存储任何敏感个人信息
- 所有数据通过手动录入方式获得
- 禁止用于商业用途或批量采集

*/

-- notes 表：存储手动录入的小红书公开笔记信息
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL DEFAULT '',              -- 笔记标题
    content TEXT DEFAULT '',                     -- 笔记正文
    author_name TEXT DEFAULT '',                 -- 作者昵称
    like_count INTEGER DEFAULT 0,                -- 点赞数
    collect_count INTEGER DEFAULT 0,             -- 收藏数
    comment_count INTEGER DEFAULT 0,             -- 评论数
    publish_time TEXT DEFAULT '',                -- 发布时间 (YYYY-MM-DD)
    url TEXT DEFAULT '',                         -- 笔记链接
    tags TEXT DEFAULT '',                        -- 标签，逗号分隔
    note_type TEXT DEFAULT '',                   -- 内容类型
    my_notes TEXT DEFAULT '',                    -- 我的备注
    created_at TEXT DEFAULT (datetime('now', 'localtime'))  -- 录入时间
);
