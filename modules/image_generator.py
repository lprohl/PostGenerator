"""
Модуль: Генерация изображений через Stability.ai API
"""

import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os
import logging
from config import (
    STABILITY_API_KEY,
    STABILITY_ENGINE,
    STABILITY_BASE_URL,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    IMAGE_CFG_SCALE,
    IMAGE_STEPS,
    TIMEOUT
)

logger = logging.getLogger(__name__)




class ImageGenerator:
    def __init__(self):
        """Инициализация генератора изображений"""
        if not STABILITY_API_KEY:
            raise ValueError("STABILITY_API_KEY не найден в переменных окружения")

        self.api_key = STABILITY_API_KEY
        self.base_url = STABILITY_BASE_URL
        self.engine = STABILITY_ENGINE
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("Инициализирован генератор изображений Stability.ai")

    def generate_image(self, prompt: str, output_path: str = None) -> Image.Image:
        """
        Генерирует изображение по текстовому описанию

        Args:
            prompt (str): Текстовое описание изображения
            output_path (str): Путь для сохранения (опционально)

        Returns:
            PIL.Image: Сгенерированное изображение
        """
        url = f"{self.base_url}/generation/{self.engine}/text-to-image"

        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": IMAGE_CFG_SCALE,
            "height": IMAGE_HEIGHT,
            "width": IMAGE_WIDTH,
            "samples": 1,
            "steps": IMAGE_STEPS,
        }

        logger.info(f"Генерация изображения: '{prompt}'")

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=TIMEOUT
            )

            if response.status_code != 200:
                logger.error(f"Ошибка Stability.ai API: {response.status_code} - {response.text}")
                return None

            data = response.json()
            image_data = data["artifacts"][0]["base64"]

            # Декодируем base64 изображение
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            if output_path:
                image.save(output_path)
                logger.info(f"Изображение сохранено: {output_path}")

            logger.info("Изображение успешно сгенерировано")
            return image

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Stability.ai: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка генерации изображения: {e}")
            return None

    def add_text_overlay(self, image: Image.Image, text: str,
                         position: str = "bottom_left") -> Image.Image:
        """
        Добавляет текст поверх изображения

        Args:
            image: PIL изображение
            text: Текст для добавления
            position: Позиция текста

        Returns:
            PIL.Image: Изображение с текстом
        """
        if not image:
            return None

        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)

        # Загружаем шрифт
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

        # Вычисляем размеры текста
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Определяем позицию
        padding = 20
        positions = {
            "top_left": (padding, padding),
            "top_right": (image.width - text_width - padding, padding),
            "bottom_left": (padding, image.height - text_height - padding),
            "bottom_right": (image.width - text_width - padding,
                             image.height - text_height - padding),
            "center": ((image.width - text_width) // 2,
                       (image.height - text_height) // 2)
        }

        text_x, text_y = positions.get(position, positions["bottom_left"])

        # Добавляем фон под текст
        background_coords = [
            (text_x - 10, text_y - 5),
            (text_x + text_width + 10, text_y + text_height + 5)
        ]
        draw.rectangle(background_coords, fill=(0, 0, 0, 128))

        # Добавляем текст
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

        return img_with_text

    def generate_with_overlay(self, image_prompt: str, overlay_text: str,
                              output_path: str = None) -> Image.Image:
        """
        Генерирует изображение и добавляет текст одним вызовом

        Args:
            image_prompt: Описание для генерации изображения
            overlay_text: Текст для наложения
            output_path: Путь для сохранения

        Returns:
            PIL.Image: Финальное изображение с текстом
        """
        # Генерируем базовое изображение
        base_image = self.generate_image(image_prompt)

        if not base_image:
            logger.error("Не удалось сгенерировать базовое изображение")
            return None

        # Добавляем текст
        final_image = self.add_text_overlay(base_image, overlay_text)

        if output_path and final_image:
            final_image.save(output_path)
            logger.info(f"Финальное изображение сохранено: {output_path}")

        return final_image

    def test_connection(self) -> bool:
        """Тестирует подключение к Stability.ai API"""
        try:
            # Простой тест с минимальными параметрами
            url = f"{self.base_url}/generation/{self.engine}/text-to-image"
            payload = {
                "text_prompts": [{"text": "test", "weight": 1}],
                "cfg_scale": 7,
                "height": 512,
                "width": 512,
                "samples": 1,
                "steps": 10,
            }

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                logger.info("Подключение к Stability.ai API успешно")
                return True
            else:
                logger.error(f"Ошибка подключения: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Ошибка тестирования Stability.ai API: {e}")
            return False

    def get_available_engines(self) -> list:
        """Получает список доступных движков"""
        url = f"{self.base_url}/v1/engines/list"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                engines = response.json()
                logger.info("Доступные движки:")
                for engine in engines:
                    logger.info(f"- {engine['id']}: {engine['name']}")
                return engines
            else:
                logger.error(f"Ошибка получения движков: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Ошибка запроса движков: {e}")
            return []

# Самотестирование
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        generator = ImageGenerator()
        if generator.test_connection():
            print("✓ Подключение работает")

            # Тест генерации
            test_image = generator.generate_with_overlay(
                image_prompt="Beautiful sunset over mountains",
                overlay_text="Тестовое изображение",
                output_path="test_image.png"
            )

            if test_image:
                print("✓ Генерация изображений работает")
            else:
                print("✗ Ошибка генерации")
        else:
            print("✗ Проблемы с подключением")

    except Exception as e:
        print(f"✗ Ошибка инициализации: {e}")
