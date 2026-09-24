-- ==========================================
-- 06_constraints.sql
-- Ограничения целостности данных цветочного склада
-- (п.1-3 требований: целостность, форматы, уникальность)
-- Применяется ПОСЛЕ Database_Init.sql / 01-05 скриптов.
-- PostgreSQL 15+. Идемпотентно (IF NOT EXISTS там, где поддерживается).
-- ==========================================

-- ---------- 1. ЦЕНЫ > 0 ----------
ALTER TABLE Product DROP CONSTRAINT IF EXISTS chk_product_purchase_price_pos;
ALTER TABLE Product ADD CONSTRAINT chk_product_purchase_price_pos
    CHECK (PurchasePrice IS NULL OR PurchasePrice > 0);

ALTER TABLE Product DROP CONSTRAINT IF EXISTS chk_product_retail_price_pos;
ALTER TABLE Product ADD CONSTRAINT chk_product_retail_price_pos
    CHECK (RetailPrice IS NULL OR RetailPrice > 0);

ALTER TABLE Batch DROP CONSTRAINT IF EXISTS chk_batch_cost_price_pos;
ALTER TABLE Batch ADD CONSTRAINT chk_batch_cost_price_pos
    CHECK (CostPrice IS NULL OR CostPrice > 0);

ALTER TABLE OrderPosition DROP CONSTRAINT IF EXISTS chk_orderposition_unit_price_pos;
ALTER TABLE OrderPosition ADD CONSTRAINT chk_orderposition_unit_price_pos
    CHECK (UnitPrice IS NULL OR UnitPrice > 0);

ALTER TABLE OrderItem DROP CONSTRAINT IF EXISTS chk_orderitem_unit_price_pos;
ALTER TABLE OrderItem ADD CONSTRAINT chk_orderitem_unit_price_pos
    CHECK (UnitPrice IS NULL OR UnitPrice > 0);

ALTER TABLE "Order" DROP CONSTRAINT IF EXISTS chk_order_total_nonneg;
ALTER TABLE "Order" ADD CONSTRAINT chk_order_total_nonneg
    CHECK (TotalAmount IS NULL OR TotalAmount >= 0);

-- ---------- 2. КОЛИЧЕСТВА: целые >= 0 ----------
ALTER TABLE StockPosition DROP CONSTRAINT IF EXISTS chk_stock_qty_nonneg;
ALTER TABLE StockPosition ADD CONSTRAINT chk_stock_qty_nonneg
    CHECK (Quantity >= 0);

ALTER TABLE Inventory DROP CONSTRAINT IF EXISTS chk_inventory_qty_nonneg;
ALTER TABLE Inventory ADD CONSTRAINT chk_inventory_qty_nonneg
    CHECK (Quantity >= 0);

ALTER TABLE Batch DROP CONSTRAINT IF EXISTS chk_batch_qty_nonneg;
ALTER TABLE Batch ADD CONSTRAINT chk_batch_qty_nonneg
    CHECK (Quantity IS NULL OR Quantity >= 0);

ALTER TABLE OrderPosition DROP CONSTRAINT IF EXISTS chk_orderposition_qty_nonneg;
ALTER TABLE OrderPosition ADD CONSTRAINT chk_orderposition_qty_nonneg
    CHECK (Quantity >= 0);

ALTER TABLE OrderItem DROP CONSTRAINT IF EXISTS chk_orderitem_qty_nonneg;
ALTER TABLE OrderItem ADD CONSTRAINT chk_orderitem_qty_nonneg
    CHECK (Quantity >= 0);

-- ---------- 3. ДАТЫ ----------
-- Дата поставки не позже текущей даты
ALTER TABLE Batch DROP CONSTRAINT IF EXISTS chk_batch_delivery_not_future;
ALTER TABLE Batch ADD CONSTRAINT chk_batch_delivery_not_future
    CHECK (DeliveryDate IS NULL OR DeliveryDate <= CURRENT_DATE);

ALTER TABLE StockPosition DROP CONSTRAINT IF EXISTS chk_stock_receipt_not_future;
ALTER TABLE StockPosition ADD CONSTRAINT chk_stock_receipt_not_future
    CHECK (ReceiptDate IS NULL OR ReceiptDate <= CURRENT_DATE);

ALTER TABLE Inventory DROP CONSTRAINT IF EXISTS chk_inventory_receipt_not_future;
ALTER TABLE Inventory ADD CONSTRAINT chk_inventory_receipt_not_future
    CHECK (ReceiptDate IS NULL OR ReceiptDate <= CURRENT_DATE);

-- Дата заказа: корректна и не в будущем
ALTER TABLE "Order" DROP CONSTRAINT IF EXISTS chk_order_date_not_future;
ALTER TABLE "Order" ADD CONSTRAINT chk_order_date_not_future
    CHECK (OrderDate <= CURRENT_DATE);

-- ---------- 4. СРОК ХРАНЕНИЯ > 0 ----------
ALTER TABLE Product DROP CONSTRAINT IF EXISTS chk_product_shelf_life_pos;
ALTER TABLE Product ADD CONSTRAINT chk_product_shelf_life_pos
    CHECK (ShelfLifeDays IS NULL OR ShelfLifeDays > 0);

