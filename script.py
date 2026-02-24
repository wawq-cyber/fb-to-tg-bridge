import os
import json
import requests
from facebook_page_scraper import Facebook_scraper

# Настройки из секретов GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GROUP_ID = "ID_ВАШЕЙ_ГРУППЫ"  # Вставьте сюда ID или название из URL группы

def send_to_telegram(text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        data = {"chat_id": CHAT_ID, "caption": text[:1024], "photo": image_url}
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
    
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def main():
    # 1. Загружаем историю отправленных постов
    if os.path.exists('posted_ids.json'):
        with open('posted_ids.json', 'r') as f:
            posted_ids = json.load(f)
    else:
        posted_ids = []

    # 2. Инициализируем скрейпер
    # proxy можно не указывать, GitHub имеет хорошие IP
    scraper = Facebook_scraper(GROUP_ID, 10, "firefox", timeout=600)
    
    # 3. Получаем посты (в формате JSON)
    posts_data = scraper.get_posts()
    new_posts_count = 0

    for post_id, data in posts_data.items():
        if post_id not in posted_ids:
            # Формируем текст поста
            content = data.get('content', '')
            post_url = data.get('post_url', '')
            img = data.get('images', [None])[0] # Берем первое фото, если есть
            
            message = f"{content}\n\n🔗 Источник: {post_url}"
            
            # Отправляем
            send_to_telegram(message, img)
            
            # Сохраняем ID, чтобы не дублировать
            posted_ids.append(post_id)
            new_posts_count += 1
            
            if new_posts_count >= 10: # Лимит 10 новых постов за раз
                break

    # 4. Обновляем базу данных (оставляем последние 100 ID, чтобы файл не рос вечно)
    with open('posted_ids.json', 'w') as f:
        json.dump(posted_ids[-100:], f)

if __name__ == "__main__":
    main()
