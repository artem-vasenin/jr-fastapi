from telethon.sync import TelegramClient
from local_settings import API_ID, API_HASH


CHANNEL = "techmedia"
POSTS_LIMIT = 5


def main():
    with TelegramClient("tg_session", API_ID, API_HASH) as client:

        for msg in client.iter_messages(CHANNEL, limit=POSTS_LIMIT):
            print("ID:", msg.id)
            print("DATE:", msg.date)
            print("TEXT:", msg.text)
            print("LINK:", f"https://t.me/{CHANNEL}/{msg.id}")
            print("-" * 40)

main()
