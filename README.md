# AI Developer Portfolio

Backend-ориентированное тестовое задание: адаптивный лендинг разработчика и API формы обратной связи с AI-анализом, SMTP-уведомлениями, защитой от спама и наблюдаемостью.

## Возможности

- `POST /api/contact`: валидация, rate limit, сохранение, Gemini-анализ и два email-уведомления.
- `GET /api/health`: состояние БД и конфигурации интеграций.
- `GET /api/health/live` и `/api/health/ready`: liveness/readiness probes.
- `GET /api/metrics`: защищённая агрегированная статистика.
- Graceful fallback: отсутствие/таймаут/ошибка AI не мешают принять заявку.
- Alembic-миграции и атомарный PostgreSQL rate limiting с `Retry-After`.
- PostgreSQL, JSON-логи с ротацией, request ID, единый формат ошибок, CORS.
- Swagger: `http://localhost:8000/docs`.
- Next.js-лендинг с Zustand-формой, scroll-анимациями и адаптивной сеткой.
- Docker Compose, pytest, Vitest, Postman и GitHub Actions.

## Быстрый запуск

Требуются Docker Desktop и Docker Compose.

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Откройте:

- frontend: `http://localhost:3000`;
- API: `http://localhost:8000`;
- Swagger: `http://localhost:8000/docs`.

Для остановки: `docker compose down`. Данные PostgreSQL сохраняются в named volume.

## Переменные окружения

Скопируйте `backend/.env.example` в `backend/.env`. Файл `.env` исключён из Git.

| Переменная | Назначение |
|---|---|
| `DATABASE_URL` | Async SQLAlchemy URL PostgreSQL |
| `CORS_ORIGINS` | Разрешённые frontend-origin через запятую |
| `GEMINI_API_KEY` | Ключ Google AI Studio |
| `GEMINI_MODEL` | Модель, по умолчанию `gemini-flash-latest` |
| `SMTP_*` | SMTP-хост, порт, логин, пароль и TLS |
| `OWNER_EMAIL` | Получатель новой заявки |
| `METRICS_API_KEY` | Секрет для `X-API-Key` на metrics |
| `RATE_LIMIT_*` | 5 запросов за 900 секунд по умолчанию |

Frontend использует `NEXT_PUBLIC_API_URL`. Для локального Docker build это `http://localhost:8000`.

## API

### Создание обращения

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Анна","phone":"+79991234567","email":"anna@example.com","comment":"Нужен корпоративный сайт с личным кабинетом"}'
```

Успех — `201 Created`:

```json
{
  "id": "9e1a43e2-45e2-4ed4-b0e6-ea2caf95fd01",
  "message": "Обращение принято",
  "owner_delivery": "sent",
  "user_delivery": "sent",
  "ai_used_fallback": false,
  "created_at": "2026-07-16T12:00:00Z"
}
```

Возможные статусы: `201`, `422` для невалидных данных, `429` для rate limit, `503` при недоступной БД. Сбой AI/SMTP не уничтожает уже принятую заявку.

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/metrics -H "X-API-Key: your-secret"
```

Готовая Postman-коллекция находится в `postman/AiDevPortfolio.postman_collection.json`.

## Архитектура

```text
frontend (Next.js → Zustand store → FastAPI)
backend
├── api.py                 HTTP-контракт и зависимости
├── schemas.py             входные/выходные Pydantic-схемы
├── services/              бизнес-логика, AI и SMTP
├── repositories/          SQLAlchemy-запросы
├── models.py              модели PostgreSQL
└── core/                  env, ошибки и логирование
```

Контроллер не знает деталей Gemini, SMTP или SQL-запросов. `ContactService` координирует use case, repository отвечает за хранение, интеграционные сервисы изолируют внешние системы.

Заявка сохраняется **до** отправки почты. Если SMTP недоступен, API всё равно возвращает `201`, а статусы `owner_delivery`/`user_delivery` и тип ошибки остаются в БД. Для production следующим шагом будет outbox + очередь повторной доставки.

Rate limiting хранится в PostgreSQL: атомарный upsert увеличивает bucket по SHA-256 от IP и фиксированному временному окну. Это работает между несколькими экземплярами API без Redis. За reverse proxy включите `TRUST_PROXY_HEADERS=true` только если прокси очищает входящий `X-Forwarded-For`.

Схема БД управляется Alembic. Backend-контейнер перед запуском выполняет `alembic upgrade head`; `create_all()` в runtime не используется.

## AI-интеграция

Gemini получает только имя и комментарий и возвращает JSON:

```json
{"category":"website","sentiment":"neutral","priority":"medium","summary":"...","suggested_reply":"..."}
```

Результат повторно валидируется Pydantic. Системный prompt ограничивает категории, запрещает следовать инструкциям из пользовательского комментария и не позволяет обещать цену/срок. При отсутствии ключа, HTTP-ошибке, таймауте, неверном JSON или нарушении схемы используется нейтральный локальный ответ. Контакт всё равно сохраняется.

## Разработка и тесты

Backend:

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -e ".[dev]"
ruff check .
pytest --cov=app
```

Frontend:

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

CI выполняет backend lint/tests, frontend lint/typecheck/tests/build, Playwright desktop/mobile и затем Docker build. Секреты для CI не нужны: AI fallback тестируется без внешнего ключа. Текущий backend-набор содержит 13 тестов и покрывает около 76% кода.

## Деплой

Frontend разворачивается на Netlify из папки `frontend`; конфигурация находится в `netlify.toml`. В Netlify задайте `NEXT_PUBLIC_API_URL` публичного backend.

FastAPI и PostgreSQL нельзя разместить в обычном статическом Netlify deployment. Backend следует развернуть на Render/Railway/AnyHost как Docker service, добавить env-переменные и persistent PostgreSQL. После этого домен backend указывается в `NEXT_PUBLIC_API_URL`, а домен Netlify — в `CORS_ORIGINS`.

## Что сделано с помощью AI

AI применялся для первичного каркаса слоёв, вариантов API-контракта, frontend-композиции и тестовых сценариев. Вручную были уточнены политика частичного SMTP-сбоя, защита metrics, хранение rate limit в PostgreSQL, валидация структурированного AI-ответа, CORS, request ID и правила работы с секретами. Финальные изменения проверяются линтерами, тестами, production build и Docker-интеграцией.

Основные рабочие запросы к AI: спроектировать минимальный надёжный contact pipeline; выделить Controller/Service/Repository; сформировать строгий JSON prompt для классификации; составить тесты fallback/rate limit/валидации; проверить Docker и CI границы.

## Безопасность

- секреты существуют только в env и никогда не передаются frontend;
- IP не хранится в открытом виде;
- пользовательский ввод не интерпретируется как HTML;
- внешние исключения не возвращаются клиенту;
- metrics использует constant-time сравнение API-ключа;
- CORS ограничен явным списком origin;
- AI prompt рассматривает комментарий как недоверенные данные.
