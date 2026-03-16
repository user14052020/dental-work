# Зуботехническая лаборатория

Готовый комплект для промышленной эксплуатации зуботехнической лаборатории.

Сейчас в репозитории оставлены:

- `backend` на `FastAPI + PostgreSQL + SQLAlchemy Async + Redis + Elasticsearch`
- `web` на `Next.js + TypeScript + Mantine + Tailwind CSS`

## Почему выбраны Modular Architecture и Clean Architecture

Для проекта выбраны:

- `Modular Architecture` по бизнес-модулям
- `Clean Architecture` внутри каждого модуля

`FDD` не используется как основная техническая архитектура, потому что это подход к организации разработки, а не способ строить границы кода, зависимости и изоляцию слоев выполнения.

В итоге проект устроен так:

- верхний уровень делится по функциональным модулям
- внутри каждого модуля есть слои `Presentation / Domain / Data`
- роуты не ходят в базу напрямую
- бизнес-логика живет в сервисах
- доступ к данным сосредоточен в репозиториях
- все операции записи проходят через `Unit of Work`

## Структура проекта

```text
.
├── .env.example
├── docker-compose.yml
├── README.md
├── backend
│   ├── Dockerfile
│   ├── alembic
│   ├── app
│   │   ├── api
│   │   ├── common
│   │   ├── core
│   │   ├── db
│   │   ├── modules
│   │   │   ├── auth
│   │   │   ├── clients
│   │   │   ├── executors
│   │   │   ├── materials
│   │   │   ├── works
│   │   │   ├── cost_calculation
│   │   │   └── dashboard
│   │   └── seeds
│   ├── scripts
│   └── tests
└── web
    ├── Dockerfile
    ├── package.json
    ├── src
    │   ├── app
    │   ├── entities
    │   ├── features
    │   ├── screens
    │   ├── shared
    │   └── widgets
    └── public
```

## Архитектура backend

Основные принципы:

- `routers` принимают запрос, валидируют вход и вызывают сервис
- `services` содержат бизнес-логику и оркестрацию сценариев
- `repositories` инкапсулируют ORM и SQL
- `SQLAlchemyUnitOfWork` централизует транзакции
- `engine.py` содержит async engine и фабрику сессий
- глобальные ошибки обрабатываются через `exception_handlers.py`
- API версионирован как `/api/v1/...`

Поиск и инфраструктура:

- `PostgreSQL` хранит основные данные
- `Elasticsearch` обеспечивает быстрый поиск по клиентам, исполнителям, материалам и работам
- `Redis` используется для кэша dashboard и служебных фоновых задач

JWT-авторизация реализована по боевой схеме:

- короткоживущий `access token`
- долгоживущий `refresh token`
- `refresh token` хранится в БД в хэшированном виде
- есть `refresh` и `logout`
- веб-интерфейс использует `HttpOnly` cookies и BFF-слой на `Next.js`

## Архитектура веб-интерфейса

Веб-часть собрана на:

- `Next.js App Router`
- `TypeScript`
- `Mantine`
- `Tailwind CSS`
- `TanStack Query`

Структура разложена по FSD-подходу с адаптацией под App Router:

- `app` — маршрутизация фреймворка и обработчики маршрутов
- `screens` — экранные композиции
- `widgets` — крупные переиспользуемые блоки
- `features` — пользовательские сценарии
- `entities` — модели и API по сущностям
- `shared` — общий UI, конфиг, форматтеры и инфраструктура

Авторизация в веб-интерфейсе:

- браузер ходит только в `/api/auth/*` и `/api/proxy/*`
- обработчики маршрутов `Next.js` проксируют запросы в backend
- `access` и `refresh` хранятся в `HttpOnly` cookies
- при `401` запрос автоматически обновляет `access token` через `refresh token`
- JWT не хранятся в `localStorage`

## Поиск по всем реквизитам

Поиск реализован на каждом ключевом экране:

- `Клиенты`
- `Исполнители`
- `Материалы`
- `Работы`

В индекс попадают все основные введенные реквизиты:

- клиенты: название, контактное лицо, телефон, эл. почта, адрес, комментарий
- исполнители: ФИО, телефон, эл. почта, специализация, ставка, комментарий, активность
- материалы: название, категория, единица измерения, остаток, цены, поставщик, минимальный остаток, комментарий
- работы: номер заказа, клиент, исполнитель, тип работы, описание, статус, даты, финансовые поля, материалы, комментарий

