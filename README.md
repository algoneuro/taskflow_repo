# TaskFlow

**Система управления задачами с комплексным тестированием**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![pytest](https://img.shields.io/badge/pytest-9.0-orange.svg)](https://pytest.org)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](https://coverage.readthedocs.io)

---

## О проекте

TaskFlow – это современное веб-приложение для управления личными и командными задачами. Проект разработан в рамках дипломной работы и демонстрирует полный цикл разработки с акцентом на качественное тестирование.

### Основные возможности

- Регистрация и аутентификация пользователей (JWT)
- Создание, просмотр, редактирование и удаление задач
- Установка приоритета (низкий, средний, высокий)
- Управление статусом задачи (ожидает, в работе, выполнена)
- Указание срока выполнения (due_date)
- Фильтрация задач по статусу
- Статистика: процент выполнения, средний приоритет, workload score
- Визуализация распределения задач по приоритетам

### Технологический стек

| Компонент | Технологии |
|-----------|------------|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy, SQLite, JWT, passlib (bcrypt) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Тестирование** | pytest, pytest-cov, requests, Playwright |
| **Документация** | Markdown, Swagger/OpenAPI |

---

## Быстрый старт

### Требования

- Python 3.11 или выше
- pip (менеджер пакетов Python)
- Браузер Chromium (для UI-тестов)

### Установка и запуск

#### 1. Клонирование репозитория

```bash
git clone <url-репозитория>
cd taskflow
```

#### 2. Запуск бэкенда

```bash
cd backend
pip install -r requirements.txt
python run.py
```

После запуска API будет доступно по адресу:
- `http://127.0.0.1:8000` – главная страница
- `http://127.0.0.1:8000/docs` – документация Swagger
- `http://127.0.0.1:8000/health` – проверка состояния

#### 3. Запуск фронтенда (в отдельном терминале)

```bash
cd frontend
python -m http.server 5500
```

Откройте в браузере: `http://localhost:5500`


## Тестирование

### Установка зависимостей для тестирования

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
```

### Запуск API-тестов

```bash
cd backend
pytest tests/test_auth.py tests/test_tasks.py tests/test_business_logic.py -v
```

### Запуск UI-тестов (требуется запущенный фронтенд и бэкенд)

```bash
pytest tests/test_ui.py -v
```

### Запуск всех тестов с измерением покрытия

```bash
pytest tests/ -v --cov=app --cov-report=html
```

Откройте `htmlcov/index.html` для просмотра отчёта о покрытии.

### Результаты тестирования

| Показатель | Значение |
|------------|----------|
| Всего тестов | 72 |
| Успешно | 72 |
| Покрытие кода | 99% |


## Структура проекта

```
taskflow/
├── backend/                    # Бэкенд на FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Точка входа приложения
│   │   ├── models.py          # Модели SQLAlchemy
│   │   ├── schemas.py         # Pydantic-схемы
│   │   ├── database.py        # Подключение к БД
│   │   ├── auth.py            # Аутентификация (JWT, bcrypt)
│   │   ├── crud.py            # CRUD-операции
│   │   └── routers/           # Маршруты API
│   │       ├── auth.py
│   │       ├── tasks.py
│   │       └── statistics.py
│   ├── tests/                 # Автоматизированные тесты
│   │   ├── conftest.py        # Фикстуры
│   │   ├── test_auth.py       # 19 тестов аутентификации
│   │   ├── test_tasks.py      # 25 тестов задач
│   │   ├── test_business_logic.py  # 7 тестов бизнес-логики
│   │   ├── test_contract.py   # 4 контрактных теста
│   │   ├── test_integration.py     # 2 интеграционных теста
│   │   ├── test_main.py       # 3 теста корневых эндпоинтов
│   │   ├── test_database.py   # 1 тест базы данных
│   │   └── test_ui.py         # 11 UI-тестов (Playwright)
│   ├── requirements.txt
│   └── run.py
├── frontend/                   # Фронтенд (статический)
│   ├── index.html             # Главная страница (лендинг)
│   ├── login.html             # Страница входа
│   ├── register.html          # Страница регистрации
│   ├── dashboard.html         # Дашборд (список задач)
│   ├── task-detail.html       # Детальная страница задачи
│   ├── style.css              # Стили
│   ├── common.js              # Общие функции
│   ├── auth.js                # Логика аутентификации
│   ├── dashboard.js           # Логика дашборда
│   └── task-detail.js         # Логика детальной страницы
├── test_docs/                  # Документация тестирования
│   ├── test_plan.md           # Тест-план
│   ├── test_cases.md          # Тест-кейсы (41 шт.)
│   ├── checklist.md           # Чек-лист (59 пунктов)
│   └── bug_reports.md         # Баг-репорты (5 шт.)
└── README.md                  # Этот файл
```

## Статистика тестирования

### Автоматизированные тесты

| Файл | Количество |
|------|------------|
| `test_auth.py` | 19 |
| `test_tasks.py` | 25 |
| `test_business_logic.py` | 7 |
| `test_contract.py` | 4 |
| `test_integration.py` | 2 |
| `test_main.py` | 3 |
| `test_database.py` | 1 |
| `test_ui.py` | 11 |
| **ИТОГО** | **72** |

### Покрытие кода

| Модуль | % покрытия |
|--------|------------|
| app/auth.py | 100% |
| app/crud.py | 100% |
| app/database.py | 100% |
| app/main.py | 88% |
| app/models.py | 100% |
| app/routers/auth.py | 100% |
| app/routers/statistics.py | 100% |
| app/routers/tasks.py | 100% |
| app/schemas.py | 98% |
| **ИТОГО** | **99%** |

### Ручное тестирование

- **Тест-кейсы:** 41
- **Чек-лист:** 59 пунктов
- **Выявлено дефектов:** 5 (1 исправлен, 4 в работе)


## Документация API

После запуска бэкенда документация доступна по адресу:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Основные эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/auth/register` | Регистрация пользователя |
| POST | `/auth/login` | Вход в систему |
| GET | `/auth/me` | Получение текущего пользователя |
| POST | `/tasks/` | Создание задачи |
| GET | `/tasks/` | Получение списка задач |
| GET | `/tasks/{id}` | Получение задачи по ID |
| PUT | `/tasks/{id}` | Обновление задачи |
| DELETE | `/tasks/{id}` | Удаление задачи |
| GET | `/statistics/tasks-summary` | Статистика по задачам |
| GET | `/statistics/priority-distribution` | Распределение по приоритетам |


**Итоговая статистика**

| Показатель | Значение |
|------------|----------|
| Общее количество тестов | 72 |
| Успешных тестов | 72 (100%) |
| Покрытие кода | 99% |
| Тест-кейсов (ручное) | 41 |
| Пунктов чек-листа | 59 |
| Выявлено дефектов | 5 |
| Исправлено дефектов | 1 |
