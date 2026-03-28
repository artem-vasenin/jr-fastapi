from pathlib import Path
from datetime import datetime
from telethon.sync import TelegramClient

from local_settings import API_ID, API_HASH, CHANNEL_USERNAME


session_path = Path(__file__).resolve().parent.parent.parent / "tg_session"

def post_to_channel(title: str, text: str, source: str, date: str):
    """Функция публикации поста"""
    # Получаем сущность канала
    with TelegramClient(str(session_path), API_ID, API_HASH) as client:
        entity = client.get_entity(CHANNEL_USERNAME)

        # Формируем сообщение с текущим временем
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
        formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S')

        message = f"<b>{title}</b>\n\n{text}\n\n[{source}]: 🕒 {formatted_date}"

        # Отправляем сообщение в канал
        client.send_message(entity, message, parse_mode='html')
        print(f"Пост отправлен в канал {CHANNEL_USERNAME}")


if __name__ == "__main__":
    # Тестируем работоспособность отправки данных в телеграм канал
    post_to_channel(
        "Тестовый заголовок",
        "Это текст поста.",
        "habr",
        "2026-03-21T18:00:12.084500",
    )