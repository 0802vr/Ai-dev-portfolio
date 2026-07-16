# Как устроен AI Developer Portfolio

Этот документ объясняет проект с точки зрения разработчика: что происходит после отправки формы, зачем нужны слои, где искать конкретную логику и как аргументировать решения на собеседовании.

## 1. Что делает проект

Посетитель открывает лендинг разработчика и отправляет форму: имя, телефон, email и описание задачи. Backend:

1. принимает HTTP-запрос;
2. присваивает ему `request_id` и пишет access log;
3. проверяет CORS и валидирует данные;
4. атомарно проверяет лимит по хешу IP;
5. отправляет комментарий в Gemini;
6. валидирует структурированный AI-ответ;
7. при любой ошибке AI использует безопасный локальный fallback;
8. сохраняет заявку и AI-анализ в PostgreSQL;
9. пытается отправить письмо владельцу и подтверждение пользователю;
10. сохраняет статусы доставки;
11. возвращает `201 Created`.

Главный принцип: внешние интеграции не должны приводить к потере заявки. Если AI или SMTP недоступны, контакт всё равно сохраняется.

## 2. Общая схема

```text
Next.js form
    │ POST /api/contact
    ▼
FastAPI middleware
    │ request_id + access log + CORS
    ▼
Pydantic validation
    ▼
ContactService
    ├── RateLimitRepository → PostgreSQL
    ├── AIService → Gemini API / fallback
    ├── ContactRepository → PostgreSQL
    └── EmailService → SMTP
    ▼
201 Created + delivery statuses
```

## 3. Структура репозитория

```text
ai-developer-portfolio/
├── backend/                 FastAPI-приложение
│   ├── alembic/             миграции PostgreSQL
│   ├── app/
│   │   ├── core/            конфигурация, ошибки, логирование
│   │   ├── repositories/    работа с PostgreSQL
│   │   ├── services/        бизнес-логика и интеграции
│   │   ├── api.py           HTTP endpoints
│   │   ├── db.py            engine и сессии SQLAlchemy
│   │   ├── main.py          создание FastAPI app и middleware
│   │   ├── models.py        таблицы SQLAlchemy
│   │   └── schemas.py       входные и выходные Pydantic-схемы
│   └── tests/               pytest-тесты
├── frontend/                Next.js-приложение
│   ├── e2e/                 Playwright
│   └── src/
│       ├── app/             App Router, страница и CSS
│       ├── components/      форма и scroll-анимация
│       └── store/           Zustand
├── postman/                 коллекция ручных/API-тестов
├── .github/workflows/       CI pipeline
├── docker-compose.yml       локальная инфраструктура
└── netlify.toml             deployment frontend
```

## 4. Backend: ключевые файлы

### `backend/app/main.py`

Точка сборки HTTP-приложения. Здесь:

- создаётся `FastAPI`;
- подключается CORS;
- регистрируется router;
- middleware создаёт или принимает `X-Request-ID`;
- измеряется длительность каждого запроса;
- access log содержит method, path, status и duration;
- глобальные exception handlers скрывают внутренние ошибки.

Почему глобальные handlers лучше `try/except` в каждом endpoint: контроллеры остаются короткими, а формат ошибок одинаков для всего API.

### `backend/app/api.py`

HTTP-слой. Он переводит HTTP в вызовы бизнес-логики:

- `POST /api/contact` создаёт сервисы и передаёт заявку в `ContactService`;
- `GET /api/health/live` проверяет, что процесс жив;
- `GET /api/health/ready` проверяет PostgreSQL и сообщает конфигурацию AI/SMTP;
- `GET /api/metrics` требует `X-API-Key`.

Контроллер не содержит SQL, SMTP или Gemini-логику. Это важный признак слоистой архитектуры.

### `backend/app/schemas.py`

Pydantic-контракт API:

- ограничивает длину имени и комментария;
- проверяет email;
- разрешает только безопасные символы и разумное количество цифр в телефоне;
- описывает структурированный AI-ответ;
- формирует OpenAPI/Swagger автоматически.

Валидация схемы не заменяет защиту HTML. В этом проекте пользовательские значения отправляются как plain text и не вставляются в HTML-письмо.

### `backend/app/services/contact.py`

Главный use case. `ContactService` определяет порядок операций:

```text
IP hash → rate limit → AI → save contact → email → save delivery status
```

Сервис ничего не знает о конкретных SQL-запросах. Он зависит от repository-интерфейсов по поведению, поэтому его удобно тестировать через `AsyncMock`.

### `backend/app/services/ai.py`

Интеграция с Gemini через `httpx.AsyncClient`:

- ключ берётся только из env;
- есть короткий timeout;
- комментарий считается недоверенными данными;
- prompt запрещает выполнять инструкции из комментария;
- Gemini должен вернуть JSON;
- JSON повторно проверяется `AIAnalysis`;
- любая внешняя ошибка включает fallback.

Fallback — не mock. Это реальная ветка production-поведения: заявка получает нейтральную классификацию и шаблонный ответ.

### `backend/app/services/email.py`

Создаёт два plain-text письма:

- владельцу: контакты, комментарий и AI-анализ;
- пользователю: подтверждение или AI-вариант ответа.

