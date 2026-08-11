import os
import time
import requests
import xml.etree.ElementTree as ET
from flask import Flask
import threading

TOKEN = "8859334490:AAGHo_cCVvZgFMt-NRmnUReFLUfuYM6aKfU"
CHANNEL_NAME = "@work_ua_hub"

app = Flask(__name__)

# Зберігаємо вже відправлені посилання, щоб не було дублікатів
sent_vacancies = set()

@app.route("/")
def home():
    return "Бот для вакансій працює 24/7!"

def fetch_and_post_vacancies():
    time.sleep(5)
    
    while True:
        try:
            print("Збираємо свіжі вакансії через RSS Work.ua...", flush=True)
            url = "https://www.work.ua/rss/"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Статус відповіді RSS: {response.status_code}", flush=True)
            
            if response.status_code == 200:
                # Парсимо XML-документ стрічки RSS
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                # Беремо перші 5 найсвіжіших вакансій
                for item in items[:5]:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    desc_elem = item.find("description")
                    
                    title = title_elem.text if title_elem is not None else "Вакансія"
                    link = link_elem.text if link_elem is not None else "https://www.work.ua"
                    description = desc_elem.text if desc_elem is not None else ""
                    
                    if link and link not in sent_vacancies:
                        # Формуємо текст поста для каналу
                        text = (
                            f"🔵 **{title}**\n\n"
                            f"📄 {description[:150]}...\n\n"
                            f"👉 [Відгукнутися на вакансію]({link})\n\n"
                            f"#Україна #Робота"
                        )
                        
                        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        payload = {
                            "chat_id": CHANNEL_NAME,
                            "text": text,
                            "parse_mode": "Markdown"
                        }
                        
                        res = requests.post(tg_url, json=payload)
                        if res.status_code == 200:
                            sent_vacancies.add(link)
                            print(f"Успішно опубліковано: {title}", flush=True)
                        else:
                            print(f"Помилка відправки в Telegram: {res.text}", flush=True)
                        
                        time.sleep(5)
            else:
                print(f"Помилка завантаження RSS: {response.status_code}", flush=True)
                
        except Exception as e:
            print("ПОМИЛКА У ПАРСЕРІ:", e, flush=True)
            
        # Наступна перевірка через 30 хвилин
        time.sleep(1800)

if __name__ == "__main__":
    t = threading.Thread(target=fetch_and_post_vacancies)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
