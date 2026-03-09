import requests
import time
import random

# Настройки — подставь свой адрес FastAPI, если порт другой
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT_SEND = "/send/"
ENDPOINT_HEALTH = "/health"

def check_health():
    """Проверяем, что FastAPI живой"""
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT_HEALTH}")
        if response.status_code == 200:
            print("FastAPI работает нормально:", response.json())
            return True
        else:
            print(f"Ошибка health-check: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Не удалось подключиться к FastAPI: {e}")
        return False


def send_message(content: str):
    """Отправляем одно сообщение в очередь"""
    payload = {"content": content}

    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT_SEND}",
            json=payload,  # автоматически сериализует в JSON
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print(f"Успешно отправлено: {content!r} → {response.json()}")
        else:
            print(f"Ошибка отправки: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")


def main():
    if not check_health():
        print("Прерываем — сервер недоступен")
        return

    print("\nОтправляем тестовые сообщения...\n")

    messages = [
        "Привет из requests-скрипта! №1",
        "Тестовое задание 2026",
        "Проверить интеграцию FastAPI + RabbitMQ",
        "Сообщение с эмодзи: 🚀🐇",
        "Последнее сообщение для теста"
    ]

    for msg in messages * 10:
        send_message(msg)
        # небольшая пауза, чтобы увидеть динамику в UI RabbitMQ
        time.sleep(random.uniform(0.5, 1))

    print("\nВсе сообщения отправлены. Проверь консоль FastAPI и RabbitMQ UI.")


if __name__ == "__main__":
    main()
