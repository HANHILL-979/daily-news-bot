import os
import smtplib
import feedparser
from email.mime.text import MIMEText
from email.header import Header

def get_content():
    # 1. 抓取科技早报 (使用 36Kr RSS 源)
    tech_content = "【科技早报】\n"
    try:
        feed = feedparser.parse("https://36kr.com/feed")
        for entry in feed.entries[:5]: # 取前5条
            tech_content += f"- {entry.title}\n  链接: {entry.link}\n"
    except Exception as e:
        tech_content += "科技新闻抓取失败，请检查网络或源地址。"

    # 2. CET-6 英语阅读 (这里使用 BBC Learning English 作为高质量源)
    eng_content = "\n【CET-6 英语阅读】\n"
    try:
        eng_feed = feedparser.parse("https://www.bbc.co.uk/learningenglish/english/features/6-minute-english/rss")
        if eng_feed.entries:
            entry = eng_feed.entries[0]
            eng_content += f"Topic: {entry.title}\nSummary: {entry.summary}\nFull Article: {entry.link}\n"
    except Exception:
        eng_content += "英语文章抓取失败。"

    return tech_content + eng_content

def send_email(content):
    sender = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header('每日科技与 CET6 早报', 'utf-8')
    msg['From'] = sender
    msg['To'] = sender

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    content = get_content()
    send_email(content)
