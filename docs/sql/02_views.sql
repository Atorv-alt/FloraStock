-- ==========================================
-- 1.7. Представления (4 представления по курсовой)
-- ==========================================

-- 1. Полная информация о заказах с подстановкой названий вместо ID
CREATE OR REPLACE VIEW vw_Заказы_с_деталями AS
SELECT
  o.OrderNumber,
  o.OrderDate,
  o.Status,
  o.TotalAmount,
  c.FullName AS Клиент,
  e.FullName AS Сотрудник,
  p.Name AS Товар
FROM "Order" o
JOIN "Client" c ON o.ClientID = c.ID
JOIN "Employee" e ON o.EmployeeID = e.ID
JOIN "Product" p ON o.ProductID = p.ID;

-- 2. Сотрудники-флористы (обновляемое представление)
CREATE OR REPLACE VIEW vw_Флористы AS
SELECT
  ID,
  FullName,
  Position,
  PhoneNumber
FROM "Employee"
WHERE Position = 'Флорист';

-- Примеры работы через представление:
-- INSERT INTO vw_Флористы (FullName, Position, PhoneNumber)
-- VALUES ('Петрова Анна Ивановна', 'Флорист', '+79161234567');
-- UPDATE vw_Флористы SET PhoneNumber = '+79160000001'
-- WHERE ID = (SELECT MAX(ID) FROM "Employee");
-- DELETE FROM vw_Флористы WHERE ID = (SELECT MAX(ID) FROM "Employee");

-- 3. Только активные заказы (статус 'Новый' или 'В обработке')
CREATE OR REPLACE VIEW vw_Активные_заказы AS
SELECT
  ID,
  OrderNumber,
  ClientID,
  EmployeeID,
  OrderDate,
  Status,
  TotalAmount
FROM "Order"
WHERE Status IN ('Новый', 'В обработке')
WITH CHECK OPTION;

-- Проверка CHECK OPTION (должна завершиться ошибкой):
-- INSERT INTO vw_Активные_заказы (OrderNumber, ClientID, EmployeeID, OrderDate, Status, TotalAmount)
-- VALUES ('ORD-103/2024', 1, 1, CURRENT_DATE, 'Доставлен', 1500.00);

-- 4. Устаревшие заказы (более 6 месяцев)
CREATE OR REPLACE VIEW vw_Устаревшие_заказы AS
SELECT *
FROM "Order"
WHERE OrderDate < CURRENT_DATE - INTERVAL '6 months';

-- Пример удаления через представление:
-- DELETE FROM vw_Устаревшие_заказы
-- WHERE ID = (SELECT MIN(ID) FROM "Order");
