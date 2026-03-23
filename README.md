# Java Rush - FastAPI

## Работа с проектом

---

### Запуск проекта

Для корректной работы почты добавить свои настройки в base_local_settings.py
и переименовать этот файл в local_settings.py

Также в корне проекта необходим файл сессии для телеграм tg_session.session

Запуск контейнера с redis
`docker compose up --build`

Остановка контейнеров  
`docker compose down -v`

### Запуск проекта локально
Предварительно надо добавить в файл .env данные с настойками почты
Далее необходимо виртуальное окружение для работы с проектом

`python -m venv .venv`

`source .venv/bin/activate`

`pip install -m requirements.txt`

Запускаем сервер uvicorn

`uvicorn app.main:app --reload`

Другим окном терминала запускаем воркеры celery

`celery -A celery_app worker --pool=solo -l info`

API документация проекта доступна по адресу:  
[http://localhost/docs](http://localhost/docs)

## Структура проекта
```text
project/
├── app/
│   ├── api/                        # Каталог с эндпойнтами fastapi
│   │   └── v1/
│   │       ├── filtered_posts.py   # Апи для отфильтрованных новостей
│   │       ├── generate.py         # Апи для генерации ИИ новостей
│   │       ├── history.py          # История опубликованных новостей
│   │       ├── keywords.py         # Апи для работы с ключевыми словами
│   │       ├── posts.py            # Апи для работы с сырыми новостями
│   │       ├── site_sources.py     # Апи для работы с источниками rss
│   │       └── tg_sources.py       # Апи для работы с телеграм каналами
│   ├── news_parser/
│   │   ├── sites.py                # Парсер rss лент
│   │   └── channels.py             # Парсер tg каналов
│   ├── ai/
│   │   └── generator.py            # ИИ генератор заголовков и текста
│   ├── schemas/
│   │   ├── filtered_posts.py       # Модель отфильтрованных постов
│   │   ├── generate.py             # Модель сгенерированных постов
│   │   ├── history.py              # Модель опубликованных постов
│   │   ├── keywords.py             # Модель ключевых слов
│   │   ├── posts.py                # Модель сырых новостей
│   │   ├── site_sources.py         # Модель ресурсов
│   │   └── tg_sources.py           # Модель каналов
│   ├── services/
│   │   ├── dedup_service.py        # Сервис дедубликации постов
│   │   ├── filter_service.py       # Сервис фильтрации постов
│   │   ├── keyword_service.py      # Сервис работы с ключевыми словами
│   │   ├── publish.py              # Сервис публикации
│   │   └── source_service.py       # Сервис работы с источниками
│   ├── tasks/
│   │   ├── filter.py               # Задача фильтрации постов
│   │   ├── generate.py             # Задача ИИ генерации постов
│   │   ├── parse_channels.py       # Задача парсинга tg каналов
│   │   ├── parse_sites.py          # Задача парсинга rss лент
│   │   └── publication.py          # Задача публикации постов
│   ├── utils/
│   │   ├── initialization.py       # Утилита инициализации базы при запуске
│   │   └── logging.py              # Утилита логирования
│   ├── config.py                   # Конфиг для FastAPI
│   ├── dependencies.py             # Инициализация подключения к redis
│   ├── main.py                     # Точка входа для FastAPI
│   └── redis_sync.py               # Ленивая инициализация sync Redis-пула
├── celery_app.py                   # Настройка Celery
├── celery_worker.py                # .....
├── docker-compose.py               # Docker
├── local_settings.py               # Настройки проекта (не в git-е)
├── run_pipeline.py                 # Pipeline для задач Celery
├── requirements.txt                # Зависимости проекта
└── README.md                       # Описание проекта
```

---

## Роуты

```
GET     /health                 # Проверка здоровья системы

GET     /v1/keywords/           # Получение списка ключевых слов
POST    /v1/keywords/           # Создание нового ключевого слова
GET     /v1/keywords/{keyword}  # Получение ключевика
PATCH   /v1/keywords/{keyword}  # Изменение ключевика
DELETE  /v1/keywords/{keyword}  # Удаление ключевика

GET     /v1/site_sources/       # Получение списка источников rss
POST    /v1/site_sources/       # Создание нового источника rss
GET     /v1/site_sources/{name} # Получение источника rss
PATCH   /v1/site_sources/{name} # Изменение источника rss
DELETE  /v1/site_sources/{name} # Удаление источника rss

GET     /v1/tg_sources/         # Получение списка источников tg
POST    /v1/tg_sources/         # Создание нового источника tg
GET     /v1/tg_sources/{name}   # Получение источника tg
PATCH   /v1/tg_sources/{name}   # Изменение источника tg
DELETE  /v1/tg_sources/{name}   # Удаление источника tg

GET     /v1/posts/              # Получение списка сырых новостей

GET     /v1/history/            # Получение списка опубликованных новостей

GET     /v1/filtered_posts/     # Получение списка отфильтрованных новостей

POST    /v1/generate/           # Генерация новости с ИИ
GET     /v1/generate/           # Получение списка сгенерированных новостей
```

---

## Чек-лист

- [x] Сбор новостей (Сайты).
- [x] Сбор новостей (Telegram).
- [x] Фильтрация новостей.
- [x] AI-генерация постов.
- [x] Публикация в Telegram.
- [x] API-управление.
- [x] API-фильтры.
- [x] История постов.
- [x] Генерация вручную.
- [x] Документация API.
- [x] Логирование.
