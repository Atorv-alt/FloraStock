Ниже — сводка всех примеров SQL-запросов с 1 по 30 для гипотетической БД **FloraStock**.
Предполагаемые таблицы: `plants`, `inventory`, `suppliers`, `orders`, `order_items`, `categories`, `customers`.

---

## 1. Выборка всех записей из одной таблицы

```sql
SELECT * FROM plants;
SELECT id, name, price FROM plants;
SELECT * FROM plants WHERE price > 100;
SELECT * FROM plants ORDER BY price DESC;
```

---

## 2. INNER JOIN

```sql
SELECT p.name, p.species, i.quantity, i.location
FROM plants p
INNER JOIN inventory i ON p.id = i.plant_id
WHERE i.quantity > 0;
```

---

## 3. LEFT JOIN

```sql
SELECT p.name, p.species, i.quantity
FROM plants p
LEFT JOIN inventory i ON p.id = i.plant_id
ORDER BY p.name;
```

---

## 4. JOIN трёх и более таблиц

```sql
SELECT o.id AS order_id,
       o.order_date,
       s.name AS supplier_name,
       p.name AS plant_name,
       oi.quantity,
       oi.price
FROM orders o
JOIN suppliers s ON o.supplier_id = s.id
JOIN order_items oi ON o.id = oi.order_id
JOIN plants p ON oi.plant_id = p.id
WHERE o.status = 'completed'
ORDER BY o.order_date DESC;
```

---

## 5. GROUP BY с агрегатными функциями

```sql
SELECT p.name,
       SUM(i.quantity) AS total_quantity
FROM plants p
JOIN inventory i ON p.id = i.plant_id
GROUP BY p.id, p.name
HAVING SUM(i.quantity) > 0
ORDER BY total_quantity DESC;
```

```sql
SELECT s.name AS supplier_name,
       AVG(o.total_amount) AS avg_order_amount,
       COUNT(*) AS order_count
FROM orders o
JOIN suppliers s ON o.supplier_id = s.id
GROUP BY s.id, s.name
HAVING COUNT(*) >= 3;
```

---

## 6. Подзапросы

```sql
SELECT name
FROM plants
WHERE id NOT IN (
    SELECT DISTINCT plant_id
    FROM order_items
);
```

```sql
SELECT s.name
FROM suppliers s
JOIN orders o ON s.id = o.supplier_id
GROUP BY s.id, s.name
HAVING AVG(o.total_amount) > (SELECT AVG(total_amount) FROM orders);
```

---

## 7. UNION

```sql
SELECT name, 'supplier' AS type FROM suppliers
UNION
SELECT name, 'customer' AS type FROM customers
ORDER BY name;
```

---

## 8. Оконные функции

```sql
SELECT p.name,
       SUM(oi.quantity * oi.price) AS total_sales,
       RANK() OVER (ORDER BY SUM(oi.quantity * oi.price) DESC) AS sales_rank
FROM plants p
JOIN order_items oi ON p.id = oi.plant_id
JOIN orders o ON oi.order_id = o.id
WHERE o.status = 'completed'
GROUP BY p.id, p.name;
```

---

## 9. UPDATE и DELETE

```sql
UPDATE inventory
SET quantity = quantity + 10
WHERE plant_id = 1 AND location = 'Основной склад';

DELETE FROM orders
WHERE status = 'cancelled' AND order_date < NOW() - INTERVAL '1 year';
```

---

## 10. RIGHT JOIN и FULL OUTER JOIN

```sql
SELECT s.name AS supplier_name, o.id AS order_id, o.order_date
FROM orders o
RIGHT JOIN suppliers s ON o.supplier_id = s.id
ORDER BY s.name;
```

```sql
SELECT p.name AS plant_name, i.quantity, i.location
FROM plants p
FULL OUTER JOIN inventory i ON p.id = i.plant_id
WHERE p.id IS NULL OR i.id IS NULL;
```

---

## 11. SELF JOIN

