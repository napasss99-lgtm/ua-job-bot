import os
import time
import re
import requests
from flask import Flask
import threading

TOKEN = "8859334490:AAGHo_cCVvZgFMt-NRmnUReFLUfuYM6aKfU"
CHANNEL_NAME = "@work_ua_hub"

app = Flask(__name__)

# Множина для збереження хешів вже відправлених повідомлень
sent_messages = set()

@app.route("/")
def home():
    return "Бот працює 24/7!"

def fetch_and_post_vacancies():
    time.sleep(5)
    
    while True:
        try:
            print("Збираємо вакансії з публічного джерела...", flush=True)
            # Читаємо публічну веб-стрічку каналу з вакансіями
            url = "https://t.me/s/it_jobs_ua"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Статус відповіді Telegram Web: {response.status_code}", flush=True)
            
            if response.status_code == 200:
                html = response.text
                # Витягуємо тексти повідомлень за допомогою регулярних виразів
                messages = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
                
                # Беремо останні 5 повідомлень із ленти
                for raw_msg in messages[-5:]:
                    # Очищаємо від HTML-тегів
                    clean_text = re.sub(r'<br\s*/?>', '\n', raw_msg)
                    clean_text = re.sub(r'<.*?>', '', clean_text)
                    clean_text = clean_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    
                    msg_id = hash(clean_text)
                    
                    if clean_text and msg_id not in sent_messages and len(clean_text) > 20:
                        post_text = f"🔵 **Свіжа вакансія:**\n\n{clean_text}\n\n#Робота #Україна"
                        
                        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        payload = {
                            "chat_id": CHANNEL_NAME,
                            "text": post_text,
                            "parse_mode": "Markdown"
                        }
                        
                        res = requests.post(tg_url, json=payload)
                        if res.status_code == 200:
                            sent_messages.add(msg_id)
                            print("Успішно опубліковано вакансію в канал!", flush=True)
                        else:
                            print(f"Помилка відправки в Telegram: {res.text}", flush=True)
                        
                        time.sleep(5)
            else:
                print(f"Помилка доступу: {response.status_code}", flush=True)
                
        except Exception as e:
            print("ПОМИЛКА У ПАРСЕРІ:", e, flush=True)
            
        # Перевірка нових постів кожні 30 хвилин
        time.sleep(1800)

if __name__ == "__main__":
    t = threading.Thread(target=fetch_and_post_vacancies)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
