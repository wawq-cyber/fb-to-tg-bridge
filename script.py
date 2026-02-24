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
        # Сообщения в ТГ ограничены 4096 символами, а caption у фото 1024
        limit = 1024 if image else 4000
        payload = {"chat_id": CHAT_ID, "caption" if image else "text": text[:limit]}
        if image: payload["photo"] = image
        requests.post(url, data=payload, timeout=20)
    except: pass

def main():
    print(f"🚀 Сбор постов из {GROUP_ID}...")
    try:
        # Увеличиваем количество страниц и добавляем User-Agent
        # Это заставляет Facebook думать, что зашел реальный человек
        # Пробуем зайти через мобильный интерфейс (он легче отдается ботам)
        posts = get_posts(
            group=GROUP_ID, # используем параметр group вместо первого аргумента
            pages=2,
            options={"substream": "posts", "allow_extra_requests": True},
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.5993.111 Mobile Safari/537.36"
        )
        
        if os.path.exists('posted_ids.json'):
            with open('posted_ids.json', 'r') as f:
                try: posted_ids = json.load(f)
                except: posted_ids = []
        else:
            posted_ids = []

        new_count = 0
        for post in posts:
            p_id = post['post_id']
            if p_id and p_id not in posted_ids:
                text = post.get('text') or post.get('post_text', 'Пост без текста')
                url = post.get('post_url') or f"https://facebook.com/{p_id}"
                msg = f"{text}\n\n🔗 {url}"
                
                print(f"📡 Отправляем пост {p_id}...")
                send_telegram(msg, post.get('image'))
                posted_ids.append(p_id)
                new_count += 1
                if new_count >= 5: break

        with open('posted_ids.json', 'w') as f:
            json.dump(posted_ids[-100:], f)
        print(f"✅ Готово! Найдено и отправлено: {new_count}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