```sql
SELECT a.name AS name_1, b.name AS name_2, a.species
FROM plants a
JOIN plants b ON a.species = b.species AND a.id < b.id;
```

```sql
SELECT child.name AS child_category,
       parent.name AS parent_category
FROM categories child
LEFT JOIN categories parent ON child.parent_id = parent.id;
```

---

## 12. CASE WHEN

```sql
SELECT p.name,
       i.quantity,
       CASE
           WHEN i.quantity = 0 THEN 'Нет в наличии'
           WHEN i.quantity < 10 THEN 'Мало'
           WHEN i.quantity BETWEEN 10 AND 100 THEN 'Достаточно'
           ELSE 'Избыток'
       END AS stock_status
FROM plants p
JOIN inventory i ON p.id = i.plant_id;
```

```sql
SELECT o.id,
       o.total_amount,
       CASE
           WHEN o.total_amount > 10000 THEN o.total_amount * 0.85
           WHEN o.total_amount > 5000 THEN o.total_amount * 0.92
           ELSE o.total_amount
       END AS final_amount
FROM orders o
WHERE o.status = 'pending';
```

---

## 13. EXISTS и NOT EXISTS

```sql
SELECT p.name
FROM plants p
WHERE EXISTS (
    SELECT 1
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.plant_id = p.id AND o.status = 'pending'
);
```

```sql
SELECT s.name
FROM suppliers s
WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.supplier_id = s.id AND o.status = 'cancelled'
);
```

---

## 14. CTE (WITH)

```sql
WITH monthly_sales AS (
    SELECT oi.plant_id,
           SUM(oi.quantity) AS sold_qty,
           SUM(oi.quantity * oi.price) AS revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE o.order_date >= NOW() - INTERVAL '1 month'
      AND o.status = 'completed'
    GROUP BY oi.plant_id
)
SELECT p.name, ms.sold_qty, ms.revenue
FROM monthly_sales ms
JOIN plants p ON p.id = ms.plant_id
ORDER BY ms.revenue DESC
LIMIT 5;
```

```sql
WITH stock AS (
    SELECT plant_id, SUM(quantity) AS total_stock
    FROM inventory GROUP BY plant_id
),
sales AS (
    SELECT plant_id, SUM(quantity) AS total_sold
    FROM order_items GROUP BY plant_id
)
SELECT p.name,
       COALESCE(s.total_stock, 0) AS stock,
       COALESCE(sa.total_sold, 0) AS sold,
       COALESCE(s.total_stock, 0) - COALESCE(sa.total_sold, 0) AS balance
FROM plants p
LEFT JOIN stock s ON p.id = s.plant_id
LEFT JOIN sales sa ON p.id = sa.plant_id;
```

---

## 15. Оконные функции — расширенные примеры

```sql
SELECT o.order_date,
       SUM(oi.quantity * oi.price) AS daily_revenue,
       SUM(SUM(oi.quantity * oi.price))
           OVER (ORDER BY o.order_date) AS cumulative_revenue
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.order_date
ORDER BY o.order_date;
```

```sql
SELECT i.location,
       p.name,
       i.quantity,
       ROUND(100.0 * i.quantity / SUM(i.quantity) OVER (PARTITION BY i.location), 2) AS pct_of_location
FROM inventory i
JOIN plants p ON p.id = i.plant_id;
```

```sql
SELECT s.name AS supplier,
       o.order_date,
       LAG(o.order_date) OVER (PARTITION BY o.supplier_id ORDER BY o.order_date) AS prev_order,
       LEAD(o.order_date) OVER (PARTITION BY o.supplier_id ORDER BY o.order_date) AS next_order
FROM orders o
JOIN suppliers s ON s.id = o.supplier_id;
```

```sql
WITH ranked AS (
    SELECT o.*,
           ROW_NUMBER() OVER (PARTITION BY supplier_id ORDER BY order_date DESC) AS rn
    FROM orders o
)
SELECT s.name, r.order_date, r.total_amount
FROM ranked r
JOIN suppliers s ON s.id = r.supplier_id
WHERE r.rn = 1;
```

