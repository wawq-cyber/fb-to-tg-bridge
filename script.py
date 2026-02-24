import os
import json
import requests
from facebook_scraper import get_posts

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "worknpoland"
COOKIES_JSON = os.getenv('FB_COOKIES') # Получаем куки из секретов

def send_telegram(text, image=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" if image else f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        limit = 1024 if image else 4000
        payload = {"chat_id": CHAT_ID, "caption" if image else "text": text[:limit]}
        if image: payload["photo"] = image
        requests.post(url, data=payload, timeout=20)
    except: pass

def main():
    print(f"🚀 Сбор постов из {GROUP_ID} с использованием Cookies...")
    
    # Создаем временный файл кук, так как библиотека требует путь к файлу
    if COOKIES_JSON:
        with open('cookies.json', 'w') as f:
            f.write(COOKIES_JSON)
        cookies_path = 'cookies.json'
    else:
        cookies_path = None
        print("⚠️ Внимание: Куки не найдены, пробуем анонимно...")

    try:
        posts = get_posts(
            group=GROUP_ID,
            pages=2,
            cookies=cookies_path,
            options={"substream": "posts"}
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
                text = post.get('text') or "Новый пост"
                url = post.get('post_url') or f"https://facebook.com/{p_id}"
                print(f"📡 Отправка поста {p_id}...")
                send_telegram(f"{text}\n\n🔗 {url}", post.get('image'))
                posted_ids.append(p_id)
                new_count += 1
                if new_count >= 5: break

        with open('posted_ids.json', 'w') as f:
            json.dump(posted_ids[-100:], f)
        
        # Удаляем временный файл кук в целях безопасности
        if os.path.exists('cookies.json'): os.remove('cookies.json')
        
        print(f"✅ Готово! Отправлено: {new_count}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
