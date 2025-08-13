"""
Главный модуль: управление процессом от A до Z
"""

import logging
import os
from datetime import datetime

from modules import news_fetcher, telegram_publisher
from modules.content_generator import ContentGenerator
from modules.image_generator import ImageGenerator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def main():
    logger = logging.getLogger("main")
    logger.info("Запуск процесса генерации новостного поста...")

    try:
        # 1. Получаем новости
        news_list = news_fetcher.fetch_latest_news("conflict Middle East", language="en")

        if not news_list:
            logger.warning("Новости не найдены.")
            return

        # Берем первую новость
        selected_news = news_list[0]
        logger.info(f"Выбрана новость: {selected_news['title']}")

        # 2. Генерируем текстовый контент
        content_generator = ContentGenerator()
        title, description, image_prompt = content_generator.generate_post_content(selected_news)

        if not title or not description:
            logger.error("Не удалось сгенерировать текстовый контент")
            return

        logger.info(f"Сгенерирован контент: {title}")

        # 3. Генерируем изображение (если есть промпт)
        image_path = None
        if image_prompt:
            try:
                image_generator = ImageGenerator()

                # Создаем директорию для изображений если её нет
                images_dir = "generated_images"
                os.makedirs(images_dir, exist_ok=True)

                # Генерируем уникальное имя файла
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = os.path.join(images_dir, f"news_image_{timestamp}.png")

                # Генерируем изображение с наложенным заголовком
                final_image = image_generator.generate_with_overlay(
                    image_prompt=image_prompt,
                    overlay_text=title[:50] + "..." if len(title) > 50 else title,
                    output_path=image_path
                )

                if final_image:
                    logger.info(f"Изображение сгенерировано: {image_path}")
                else:
                    logger.warning("Не удалось сгенерировать изображение")
                    image_path = None

            except Exception as e:
                logger.error(f"Ошибка при генерации изображения: {e}")
                image_path = None

        # 4. Публикуем в Telegram
        success = telegram_publisher.publish_to_telegram(
            title=title,
            body=description,
            image_path=image_path
        )

        if success:
            logger.info("✅ Пост успешно опубликован!")

            # Удаляем временный файл изображения (опционально)
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logger.info("Временное изображение удалено")
                except Exception as e:
                    logger.warning(f"Не удалось удалить изображение: {e}")
        else:
            logger.error("❌ Не удалось опубликовать пост.")

    except Exception as e:
        logger.error(f"Критическая ошибка в main: {e}")


if __name__ == "__main__":
    main()