-- ---------- 5. СТАТУС ЗАКАЗА ----------
ALTER TABLE "Order" DROP CONSTRAINT IF EXISTS chk_order_status_allowed;
ALTER TABLE "Order" ADD CONSTRAINT chk_order_status_allowed
    CHECK (Status IS NULL OR Status IN ('Новый', 'В обработке', 'Выполнен', 'Доставлен'));

-- ---------- 6. УРОВЕНЬ ДОСТУПА ----------
ALTER TABLE Employee DROP CONSTRAINT IF EXISTS chk_employee_access_level;
ALTER TABLE Employee ADD CONSTRAINT chk_employee_access_level
    CHECK (AccessLevel IS NULL OR AccessLevel IN
        ('admin', 'florist', 'seller', 'purchasing', 'courier', 'warehouse'));

-- ---------- 7. ФОРМАТЫ (SIMILAR TO / Regex) ----------
-- Номер заказа ORD-XXX/ГГГГ, напр. ORD-001/2024
ALTER TABLE "Order" DROP CONSTRAINT IF EXISTS chk_order_number_format;
ALTER TABLE "Order" ADD CONSTRAINT chk_order_number_format
    CHECK (OrderNumber IS NULL OR OrderNumber ~ '^ORD-[0-9]{3,}/[0-9]{4}$');

-- Номер накладной ХХХ-YYY/ГГГГ, напр. РОЗ-001/2024 (кириллица или латиница)
ALTER TABLE Batch DROP CONSTRAINT IF EXISTS chk_batch_invoice_format;
ALTER TABLE Batch ADD CONSTRAINT chk_batch_invoice_format
    CHECK (InvoiceNumber IS NULL OR InvoiceNumber ~ '^[А-ЯЁA-Z]{2,5}-[0-9]{3,}/[0-9]{4}$');

-- Телефон +7XXXXXXXXXX
ALTER TABLE Employee DROP CONSTRAINT IF EXISTS chk_employee_phone_format;
ALTER TABLE Employee ADD CONSTRAINT chk_employee_phone_format
    CHECK (PhoneNumber IS NULL OR PhoneNumber ~ '^\+7[0-9]{10}$');

ALTER TABLE Client DROP CONSTRAINT IF EXISTS chk_client_phone_format;
ALTER TABLE Client ADD CONSTRAINT chk_client_phone_format
    CHECK (PhoneNumber IS NULL OR PhoneNumber ~ '^\+7[0-9]{10}$');

ALTER TABLE Supplier DROP CONSTRAINT IF EXISTS chk_supplier_phone_format;
ALTER TABLE Supplier ADD CONSTRAINT chk_supplier_phone_format
    CHECK (PhoneNumber IS NULL OR PhoneNumber ~ '^\+7[0-9]{10}$');

-- Email стандартного формата
ALTER TABLE Employee DROP CONSTRAINT IF EXISTS chk_employee_email_format;
ALTER TABLE Employee ADD CONSTRAINT chk_employee_email_format
    CHECK (Email IS NULL OR Email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$');

ALTER TABLE Client DROP CONSTRAINT IF EXISTS chk_client_email_format;
ALTER TABLE Client ADD CONSTRAINT chk_client_email_format
    CHECK (Email IS NULL OR Email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$');

ALTER TABLE Supplier DROP CONSTRAINT IF EXISTS chk_supplier_email_format;
ALTER TABLE Supplier ADD CONSTRAINT chk_supplier_email_format
    CHECK (Email IS NULL OR Email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$');

-- Пароль сотрудника не пустой (когда указан)
ALTER TABLE Employee DROP CONSTRAINT IF EXISTS chk_employee_password_not_empty;
ALTER TABLE Employee ADD CONSTRAINT chk_employee_password_not_empty
    CHECK (LoginPassword IS NULL OR char_length(btrim(LoginPassword)) > 0);

-- Цвет товара: только буквы (без цифр)
ALTER TABLE Product DROP CONSTRAINT IF EXISTS chk_product_color_letters;
ALTER TABLE Product ADD CONSTRAINT chk_product_color_letters
    CHECK (Color IS NULL OR Color ~ '^[А-ЯЁA-Za-zа-яё \-]+$');

-- Единица измерения: только буквы (без цифр)
ALTER TABLE Product DROP CONSTRAINT IF EXISTS chk_product_unit_letters;
ALTER TABLE Product ADD CONSTRAINT chk_product_unit_letters
    CHECK (Unit IS NULL OR Unit ~ '^[А-ЯЁA-Za-zа-яё \-]+$');

-- ---------- 8. УНИКАЛЬНОСТЬ ----------
CREATE UNIQUE INDEX IF NOT EXISTS uq_order_number ON "Order"(OrderNumber);
CREATE UNIQUE INDEX IF NOT EXISTS uq_batch_invoice ON Batch(InvoiceNumber);
CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_email ON Employee(Email);
CREATE UNIQUE INDEX IF NOT EXISTS uq_client_email ON Client(Email);
CREATE UNIQUE INDEX IF NOT EXISTS uq_category_name ON Category(Name);

-- ==========================================
-- Проверка: запрос для самодиагностики
-- SELECT conname, contype FROM pg_constraint
-- WHERE conname LIKE 'chk\_%' OR conname LIKE 'uq\_%';
-- ==========================================
