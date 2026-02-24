import os
import json
import requests
import sys
from types import ModuleType

# Заплатка для blinker
try:
    import blinker
    mock_saferef = ModuleType('blinker._saferef')
    sys.modules['blinker._saferef'] = mock_saferef
except: pass

from facebook_page_scraper import Facebook_scraper

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "worknpoland" # ID уже вписан

def send_to_telegram(text, image_url=None):
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            data = {"chat_id": CHAT_ID, "caption": text[:1000], "photo": image_url}
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Ошибка TG: {e}")

def main():
    if os.path.exists('posted_ids.json'):
        with open('posted_ids.json', 'r') as f:
            posted_ids = json.load(f)
    else:
        posted_ids = []

    print(f"🚀 Запуск скрейпера для {GROUP_ID}...")
    
    # В версии 4.0.0 аргумент часто называется page_name
    scraper = Facebook_scraper(
        page_name=GROUP_ID,
        posts_count=5,
        browser="firefox",
        proxy=None,
        timeout=600,
        headless=True
    )

    # В версии 4.0.0 метод получения данных называется get_posts()
    try:
        posts_data = scraper.get_posts()
    except Exception as e:
        print(f"❌ Ошибка при сборе: {e}")
        return

    if not posts_data:
        print("ℹ️ Посты не найдены (возможно, нужна авторизация/cookies)")
        return

    for post_id, data in posts_data.items():
        if post_id not in posted_ids:
            content = data.get('content', '')
            post_url = data.get('post_url', '')
            img = data.get('images', [None])[0]
            
            send_to_telegram(f"{content}\n\n🔗 {post_url}", img)
            posted_ids.append(post_id)

    with open('posted_ids.json', 'w') as f:
        json.dump(posted_ids[-100:], f)
    print("✅ Готово!")

if __name__ == "__main__":
    main()
