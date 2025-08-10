import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# API Endpoints
CURRENTS_BASE_URL = "https://api.currentsapi.services/v1/search"
OPENAI_MODEL = "gpt-3.5-turbo"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# Настройки
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES = 3
TIMEOUT = 120