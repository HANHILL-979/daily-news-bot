import os
import smtplib
import feedparser
import datetime
import random
from zhipuai import ZhipuAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 1. 初始化智谱客户端
ZHIPU_API_KEY = os.environ.get('ZHIPU_API_KEY')
client = ZhipuAI(api_key=ZHIPU_API_KEY)

def get_tech_news_cn():
    """获取中文科技热点 (36kr)"""
    print("正在抓取 36kr 科技热点...")
    feed = feedparser.parse("https://36kr.com/feed")
    html = "<h2 style='color: #2c3e50; border-bottom: 2px solid #3498db;'>🚀 今日科技热点</h2><ul>"
    for entry in feed.entries[:5]:
        html += f"<li style='margin-bottom: 10px;'><a href='{entry.link}' style='text-decoration:none; color:#34495e;'><b>{entry.title}</b></a></li>"
    html += "</ul><br>"
    return html

def get_cet6_article_en():
    """获取每日轮换的纯英 CET-6 阅读"""
    # 领域轮换配置
    FEED_CONFIG = {
        0: {"topic": "Technology & AI", "url": "https://www.theverge.com/rss/index.xml"},
        1: {"topic": "Global Economy & Finance", "url": "https://www.economist.com/latest/rss.xml"},
        2: {"topic": "International Politics", "url": "https://www.vox.com/rss/world-politics/index.xml"},
        3: {"topic": "Social Issues & Culture", "url": "https://theconversation.com/us/articles.atom"},
        4: {"topic": "Natural Science", "url": "https://www.sciencedaily.com/rss/all.xml"},
        5: {"topic": "Health & Bio-medical", "url": "https://www.sciencedaily.com/rss/health_medicine/index.xml"},
        6: {"topic": "Space & Astronomy", "url": "https://www.sciencedaily.com/rss/space_time/index.xml"}
    }

    weekday = datetime.datetime.now().weekday()
    config = FEED_CONFIG.get(weekday, FEED_CONFIG[4])
    print(f"今日主题领域: {config['topic']}")

    # 抓取素材并加入保底逻辑
    eng_feed = feedparser.parse(config['url'])
    if eng_feed.entries:
        entry = random.choice(eng_feed.entries[:min(5, len(eng_feed.entries))])
        raw_material = f"Title: {entry.title}. Summary: {entry.summary}"
    else:
        print("RSS 抓取失败，使用保底素材。")
        raw_material = "Global scientific advancement and institutional cooperation."

    # 智谱 Prompt：强调客观、CET-6 难度、无中文
    prompt = f"""
    Context Topic: {config['topic']}
    Input Material: {raw_material}
    Task: Write an English academic passage.
    Constraints:
    1. Difficulty: Strictly CET-6 (College English Test Band 6) level.
    2. Tone: Scientific, impartial, and factual. No emotional embellishment.
    3. Content: English ONLY. Do NOT provide any Chinese translation.
    4. Structure: 
       - An engaging Title
       - A 250-word Passage (use complex sentence structures like inversions or subjunctives)
       - 'Key Vocabulary' (6 advanced words with English definitions).
    """

    print(f"正在调用智谱 GLM-5 生成 {config['topic']} 文章...")
    response = client.chat.completions.create(
        model='glm-5',
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=0.8
    )
    
    ai_text = response.choices[0].message.content.replace('\n', '<br>')
    html = f"""
    <h2 style='color: #e67e22; border-bottom: 2px solid #e67e22;'>📖 Daily Reading ({config['topic']})</h2>
    <div style='line-height: 1.8; color: #2c3e50; background: #fdfdfd; padding: 20px; border: 1px solid #eee; border-radius: 8px; font-family: "Times New Roman", Times, serif;'>
        {ai_text}
    </div>
    """
    return html

def send_email(tech_html, eng_html):
    """发送邮件逻辑"""
    sender = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    
    if not sender or not password:
        raise ValueError("邮件环境变量缺失！")

    msg = MIMEMultipart()
    msg['Subject'] = Header(f"【{datetime.date.today()}】hqh 每日早报", 'utf-8')
    msg['From'] = f"hqh-Intelligence-Bot <{sender}>"
    msg['To'] = sender

    full_html = f"""
    <html>
        <body style='max-width: 600px; margin: auto; padding: 20px;'>
            {tech_html}
            {eng_html}
            <p style='text-align: center; color: #95a5a6; font-size: 12px; margin-top: 40px;'>
                Powered by GitHub Actions & Zhipu AI (GLM-5)<br>
                Stay objective. Keep learning, hqh.
            </p>
        </body>
    </html>
    """
    msg.attach(MIMEText(full_html, 'html', 'utf-8'))

    print("正在连接 SMTP 服务器发送邮件...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)
    print("邮件发送成功！")

# --- 关键执行块：确保脚本运行 ---
if __name__ == "__main__":
    print(f"--- 任务启动: {datetime.datetime.now()} ---")
    try:
        t_html = get_tech_news_cn()
        e_html = get_cet6_article_en()
        send_email(t_html, e_html)
        print("--- 任务圆满完成 ---")
    except Exception as e:
        print(f"❌ 程序发生致命错误: {e}")
        import sys
        sys.exit(1)
