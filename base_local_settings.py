# --- Telegram ---------------------------------------------------------------
API_ID = 12345                  # необходимо добавить свой TG ID
API_HASH = "***"                # необходимо добавить свой TG HASH
CHANNEL_USERNAME = "jr_rusich"  # или -1001234567890 (ID канала)

# --- AI SERVICE --------------------------------------------------------------
AI_API_KEY = "***"

# --- Redis -------------------------------------------------------------------
REDIS_URL = "redis://127.0.0.1:6379/0"

# --- Периодичность парсинга (Celery Beat) ------------------------------------
PARSING_INTERVAL_MINUTES = 30

# --- Максимальное число новостей на 1 источник ---
MAX_NEWS_PER_SOURCE_PER_RUN = 7

# --- Дефолтные ключевые слова ------------------------------------------------
KEYWORDS = ["python", "ai", "startup", "telegram"]

# --- Telegram-каналы и сайты -------------------------------------------------
SITE_SOURCES = [
    {"name": "habr", "url": "https://habr.com/ru/rss/"},
    {"name": "rbc", "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"},
    {"name": "vc", "url": "https://vc.ru/rss"},
    {"name": "tproger", "url": "https://tproger.ru/feed/"},
]

TG_SOURCES = [
    {"name": "purpleschool", "id": "purple_code_channel"},
    {"name": "techmedia", "id": "techmedia"},
]
