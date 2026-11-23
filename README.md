# Snake API

Небольшой учебный проект для практики DevOps: FastAPI-приложение, PostgreSQL, JWT-аутентификация, таблица рекордов и браузерная Snake-игра на чистом JavaScript.

## Стек

- Python 3.12, FastAPI, SQLAlchemy 2
- PostgreSQL через psycopg 3
- Argon2 для хеширования паролей, JWT (HS256) для авторизации
- HTML/CSS/vanilla JS
- pytest + SQLite in-memory для тестов

## Структура

```text
snake-api/
├── backend/
│   ├── config.py       # переменные окружения
│   ├── database.py     # SQLAlchemy engine/session
│   ├── main.py         # FastAPI routes
│   ├── models.py       # ORM-модели
│   ├── schemas.py      # Pydantic-схемы
│   └── security.py     # Argon2 + JWT
├── frontend/
│   └── index.html      # игра и клиент API
├── sql/
│   └── schema.sql      # схема PostgreSQL
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
└── requirements.txt
```

## Запуск без Docker

Требуются Python 3.12 и работающий PostgreSQL.

1. Создай базу и отдельного пользователя PostgreSQL (пример команд для `psql` под администратором):

   ```sql
   CREATE USER snake_user WITH PASSWORD 'change_me';
   CREATE DATABASE snake_db OWNER snake_user;
   ```

2. Перейди в каталог проекта, создай виртуальное окружение и установи зависимости:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Создай конфигурацию и замени секрет и пароль БД на собственные значения:

   ```bash
   cp .env.example .env
   python -c 'import secrets; print(secrets.token_urlsafe(48))'
   ```

   Скопируй сгенерированную строку в `SECRET_KEY` в `.env`. В `DATABASE_URL` укажи правильные credentials, host, port и имя базы. Формат:

   ```text
   postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
   ```

4. Примени SQL-схему:

   ```bash
   psql -h localhost -U snake_user -d snake_db -f sql/schema.sql
   ```

5. Запусти приложение:

   ```bash
   set -a
   source .env
   set +a
   uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"
   ```

   Открой `http://localhost:8000` (или порт из `.env`). Документация API: `/docs`.

> Приложение не создаёт таблицы автоматически: схема намеренно вынесена в `sql/schema.sql`, чтобы её применение было отдельным и контролируемым шагом.

## Переменные окружения

| Переменная | Назначение |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL PostgreSQL, обязательна |
| `SECRET_KEY` | секрет подписи JWT, минимум 32 символа, обязательна |
| `PORT` | порт HTTP-сервера, по умолчанию `8000` |
| `LOG_LEVEL` | уровень логирования, по умолчанию `INFO` |

Логи приложения направляются в stdout. Файл `.env` не коммить: он уже добавлен в `.gitignore`.

## API

| Метод | Endpoint | Назначение | Авторизация |
|---|---|---|---|
| `POST` | `/api/register` | регистрация `{ "username": "player", "password": "strong-pass" }` | нет |
| `POST` | `/api/login` | получение JWT с теми же полями | нет |
| `POST` | `/api/scores` | отправка `{ "score": 100 }` | `Authorization: Bearer <token>` |
| `GET` | `/api/scores/top` | топ-10 результатов | нет |
| `GET` | `/health` | проверка доступности БД | нет |

Username: 3–32 символа (`a-z`, `A-Z`, цифры, `_`, `-`). Пароль: 8–128 символов. Score: целое число от 0 до 1 000 000. JWT действует 60 минут.

## Тесты

Тесты не подключаются к PostgreSQL: для каждого теста создаётся отдельная SQLite in-memory база, а FastAPI dependency переопределяется.

```bash
python -m pytest -v
```

В наборе 10 тестов: health check, регистрация, дубликат username, валидация пароля, успешный/неуспешный login, запрет записи без токена, отправка результата, порядок и лимит таблицы лидеров, валидация отрицательного результата.

## Идеи для DevOps-практики

- Написать multi-stage Dockerfile и запускать приложение не от root.
- Создать compose-конфигурацию с отдельным PostgreSQL volume и healthcheck.
- Добавить CI: lint, pytest, сборка образа и проверка уязвимостей зависимостей.
- Добавить миграции Alembic, метрики и структурированные JSON-логи.
- Проверить graceful shutdown, конфигурацию секретов и резервное копирование БД.
