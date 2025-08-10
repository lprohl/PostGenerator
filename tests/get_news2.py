import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем API-ключ
API_KEY = os.getenv("CURRENTS_API_KEY")
if not API_KEY:
    raise ValueError("API ключ не найден. Убедитесь, что CURRENTS_API_KEY задан в .env файле.")

# Настройки
BASE_URL = "https://api.currentsapi.services/v1/search"
TIMEOUT = 120  # Увеличенный таймаут

# Параметры запроса
params = {
    "keywords": "Artificial Intelligence",
    #"keywords": "Iran and Israel",
    "apiKey": API_KEY,
    # Дополнительные опции (по желанию):
    # "language": "en",
    # "country": "US",
    # "start_date": "2024-01-01",
    # "end_date": "2024-12-31",
}

# Заголовки (опционально, но рекомендуется)
headers = {
    "User-Agent": "MyNewsApp/1.0"  # Можно указать своё имя приложения
}

# Выполнение запроса
try:
    print("Отправка запроса к Currents API...")
    response = requests.get(BASE_URL, params=params, headers=headers, timeout=TIMEOUT)

    # Проверка статуса ответа
    if response.status_code == 200:
        data = response.json()
        print("✅ Успешно! Новости получены:")
        for article in data.get("news", [])[:3]:  # Печатаем первые 3 новости
            print(f"- {article.get('title')} [{article.get('published')}]")
            print(f"  Источник: {article.get('url')}\n")
    elif response.status_code == 429:
        print("❌ Ошибка 429: Слишком много запросов. Попробуйте позже или проверьте тарифный план.")
    elif response.status_code == 401:
        print("❌ Ошибка 401: Неверный API-ключ.")
    else:
        print(f"❌ Ошибка {response.status_code}: {response.text}")

except requests.exceptions.ReadTimeout:
    print(f"❌ Ошибка: Превышен таймаут чтения ({TIMEOUT} секунд).")
except requests.exceptions.ConnectTimeout:
    print("❌ Ошибка: Не удалось подключиться к серверу (таймаут соединения).")
except requests.exceptions.RequestException as e:
    print(f"❌ Произошла ошибка при выполнении запроса: {e}")