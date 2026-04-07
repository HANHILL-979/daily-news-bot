import os
import smtplib
import feedparser
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 1. 配置 Gemini (使用最稳定的 generativeai 库)
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash') # 也可以用 gemini-2.0-flash-exp

def get_tech_news():
    """获取科技早报"""
    feed = feedparser.parse("https://36kr.com/feed")
    html = "<h2 style='color: #2c3e50; border-bottom: 2px solid #3498db;'>🚀 今日科技热点</h2><ul>"
    for entry in feed.entries[:5]:
        html += f"<li style='margin-bottom: 10px;'><a href='{entry.link}' style='text-decoration:none; color:#34495e;'><b>{entry.title}</b></a></li>"
    html += "</ul><br>"
    return html

def get_cet6_article():
    """利用 AI 生成 CET-6 水平的阅读全文"""
    # 抓取英文素材
    eng_feed = feedparser.parse("https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml")
    raw_material = eng_feed.entries[0].summary if eng_feed.entries else "The advancement of technology in 2026."

    prompt = f"""
    Based on the following material, write a formal English passage.
    Material: {raw_material}
    Requirements:
    1. Level: Strictly CET-6 difficulty. 
    2. Style: Academic with complex sentences (subjunctive, inversions).
    3. Length: 250 words.
    4. Format: Title + Passage + 'Vocabulary & Expressions' list (5-8 difficult CET-6 words with English meanings).
    5. Output: Strictly English only.
    """
    
    # 稳定的调用方式
    response = model.generate_content(prompt)
    ai_text = response.text.replace('\n', '<br>')
    
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
    msg['Subject'] = Header(f"【{os.environ.get('GITHUB_RUN_NUMBER')}期】每日科技与 CET6 专刊", 'utf-8')
    msg['From'] = f"hqh-Daily-Bot <{sender}>"
    msg['To'] = sender

    full_html = f"""
    <html>
        <body style='max-width: 600px; margin: auto; padding: 20px;'>
            {tech_body}
            {eng_body}
            <p style='text-align: center; color: #95a5a6; font-size: 12px; margin-top: 40px;'>
                Powered by GitHub Actions & Gemini AI<br>
                Keep studying, Huang!
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
        print("Success: Email sent!")
    except Exception as e:
        print(f"Error: {e}")
        # 这里故意抛出错误让 GitHub Action 标记为失败以便查看日志
        raise e
