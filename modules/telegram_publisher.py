"""
Модуль: Публикация поста в Telegram канал
"""
import os
import requests
import logging
from config import TELEGRAM_API_URL, TELEGRAM_CHANNEL_ID, TELEGRAM_BOT_TOKEN, TIMEOUT

logger = logging.getLogger(__name__)


def publish_to_telegram(title: str, body: str, image_path: str = None, image_url: str = None) -> bool:
    """
    Публикует пост в Telegram.

    :param title: заголовок
    :param body: текст поста
    :param image_path: путь к локальному файлу изображения
    :param image_url: URL изображения (опционально)
    :return: True при успехе
    """
    try:
        message = f"{title}\n\n{body}"

        # Если есть локальное изображение
        if image_path and os.path.exists(image_path):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    "chat_id": TELEGRAM_CHANNEL_ID,
                    "caption": message,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, data=data, files=files, timeout=TIMEOUT)

        # Если есть URL изображения
        elif image_url:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            data = {
                "chat_id": TELEGRAM_CHANNEL_ID,
                "photo": image_url,
                "caption": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=TIMEOUT)

        # Только текст
        else:
            data = {
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": "false"
            }
            response = requests.post(TELEGRAM_API_URL, data=data, timeout=TIMEOUT)

        if response.status_code == 200:
            logger.info("Пост успешно опубликован в Telegram.")
            return True
        else:
            logger.error(f"Ошибка публикации: {response.status_code} — {response.text}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при публикации: {e}")
        return False


# === Самотестирование ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    success = publish_to_telegram(
        title="Тестовый заголовок",
        body="Это тестовый пост.\n\n#тест"
    )
    print("Опубликовано:", success)