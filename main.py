import os
import smtplib
import feedparser
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 配置 AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_tech_news():
    feed = feedparser.parse("https://36kr.com/feed")
    html = "<h2 style='color: #2c3e50;'>【今日科技热点】</h2><ul>"
    for entry in feed.entries[:5]:
        html += f"<li><a href='{entry.link}'>{entry.title}</a></li>"
    html += "</ul><hr>"
    return html

def get_ai_cet6_article():
    # 抓取一个英文素材作为 AI 改写的原材料
    eng_feed = feedparser.parse("https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml")
    raw_text = eng_feed.entries[0].summary if eng_feed.entries else "Global technology trends in 2026."
    
    # 核心：利用 AI 改写
    prompt = f"""
    Please rewrite the following news text into a CET-6 (College English Test Band 6) level reading passage.
    Requirements:
    1. Language: Strictly in English.
    2. Length: 200-300 words.
    3. Style: Academic and formal, suitable for a reading comprehension test.
    4. Format: Return the passage directly, followed by a 'Vocabulary List' for CET-6 difficult words found in the text.
    Raw material: {raw_text}
    """
    response = model.generate_content(prompt)
    
    html = "<h2 style='color: #e67e22;'>【CET-6 Daily Reading】</h2>"
    html += f"<div style='line-height: 1.6; color: #34495e; background: #f9f9f9; padding: 15px; border-radius: 5px;'>{response.text.replace('\n', '<break>').replace('<break>', '<br>')}</div>"
    return html

def send_email(tech_html, eng_html):
    sender = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    
    msg = MIMEMultipart()
    msg['Subject'] = Header('每日科技与 CET6 英语专刊', 'utf-8')
    msg['From'] = sender
    msg['To'] = sender

    # 合并 HTML
    full_html = f"""
    <html>
        <body>
            {tech_html}
            <br>
            {eng_html}
            <p style='font-size: 12px; color: #bdc3c7;'>Sent by GitHub Actions Bot</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(full_html, 'html', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    t_html = get_tech_news()
    e_html = get_ai_cet6_article()
    send_email(t_html, e_html)
