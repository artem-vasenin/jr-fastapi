from pathlib import Path
from datetime import datetime
from telethon.sync import TelegramClient

from local_settings import API_ID, API_HASH, CHANNEL_USERNAME


session_path = Path(__file__).resolve().parent.parent.parent / "tg_session"

# --- Функция публикации поста ---
def post_to_channel(title: str, text: str):
    # Получаем сущность канала
    with TelegramClient(str(session_path), API_ID, API_HASH) as client:
        entity = client.get_entity(CHANNEL_USERNAME)

        # Формируем сообщение с текущим временем
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{title}\n\n{text}\n\n🕒 {now}"

        # Отправляем сообщение в канал
        client.send_message(entity, message)
        print(f"Пост отправлен в канал {CHANNEL_USERNAME}")


if __name__ == "__main__":
    # Тестируем работоспособность отправки данных в телеграм канал
    post_to_channel("Тестовый заголовок", "Это текст поста.")