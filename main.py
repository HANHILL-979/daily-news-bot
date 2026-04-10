import datetime
import random
import feedparser

def get_cet6_article():
    # 1. 建立领域轮换表：每天关注不同领域，确保内容多样性
    # 0:周一, 1:周二 ... 6:周日
    FEED_CONFIG = {
        0: {"topic": "Technology & AI", "url": "https://www.theverge.com/rss/index.xml"},
        1: {"topic": "Global Economy & Finance", "url": "https://www.economist.com/latest/rss.xml"},
        2: {"topic": "International Politics", "url": "https://www.vox.com/rss/world-politics/index.xml"},
        3: {"topic": "Social Issues & Culture", "url": "https://theconversation.com/us/articles.atom"},
        4: {"topic": "Natural Science & Environment", "url": "https://www.sciencedaily.com/rss/all.xml"},
        5: {"topic": "Health & Bio-medical", "url": "https://www.sciencedaily.com/rss/health_medicine/index.xml"},
        6: {"topic": "Space & Astronomy", "url": "https://www.sciencedaily.com/rss/space_time/index.xml"}
    }

    # 获取当前日期对应的领域
    weekday = datetime.datetime.now().weekday()
    config = FEED_CONFIG.get(weekday, FEED_CONFIG[0])
    
    # 2. 抓取素材
    eng_feed = feedparser.parse(config['url'])
    if eng_feed.entries:
        # 随机选择前 5 篇中的一篇，进一步避免重复
        entry = random.choice(eng_feed.entries[:5])
        raw_material = f"Title: {entry.title}. Content: {entry.summary}"
    else:
        raw_material = "Developments in modern global infrastructure."

    # 3. 极简 Prompt：去除翻译，强调客观，节省 Token
    prompt = f"""
    Context: {config['topic']}
    Material: {raw_material}
    Task: Write a CET-6 level academic passage.
    Constraints:
    1. Language: Strictly English ONLY. No translation.
    2. Style: Objective, factual, and scientific. Avoid emotional adjectives.
    3. Structure: 
       - Title
       - 250-word Passage
       - 'Key Vocabulary' list (6 words with English definitions).
    """
    
    # 4. 调用智谱 API (使用旗舰模型 GLM-5)
    response = client.chat.completions.create(
        model='glm-5', 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6, # 适中温度，兼顾多样性与严谨
        max_tokens=800  # 限制输出长度，防止 Token 溢出
    )
    
    ai_text = response.choices[0].message.content.replace('\n', '<br>')
    
    html = f"""
    <h2 style='color: #e67e22; border-bottom: 2px solid #e67e22;'>📖 Daily Reading ({config['topic']})</h2>
    <div style='line-height: 1.8; color: #2c3e50; background: #fdfdfd; padding: 20px; border: 1px solid #eee; border-radius: 8px; font-family: "Times New Roman", Times, serif;'>
        {ai_text}
    </div>
    """
    return html
