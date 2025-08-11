"""
Модуль: Генерация поста для Telegram через OpenAI или DeepSeek
"""
import logging
import re
import json
from openai import OpenAI, AzureOpenAI  # Для OpenAI
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
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Ты — опытный журналист. На основе предоставленной новости сформируй:
1. Краткий заголовок (не более {title_length} символов)
2. Краткое описание (не более {desc_length} символов)
3. Текст поста для Telegram (на русском языке, в стиле новостного канала: лаконично, драматично, без воды)
4. Подсказку для генерации изображения (на английском, детализированная, в стиле photojournalism)

Верни ТОЛЬКО JSON в точном формате:
{{
  "title": "заголовок",
  "description": "описание",
  "body": "текст поста",
  "image_prompt": "подсказка для изображения"
}}

Никаких пояснений, комментариев, markdown-разметки или текста вне JSON!
"""

def get_ai_client():
    """Возвращает клиент в зависимости от выбранного провайдера"""
    if AI_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY не задан в .env")
        client = OpenAI(api_key=OPENAI_API_KEY)
        return client, OPENAI_MODEL

    elif AI_PROVIDER == "deepseek":
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY не задан в .env")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        return client, DEEPSEEK_MODEL

    elif AI_PROVIDER == "yandex":

        if not YANDEX_GPT_API_KEY:
            raise ValueError("YANDEX_GPT_API_KEY не задан в .env")
        if not YANDEX_FOLDER_ID:
            raise ValueError("YANDEX_GPT_API_KEY не задан в .env")

        client = OpenAI(api_key=YANDEX_GPT_API_KEY, base_url=YANDEX_GPT_URL)

        return client, YANDEX_MODEL

    else:
        raise ValueError(f"Неподдерживаемый AI_PROVIDER: {AI_PROVIDER}")


def generate_post_content(news_item: dict, title_length: int = 60, desc_length: int = 120) -> dict:
    """
    Генерирует контент на основе новости через OpenAI или DeepSeek.
    """
    try:
        client, model_name = get_ai_client()
    except Exception as e:
        logger.critical(f"Не удалось инициализировать клиент ИИ: {e}")
        return {
            "title": "Ошибка",
            "description": "Не задан API-ключ",
            "body": "Ошибка: не задан ключ ИИ-провайдера.",
            "image_prompt": "error"
        }

    user_prompt = f"""
Новость:
Заголовок: {news_item.get('title', 'No title')}
Описание: {news_item.get('description', 'No description')}
Ссылка: {news_item.get('url')}
Дата: {news_item.get('published')}
Источник: {news_item.get('author')}
    """

    try:
        logger.info(f"Генерация контента через {AI_PROVIDER.upper()} (модель: {model_name})...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(title_length=title_length, desc_length=desc_length)},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        raw_content = response.choices[0].message.content.strip()
        logger.debug(f"Raw {AI_PROVIDER.upper()} response:\n{raw_content}")

        # Извлекаем JSON
        json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if not json_match:
            raise ValueError("JSON не найден в ответе")

        cleaned_json_str = json_match.group(0).replace("'", '"')

        try:
            result = json.loads(cleaned_json_str)
            required_keys = ["title", "description", "body", "image_prompt"]
            for k in required_keys:
                if k not in result:
                    result[k] = "не указано"
            return result
        except json.JSONDecodeError as je:
            logger.error(f"Ошибка парсинга JSON: {je}")
            raise

    except Exception as e:
        logger.error(f"Ошибка при генерации контента: {e}")
        return {
            "title": "Ошибка генерации",
            "description": "Не удалось сгенерировать текст",
            "body": "Произошла ошибка при обработке новости.",
            "image_prompt": "abstract error"
        }


# === Самотестирование ===
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s: %(message)s")

    # Тестовая новость
    test_news = {
        "title": "Iran and Israel clash in new escalation",
        "description": "Tensions rise after missile strikes.",
        "url": "https://example.com/news1",
        "published": "2025-04-05T10:00:00Z",
        "author": "Reuters"
    }

    print(f"Используется провайдер: {AI_PROVIDER.upper()}")
    result = generate_post_content(test_news, title_length=70, desc_length=100)

    print("\nРезультат генерации:")
    print(json.dumps(result, ensure_ascii=False, indent=2))