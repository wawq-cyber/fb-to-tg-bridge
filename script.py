import os
import json
import requests
import traceback
import sys
from types import ModuleType

# === БЛОК ЗАПЛАТОК (Исправляет ошибку blinker._saferef) ===
try:
    import blinker
    # Создаем фиктивный модуль, если библиотека требует старый путь
    mock_saferef = ModuleType('blinker._saferef')
    sys.modules['blinker._saferef'] = mock_saferef
    print("✅ Заплатка для blinker успешно применена")
except Exception as e:
    print(f"⚠️ Не удалось применить заплатку для blinker: {e}")

# Теперь импортируем основной скрейпер
try:
    from facebook_page_scraper import Facebook_scraper
except ImportError as e:
    print(f"❌ Ошибка импорта скрейпера: {e}")
    sys.exit(1)

# === НАСТРОЙКИ ===
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# ВАЖНО: Замени 'ID_ВАШЕЙ_ГРУППЫ' на реальный ID или название из URL
GROUP_ID = "worknpoland" 

def send_to_telegram(text, image_url=None):
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            # caption ограничен 1024 символами в TG
            payload = {"chat_id": CHAT_ID, "caption": text[:1000], "photo": image_url}
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": text}
        
        response = requests.post(url, data=payload, timeout=10)
        return response.ok
    except Exception as e:
        print(f"⚠️ Ошибка при отправке в Telegram: {e}")
        return False

def main():
    try:
        # 1. Загружаем базу отправленных ID
        if os.path.exists('posted_ids.json'):
            with open('posted_ids.json', 'r') as f:
                try:
                    posted_ids = json.load(f)
                except:
                    posted_ids = []
        else:
            posted_ids = []

        print(f"🚀 Начинаем сбор постов для: {GROUP_ID}...")

        # 2. Инициализация скрейпера
        # Передаем GROUP_ID первым аргументом без указания имени (page или group)
        # Это самый совместимый способ для разных версий библиотеки
        scraper = Facebook_scraper(
            GROUP_ID, 
            10, 
            "firefox", 
            timeout=600, 
            headless=True
        )
        
        # 3. Получение данных (пробуем разные методы для совместимости версий)
        print("🔍 Пробуем получить данные со страницы...")
        if hasattr(scraper, 'get_posts'):
            posts_data = scraper.get_posts()
        elif hasattr(scraper, 'get_dict'):
            posts_data = scraper.get_dict()
        else:
            # Если методы выше не найдены, пробуем вызвать как итератор
            try:
                posts_data = next(scraper)
            except:
                print("❌ Ошибка: Не удалось найти метод получения постов в этой версии библиотеки.")
                return
        
        # 4. Обработка постов
        for post_id, data in posts_data.items():
            if post_id not in posted_ids:
                content = data.get('content', '')
                post_url = data.get('post_url', 'https://facebook.com/' + str(post_id))
                images = data.get('images', [])
                img_url = images[0] if images else None
                
                message = f"{content}\n\n🔗 Источник: {post_url}"
                
                print(f"📤 Отправляем пост {post_id}...")
                if send_to_telegram(message, img_url):
                    posted_ids.append(post_id)
                    new_posts_count += 1
                
                if new_posts_count >= 10:
                    break

        # 5. Сохранение обновленного списка ID
        # Храним последние 100 постов, чтобы файл не раздувался
        with open('posted_ids.json', 'w') as f:
            json.dump(posted_ids[-100:], f)
        
        print(f"✅ Работа завершена. Отправлено новых постов: {new_posts_count}")

    except Exception:
        print("❌ Произошла критическая ошибка выполнения:")
        print(traceback.format_exc())

if __name__ == "__main__":
    # Проверка переменных окружения перед запуском
    if not TOKEN or not CHAT_ID:
        print("❌ ОШИБКА: Проверьте SECRETS в настройках GitHub (TOKEN или CHAT_ID)")
    else:
        main()