Стандартный `smtplib` блокирующий, поэтому вызов переносится в thread через `asyncio.to_thread`. Ошибки каждого письма обрабатываются независимо.

### `backend/app/repositories/contact.py`

Содержит SQLAlchemy-запросы для:

- сохранения контакта;
- обновления статусов писем;
- агрегирования metrics.

Repository отделяет бизнес-логику от способа хранения.

### `backend/app/repositories/rate_limit.py`

Rate limiting использует PostgreSQL upsert:

```sql
INSERT ... ON CONFLICT ... DO UPDATE request_count = request_count + 1
```

Операция атомарная: два одновременных запроса не потеряют увеличение счётчика. IP хранится как SHA-256, а не в открытом виде. При превышении лимита API возвращает `429` и `Retry-After`.

### `backend/app/models.py`

ORM-модели:

- `Contact` — заявка, AI-анализ и статусы доставки;
- `RateLimitBucket` — число запросов конкретного IP-хеша в фиксированном временном окне.

### `backend/app/core/config.py`

Typed-конфигурация из `.env`:

- PostgreSQL;
- CORS;
- Gemini;
- SMTP;
- metrics API key;
- rate limit;
- reverse proxy headers.

В `production` приложение отказывается запускаться с `METRICS_API_KEY=change-me` или wildcard CORS. Это fail-fast: опасная конфигурация обнаруживается при запуске, а не после инцидента.

### `backend/alembic/`

Версионирует структуру БД. При старте Docker backend выполняет:

```bash
alembic upgrade head
```

`create_all()` удалён: изменение моделей больше не меняет production-БД неявно.

## 5. Frontend: ключевые файлы

### `frontend/src/app/page.tsx`

Семантическая страница с `header`, `nav`, `main`, `section`, `article` и `footer`. Секции: hero, подход/стек, проекты и контакты.

### `frontend/src/components/contact-form.tsx`

Управляемая форма. HTML-атрибуты дают базовую клиентскую валидацию, а окончательное решение всегда принимает backend.

### `frontend/src/store/contact.ts`

Zustand хранит:

- значения полей;
- статус `idle/loading/success/error`;
- сообщение для пользователя;
- асинхронную отправку в FastAPI.

API key Gemini здесь отсутствует. Frontend знает только публичный URL backend.

### `frontend/src/components/reveal.tsx`

Framer Motion показывает элементы при попадании в viewport. Анимация выполняется один раз, чтобы повторный скролл не раздражал пользователя.

### `frontend/src/app/globals.css`

Токены цветов и типографики, responsive layout и mobile breakpoints. `prefers-reduced-motion` уменьшает анимацию для пользователей с соответствующей системной настройкой.

## 6. Docker и CI

`docker-compose.yml` поднимает:

1. PostgreSQL;
2. FastAPI;
3. Next.js standalone server.

Backend ждёт healthy PostgreSQL, применяет миграции и запускает Uvicorn. Frontend собирается multi-stage Dockerfile и работает не от root.

GitHub Actions выполняет:

- Ruff и pytest;
- ESLint и TypeScript;
- Vitest;
- production Next.js build;
- Playwright desktop/mobile;
- Docker build.

## 7. Политика ошибок

| Сценарий | Результат |
|---|---|
| Невалидные поля | `422 validation_error` |
| Слишком много запросов | `429 rate_limit_exceeded` + `Retry-After` |
| Gemini недоступен | заявка продолжается с fallback |
| SMTP недоступен | заявка сохранена, delivery=`failed/skipped` |
| PostgreSQL недоступен | `503 database_unavailable` |
| Неизвестная ошибка | `500 internal_error` |
| Неверный metrics key | `401 metrics_unauthorized` |

Внутренний exception не отправляется клиенту. Для связи ответа с логом возвращается `request_id`.

## 8. Что сказать на защите

Краткая формулировка:

> Я разделил HTTP, бизнес-логику и инфраструктуру. Контроллер валидирует контракт и вызывает use case. ContactService координирует rate limit, AI, хранение и уведомления. Все внешние интеграции имеют fallback, поэтому временная ошибка Gemini или SMTP не приводит к потере заявки. PostgreSQL изменяется только через Alembic, а CI проверяет backend, frontend, E2E и Docker.

Компромиссы:

- PostgreSQL rate limit выбран, чтобы не добавлять четвёртый Redis-контейнер;
- SMTP пока выполняется в request lifecycle, но заявка сохраняется до отправки;
- для production следующий шаг — transactional outbox и отдельный worker;
- frontend деплоится на Netlify, backend и PostgreSQL — на Render/Railway/другом Docker-хостинге.

## 9. Достаточно ли этого для тестового

Да. Обязательные требования закрыты:

- REST API и валидация;
- два email-уведомления;
- HTTP-статусы и глобальные ошибки;
- rate limiting;
- файловые логи;
- реальный AI и graceful fallback;
- env, CORS и Swagger;
- слоистая архитектура;
- PostgreSQL;
- Docker;
- тесты, Postman, README и CI;
- дополнительный адаптивный frontend.

Оставшиеся улучшения повышают production-зрелость, но не являются причиной откладывать сдачу тестового.
