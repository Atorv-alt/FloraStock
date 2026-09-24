-- ==========================================
-- 1.8. Функции (7 функций по курсовой)
-- ==========================================

-- 1. Проверка количества товара на складе, возврат рекомендации
CREATE OR REPLACE FUNCTION проверить_остаток(p_product_id INTEGER)
RETURNS TEXT AS $$
DECLARE
  v_quantity INTEGER;
  v_recommendation TEXT;
BEGIN
  SELECT SUM(Quantity) INTO v_quantity
  FROM "StockPosition"
  WHERE ProductID = p_product_id;
  IF v_quantity IS NULL OR v_quantity = 0 THEN
    v_recommendation := 'Товар отсутствует на складе. Требуется закупка';
  ELSIF v_quantity < 50 THEN
    v_recommendation := 'Остаток менее 50 ед. Рекомендуется пополнение';
  ELSIF v_quantity < 200 THEN
    v_recommendation := 'Средний остаток. Закупка не требуется';
  ELSE
    v_recommendation := 'Достаточный запас. Закупка не требуется';
  END IF;
  RETURN v_recommendation;
END;
$$ LANGUAGE plpgsql;
-- SELECT проверить_остаток(1);

-- 2. Массовая вставка тестовых товаров
CREATE OR REPLACE FUNCTION массовая_вставка_товаров()
RETURNS INTEGER AS $$
DECLARE
  v_inserted_count INTEGER;
BEGIN
  INSERT INTO "Product" (CategoryID, Name, Unit, PurchasePrice, RetailPrice, ShelfLifeDays, Color)
  VALUES
    (1, 'Роза Тестовая 1', 'шт', 100.00, 200.00, 10, 'Красный'),
    (1, 'Роза Тестовая 2', 'шт', 110.00, 220.00, 10, 'Белый'),
    (2, 'Тюльпан Тестовый 1', 'шт', 50.00, 100.00, 7, 'Желтый'),
    (2, 'Тюльпан Тестовый 2', 'шт', 55.00, 110.00, 7, 'Красный'),
    (3, 'Хризантема Тестовая', 'шт', 70.00, 140.00, 14, 'Белый');
  GET DIAGNOSTICS v_inserted_count = ROW_COUNT;
  RETURN v_inserted_count;
END;
$$ LANGUAGE plpgsql;
-- SELECT массовая_вставка_товаров();

-- 3. Обновление статуса заказа
CREATE OR REPLACE FUNCTION обновить_статус_заказа(
  p_order_id INTEGER,
  p_new_status VARCHAR(50)
)
RETURNS BOOLEAN AS $$
BEGIN
  UPDATE "Order"
  SET Status = p_new_status
  WHERE ID = p_order_id;
  IF FOUND THEN
    RETURN TRUE;
  ELSE
    RETURN FALSE;
  END IF;
END;
$$ LANGUAGE plpgsql;
-- SELECT обновить_статус_заказа(1, 'Доставлен');

-- 4. Обновление цены товара, возврат числа измененных строк
CREATE OR REPLACE FUNCTION обновить_цену_товара(
  p_product_id INTEGER,
  p_new_price DECIMAL(10,2)
)
RETURNS INTEGER AS $$
DECLARE
  v_updated_rows INTEGER;
BEGIN
  UPDATE "Product"
  SET RetailPrice = p_new_price
  WHERE ID = p_product_id;
  GET DIAGNOSTICS v_updated_rows = ROW_COUNT;
  RETURN v_updated_rows;
END;
$$ LANGUAGE plpgsql;
-- SELECT обновить_цену_товара(1, 350.00);

-- 5. Все складские остатки для заданного товара
CREATE OR REPLACE FUNCTION получить_остатки_по_товару(p_product_id INTEGER)
RETURNS SETOF "StockPosition" AS $$
BEGIN
  RETURN QUERY
  SELECT *
  FROM "StockPosition"
  WHERE ProductID = p_product_id
  ORDER BY ReceiptDate DESC;
END;
$$ LANGUAGE plpgsql;
-- SELECT * FROM получить_остатки_по_товару(1);

-- 6. Безопасное удаление категории с обработкой ошибок
CREATE OR REPLACE FUNCTION безопасно_удалить_категорию(p_category_id INTEGER)
RETURNS TEXT AS $$
BEGIN
  DELETE FROM "Category" WHERE ID = p_category_id;
  RETURN 'Категория успешно удалена';
EXCEPTION
  WHEN foreign_key_violation THEN
    RETURN 'Ошибка: на эту категорию есть ссылки в таблице Товары';
  WHEN OTHERS THEN
    RETURN 'Произошла непредвиденная ошибка: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
-- SELECT безопасно_удалить_категорию(1);

-- 7. Проверка возможности изменения уровня доступа сотрудника
CREATE OR REPLACE FUNCTION изменить_уровень_доступа(
  p_employee_id INTEGER,
  p_new_level VARCHAR(50)
)
RETURNS TEXT AS $$
DECLARE
  v_current_level VARCHAR(50);
BEGIN
  SELECT AccessLevel INTO v_current_level
  FROM "Employee" WHERE ID = p_employee_id;
  IF v_current_level = p_new_level THEN
    RAISE EXCEPTION 'Сотрудник уже имеет этот уровень доступа (%)', p_new_level;
  END IF;
  UPDATE "Employee"
  SET AccessLevel = p_new_level
  WHERE ID = p_employee_id;
  RETURN 'Уровень доступа успешно изменён';
END;
$$ LANGUAGE plpgsql;
-- SELECT изменить_уровень_доступа(1, 'admin');
