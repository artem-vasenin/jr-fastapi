from datetime import datetime
from telethon.sync import TelegramClient

from local_settings import API_ID, API_HASH, CHANNEL_USERNAME

client = TelegramClient("tg_session", API_ID, API_HASH)


# --- Функция публикации поста ---
def post_to_channel(channel_username: str, title: str, text: str):
    # Получаем сущность канала
    entity = client.get_entity(channel_username)

    # Формируем сообщение с текущим временем
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{title}\n\n{text}\n\n🕒 {now}"

    # Отправляем сообщение в канал
    client.send_message(entity, message)
    print(f"Пост отправлен в канал {channel_username}")


# --- Главная функция ---
def main():
    channel_username = CHANNEL_USERNAME
    title = "Тестовый заголовок"
    text = "Это текст поста."
    post_to_channel(channel_username, title, text)


# --- Запуск клиента ---
if __name__ == "__main__":
    with client:
        main()