---

## 16. DISTINCT и DISTINCT ON

```sql
SELECT DISTINCT species FROM plants ORDER BY species;
```

```sql
SELECT DISTINCT ON (oi.plant_id)
       oi.plant_id,
       p.name,
       oi.price,
       o.order_date
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN plants p ON p.id = oi.plant_id
ORDER BY oi.plant_id, o.order_date DESC;
```

---

## 17. Агрегаты с FILTER

```sql
SELECT s.name,
       COUNT(*) FILTER (WHERE o.status = 'completed') AS completed,
       COUNT(*) FILTER (WHERE o.status = 'pending')   AS pending,
       COUNT(*) FILTER (WHERE o.status = 'cancelled') AS cancelled,
       COUNT(*) AS total
FROM suppliers s
LEFT JOIN orders o ON o.supplier_id = s.id
GROUP BY s.id, s.name;
```

---

## 18. UPSERT — вставка с обновлением

```sql
INSERT INTO inventory (plant_id, location, quantity)
VALUES (1, 'Основной склад', 50)
ON CONFLICT (plant_id, location)
DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity;
```

```sql
-- MySQL-вариант
INSERT INTO inventory (plant_id, location, quantity)
VALUES (1, 'Основной склад', 50)
ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
```

---

## 19. Работа с JSON-полями

```sql
SELECT name,
       attributes->>'care_level' AS care,
       (attributes->>'height_cm')::int AS height
FROM plants
WHERE attributes @> '{"care_level": "easy"}';
```

```sql
SELECT p.name, tag
FROM plants p,
     jsonb_array_elements_text(p.tags) AS tag
WHERE tag = 'суккулент';
```

---

## 20. Представления и материализованные представления

```sql
CREATE VIEW v_stock_summary AS
SELECT p.id, p.name, p.species,
       COALESCE(SUM(i.quantity), 0) AS total_stock,
       COUNT(DISTINCT i.location) AS locations_count
FROM plants p
LEFT JOIN inventory i ON p.id = i.plant_id
GROUP BY p.id, p.name, p.species;

SELECT * FROM v_stock_summary WHERE total_stock = 0;
```

```sql
CREATE MATERIALIZED VIEW mv_monthly_revenue AS
SELECT DATE_TRUNC('month', o.order_date) AS month,
       SUM(oi.quantity * oi.price) AS revenue
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.status = 'completed'
GROUP BY 1;

REFRESH MATERIALIZED VIEW mv_monthly_revenue;
```

---

## 21. Транзакции и блокировки

```sql
BEGIN;

UPDATE inventory
SET quantity = quantity - 10
WHERE plant_id = 1 AND location = 'Склад A';

UPDATE inventory
SET quantity = quantity + 10
WHERE plant_id = 1 AND location = 'Склад B';

COMMIT;
```

```sql
SELECT * FROM inventory
WHERE plant_id = 1 AND location = 'Склад A'
FOR UPDATE;
```

---

## 22. Аналитические запросы «в одном запросе»

```sql
SELECT p.id,
       p.name,
       p.species,
       (SELECT COALESCE(SUM(quantity),0) FROM inventory WHERE plant_id = p.id) AS stock,
       (SELECT COALESCE(SUM(oi.quantity),0)
          FROM order_items oi WHERE oi.plant_id = p.id) AS sold_total,
       (SELECT COUNT(DISTINCT o.supplier_id)
          FROM order_items oi
          JOIN orders o ON o.id = oi.order_id
         WHERE oi.plant_id = p.id) AS suppliers_count,
       (SELECT MAX(o.order_date)
          FROM order_items oi
          JOIN orders o ON o.id = oi.order_id
         WHERE oi.plant_id = p.id) AS last_ordered
FROM plants p
ORDER BY sold_total DESC NULLS LAST;
```

---

## 23. Пагинация