## Тестовые данные

Seed создает и обновляет тестовый набор на русском языке.

Логин администратора:

- `admin@dentallab.app`
- `admin123`

Тестовые данные:

- клиент `Клиника Улыбка`
- исполнитель `Дмитрий Иванов`
- материал `Циркониевый диск`
- тестовая работа `DL-2026-0001`

Все денежные значения в интерфейсе отображаются в рублях.

Если база уже была поднята раньше, повторный запуск `seed` обновит тестовые записи на русский язык и актуальные значения.

## Порты для VPS рядом с jp-cars-parser

В репозитории `jp-cars-parser` уже заняты:

- frontend: `3000`
- backend: `8000`
- `Redis`: `6379`
- `Elasticsearch`: `9200`
- `MongoDB`: `27017`

Для этого проекта без Docker оставляем отдельными только публичные порты приложения и `PostgreSQL`:

- веб-интерфейс: `3100`
- backend API: `8100`
- `PostgreSQL`: `5433`

`Redis` и `Elasticsearch` можно переиспользовать от `jp-cars-parser`:

- `Redis`: `127.0.0.1:6379`, отдельная БД `1`
- `Elasticsearch`: `127.0.0.1:9200`, отдельные индексы `dental_*`

## Локальный запуск на VPS без Docker

1. Скопировать переменные окружения:

```bash
cp .env.example .env
cp web/.env.example web/.env
```

Для запуска по обычному `http://`, без `https`, в `web/.env` обязательно должно быть:

```text
AUTH_COOKIE_SECURE=false
INTERNAL_API_URL=http://127.0.0.1:8100/api/v1
```

2. Убедиться, что локальные сервисы подняты именно на новых портах:

- `PostgreSQL` на `127.0.0.1:5433`
- `Redis` на `127.0.0.1:6379`
- `Elasticsearch` на `127.0.0.1:9200`

### Установка PostgreSQL на Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
PG_VERSION=$(ls /etc/postgresql | sort -V | tail -n 1)
sudo sed -i "s/^port = .*/port = 5433/" /etc/postgresql/$PG_VERSION/main/postgresql.conf
sudo systemctl restart postgresql
sudo -u postgres psql -c "CREATE USER dental_lab WITH PASSWORD 'dental_lab';"
sudo -u postgres psql -c "CREATE DATABASE dental_lab OWNER dental_lab;"
sudo -u postgres psql -c "ALTER ROLE dental_lab SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE dental_lab SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE dental_lab SET timezone TO 'UTC';"
```

Проверка:

```bash
pg_isready -h 127.0.0.1 -p 5433
psql "postgresql://dental_lab:dental_lab@127.0.0.1:5433/dental_lab" -c "\l"
```

3. Поднять backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
PYTHONPATH=backend backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
PYTHONPATH=backend backend/.venv/bin/python -m app.seeds.seed
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8100
```

4. В отдельной сессии поднять веб-интерфейс:

```bash
cd web
npm ci
NEXT_PUBLIC_API_URL=http://127.0.0.1:8100/api/v1 INTERNAL_API_URL=http://127.0.0.1:8100/api/v1 npm run build
NEXT_PUBLIC_API_URL=http://127.0.0.1:8100/api/v1 INTERNAL_API_URL=http://127.0.0.1:8100/api/v1 npm run start -- --hostname 0.0.0.0 --port 3100
```

После запуска будут доступны:

- проверка backend: `http://localhost:8100/health`
- документация backend: `http://localhost:8100/docs`
- веб-интерфейс: `http://localhost:3100`

### Короткий запуск через PM2 на VPS

Если на сервере уже есть обычный общий `pm2`, для этого проекта не нужно поднимать отдельный daemon через `PM2_HOME`. Достаточно запускать процессы через `ecosystem.config.cjs`, где логи уже направлены в `/opt/dental-work/.pm2/logs`.

```bash
cd /opt/dental-work
mkdir -p /opt/dental-work/.pm2/logs
pm2 start ecosystem.config.cjs
pm2 save
```

После этого логи будут лежать здесь:

- `/opt/dental-work/.pm2/logs/dental-lab-backend-out.log`
- `/opt/dental-work/.pm2/logs/dental-lab-backend-error.log`
- `/opt/dental-work/.pm2/logs/dental-lab-web-out.log`
- `/opt/dental-work/.pm2/logs/dental-lab-web-error.log`

Для управления этим проектом используется обычный `pm2`:

