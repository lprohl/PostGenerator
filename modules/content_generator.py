import logging
import openai
import requests
import json
from typing import Dict, Tuple
from config import (
    AI_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    DEEPSEEK_BASE_URL,
    YANDEX_GPT_API_KEY,
    YANDEX_FOLDER_ID,
    YANDEX_MODEL,
    YANDEX_GPT_URL,
    MAX_TITLE_LENGTH,
    MAX_DESCRIPTION_LENGTH,
)

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.ai_provider = AI_PROVIDER

        # Инициализация в зависимости от провайдера
        if self.ai_provider == 'openai':
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            self.model = OPENAI_MODEL
        elif self.ai_provider == 'yandex':
            self.api_key = YANDEX_GPT_API_KEY
            self.folder_id = YANDEX_FOLDER_ID
            self.model = YANDEX_MODEL
            self.yandex_url = YANDEX_GPT_URL

        logger.info(f"Инициализирован генератор контента с провайдером: {self.ai_provider}")

    def _generate_with_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Генерация контента с помощью OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Ошибка при обращении к OpenAI: {e}")
            return ""

    def _generate_with_yandex(self, system_prompt: str, user_prompt: str) -> str:
        """Генерация контента с помощью YandexGPT"""
        try:
            headers = {
                'Authorization': f'Api-Key {self.api_key}',
                'Content-Type': 'application/json',
                'x-folder-id': self.folder_id  # Добавляем заголовок x-folder-id
            }

            # Правильная структура данных для YandexGPT
            data = {
                "modelUri": f"gpt://{self.folder_id}/{self.model}",  # Убираем /latest
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.7,
                    "maxTokens": 1000
                },
                "messages": [
                    {
                        "role": "system",
                        "text": system_prompt  # Используем "text" вместо "content"
                    },
                    {
                        "role": "user",
                        "text": user_prompt  # Используем "text" вместо "content"
                    }
                ]
            }

            logger.info(f"Отправка запроса к YandexGPT: {self.yandex_url}")
            logger.debug(f"Данные запроса: {json.dumps(data, ensure_ascii=False, indent=2)}")

            response = requests.post(
                self.yandex_url,
                headers=headers,
                json=data,
                timeout=30  # Добавляем таймаут
            )

            logger.info(f"Статус ответа YandexGPT: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                return result['result']['alternatives'][0]['message']['text']
            else:
                logger.error(f"Ошибка YandexGPT API: {response.status_code}")
                logger.error(f"Текст ошибки: {response.text}")
                return ""

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к YandexGPT: {e}")
            return ""
        except KeyError as e:
            logger.error(f"Ошибка парсинга ответа YandexGPT: {e}")
            return ""
        except Exception as e:
            logger.error(f"Неожиданная ошибка при обращении к YandexGPT: {e}")
            return ""

    def generate_post_content(self, news_data: Dict,
                              max_title_length: int = None,
                              max_description_length: int = None) -> Tuple[str, str, str]:
        """
        Генерация контента поста на основе новости
        """
        try:
            max_title_length = max_title_length or MAX_TITLE_LENGTH
            max_description_length = max_description_length or MAX_DESCRIPTION_LENGTH

            original_title = news_data.get('title', '')
            original_description = news_data.get('description', '')

            system_prompt = f"""Ты - опытный журналист российского информационного агентства. 
Твоя задача - адаптировать зарубежные новости для русскоязычной аудитории.

Создай на основе предоставленной новости:
1. Заголовок (максимум {max_title_length} символов) - яркий, информативный, в стиле российских СМИ
2. Описание (максимум {max_description_length} символов) - краткое изложение сути новости
3. Описание для генерации изображения (на английском языке, до 100 символов)

Стиль: официальный, но доступный, без сенсационности.
Язык заголовка и описания: русский.
Избегай прямого перевода, адаптируй под российские реалии.

Верни ТОЛЬКО JSON в точном формате:
{{
  "title": "заголовок",
  "description": "описание",
  "body": "текст поста",
  "image_prompt": "подсказка для изображения на английском"
}}"""

            user_prompt = f"""Оригинальный заголовок: {original_title}
Оригинальное описание: {original_description}"""

            logger.info(f"Генерация контента с помощью {self.ai_provider}")

            # Выбираем метод генерации в зависимости от провайдера
            if self.ai_provider == 'openai':
                content = self._generate_with_openai(system_prompt, user_prompt)
            elif self.ai_provider == 'yandex':
                content = self._generate_with_yandex(system_prompt, user_prompt)
            else:
                logger.error(f"Неподдерживаемый AI провайдер: {self.ai_provider}")
                return "", "", ""

            if not content:
                return "", "", ""

            logger.info("Контент успешно сгенерирован")

            # Парсим JSON ответ
            try:
                # Пытаемся найти JSON в ответе
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1

                if start_idx != -1 and end_idx != 0:
                    json_content = content[start_idx:end_idx]
                    result = json.loads(json_content)
                else:
                    result = json.loads(content)

                title = result.get('title', '')
                description = result.get('description', '')
                image_prompt = result.get('image_prompt', '')

                logger.info(f"Сгенерированный заголовок: {title}")
                return title, description, image_prompt

            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON ответа: {e}")
                logger.error(f"Полученный ответ: {content}")
                return "", "", ""

        except Exception as e:
            logger.error(f"Ошибка генерации контента: {e}")
            return "", "", ""

    def test_api_connection(self) -> bool:
        """Тестирование подключения к выбранному AI API"""
        try:
            logger.info(f"Тестирование подключения к {self.ai_provider}")

            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Привет"}],
                    max_tokens=10
                )

                if response.choices:
                    logger.info("Тест подключения к OpenAI API успешен")
                    return True

            elif self.ai_provider == 'yandex':
                headers = {
                    'Authorization': f'Api-Key {self.api_key}',
                    'Content-Type': 'application/json',
                    'x-folder-id': self.folder_id
                }

                data = {
                    "modelUri": f"gpt://{self.folder_id}/{self.model}",
                    "completionOptions": {
                        "stream": False,
                        "temperature": 0.1,
                        "maxTokens": 10
                    },
                    "messages": [
                        {
                            "role": "user",
                            "text": "Привет"
                        }
                    ]
                }

                response = requests.post(
                    self.yandex_url,
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if response.status_code == 200:
                    logger.info("Тест подключения к YandexGPT API успешен")
                    return True
                else:
                    logger.error(f"Ошибка YandexGPT API: {response.status_code}")
                    logger.error(f"Текст ошибки: {response.text}")
                    return False

            return False

        except Exception as e:
            logger.error(f"Ошибка тестирования {self.ai_provider} API: {e}")
            return False


# Самотестирование модуля
if __name__ == "__main__":
    generator = ContentGenerator()

    # Тест подключения
    if generator.test_api_connection():
        print(f"✓ Подключение к {generator.ai_provider} API работает")

        # Тест генерации контента
        test_news = {
            "title": "U.N. Security Council condemns Gaza war plans, 'inadequate’ aid",
            "description": "Aug. 10 (UPI) -- The United Nations Security Council convened an emergency meeting Sunday to discuss Gaza and the Middle East, specifically Israel's plan announced Friday to seize control of Gaza City. The Sunday meeting of the U.N. Security Council was called for by Britain, Denmark, France, Greece and Slovenia. It did not place a resolution on the table, a measure that the United States has used its veto power to block five times previously, but saw condemnation of Israel's plans for Gaza City. Miroslav Jenca, the assistant secretary-general for Europe, Central Asia and Americas in the United Nations Department of Political Affairs, opened the meeting with a briefing about the conditions on the ground in Gaza, including mass starvation. Jenca said the situation in Gaza continues to deteriorate, placing 2 million Palestinians in 'even greater peril' while the plan would further endanger the lives of the remaining captives taken by Hamas.",
        }

        title, description, image_prompt = generator.generate_post_content(test_news)

        if title and description:
            print("✓ Генерация контента работает")
            print(f"Заголовок: {title}")
            print(f"Описание: {description}")
            print(f"Промпт изображения: {image_prompt}")
        else:
            print("✗ Ошибка генерации контента")
    else:
        print(f"✗ Подключение к {generator.ai_provider} API не работает")
