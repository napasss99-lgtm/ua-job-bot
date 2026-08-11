import os
import time
import requests
from flask import Flask
import threading

TOKEN = "8859334490:AAGHo_cCVvZgFMt-NRmnUReFLUfuYM6aKfU"
CHANNEL_NAME = "@work_ua_hub"

app = Flask(__name__)

sent_vacancies = set()

@app.route("/")
def home():
    return "Бот для пошуку вакансій працює 24/7!"

def fetch_and_post_vacancies():
    time.sleep(5)
    
    while True:
        try:
            print("Шукаємо нові вакансії на robota.ua...", flush=True)
            
            # Повні заголовки справжнього браузера для обходу захисту 403
            url = "https://api.robota.ua/vacancies?page=0"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://robota.ua/",
                "Origin": "https://robota.ua/"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            print(코드_статус := f"Статус відповіді robota.ua: {response.status_code}", flush=True)
            
            if response.status_code == 200:
                data = response.json()
                vacancies = data.get("items", [])
                
                for vac in vacancies[:5]:
                    vac_id = str(vac.get("id"))
                    
                    if vac_id and vac_id not in sent_vacancies:
                        title = vac.get("name", "Вакансія")
                        company = vac.get("company", {}).get("name", "Компанія")
                        salary_data = vac.get("salary")
                        
                        if salary_data and salary_data.get("amount"):
                            salary = f"{salary_data.get('amount')} грн"
                        else:
                            salary = "Не вказано"
                            
                        city = vac.get("city", {}).get("name", "Україна")
                        
                        text = (
                            f"🔵 **{title}**\n\n"
                            f"🏢 Компанія: {company}\n"
                            f"💰 Зарплата: {salary}\n"
                            f"📍 Місто: {city}\n\n"
                            f"👉 [Відгукнутися на вакансію](https://robota.ua/vacancies/{vac_id})\n\n"
                            f"#{city.replace(' ', '')} #Україна"
                        )
                        
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
                        
                        time.sleep(5)
            else:
                print(f"Помилка доступу до сайту (код {response.status_code})", flush=True)
                
        except Exception as e:
            print("ПОМИЛКА У ПАРСЕРІ:", e, flush=True)
            
        time.sleep(1800)

if __name__ == "__main__":
    t = threading.Thread(target=fetch_and_post_vacancies)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
