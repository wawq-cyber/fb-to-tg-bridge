import os
import json
import requests
from facebook_scraper import get_posts, set_cookies

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "worknpoland"
COOKIES_JSON = os.getenv('FB_COOKIES')

def send_telegram(text, image=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" if image else f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "caption" if image else "text": text[:1024]}
        if image: payload["photo"] = image
        requests.post(url, data=payload, timeout=20)
    except: pass

def main():
    print(f"🚀 Запуск с куками для группы: {GROUP_ID}")
    
    cookies_data = None
    if COOKIES_JSON:
        try:
            cookies_data = json.loads(COOKIES_JSON)
            # Записываем в файл для библиотеки
            with open('cookies.json', 'w') as f:
                json.dump(cookies_data, f)
            print("✅ Куки загружены и сохранены в файл.")
        except Exception as e:
            print(f"❌ Ошибка парсинга кук: {e}")

    try:
        # Пробуем получить посты с более агрессивными настройками
        # pages=3, чтобы точно пролистать возможные закрепленные посты
        posts = get_posts(
            group=GROUP_ID,
            pages=3,
            cookies="cookies.json" if cookies_data else None,
            options={"substream": "posts", "allow_extra_requests": True}
        )
        
        found_any = False
        new_count = 0
        
        # Список уже опубликованных
        if os.path.exists('posted_ids.json'):
            with open('posted_ids.json', 'r') as f:
                try: posted_ids = json.load(f)
                except: posted_ids = []
        else:
            posted_ids = []

        for post in posts:
            found_any = True
            p_id = post.get('post_id')
            if p_id and p_id not in posted_ids:
                text = post.get('text') or "Новый пост"
                url = post.get('post_url') or f"https://facebook.com/{p_id}"
                print(f"📡 Отправляю пост: {p_id}")
                send_telegram(f"{text}\n\n🔗 {url}", post.get('image'))
                posted_ids.append(p_id)
                new_count += 1
                if new_count >= 5: break

        if not found_any:
            print("ℹ️ Facebook не вернул ни одного поста. Возможно, формат кук не подошел или IP забанен.")
        
        with open('posted_ids.json', 'w') as f:
            json.dump(posted_ids[-100:], f)
            
        print(f"✅ Завершено. Отправлено новых: {new_count}")

    except Exception as e:
        print(f"❌ Критическая ошибка при сборе: {e}")
    finally:
        if os.path.exists('cookies.json'):
            os.remove('cookies.json')

if __name__ == "__main__":
    main()
