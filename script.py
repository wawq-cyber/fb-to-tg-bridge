import os
import json
import requests
from facebook_scraper import get_posts

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "worknpoland" # Возвращаемся к названию
COOKIES_JSON = os.getenv('FB_COOKIES')

def send_telegram(text, image=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" if image else f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "caption" if image else "text": text[:1024]}
        if image: payload["photo"] = image
        requests.post(url, data=payload, timeout=20)
    except: pass

def main():
    print(f"📡 Финальная проверка группы: {GROUP_ID}")
    
    if not COOKIES_JSON:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Секрет FB_COOKIES пуст!")
        return

    with open('cookies.json', 'w') as f:
        f.write(COOKIES_JSON)

    try:
        # Пробуем получить посты через m.facebook.com
        posts = get_posts(
            group=GROUP_ID,
            pages=1,
            cookies="cookies.json",
            options={"allow_extra_requests": True, "vga": True} # vga помогает обходить проверки
        )
        
        new_count = 0
        found_any = False
        
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
                text = post.get('text') or "Новое объявление"
                link = post.get('post_url') or f"https://facebook.com/{p_id}"
                print(f"✨ Пост найден! ID: {p_id}")
                send_telegram(f"{text}\n\n🔗 {link}", post.get('image'))
                posted_ids.append(p_id)
                new_count += 1
                if new_count >= 5: break

        if not found_any:
            print("❗ Facebook всё еще не отдает посты. Это значит, что куки не прошли проверку или IP заблокирован.")
        
        with open('posted_ids.json', 'w') as f:
            json.dump(posted_ids[-100:], f)
        print(f"✅ Результат: {new_count}")

    except Exception as e:
        print(f"❌ Ошибка библиотеки: {e}")
    finally:
        if os.path.exists('cookies.json'): os.remove('cookies.json')

if __name__ == "__main__":
    main()
