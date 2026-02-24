import os
import json
import requests
import traceback
from facebook_page_scraper import Facebook_scraper

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "worknpoland" # ПРОВЕРЬТЕ ЭТОТ ID!

def send_to_telegram(text, image_url=None):
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            data = {"chat_id": CHAT_ID, "caption": text[:1024], "photo": image_url}
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def main():
    try:
        if os.path.exists('posted_ids.json'):
            with open('posted_ids.json', 'r') as f:
                posted_ids = json.load(f)
        else:
            posted_ids = []

        print(f"Начинаем поиск постов для группы: {GROUP_ID}")
        
        # Инициализация с увеличенным таймаутом
        scraper = Facebook_scraper(GROUP_ID, 10, "firefox", timeout=600, headless=True)
        posts_data = scraper.get_posts()
        
        if not posts_data:
            print("Посты не найдены. Возможно, группа приватная или сработала защита Facebook.")
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
        print(f"Успешно отправлено новых постов: {new_posts_count}")

    except Exception:
        print("Произошла ошибка при выполнении скрипта:")
        print(traceback.format_exc()) # Это выведет подробности ошибки в логи

if __name__ == "__main__":
    main()
