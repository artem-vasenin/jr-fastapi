from telethon import TelegramClient

from local_settings import API_ID, API_HASH

client = TelegramClient("tg_session", API_ID, API_HASH)

async def main():
    me = await client.get_me()
    print(me)

with client:
    client.loop.run_until_complete(main())