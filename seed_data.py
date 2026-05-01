"""
seed_data.py — 初始化数据库并插入示例笔记数据

运行方式：python seed_data.py

本项目仅供个人学习和内容分析使用。
数据均为虚构示例，不涉及真实用户信息。
"""

from database import init_database, add_note


SAMPLE_NOTES = [
    {
        "title": "618必买清单｜这些好物我真的会谢",
        "content": ""618快到了，整理了一份我回购最多次的好物清单
1. 洗面奶：氨基酸配方温和不刺激
2. 精华液：提亮效果明显，用了一个月肤色均匀了很多
3. 身体乳：清爽不黏腻，夏天用刚好
4. 防晒霜：SPF50+高倍防晒，成膜快不假白
5. 护发精油：一抹顺滑，毛躁星人的救星
这些都是我用了至少半年以上才推荐的好物，姐妹们可以放心冲！""",
        "author_name": "小美的购物车",
        "like_count": 2847,
        "collect_count": 3521,
        "comment_count": 356,
        "publish_time": "2026-05-20",
        "url": "https://www.xiaohongshu.com/explore/example001",
        "tags": "618,好物推荐,购物清单,必买",
        "note_type": "618攻略",
        "my_notes": "收藏量很高，标题用了\"真的会谢\"这种网络流行语增加亲近感",
    },
    {
        "title": "李佳琦直播间618攻略｜什么时候买最划算？",
        "content": ""整理了李佳琦直播间618各阶段的时间节点
【预售期】
- 5月26日晚8点：付定金
- 6月1日-3日：付尾款
【现货期】
- 6月4日-13日：各类目专场
- 6月14日-18日：最后狂欢

建议大家重点关注：
1. 大牌美妆：预售期最划算
2. 生活日用品：现货期慢慢挑
3. 家电数码：618当天可能有惊喜价""",
        "author_name": "省钱小能手",
        "like_count": 5621,
        "collect_count": 8234,
        "comment_count": 892,
        "publish_time": "2026-05-22",
        "url": "https://www.xiaohongshu.com/explore/example002",
        "tags": "李佳琦,618,攻略,省钱",
        "note_type": "618攻略",
        "my_notes": "时间线梳理得非常清晰，适合作为攻略模板",
    },
    {
        "title": "租房改造｜200元搞定出租屋氛围感",
        "content": ""分享我的低成本租房改造方案
客厅：
- 暖色调灯带 35元
- 仿真绿植 28元
- 地毯 60元
卧室：
- 四件套 79元
- 床头灯 45元
- 墙贴装饰 20元
总花费不到200块，租房党也能有温馨的小家！
改造前后对比图在最后""",
        "author_name": "家居改造日记",
        "like_count": 12340,
        "collect_count": 15600,
        "comment_count": 1245,
        "publish_time": "2026-04-15",
        "url": "https://www.xiaohongshu.com/explore/example003",
        "tags": "出租屋,改造,家居,省钱",
        "note_type": "家居",
        "my_notes": "爆款笔记，改造前后对比是核心吸引力，价格明细增加可信度",
    },
    {
        "title": "考研英语85分｜我用过的神仙资料合集",
        "content": ""二战上岸985，英语从60提到85，这些资料功不可没！
【单词】
- 红宝书：基础阶段必备
- 墨墨背单词APP：利用碎片时间
【阅读】
- 张剑黄皮书：真题解析yyds
- 唐迟阅读课：逻辑分析很强
【作文】
- 王江涛高分写作：模板背起来
- 石雷鹏押题：考前必看
【翻译&完形】
- 唐静翻译课：拆分长难句
- 宋逸轩完形：技巧型""",
        "author_name": "学习博主小李",
        "like_count": 8920,
        "collect_count": 12500,
        "comment_count": 678,
        "publish_time": "2026-03-10",
        "url": "https://www.xiaohongshu.com/explore/example004",
        "tags": "考研,英语,学习,备考",
        "note_type": "读书学习",
        "my_notes": "资料整理类笔记收藏量非常高，可以学习这种分类呈现方式",
    },
    {
        "title": "别乱买｜平价面膜红黑榜测评",
        "content": ""用了一年平价面膜，给大家分享真实的红黑榜
红榜：
1. 某日记玻尿酸面膜 补水效果巨好
2. 某叶修护面膜 敏感肌可用
3. 某石碳酸面膜 清洁力棒
黑榜：
1. 某森林海藻面膜 根本不吸收
2. 某女王面膜 香精味太重
3. 某园蜂蜜面膜 黏糊糊的

以上纯属个人使用感受，不同肤质效果可能不一样""",
        "author_name": "护肤达人小圆",
        "like_count": 4560,
        "collect_count": 5200,
        "comment_count": 890,
        "publish_time": "2026-02-28",
        "url": "https://www.xiaohongshu.com/explore/example005",
        "tags": "面膜,测评,护肤,红黑榜",
        "note_type": "测评",
        "my_notes": "红黑榜对比形式很有说服力，能引发评论区讨论",
    },
    {
        "title": "上班带饭一周不重样｜30分钟备菜攻略",
        "content": ""打工人如何高效准备一周午餐？
【备菜日：周日晚上】
1. 肉类预处理：切好分装冷冻
2. 蔬菜洗净切好：密封冷藏
3. 酱料调好：分装小盒
【每日搭配模板】
周一：鸡胸肉+西兰花+杂粮饭
周二：牛肉+西兰花+紫薯
周三：虾仁+沙拉+荞麦面
周四：豆腐+时蔬+糙米
周五：三文鱼+芦笋+藜麦

每餐成本不到15块，比外卖省钱又健康""",
        "author_name": "健康饮食日记",
        "like_count": 6780,
        "collect_count": 9200,
        "comment_count": 456,
        "publish_time": "2026-05-01",
        "url": "https://www.xiaohongshu.com/explore/example006",
        "tags": "带饭,食谱,省钱,健康",
        "note_type": "美食",
        "my_notes": "模板化内容，读者可以直接抄作业，收藏率非常高",
    },
    {
        "title": "毕业三年存款30w｜普通女孩的攒钱心得",
        "content": ""普通二本毕业，工资从5k到1.5w，分享我的攒钱方法
【收入篇】
- 主业：努力提升技能争取涨薪
- 副业：利用业余时间做自媒体
- 理财：基金定投+活期理财
【省钱篇】
- 记账！记账！记账！重要的事说三遍
- 减少外卖，自己带饭
- 衣服买精不买多
- 护肤品用完再买不囤货
【心态篇】
- 不攀比不跟风
- 设置明确的存款目标
- 享受省钱的过程而不是痛苦""",
        "author_name": "省钱女孩日记",
        "like_count": 15300,
        "collect_count": 18200,
        "comment_count": 2340,
        "publish_time": "2026-04-28",
        "url": "https://www.xiaohongshu.com/explore/example007",
        "tags": "攒钱,存钱,省钱,理财",
        "note_type": "省钱",
        "my_notes": "真实经历分享最容易引发共鸣，收藏和评论都很高",
    },
    {
        "title": "三亚旅游避雷指南｜这些坑我替你们踩过了",
        "content": ""刚从三亚回来，整理了一份避雷清单
【住宿】
- 别信网图：一定要看最新评价
- 别住三亚湾：水质一般，推荐海棠湾
【美食】
- 海鲜市场：记得砍价！先问清楚价格
- 椰子鸡：网红店不一定好吃，巷子里的老店才是yyds
【景点】
- 蜈支洲岛：值得去，但早点去避开人流
- 天涯海角：可以不去，性价比低
- 亚龙湾森林公园：玻璃栈道出片率高
【交通】
- 租车方便但停车难
- 滴滴比出租车靠谱""",
        "author_name": "旅行达人小张",
        "like_count": 3890,
        "collect_count": 5400,
        "comment_count": 567,
        "publish_time": "2026-05-10",
        "url": "https://www.xiaohongshu.com/explore/example008",
        "tags": "三亚,旅游,避雷,攻略",
        "note_type": "旅行",
        "my_notes": "避雷类内容互动高，因为用户害怕踩坑",
    },
    {
        "title": "面试被问缺点怎么回答？HR听了直接给offer",
        "content": ""面试中最大的送命题就是"你的缺点是什么"
很多人的回答：我太完美主义（太假）
或者：我脾气不太好（直接凉了）

正确回答公式：
承认缺点+具体案例+改进措施

【模板】
"我之前在时间管理上做得不够好，
有一次因为多任务并行导致项目延期，
后来我学习了GTD方法和番茄工作法，
现在会用Trello规划每项任务，
效率提升了很多。"

核心逻辑：说一个真实但不致命的缺点，重点放在你的改进上""",
        "author_name": "职场教练老王",
        "like_count": 7230,
        "collect_count": 9800,
        "comment_count": 1234,
        "publish_time": "2026-03-20",
        "url": "https://www.xiaohongshu.com/explore/example009",
        "tags": "面试,职场,求职,技巧",
        "note_type": "职场",
        "my_notes": "直接给模板的笔记收藏率高，读者可以直接复制使用",
    },
    {
        "title": "敏感肌换季护肤流程｜泛红急救全攻略",
        "content": ""每年换季就是敏感肌的噩梦...
我的急救流程：
【早晨】
清水洗脸 → 修护精华 → 保湿乳 → 防晒
【晚上】
氨基酸洁面 → 修护精华 → 面霜 → 修护油

关键产品选择原则：
1. 成分越简单越好
2. 无酒精无香精无防腐
3. 修护屏障成分：神经酰胺、积雪草、泛醇

换季期间：停用酸类、A醇等刺激成分
保持精简护肤，给皮肤自我修复的时间""",
        "author_name": "成分党小月",
        "like_count": 5670,
        "collect_count": 7800,
        "comment_count": 890,
        "publish_time": "2026-04-05",
        "url": "https://www.xiaohongshu.com/explore/example010",
        "tags": "敏感肌,护肤,换季,修护",
        "note_type": "美妆",
        "my_notes": "实用型教程，流程清晰产品有依据，信任感强",
    },
    {
        "title": "淘宝隐藏优惠券｜双十一前必看的省钱秘籍",
        "content": ""在淘宝买东西别再直接下单了！教你几个隐藏省钱技巧
1. 先用返利APP查一下，大部分商品都有返利
2. 关注店铺会员，首单优惠+积分抵现
3. 商品页面领券+店铺首页领券+客服发券
4. 88VIP折扣，双十一可以叠加
5. 凑满减是核心技巧，凑完再退

省到就是赚到，姐妹们一定要学会！""",
        "author_name": "抠门小能手",
        "like_count": 10200,
        "collect_count": 14500,
        "comment_count": 1567,
        "publish_time": "2026-05-15",
        "url": "https://www.xiaohongshu.com/explore/example011",
        "tags": "省钱,优惠券,淘宝,购物技巧",
        "note_type": "省钱",
        "my_notes": "省钱类内容在小红书上一直很受欢迎，收藏量普遍高于点赞量",
    },
    {
        "title": "极简衣橱｜10件单品搞定一周通勤穿搭",
        "content": ""践行极简穿搭一年，发现衣服越少反而越会穿
我的10件核心单品：
上装：白衬衫、条纹T恤、黑色针织衫、西装外套
下装：直筒牛仔裤、黑色西裤、百褶裙
鞋：小白鞋、乐福鞋、黑色短靴

搭配公式：
白衬衫+西裤 = 正式商务
条纹T恤+牛仔裤 = 休闲日常
针织衫+百褶裙 = 温柔通勤
西装外套+all black = 气场全开

核心原则：基础款+中性色+好质感""",
        "author_name": "极简穿搭笔记",
        "like_count": 4890,
        "collect_count": 6200,
        "comment_count": 345,
        "publish_time": "2026-02-20",
        "url": "https://www.xiaohongshu.com/explore/example012",
        "tags": "极简,穿搭,通勤,胶囊衣橱",
        "note_type": "穿搭",
        "my_notes": "胶囊衣橱类内容在小红书上是个长期热门选题",
    },
]


def main():
    """初始化数据库并插入示例数据"""
    print("正在初始化数据库...")
    init_database()
    print("数据库初始化完成。")

    print(f"正在插入 {len(SAMPLE_NOTES)} 条示例笔记...")
    for note in SAMPLE_NOTES:
        note_id = add_note(note)
        print(f"  ✓ 已添加: {note['title'][:30]}... (ID: {note_id})")

    print(f"\n完成！共插入 {len(SAMPLE_NOTES)} 条示例数据。")
    print("运行 streamlit run app.py 启动 Web 界面。")


if __name__ == "__main__":
    main()
