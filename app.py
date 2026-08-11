import os
import time
import requests
from flask import Flask
import threading

TOKEN = "8859334490:AAGHo_cCVvZgFMt-NRmnUReFLUfuYM6aKfU"
CHANNEL_NAME = "@work_ua_hub"

app = Flask(__name__)

# Множина для зберігання ID вже відправлених вакансій (щоб уникнути дублікатів)
sent_vacancies = set()

@app.route("/")
def home():
    return "Бот для пошуку вакансій працює 24/7!"

def fetch_and_post_vacancies():
    # Робимо коротку паузу при старті, щоб сервер встиг повністю запуститися
    time.sleep(5)
    
    while True:
        try:
            print("Шукаємо нові вакансії на robota.ua...", flush=True)
            
            # Запит до публічного API пошуку robota.ua по всій Україні
            url = "https://api.robota.ua/vacancies?page=0"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                vacancies = data.get("items", [])
                
                # Беремо перші 5 найсвіжіших вакансій за раз
                for vac in vacancies[:5]:
                    vac_id = str(vac.get("id"))
                    
                    if vac_id and vac_id not in sent_vacancies:
                        title = vac.get("name", "Вакансія")
                        company = vac.get("company", {}).get("name", "Компанія")
                        salary_data = vac.get("salary")
                        
                        # Обробка зарплати
                        if salary_data and salary_data.get("amount"):
                            salary = f"{salary_data.get('amount')} грн"
                        else:
                            salary = "Не вказано"
                            
                        city = vac.get("city", {}).get("name", "Україна")
                        
                        # Формуємо текст повідомлення з хештегами
                        text = (
                            f"🔵 **{title}**\n\n"
                            f"🏢 Компанія: {company}\n"
                            f"💰 Зарплата: {salary}\n"
                            f"📍 Місто: {city}\n\n"
                            f"👉 [Відгукнутися на вакансію](https://robota.ua/vacancies/{vac_id})\n\n"
                            f"#{city.replace(' ', '')} #Україна"
                        )
                        
                        # Надсилаємо в Telegram канал
                        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        payload = {
                            "chat_id": CHANNEL_NAME,
                            "text": text,
                            "parse_mode": "Markdown"
                        }
                        
                        res = requests.post(tg_url, json=payload)
                        if res.status_code == 200:
                            sent_vacancies.add(vac_id)
                            print(f"Успішно опубліковано: {title}", flush=True)
                        else:
                            print(f"Помилка відправки в Telegram: {res.text}", flush=True)
                        
                        # Пауза між постами, щоб уникнути обмежень Telegram
                        time.sleep(5)
            else:
                print(f"Помилка запиту до robota.ua: {response.status_code}", flush=True)
                
        except Exception as e:
            print("ПОМИЛКА У ПАРСЕРІ:", e, flush=True)
            
        # Повторна перевірка нових вакансій кожні 30 хвилин (1800 секунд)
        time.sleep(1800)

if __name__ == "__main__":
    # Запуск фонового потоку для автоматичного парсингу та публікації
    t = threading.Thread(target=fetch_and_post_vacancies)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
