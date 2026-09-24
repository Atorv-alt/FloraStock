-- ==========================================
-- 1.9. Транзакции (2 транзакции по курсовой)
-- ==========================================

-- 1. Транзакция: новый заказ + списание товара со склада
BEGIN ISOLATION LEVEL READ COMMITTED;
-- Шаг 1: создаём новый заказ (номер в формате ORD-XXX/ГГГГ, см. 06_constraints.sql)
INSERT INTO "Order" (ClientID, EmployeeID, ProductID, OrderDate, Status, OrderNumber, TotalAmount)
VALUES (1, 1, 1, CURRENT_DATE, 'Новый', 'ORD-101/2024', 1500.00);
-- Точка сохранения
SAVEPOINT после_создания_заказа;
-- Шаг 2: добавляем позиции заказа
INSERT INTO "OrderPosition" (OrderID, ProductID, Quantity, UnitPrice)
VALUES
((SELECT ID FROM "Order" WHERE OrderNumber = 'ORD-101/2024'), 1, 5, 300.00);
-- Шаг 3: списываем товар со склада
UPDATE "StockPosition"
SET Quantity = Quantity - 5
WHERE ProductID = 1 AND BatchID = 1;
COMMIT;

-- 2. Транзакция с примером ошибки и ROLLBACK
-- Внимание: имена таблиц в кавычках с учетом регистра!
BEGIN;
INSERT INTO "StockPosition" (ProductID, BatchID, Quantity, ReceiptDate, StorageLocation)
VALUES (9999, 1, 100, CURRENT_DATE, 'Холодильник А1');
ROLLBACK;
-- Проверка отката:
-- SELECT * FROM "StockPosition" WHERE StorageLocation = 'Холодильник А1';
