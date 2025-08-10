# modules/news_fetcher.py
"""
Модуль: Получение новостей из Currents API (за последние 24 часа)
"""
import requests
import logging
from datetime import datetime, timedelta
from config import CURRENTS_API_KEY, CURRENTS_BASE_URL, TIMEOUT
from time import sleep

logger = logging.getLogger(__name__)

def fetch_latest_news(keywords: str, language: str = "en", max_retries: int = 3) -> list:
    """
    Получает новости с повторными попытками.
    """
    start_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    logger.info(f"start_date = {start_date}")

    params = {
        "keywords": keywords,
        "apiKey": CURRENTS_API_KEY,
        "language": language,
        #"start_date": start_date,
        #"page_size": 5,
    }

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Запрос к Currents API (попытка {attempt}): {keywords}")
            response = requests.get(CURRENTS_BASE_URL, params=params, timeout=TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                news = data.get("news", [])
                logger.info(f"Успешно получено {len(news)} новостей.")
                return news
            elif response.status_code == 429:
                logger.warning(f"Слишком много запросов (429). Пауза перед повтором...")
                wait = 5 * attempt
                sleep(wait)
            elif response.status_code == 401:
                logger.critical("Ошибка авторизации: проверь API-ключ!")
                return []
            else:
                logger.error(f"Ошибка {response.status_code}: {response.text}")
                if attempt < max_retries:
                    sleep(5)

        except requests.exceptions.ReadTimeout:
            logger.warning(f"Таймаут чтения (попытка {attempt}). Повтор...")
            if attempt < max_retries:
                sleep(5)
        except requests.exceptions.RequestException as e:
            logger.error(f"Сетевая ошибка: {e}")
            if attempt < max_retries:
                sleep(5)

    logger.critical("Не удалось получить новости после всех попыток.")
    return []

# === Самотестирование ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    news = fetch_latest_news("Artificial Intelligence")
    for n in news[:2]:
        print(f"• {n['title']} — {n['published']}")