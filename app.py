import os
import time
import requests
from flask import Flask
import threading

TOKEN = "8859334490:AAGHo_cCVvZgFMt-NRmnUReFLUfuYM6aKfU"
CHANNEL_NAME = "@work_ua_hub"

app = Flask(__name__)

@app.route("/")
def home():
    return "Бот працює 24/7!"

def send_test_post():
    print("Очікування 10 секунд перед відправкою...", flush=True)
    time.sleep(10)
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_NAME, 
            "text": "🔵 Бот успішно запущений і працює у каналі!"
        }
        
        print("Надсилаємо повідомлення до Telegram...", flush=True)
        response = requests.post(url, json=payload)
        print("ВІДПОВІДЬ ВІД ТЕЛЕГРАМУ:", response.text, flush=True)
    except Exception as e:
        print("ПОМИЛКА:", e, flush=True)

if __name__ == "__main__":
    t = threading.Thread(target=send_test_post)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
