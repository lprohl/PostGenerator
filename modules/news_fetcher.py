# modules/news_fetcher.py
"""
Модуль: Получение новостей из Currents API или NewsAPI.org
"""
import requests
import logging
from datetime import datetime, timedelta
from config import (
    NEWS_SOURCE,
    CURRENTS_API_KEY,
    CURRENTS_BASE_URL,
    NEWSAPI_API_KEY,
    NEWSAPI_BASE_URL,
    TIMEOUT,
)
from time import sleep

logger = logging.getLogger(__name__)

# === Вспомогательная функция: унифицированный формат новости ===
def _format_news_item(title, description, url, published, source_name, author=None):
    """Унифицирует формат новости независимо от источника"""
    return {
        "title": title,
        "description": description,
        "url": url,
        "published": published,
        "source": source_name,
        "author": author,
    }


# === Функция: Currents API (остаётся без изменений, но немного улучшена) ===
def fetch_latest_news_from_currents(keywords: str, language: str = "en", max_retries: int = 3) -> list:
    start_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    logger.info(f"[Currents] Запрашиваем новости с {start_date} по ключевым словам: {keywords}")

    params = {
        "keywords": keywords,
        "apiKey": CURRENTS_API_KEY,
        "language": language,
        "start_date": start_date,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(CURRENTS_BASE_URL, params=params, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                news = data.get("news", [])
                formatted_news = [
                    _format_news_item(
                        title=n["title"],
                        description=n.get("description", ""),
                        url=n["url"],
                        published=n["published"],
                        source_name=n["source"],
                        author=n.get("author"),
                    )
                    for n in news
                ]
                logger.info(f"[Currents] Успешно получено {len(formatted_news)} новостей.")
                return formatted_news
            elif response.status_code == 429:
                logger.warning(f"[Currents] Слишком много запросов. Пауза {5 * attempt} сек...")
                sleep(5 * attempt)
            elif response.status_code == 401:
                logger.critical("[Currents] Ошибка авторизации — проверь API-ключ!")
                return []
            else:
                logger.error(f"[Currents] Ошибка {response.status_code}: {response.text}")
                if attempt < max_retries:
                    sleep(5)

        except requests.exceptions.Timeout:
            logger.warning(f"[Currents] Таймаут (попытка {attempt}). Повтор...")
            if attempt < max_retries:
                sleep(5)
        except requests.exceptions.RequestException as e:
            logger.error(f"[Currents] Сетевая ошибка: {e}")
            if attempt < max_retries:
                sleep(5)

    logger.critical("[Currents] Не удалось получить данные после всех попыток.")
    return []


# === Функция: NewsAPI.org ===
def fetch_latest_news_from_newsapi(keywords: str, language: str = "en", max_retries: int = 3) -> list:
    logger.info(f"[NewsAPI] Запрашиваем новости по ключевым словам: {keywords}")

    # Временные рамки: последние 24 часа
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=1)
    from_str = from_date.strftime("%Y-%m-%d")
    to_str = to_date.strftime("%Y-%m-%d")

    params = {
        "q": keywords,
        "language": language,
        "from": from_str,
        "to": to_str,
        "sortBy": "publishedAt",
        "pageSize": 20,  # максимум, который можно получить
        "apiKey": NEWSAPI_API_KEY,
    }

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[NewsAPI] Запрос (попытка {attempt})")
            response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                formatted_news = []
                for item in articles:
                    # Пропускаем, если нет заголовка или ссылки
                    if not item["title"] or item["title"] == "[Removed]":
                        continue
                    formatted_news.append(
                        _format_news_item(
                            title=item["title"],
                            description=item["description"],
                            url=item["url"],
                            published=item["publishedAt"],
                            source_name=item["source"]["name"],
                            author=item.get("author"),
                        )
                    )
                logger.info(f"[NewsAPI] Успешно получено {len(formatted_news)} новостей.")
                return formatted_news

            elif response.status_code == 429:
                logger.warning(f"[NewsAPI] Лимит запросов превышен. Ждём...")
                sleep(10 * attempt)
            elif response.status_code == 401:
                logger.critical("[NewsAPI] Ошибка авторизации — проверь API-ключ!")
                return []
            else:
                logger.error(f"[NewsAPI] Ошибка {response.status_code}: {response.text}")
                if attempt < max_retries:
                    sleep(5)

        except requests.exceptions.Timeout:
            logger.warning(f"[NewsAPI] Таймаут (попытка {attempt}). Повтор...")
            if attempt < max_retries:
                sleep(5)
        except requests.exceptions.RequestException as e:
            logger.error(f"[NewsAPI] Сетевая ошибка: {e}")
            if attempt < max_retries:
                sleep(5)

    logger.critical("[NewsAPI] Не удалось получить данные после всех попыток.")
    return []


# === Основная функция: выбирает источник ===
def fetch_latest_news(keywords: str, language: str = "en", max_retries: int = 3) -> list:
    """
    Универсальная функция: получает новости с выбранного источника (из config.py)
    Возвращает список в унифицированном формате.
    """
    if NEWS_SOURCE == "currents":
        return fetch_latest_news_from_currents(keywords, language, max_retries)
    elif NEWS_SOURCE == "newsapi":
        return fetch_latest_news_from_newsapi(keywords, language, max_retries)
    else:
        logger.critical(f"Неизвестный источник новостей: {NEWS_SOURCE}")
        return []


# === Самотестирование ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    logger.info("Запуск теста получения новостей...")

    news = fetch_latest_news("Artificial Intelligence", language="en")

    if news:
        for n in news[:3]:
            print(f"• {n['title']} [{n['published']}] — {n['source']}")
            print(f"  {n['url']}\n")
    else:
        print("Новости не получены.")