```sql
SELECT * FROM plants
ORDER BY id
LIMIT 20 OFFSET 40;
```

```sql
SELECT * FROM plants
WHERE id > 100
ORDER BY id
LIMIT 20;
```

---

## 24. Регулярные выражения и LIKE

```sql
SELECT name FROM plants WHERE name LIKE 'Фи%';
SELECT name FROM plants WHERE name ILIKE '%ficus%';
SELECT * FROM plants WHERE sku ~ '^PL-\d{4}$';
```

---

## 25. Рекурсивный CTE

```sql
WITH RECURSIVE tree AS (
    SELECT id, name, parent_id, 1 AS level
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id, t.level + 1
    FROM categories c
    JOIN tree t ON c.parent_id = t.id
)
SELECT REPEAT('  ', level - 1) || name AS tree_view
FROM tree
ORDER BY level, name;
```

---

## 26. PIVOT через CASE

```sql
SELECT p.name,
       SUM(CASE WHEN i.location = 'Склад A' THEN i.quantity ELSE 0 END) AS "Склад A",
       SUM(CASE WHEN i.location = 'Склад B' THEN i.quantity ELSE 0 END) AS "Склад B",
       SUM(CASE WHEN i.location = 'Склад C' THEN i.quantity ELSE 0 END) AS "Склад C",
       SUM(i.quantity) AS total
FROM plants p
JOIN inventory i ON p.id = i.plant_id
GROUP BY p.id, p.name
ORDER BY total DESC;
```

---

## 27. EXPLAIN и индексы

```sql
EXPLAIN ANALYZE
SELECT p.name, i.quantity
FROM plants p
JOIN inventory i ON p.id = i.plant_id
WHERE i.location = 'Склад A';
```

```sql
CREATE INDEX idx_inventory_plant ON inventory(plant_id);
CREATE INDEX idx_inventory_location ON inventory(location);
CREATE INDEX idx_orders_supplier_date ON orders(supplier_id, order_date DESC);
CREATE INDEX idx_plants_species ON plants(species);
CREATE INDEX idx_plants_name_trgm ON plants USING gin (name gin_trgm_ops);
```

---

## 28. Аудит изменений через триггеры

```sql
CREATE TABLE inventory_audit (
    id SERIAL PRIMARY KEY,
    inventory_id INT,
    old_qty INT,
    new_qty INT,
    changed_at TIMESTAMP DEFAULT NOW(),
    changed_by TEXT
);

CREATE OR REPLACE FUNCTION log_inventory_change() RETURNS trigger AS $$
BEGIN
    IF OLD.quantity <> NEW.quantity THEN
        INSERT INTO inventory_audit(inventory_id, old_qty, new_qty, changed_by)
        VALUES (OLD.id, OLD.quantity, NEW.quantity, current_user);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_inventory_audit
AFTER UPDATE ON inventory
FOR EACH ROW EXECUTE FUNCTION log_inventory_change();
```

---

## 29. Агрегация по времени

```sql
SELECT TO_CHAR(o.order_date, 'YYYY-MM') AS month,
       SUM(oi.quantity * oi.price) AS revenue,
       COUNT(DISTINCT o.id) AS orders_count
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.status = 'completed'
  AND o.order_date >= DATE_TRUNC('year', NOW())
GROUP BY 1
ORDER BY 1;
```

```sql
SELECT order_date,
       daily_revenue,
       AVG(daily_revenue) OVER (
           ORDER BY order_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS moving_avg_7d
FROM (
    SELECT o.order_date, SUM(oi.quantity * oi.price) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    GROUP BY o.order_date
) t;
```

---

## 30. Полнотекстовый поиск

```sql
SELECT name, description,
       ts_rank(to_tsvector('russian', description),
               plainto_tsquery('russian', 'тенелюбивое комнатное')) AS rank
FROM plants
WHERE to_tsvector('russian', description)
      @@ plainto_tsquery('russian', 'тенелюбивое комнатное')
ORDER BY rank DESC;
```

---
