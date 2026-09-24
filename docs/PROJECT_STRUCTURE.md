# Структура проекта "Бизнес СУБД"

## Обзор

Проект состоит из бэкенда на C# .NET 8.0 и фронтенда на Python PyQt6 с PostgreSQL базой данных.

## Директории

```
project/
├── backend/                    # C# .NET Web API
│   ├── src/
│   │   ├── API/              # Основной API проект
│   │   ├── Core/             # Бизнес-логика и модели
│   │   ├── Data/             # Entity Framework и репозитории
│   │   └── Shared/           # Общие модели и утилиты
│   ├── tests/                 # Тесты
│   └── App.sln              # Solution файл
├── frontend/                   # Python PyQt6 приложение
│   ├── src/
│   │   ├── ui/               # Пользовательский интерфейс
│   │   │   ├── widgets/     # Виджеты
│   │   │   │   ├── dashboard_widget.py
│   │   │   │   ├── clients_widget.py
│   │   │   │   ├── products_widget.py
│   │   │   │   └── orders_widget.py
│   │   │   ├── main_window.py
│   │   │   └── login_dialog.py
│   │   ├── models/           # Модели данных
│   │   ├── services/         # Сервисы
│   │   └── utils/           # Утилиты
│   ├── requirements.txt         # Python зависимости
│   └── main.py              # Точка входа
├── docs/                      # Документация
│   ├── PROJECT_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   └── Sclad_Database_Init.sql
├── start.py                   # Скрипт запуска
├── start.sh                   # Скрипт запуска (Linux/macOS)
└── start.bat                  # Скрипт запуска (Windows)
```

## Компоненты

### Backend (C# .NET)

- **API/**: Основной Web API проект
  - Controllers: Контроллеры REST API
  - Program.cs: Точка входа приложения
  - appsettings.json: Конфигурация

- **Core/**: Бизнес-логика
  - Entities: Модели домена
  - Services: Сервисы бизнес-логики
  - Interfaces: Интерфейсы репозиториев

- **Data/**: Доступ к данным
  - Context: Entity Framework DbContext
  - Repositories: Реализации репозиториев
  - Migrations: Миграции базы данных

- **Shared/**: Общие компоненты
  - DTOs: Объекты передачи данных
  - Enums: Перечисления
  - Extensions: Методы расширения

### Frontend (Python PyQt6)

- **ui/**: Пользовательский интерфейс
  - main_window.py: Главное окно приложения
  - login_dialog.py: Диалог входа
  - widgets/: Основные виджеты
    - dashboard_widget.py: Панель управления
    - clients_widget.py: Управление клиентами
    - products_widget.py: Управление товарами
    - orders_widget.py: Управление заказами

- **models/**: Модели данных
  - client.py: Модель клиента
  - supplier.py: Модель поставщика
  - product.py: Модель товара
  - order.py: Модель заказа

- **services/**: Сервисы
  - api_service.py: Сервис взаимодействия с API

- **utils/**: Утилиты
  - config.py: Конфигурация приложения

## База данных

### PostgreSQL таблицы

- **Client**: Клиенты
- **Product**: Товары и услуги
- **Category**: Категории товаров
- **Order**: Заказы
- **OrderPosition**: Позиции заказов
- **StockPosition**: Складские позиции
- **Batch**: Партии товаров
- **Supplier**: Поставщики
- **Employee**: Сотрудники
- **audit_log**: Журнал аудита

## Запуск проекта

### Автоматический запуск
```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

### Ручной запуск

#### Backend
```bash
cd backend/src/API
dotnet run
```

#### Frontend
```bash
cd frontend
python src/main.py
```

## Зависимости

### Backend
- .NET 8.0 SDK
- Entity Framework Core
- PostgreSQL
- Swagger/OpenAPI

### Frontend
- Python 3.8+
- PyQt6
- requests
- pydantic

## Разработка

### Добавление нового виджета
1. Создать файл в `frontend/src/ui/widgets/`
2. Наследовать от `QWidget`
3. Добавить в `main_window.py`
4. Подключить в `__init__.py`

### Добавление нового API endpoint
1. Создать контроллер в `backend/src/API/Controllers/`
2. Добавить модель в `backend/src/Core/Entities/`
3. Создать репозиторий в `backend/src/Data/Repositories/`
4. Добавить DTO в `backend/src/Shared/`

## Тестирование

### Backend
```bash
cd backend
dotnet test
```

### Frontend
```bash
cd frontend
pytest
```

## Развёртывание

### Docker
```bash
# Сборка и запуск всех сервисов
docker-compose up -d
```

### Продакшн
- Backend: Публикация через `dotnet publish`
- Frontend: Упаковка через PyInstaller
- Database: Миграции через Entity Framework

## Безопасность

### Аутентификация
- JWT токены
- Хеширование паролей
- Ролевая модель доступа

### API Security
- CORS настройки
- Валидация входных данных
- Защита от SQL-инъекций

## Мониторинг

### Логирование
- Serilog для backend
- Python logging для frontend
- Структурированные логи

### Метрики
- Производительность API
- Использование базы данных
- Ошибки приложений
