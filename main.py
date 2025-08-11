"""
Главный модуль: управление процессом от A до Z
"""
import logging
from modules import news_fetcher,  telegram_publisher
from modules.content_generator import ContentGenerator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def main():
    logger = logging.getLogger("main")
    logger.info("Запуск процесса генерации новостного поста...")

    # 1. Получаем новости
    news_list = news_fetcher.fetch_latest_news("conflict Middle East", language="en")
    if not news_list:
        logger.warning("Новости не найдены.")
        return

    # Берем первую новость
    selected_news = news_list[0]
    logger.info(f"Выбрана новость: {selected_news['title']}")

    # 2. Генерируем контент
    generator = ContentGenerator()
    title, description, image_prompt = generator.generate_post_content(
        selected_news
    )
    # 3. Публикуем
    success = telegram_publisher.publish_to_telegram(
        title=title,
        body=description
        # image_url можно добавить позже, если интегрировать DALL·E
    )

    if success:
        logger.info("✅ Пост успешно опубликован!")
    else:
        logger.error("❌ Не удалось опубликовать пост.")

if __name__ == "__main__":
    main()