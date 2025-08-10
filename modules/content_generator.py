"""
Модуль: Генерация поста для Telegram с помощью ChatGPT (новая версия openai v1+)
"""
import openai
import logging
import re
import json
from config import OPENAI_API_KEY, OPENAI_MODEL

# Настройка клиента OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)
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

def generate_post_content(news_item: dict, title_length: int = 60, desc_length: int = 120) -> dict:
    """
    Генерирует контент на основе новости.
    """
    user_prompt = f"""
Новость:
Заголовок: {news_item.get('title', 'No title')}
Описание: {news_item.get('description', 'No description')}
Ссылка: {news_item.get('url')}
Дата: {news_item.get('published')}
Источник: {news_item.get('author')}
    """

    try:
        logger.info("Генерация контента через ChatGPT...")
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(title_length=title_length, desc_length=desc_length)},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        raw_content = response.choices[0].message.content.strip()
        logger.debug(f"Raw GPT response:\n{raw_content}")

        # Извлекаем JSON из ответа
        json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if not json_match:
            raise ValueError("JSON блок не найден в ответе")

        cleaned_json_str = json_match.group(0)
        cleaned_json_str = cleaned_json_str.replace("'", '"')  # Замена одинарных кавычек

        try:
            result = json.loads(cleaned_json_str)
            # Проверим, что все ключи на месте
            required_keys = ["title", "description", "body", "image_prompt"]
            for k in required_keys:
                if k not in result:
                    result[k] = "не указано"
            logger.info("Контент успешно сгенерирован.")
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
    logging.basicConfig(level=logging.DEBUG)
    test_news = {
        "title": "Iran and Israel clash in new escalation",
        "description": "Tensions rise after missile strikes.",
        "url": "https://example.com/news1",
        "published": "2025-04-05T10:00:00Z",
        "author": "Reuters"
    }
    result = generate_post_content(test_news, title_length=70, desc_length=100)
    print("Результат генерации:")
    print(json.dumps(result, ensure_ascii=False, indent=2))