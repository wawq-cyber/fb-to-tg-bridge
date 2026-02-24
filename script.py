import os
import json
import requests
from facebook_page_scraper import Facebook_scraper

# Секреты GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "worknpoland" # Замените на реальный ID

def send_to_telegram(text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        data = {"chat_id": CHAT_ID, "caption": text[:1024], "photo": image_url}
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def main():
    if os.path.exists('posted_ids.json'):
        with open('posted_ids.json', 'r') as f:
            posted_ids = json.load(f)
    else:
        posted_ids = []

    # В 2026 году Facebook требует headless=True для работы на серверах
    # Мы используем браузер firefox (стандарт для GitHub Actions)
    try:
        scraper = Facebook_scraper(GROUP_ID, 10, "firefox", timeout=600, headless=True)
        posts_data = scraper.get_posts()
    except Exception as e:
        print(f"Критическая ошибка скрейпера: {e}")
        return

    new_posts_count = 0
    for post_id, data in posts_data.items():
        if post_id not in posted_ids:
            content = data.get('content', '')
            post_url = data.get('post_url', '')
            img = data.get('images', [None])[0]
            
            message = f"{content}\n\n🔗 {post_url}"
            send_to_telegram(message, img)
            
            posted_ids.append(post_id)
            new_posts_count += 1
            if new_posts_count >= 10: break

    with open('posted_ids.json', 'w') as f:
        json.dump(posted_ids[-100:], f)

if __name__ == "__main__":
    main()
