import os
import time
import re
import requests
import threading
from flask import Flask

TOKEN = "8859334490:AAGHo_cCVvZgFMt-NRmnUReFLUfuYM6aKfU"
CHANNEL_NAME = "@work_ua_hub"

app = Flask(__name__)

# Множина для збереження хешів вже відправлених повідомлень
sent_messages = set()

# Усі публічні канали-джерела
SOURCES = [
    "it_jobs_ua",
    "robota_ua_chan",
    "remote_ukraine",
    "JobUkraineForex",
    "rabota_ukraine_podrabotka",
    "ua_robota"
]

def background_worker():
    """Автономний фоновий цикл, який працює сам по собі кожні 5 хвилин"""
    time.sleep(10) # Чекаємо трохи при старті сайту
    while True:
        print("=== Початок циклу перевірки каналів ===", flush=True)
        for channel in SOURCES:
            try:
                print(f"Збираємо вакансії з каналу @{channel}...", flush=True)
                url = f"https://t.me/s/{channel}"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    html = response.text
                    messages = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
                    
                    # Беремо останні 3 повідомлення з кожного каналу
                    for raw_msg in messages[-3:]:
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
                                print(f"Опубліковано з @{channel}!", flush=True)
                            
                            time.sleep(2)
                else:
                    print(f"Не вдалося зчитати @{channel}, статус: {response.status_code}", flush=True)
                    
            except Exception as e:
                print(f"ПОМИЛКА для @{channel}:", e, flush=True)
                
        print("=== Цикл завершено. Чекаємо 5 хвилин до наступної перевірки ===", flush=True)
        time.sleep(300) # Пауза 5 хвилин перед наступним колом

@app.route("/")
def home():
    return "Бот для збору вакансій працює 24/7!"

# Запускаємо автономний фоновий потік одразу при старті програми
t = threading.Thread(target=background_worker, daemon=True)
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
