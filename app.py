import os
import threading
import time
import requests
from flask import Flask

TOKEN = "8859334490:AAGHo_cCVvZgFmT-NRmnUReFLUfuYM6akfU"
CHANNEL_NAME = "@work_ua_hub"

app = Flask(__name__)

@app.route("/")
def home():
    return "Бот працює 24/7!"

def send_posts_loop():
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            photo_url = "https://raw.githubusercontent.com/napasss99-lgtm/ua-job-bot/main/Gemini_Generated_Image_bfrpo9bfrpo9bfrp.png"

            caption = (
                "🔵 **Автоматична вакансія**\n"
                "#віддалено #повназайнятість\n\n"
                "💰 **Заробітна плата за домовленістю**\n"
                "📍 Віддалено\n\n"
                "👇 **Контакти та деталі нижче**"
            )

            reply_markup = {
                "inline_keyboard": [
                    [{"text": "👉 Відгукнутися на вакансію", "url": "https://www.work.ua/"}],
                    [{"text": "💻 Робота в Україні", "url": f"https://t.me/{CHANNEL_NAME.replace('@', '')}"}]
                ]
            }

            payload = {
                "chat_id": CHANNEL_NAME,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "Markdown",
                "reply_markup": reply_markup,
            }

            requests.post(url, json=payload)
            print("Пост успішно відправлено!")

        except Exception as e:
            print("Помилка:", e)

        time.sleep(3600)

thread = threading.Thread(target=send_posts_loop)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
