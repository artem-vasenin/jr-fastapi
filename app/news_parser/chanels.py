from telethon.sync import TelegramClient
from local_settings import API_ID, API_HASH, MAX_NEWS_PER_SOURCE_PER_RUN
from pathlib import Path


session_path = Path(__file__).resolve().parent.parent.parent / "tg_session"
print(session_path)

def parse_tg(channel: str):
    with TelegramClient(str(session_path), API_ID, API_HASH) as client:
        lst = []

        for msg in client.iter_messages(channel, limit=MAX_NEWS_PER_SOURCE_PER_RUN):
            lst.append({
                "link": f"https://t.me/{channel}/{msg.id}",
                "summary": msg.message,
                "title": msg.message,
                "published_at": msg.date
            })

        return lst

# выполняем smoke-тест для функции парсинга TG канала
if __name__ == "__main__":
    CHANNEL = "purple_code_channel"

    posts = parse_tg(CHANNEL)

    for post in posts:
        print(f"{post['published_at']}")
        print(post['link'])
        print(post['summary'])
        print("-" * 80)
