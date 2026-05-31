# Документация базы данных "Sclad"
## Система управления ым магазином

---

## Содержание

1. [Общее описание](#общее-описание)
2. [Архитектура базы данных](#архитектура-базы-данных)
3. [Таблицы](#таблицы)
4. [Связи между таблицами](#связи-между-таблицами)
5. [Индексы](#индексы)
6. [Хранимые процедуры](#хранимые-процедуры)
7. [Роли и права доступа](#роли-и-права-доступа)
8. [Триггеры и аудит](#триггеры-и-аудит)
9. [ER-диаграмма](#er-диаграмма)

---

## Общее описание

**Название БД:** `Sclad`  
**СУБД:** PostgreSQL  
**Назначение:** Управление бизнес-процессами ого магазина  
**Версия:** 2.0

### Основные функции системы:
- Управление каталогом цветов и растений
- Складской учет и инвентаризация
- Управление клиентской базой
- Обработка заказов
- Аналитика и отчетность
- Управление персоналом
- Аудит изменений

---

## Архитектура базы данных

### Типы таблиц:

| Тип | Описание | Таблицы |
|-----|----------|---------|
| **Справочники** | Базовые данные | Category, Supplier, PaymentMethod, Discount |
| **Основные сущности** | Ключевые бизнес-объекты | Product, Client, Employee, "Order" |
| **Операционные** | Оперативные данные | OrderPosition, StockPosition, Batch |
| **Сервисные** | Дополнительный функционал | SupplierRating, EmployeeEncrypted |
| **Аудит** | Журналирование | audit_log, ProductCopy, DeletedProducts, OrderSummary |

---

## Таблицы

### 1. Category (Категории товаров)

**Описание:** Справочник категорий цветов и растений

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `Название` | VARCHAR(255) | NOT NULL, UNIQUE | Название категории |
| `Описание` | TEXT | | Описание категории |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |

**Примеры категорий:**
- Розы
- Тюльпаны
- Хризантемы
- Герберы
- Орхидеи
- Лилии
- Пионы
- Комнатные растения

---

### 2. Employee (Сотрудники)

**Описание:** Информация о сотрудниках магазина

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ФИО` | VARCHAR(255) | NOT NULL | Полное имя сотрудника |
| `Должность` | VARCHAR(100) | | Должность |
| `Номер_телефона` | VARCHAR(20) | | Контактный телефон |
| `Электронная_почта` | VARCHAR(255) | | Email |
| `Логин` | VARCHAR(100) | UNIQUE | Логин для входа |
| `Email` | VARCHAR(255) | UNIQUE | Email для системы |
| `Пароль` | VARCHAR(255) | | Хеш пароля |
| `Уровень_доступа` | VARCHAR(50) | DEFAULT 'seller' | Роль (admin/manager/seller) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли сотрудник |

**Уровни доступа:**
- `admin` - Администратор (полный доступ)
- `manager` - Менеджер (управление заказами, клиентами)
- `seller` - Продавец (создание заказов)
- `florist` - Флорист (работа с товарами)
- `warehouse` - Кладовщик (складской учет)
- `courier` - Курьер (доставка)

---

### 3. Client (Клиенты)

**Описание:** Клиентская база магазина

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ФИО` | VARCHAR(255) | NOT NULL | Полное имя клиента |
| `Номер_телефона` | VARCHAR(20) | | Контактный телефон |
| `Электронная_почта` | VARCHAR(255) | | Email |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата регистрации |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли клиент |

---

### 4. Supplier (Поставщики)

**Описание:** Информация о поставщиках цветов

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `Наименование` | VARCHAR(255) | NOT NULL, UNIQUE | Название поставщика |
| `Номер_телефона` | VARCHAR(20) | | Контактный телефон |
| `Электронный_адрес` | VARCHAR(255) | | Email |
| `Реквизиты` | TEXT | | Банковские реквизиты |
| `Адрес` | TEXT | | Адрес |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли поставщик |

---

### 5. Product (Товары)

**Описание:** Каталог товаров (цветы и растения)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_категория` | INTEGER | FOREIGN KEY → Category | Категория товара |
| `Наименование` | VARCHAR(255) | NOT NULL | Название товара |
| `Описание` | TEXT | | Описание |
| `Единица_измерения` | VARCHAR(50) | DEFAULT 'шт' | Единица измерения |
| `Закупочная_цена` | DECIMAL(10,2) | DEFAULT 0.00 | Закупочная цена |
| `Розничная_цена` | DECIMAL(10,2) | DEFAULT 0.00 | Розничная цена |
| `Срок_годности` | INTEGER | DEFAULT 7 | Срок годности в днях |
| `Цвет` | VARCHAR(50) | | Цвет цветка |
| `Длина_стебля_cm` | INTEGER | | Длина стебля в см |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли товар |

---

### 6. Batch (Партии поставок)

**Описание:** Информация о партиях поставок

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_поставщика` | INTEGER | FOREIGN KEY → Supplier | Поставщик |
| `Дата_поставки` | DATE | | Дата поставки |
| `Номер_накладной` | VARCHAR(100) | UNIQUE | Номер накладной |
| `Количество` | INTEGER | DEFAULT 0 | Общее количество |
| `Себестоимость` | DECIMAL(10,2) | DEFAULT 0.00 | Себестоимость партии |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активна ли партия |

---

### 7. "Order" (Заказы)

**Описание:** Заказы клиентов

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_клиента` | INTEGER | FOREIGN KEY → Client | Клиент |
| `ID_сотрудника` | INTEGER | FOREIGN KEY → Employee | Сотрудник, принявший заказ |
| `Дата` | DATE | NOT NULL, DEFAULT CURRENT_DATE | Дата заказа |
| `Статус` | VARCHAR(50) | DEFAULT 'Новый' | Статус заказа |
| `Номер_заказа` | VARCHAR(100) | UNIQUE | Номер заказа |
| `Сумма_заказа` | DECIMAL(10,2) | DEFAULT 0.00 | Общая сумма |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли заказ |

**Статусы заказов:**
- `New` / `Новый` - Новый заказ
- `Processing` / `В обработке` - В обработке
- `Ready` / `Готов` - Готов к выдаче/доставке
- `Delivered` / `Доставлен` - Доставлен
- `Cancelled` / `Отменен` - Отменен

---

### 8. OrderPosition (Позиции заказов)

**Описание:** Товары в составе заказа

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_заказа` | INTEGER | FOREIGN KEY → "Order" | Заказ |
| `ID_товара` | INTEGER | FOREIGN KEY → Product | Товар |
| `Количество` | INTEGER | NOT NULL, CHECK (> 0) | Количество |
| `Цена_за_единицу` | DECIMAL(10,2) | DEFAULT 0.00 | Цена за единицу |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |

**Уникальность:** `(ID_заказа, ID_товара)` - один товар в заказе один раз

---

### 9. StockPosition (Складские позиции)

**Описание:** Остатки товаров на складе

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_товара` | INTEGER | FOREIGN KEY → Product | Товар |
| `ID_партии` | INTEGER | FOREIGN KEY → Batch | Партия поставки |
| `Количество` | INTEGER | NOT NULL, DEFAULT 0, CHECK (>= 0) | Остаток |
| `Дата_поступления` | DATE | DEFAULT CURRENT_DATE | Дата поступления |
| `Место_хранения` | VARCHAR(255) | | Место на складе |
| `Температура_хранения` | VARCHAR(50) | | Температура хранения |
| `Уровень_влажности` | VARCHAR(50) | | Влажность |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активна ли позиция |

---

### 10. Discount (Скидки)

**Описание:** Справочник скидок

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `Название` | VARCHAR(255) | NOT NULL | Название скидки |
| `Описание` | TEXT | | Описание |
| `Процент` | DECIMAL(5,2) | CHECK (0-100) | Процент скидки |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активна ли скидка |

---

### 11. PaymentMethod (Методы оплаты)

**Описание:** Способы оплаты

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `Название` | VARCHAR(255) | NOT NULL, UNIQUE | Название метода |
| `Описание` | TEXT | | Описание |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли метод |

---

### 12. SupplierRating (Рейтинги поставщиков)

**Описание:** Оценки и отзывы о поставщиках

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_поставщика` | INTEGER | FOREIGN KEY → Supplier | Поставщик |
| `Оценка` | INTEGER | CHECK (1-5) | Оценка 1-5 |
| `Комментарий` | TEXT | | Отзыв |
| `Дата_оценки` | DATE | DEFAULT CURRENT_DATE | Дата оценки |
| `ID_сотрудника` | INTEGER | FOREIGN KEY → Employee | Кто оценил |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |

---

### 13. EmployeeEncrypted (Зашифрованные данные сотрудников)

**Описание:** Конфиденциальные данные сотрудников

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_сотрудника` | INTEGER | FOREIGN KEY → Employee | Сотрудник |
| `Паспортные_данные` | TEXT | | Зашифрованные паспортные данные |
| `Банковские_реквизиты` | TEXT | | Зашифрованные реквизиты |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата обновления |

---

### 14. ProductCopy (Копии товаров)

**Описание:** Архивные копии товаров для аудита

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_товара` | INTEGER | FOREIGN KEY → Product | Товар |
| `Наименование` | VARCHAR(255) | | Название |
| `Описание` | TEXT | | Описание |
| `Закупочная_цена` | DECIMAL(10,2) | | Закупочная цена |
| `Розничная_цена` | DECIMAL(10,2) | | Розничная цена |
| `Дата_копирования` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата копирования |
| `Тип_операции` | VARCHAR(50) | | INSERT/UPDATE/DELETE |

---

### 15. DeletedProducts (Удаленные товары)

**Описание:** Мягкое удаление товаров

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_товара` | INTEGER | UNIQUE | ID удаленного товара |
| `ID_категория` | INTEGER | | Категория |
| `Наименование` | VARCHAR(255) | | Название |
| `Описание` | TEXT | | Описание |
| `Закупочная_цена` | DECIMAL(10,2) | | Закупочная цена |
| `Розничная_цена` | DECIMAL(10,2) | | Розничная цена |
| `deletion_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата удаления |
| `deletion_reason` | TEXT | | Причина удаления |

---

### 16. OrderSummary (Сводка по заказам)

**Описание:** Агрегированные данные для аналитики

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `ID_заказа` | INTEGER | FOREIGN KEY → "Order" | Заказ |
| `Дата_заказа` | DATE | | Дата заказа |
| `Количество_товаров` | INTEGER | | Количество позиций |
| `Сумма_заказа` | DECIMAL(10,2) | | Общая сумма |
| `Средняя_цена` | DECIMAL(10,2) | | Средняя цена |
| `ID_клиента` | INTEGER | | Клиент |
| `ID_сотрудника` | INTEGER | | Сотрудник |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания записи |

---

### 17. audit_log (Журнал аудита)

**Описание:** Журнал всех изменений в БД

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `action` | VARCHAR(20) | NOT NULL | INSERT/UPDATE/DELETE |
| `table_name` | VARCHAR(100) | NOT NULL | Имя таблицы |
| `record_id` | INTEGER | | ID записи |
| `user_id` | INTEGER | FOREIGN KEY → Employee | Кто выполнил действие |
| `old_values` | JSONB | | Старые значения |
| `new_values` | JSONB | | Новые значения |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Время действия |
| `ip_address` | VARCHAR(45) | | IP адрес |

---

## Связи между таблицами

### Диаграмма связей:

```
Category (1) ←────── (N) Product
                              ↕
                         (N) StockPosition
                              ↕
Supplier (1) ←────── (N) Batch ←────── (N) StockPosition

Employee (1) ←────── (N) "Order" (N) ──────→ (1) Client
                              ↕
                         (N) OrderPosition (N)
                              ↕
                         (1) Product

Employee (1) ←────── (N) SupplierRating (N) ──────→ (1) Supplier

Employee (1) ←────── (1) EmployeeEncrypted
```

### Типы связей:

| Таблица 1 | Таблица 2 | Тип | Описание |
|-----------|-----------|-----|----------|
| Category | Product | 1:N | Одна категория - много товаров |
| Product | StockPosition | 1:N | Один товар - много складских позиций |
| Supplier | Batch | 1:N | Один поставщик - много партий |
| Batch | StockPosition | 1:N | Одна партия - много позиций |
| Client | "Order" | 1:N | Один клиент - много заказов |
| Employee | "Order" | 1:N | Один сотрудник - много заказов |
| "Order" | OrderPosition | 1:N | Один заказ - много позиций |
| Product | OrderPosition | 1:N | Один товар - много позиций в заказах |
| Employee | SupplierRating | 1:N | Один сотрудник - много оценок |
| Supplier | SupplierRating | 1:N | Один поставщик - много оценок |
| Employee | EmployeeEncrypted | 1:1 | Один сотрудник - одни зашифрованные данные |

---

## Индексы

### Производительность:

| Индекс | Таблица | Поле(я) | Назначение |
|--------|---------|---------|------------|
| `idx_product_name` | Product | Наименование | Поиск по названию |
| `idx_product_category` | Product | ID_категория | Фильтр по категории |
| `idx_product_price` | Product | Розничная_цена | Сортировка по цене |
| `idx_product_active` | Product | is_active | Фильтр активных |
| `idx_client_name` | Client | ФИО | Поиск клиентов |
| `idx_client_phone` | Client | Номер_телефона | Поиск по телефону |
| `idx_order_date` | "Order" | Дата | Сортировка по дате |
| `idx_order_status` | "Order" | Статус | Фильтр по статусу |
| `idx_order_client` | "Order" | ID_клиента | Заказы клиента |
| `idx_audit_table` | audit_log | table_name | Поиск по таблице |
| `idx_audit_record` | audit_log | record_id | Поиск по записи |
| `idx_audit_user` | audit_log | user_id | Действия пользователя |
| `idx_audit_timestamp` | audit_log | timestamp | Сортировка по времени |

---

## Хранимые процедуры

### 1. UpdateStock

```sql
CREATE OR REPLACE FUNCTION UpdateStock(
    p_product_id INTEGER,
    p_quantity_change INTEGER,
    p_batch_id INTEGER DEFAULT NULL
) RETURNS BOOLEAN
```

**Описание:** Обновление остатков на складе

**Параметры:**
- `p_product_id` - ID товара
- `p_quantity_change` - Изменение количества (+/-)
- `p_batch_id` - ID партии (опционально)

**Возвращает:** TRUE если обновление успешно

---

### 2. CalculateOrderTotal

```sql
CREATE OR REPLACE FUNCTION CalculateOrderTotal(
    p_order_id INTEGER
) RETURNS DECIMAL(10,2)
```

**Описание:** Расчет общей суммы заказа

**Параметры:**
- `p_order_id` - ID заказа

**Возвращает:** Общую сумму заказа

---

### 3. CheckStockAvailability

```sql
CREATE OR REPLACE FUNCTION CheckStockAvailability(
    p_product_id INTEGER,
    p_required_quantity INTEGER
) RETURNS BOOLEAN
```

**Описание:** Проверка наличия товара на складе

**Параметры:**
- `p_product_id` - ID товара
- `p_required_quantity` - Требуемое количество

**Возвращает:** TRUE если товар доступен в нужном количестве

---

## Роли и права доступа

### Системные роли:

| Роль | Описание | Права |
|------|----------|-------|
| `sclad_admin` | Администратор | Полные права на все таблицы |
| `sclad_manager` | Менеджер | Чтение, вставка, обновление, удаление |
| `sclad_florist` | Флорист | Работа с товарами и заказами |
| `sclad_seller` | Продавец | Работа с клиентами и заказами |
| `sclad_warehouse` | Кладовщик | Управление складом |
| `sclad_courier` | Курьер | Просмотр заказов, обновление статуса |

### Матрица прав:

| Таблица | Admin | Manager | Florist | Seller | Warehouse | Courier |
|---------|:-----:|:-------:|:-------:|:------:|:---------:|:-------:|
| Product | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| Client | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| "Order" | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| OrderPosition | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| StockPosition | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| Batch | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| Supplier | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| Employee | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| audit_log | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

✓ - Полный доступ  
- Только чтение  
✗ - Нет доступа

---

## Триггеры и аудит

### Система аудита:

**Таблица:** `audit_log`

**Логируемые действия:**
- INSERT - создание записи
- UPDATE - обновление записи
- DELETE - удаление записи

**Содержимое журнала:**
- Кто выполнил действие (user_id)
- Когда (timestamp)
- Где (table_name, record_id)
- Что изменилось (old_values → new_values)
- С какого IP (ip_address)

### Преимущества аудита:
- Отслеживание всех изменений
- Защита от несанкционированных действий
- Анализ активности пользователей
- Возможность восстановления данных

---

## ER-диаграмма

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Category     │     │    Product      │     │   Supplier      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK id           │◄────┤ FK ID_категория │     │ PK id           │
│    Название     │     │    Наименование │     │    Наименование │
│    Описание     │     │    Описание     │     │    Телефон      │
└─────────────────┘     │    Цена         │     └────────┬────────┘
                        └────────┬────────┘              │
                                 │                       │
                        ┌────────▼────────┐              │
                        │  StockPosition  │              │
                        ├─────────────────┤              │
                        │ PK id           │              │
                        │ FK ID_товара    │              │
                        │ FK ID_партии    │◄─────────────┘
                        │    Количество   │    ┌─────────┴─────────┐
                        └─────────────────┘    │      Batch        │
                                               ├───────────────────┤
                                               │ PK id             │
                                               │ FK ID_поставщика  │
                                               │    Дата_поставки  │
                                               └───────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Employee     │     │    "Order"      │     │     Client      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK id           │◄────┤ FK ID_сотрудника│     │ PK id           │◄────┐
│    ФИО          │     │ FK ID_клиента   │─────┘    ФИО          │     │
│    Должность    │     │    Дата         │          Телефон      │     │
│    Логин        │     │    Статус       │          Email        │     │
│    Пароль       │     │    Сумма        │          is_active    │     │
└────────┬────────┘     └────────┬────────┘                       │     │
         │                       │                                │     │
         │              ┌────────▼────────┐                       │     │
         │              │  OrderPosition  │                       │     │
         │              ├─────────────────┤                       │     │
         │              │ PK id           │                       │     │
         │              │ FK ID_заказа    │                       │     │
         │              │ FK ID_товара    │◄──────────────────────┘     │
         │              │    Количество   │                             │
         │              │    Цена         │                             │
         │              └─────────────────┘                             │
         │                                                            │
         └────────────────────┐                                       │
                              ▼                                       │
                    ┌─────────────────┐                              │
                    │  SupplierRating │                              │
                    ├─────────────────┤                              │
                    │ PK id           │                              │
                    │ FK ID_поставщика│◄─────────────────────────────┘
                    │ FK ID_сотрудника│
                    │    Оценка       │
                    └─────────────────┘
```

---

## Использование

### Подключение к БД:

```bash
# Параметры подключения
Host: localhost
Port: 5432
Database: sclad
User: sclad_user
Password: [указан в .env]
```

### Инициализация:

```bash
# Выполнить SQL скрипт
psql -U postgres -d sclad -f sql/Sclad_Database_Init.sql
```

### Резервное копирование:

```bash
# Создание бэкапа
pg_dump -U postgres -d sclad > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U postgres -d sclad < backup_20240115.sql
```

---

## Контакты

**Проект:** Sclad DBMS v2.0  
**Репозиторий:** https://github.com/koban-alt/Flover-sclad.git  
**База данных:** PostgreSQL 15+  
**Язык:** SQL + PL/pgSQL

---

*Документ создан: Май 2026*  
*Последнее обновление: v2.0*
