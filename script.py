import os
import json
import requests
from facebook_scraper import get_posts

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "worknpoland"

def send_telegram(text, image=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" if image else f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "caption" if image else "text": text[:1024]}
        if image: payload["photo"] = image
        requests.post(url, data=payload, timeout=20)
    except: pass

def main():
    print(f"🚀 Сбор постов из {GROUP_ID}...")
    try:
        # pages=1, собираем свежее
        posts = get_posts(GROUP_ID, pages=1, options={"substream": "posts"})
        
        # Загрузка базы
        if os.path.exists('posted_ids.json'):
            with open('posted_ids.json', 'r') as f:
                posted_ids = json.load(f)
        else:
            posted_ids = []

        new_count = 0
        for post in posts:
            p_id = post['post_id']
            if p_id not in posted_ids:
                msg = f"{post.get('text', '')}\n\n🔗 {post.get('post_url')}"
                send_telegram(msg, post.get('image'))
                posted_ids.append(p_id)
                new_count += 1
                if new_count >= 5: break

        with open('posted_ids.json', 'w') as f:
            json.dump(posted_ids[-100:], f)
        print(f"✅ Успех! Найдено: {new_count}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
