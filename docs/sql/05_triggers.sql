-- ==========================================
-- 1.10. Триггеры (по курсовой)
-- В курсовой trg_save_status_change ссылается на
-- несуществующую fn_save_status_change — здесь она реализована.
-- ==========================================

-- Таблица аудита изменений заказов
CREATE TABLE IF NOT EXISTS audit_order (
  id BIGSERIAL PRIMARY KEY,
  operation TEXT,
  order_id INT,
  old_data JSONB,
  new_data JSONB,
  changed_by TEXT DEFAULT current_user,
  changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Функция аудита, вызываемая при любом изменении "Order"
CREATE OR REPLACE FUNCTION fn_audit_order()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO audit_order (operation, order_id, new_data)
    VALUES ('INSERT', NEW.ID, to_jsonb(NEW));
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_order (operation, order_id, old_data, new_data)
    VALUES ('UPDATE', NEW.ID, to_jsonb(OLD), to_jsonb(NEW));
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO audit_order (operation, order_id, old_data)
    VALUES ('DELETE', OLD.ID, to_jsonb(OLD));
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_order ON "Order";
CREATE TRIGGER trg_audit_order
AFTER INSERT OR UPDATE OR DELETE
ON "Order"
FOR EACH ROW
EXECUTE FUNCTION fn_audit_order();

-- Недостающая в курсовой функция: фиксация смены статуса
CREATE OR REPLACE FUNCTION fn_save_status_change()
RETURNS TRIGGER AS $$
BEGIN
  -- статус уже фиксируется в audit_order через trg_audit_order,
  -- здесь только разрешаем обновление
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_save_status_change ON "Order";
CREATE TRIGGER trg_save_status_change
BEFORE UPDATE ON "Order"
FOR EACH ROW
WHEN (OLD.Status IS DISTINCT FROM NEW.Status)
EXECUTE FUNCTION fn_save_status_change();

-- Проверка работы триггера:
-- INSERT INTO "Order" (ClientID, EmployeeID, ProductID, OrderDate, Status, OrderNumber, TotalAmount)
-- VALUES (1, 1, 1, CURRENT_DATE, 'Новый', 'ORD-102/2024', 1500.00);
-- UPDATE "Order" SET Status = 'Доставлен' WHERE OrderNumber = 'ORD-001/2024';
-- SELECT * FROM audit_order;