```bash
pm2 status
pm2 restart dental-lab-backend
pm2 restart dental-lab-web
pm2 logs dental-lab-backend
pm2 logs dental-lab-web
```

### Что делать с Redis и Elasticsearch

Отдельно ставить их не нужно.

Для `Redis`:

- используется уже работающий инстанс `jp-cars-parser`
- для этого проекта достаточно отдельной БД: `REDIS_URL=redis://127.0.0.1:6379/1`
- дополнительная настройка нужна только если в Redis отключены несколько БД

Проверка:

```bash
redis-cli -n 1 ping
redis-cli CONFIG GET databases
```

Если `databases` меньше `2`, то в `/etc/redis/redis.conf` нужно выставить:

```text
databases 16
```

и перезапустить:

```bash
sudo systemctl restart redis-server
```

Для `Elasticsearch`:

- используется уже работающий инстанс `jp-cars-parser` на `127.0.0.1:9200`
- дополнительных портов не нужно
- конфликтов не будет, потому что у проекта свои индексы:
  - `dental_clients`
  - `dental_executors`
  - `dental_materials`
  - `dental_works`

Проверка:

```bash
curl http://127.0.0.1:9200/_cluster/health
```

## Запуск через Docker

1. Скопировать переменные окружения:

```bash
cp .env.example .env
```

2. Поднять весь стек:

```bash
docker compose up --build -d
```

3. Загрузить или обновить тестовые данные:

```bash
docker compose --profile tools run --rm seed
```

После запуска будут доступны:

- проверка backend: `http://localhost:8100/health`
- документация backend: `http://localhost:8100/docs`
- веб-интерфейс: `http://localhost:3100`

Локальный `docker compose` уже настроен так:

- backend: `8100`
- web: `3100`
- `PostgreSQL`: `5433`
- `Redis`: `6380`
- `Elasticsearch`: `9201`

Для локальной работы контейнера веб-интерфейса без HTTPS в compose уже выставлен:

```text
AUTH_COOKIE_SECURE=false
```

## Локальный запуск backend

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
PYTHONPATH=backend backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8100
```

Полезные команды:

```bash
cd backend
PYTHONPATH=. python3 scripts/reindex_search.py
PYTHONPATH=. python3 scripts/refresh_dashboard_cache.py
```

## Локальный запуск веб-интерфейса

```bash
cd web
npm install
npm run lint
NEXT_PUBLIC_API_URL=http://localhost:8100/api/v1 INTERNAL_API_URL=http://localhost:8100/api/v1 npm run build
NEXT_PUBLIC_API_URL=http://localhost:8100/api/v1 INTERNAL_API_URL=http://localhost:8100/api/v1 npm run dev -- --hostname 0.0.0.0 --port 3100
```

Открыть:

```text
http://localhost:3100
```

Для серверных обработчиков маршрутов веб-интерфейс использует:

```text
INTERNAL_API_URL=http://localhost:8100/api/v1
```

## Проверки

Проверки, которые были прогнаны в этой среде:

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall backend/app backend/tests
PYTHONPATH=backend .venv/bin/pytest backend/tests/unit -q
cd web && npm run lint
cd web && npm run build
docker compose up --build -d backend web
docker compose --profile tools run --rm seed
```

Также отдельно был проверен сценарий авторизации веб-интерфейса в Docker:

- вход
- `/api/auth/me`
- `/api/proxy/dashboard`

## Ключевые файлы

- backend entrypoint: `backend/app/main.py`
- backend DI: `backend/app/api/dependencies.py`
- backend UoW: `backend/app/db/unitofwork.py`
- backend JWT/security: `backend/app/core/security.py`
- backend auth service: `backend/app/modules/auth/service.py`
- backend seed: `backend/app/seeds/seed.py`
- BFF-слой авторизации веб-интерфейса: `web/src/app/api/auth/*`
- proxy-слой веб-интерфейса: `web/src/app/api/proxy/[...path]/route.ts`
- оболочка веб-интерфейса: `web/src/widgets/app-shell/ui/app-shell-layout.tsx`

## Что дальше

Логичные следующие шаги:

1. Добавить e2e-тесты для веб-интерфейса на сценарии входа, refresh и CRUD.
2. Добавить CSRF-защиту для изменяющих BFF route handlers.
3. Добавить более полную русскую локализацию системных ошибок backend.
4. Добавить отдельные тестовые скрипты для сброса базы и перегенерации данных.
