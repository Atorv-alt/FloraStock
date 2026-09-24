-- ==========================================
-- 1.6. Запросы (9 запросов по курсовой)
-- БД Sclad, таблицы в кавычках с учетом регистра
-- ==========================================

-- 1. Перечень всех категорий товаров (только название)
SELECT Name
FROM "Category";

-- 2. Количество всех заказов клиентов
SELECT COUNT(*) AS Всего_заказов
FROM "Order";

-- 3. Суммарное количество товаров на складе
SELECT SUM(Quantity) AS Общий_остаток_единиц
FROM "StockPosition";

-- 4. Список всех сотрудников (ФИО), по алфавиту
SELECT FullName, Position
FROM "Employee"
ORDER BY FullName;

-- 5. Заказы, сумма которых больше средней суммы по всем заказам
SELECT OrderNumber, TotalAmount
FROM "Order"
WHERE TotalAmount > (
  SELECT AVG(TotalAmount)
  FROM "Order"
);

-- 6. ФИО сотрудников с уровнем доступа 'admin'
SELECT FullName, Position
FROM "Employee"
WHERE AccessLevel = 'admin';

-- 7. Данные о заказах с агрегатами (оконные функции)
SELECT
  OrderNumber, TotalAmount,
  SUM(TotalAmount) OVER () AS Общая_сумма_всех_заказов,
  ROUND(AVG(TotalAmount) OVER (), 2) AS Средняя_сумма,
  SUM(TotalAmount) OVER (PARTITION BY Status) AS Сумма_по_статусу
FROM "Order"
ORDER BY Status, TotalAmount DESC;

-- 8. Ранжирование заказов по общей сумме
SELECT
  OrderNumber,
  TotalAmount,
  ROW_NUMBER() OVER (ORDER BY TotalAmount ASC) AS row_num,
  RANK() OVER (ORDER BY TotalAmount ASC) AS rank,
  DENSE_RANK() OVER (ORDER BY TotalAmount ASC) AS dense_rank
FROM "Order"
ORDER BY row_num;

-- 9. Ранжирование позиций заказов с помощью партиций
SELECT
  op.ID,
  op.OrderID,
  p.Name AS Товар,
  ROW_NUMBER() OVER (PARTITION BY op.OrderID ORDER BY op.Quantity DESC) AS номер_позиции_в_заказе,
  COUNT(*) OVER (PARTITION BY op.OrderID) AS всего_позиций_в_заказе,
  MIN(op.UnitPrice) OVER (PARTITION BY op.OrderID) AS мин_цена_в_заказе
FROM "OrderPosition" op
JOIN "Product" p ON op.ProductID = p.ID
ORDER BY op.OrderID, op.Quantity DESC;
