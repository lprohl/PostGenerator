import os
from dotenv import load_dotenv

load_dotenv()

# Источник новостей: "currents" или "newsapi"
NEWS_SOURCE = "newsapi"  # или "currents"

# === Выбор ИИ-провайдера ===
# Допустимые значения: "openai", "deepseek", "yandex"
AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek").lower()

# API Keys
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
YANDEX_GPT_API_KEY = os.getenv('YANDEX_GPT_API_KEY')
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

MAX_TITLE_LENGTH = int(os.getenv('MAX_TITLE_LENGTH', 100))
MAX_DESCRIPTION_LENGTH = int(os.getenv('MAX_DESCRIPTION_LENGTH', 500))
# API Endpoints
CURRENTS_BASE_URL = "https://api.currentsapi.services/v1/search"
NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
OPENAI_MODEL = "gpt-3.5-turbo"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

YANDEX_MODEL = os.getenv('YANDEX_MODEL', 'yandexgpt-pro')
YANDEX_GPT_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

# Настройки
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES = 3
TIMEOUT = 120

