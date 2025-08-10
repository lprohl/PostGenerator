"""
Модуль: Публикация поста в Telegram канал
"""
import requests
import logging
from config import TELEGRAM_API_URL, TELEGRAM_CHANNEL_ID, TIMEOUT

logger = logging.getLogger(__name__)

def publish_to_telegram(title: str, body: str, image_url: str = None) -> bool:
    """
    Публикует пост в Telegram.
    :param title: заголовок
    :param body: текст поста
    :param image_url: URL изображения (опционально)
    :return: True при успехе
    """
    try:
        message = f"<b>{title}</b>\n\n{body}"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": "false"
        }

        if image_url:
            # Если нужно отправить фото с подписью
            url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendPhoto"
            data = {
                "chat_id": TELEGRAM_CHANNEL_ID,
                "photo": image_url,
                "caption": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=TIMEOUT)
        else:
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