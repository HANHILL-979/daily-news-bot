import os
import smtplib
import feedparser
from zhipuai import ZhipuAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 1. 初始化智谱客户端
client = ZhipuAI(api_key=os.environ.get('ZHIPU_API_KEY'))

def get_tech_news():
    feed = feedparser.parse("https://36kr.com/feed")
    html = "<h2 style='color: #2c3e50; border-bottom: 2px solid #3498db;'>🚀 今日科技热点</h2><ul>"
    for entry in feed.entries[:5]:
        html += f"<li style='margin-bottom: 10px;'><a href='{entry.link}' style='text-decoration:none; color:#34495e;'><b>{entry.title}</b></a></li>"
    html += "</ul><br>"
    return html

def get_cet6_article():
    eng_feed = feedparser.parse("https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml")
    raw_material = eng_feed.entries[0].summary if eng_feed.entries else "The evolution of modern computing."

    # 针对智谱优化的 Prompt，强调客观与 CET-6 难度
    prompt = f"""
    You are an objective academic editor. Based on the material: {raw_material}
    Task: Write a formal English passage.
    Requirements:
    1. Level: Strictly CET-6 (College English Test Band 6) difficulty.
    2. Tone: Scientific, impartial, and factual. Avoid flowery language.
    3. Structure: Title + 250-word Passage + 'Vocabulary' list (6 key CET-6 words with meanings).
    4. Output: Strictly English only.
    """
    
    # 2. 调用智谱 GLM-5 模型 (2026年旗舰版)
    response = client.chat.completions.create(
        model='glm-5', 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3, # 保持低温度以确保输出的严谨性
        top_p=0.7
    )
    
    ai_text = response.choices[0].message.content.replace('\n', '<br>')
    
    html = f"""
    <h2 style='color: #e67e22; border-bottom: 2px solid #e67e22;'>📖 CET-6 Daily Reading</h2>
    <div style='line-height: 1.8; color: #2c3e50; background: #fdfdfd; padding: 20px; border: 1px solid #eee; border-radius: 8px; font-family: "Times New Roman", Times, serif;'>
        {ai_text}
    </div>
    """
    return html

def send_email(tech_body, eng_body):
    sender = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    
    msg = MIMEMultipart()
    msg['Subject'] = Header(f"【{os.environ.get('GITHUB_RUN_NUMBER', 'Local')}期】hqh 每日早报", 'utf-8')
    msg['From'] = f"hqh-Intelligence-Bot <{sender}>"
    msg['To'] = sender

    full_html = f"""
    <html>
        <body style='max-width: 600px; margin: auto; padding: 20px;'>
            {tech_body}
            {eng_body}
            <p style='text-align: center; color: #95a5a6; font-size: 12px; margin-top: 40px;'>
                Powered by GitHub Actions & Zhipu AI (GLM-5)<br>
                Keep advancing, hqh.
            </p>
        </body>
    </html>
    """
    msg.attach(MIMEText(full_html, 'html', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    try:
        t_html = get_tech_news()
        e_html = get_cet6_article()
        send_email(t_html, e_html)
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e
