"""Модульные тесты для моделей — дополнительные граничные случаи"""

from decimal import Decimal
from datetime import datetime, date, timedelta
import pytest
from src.models import (
    Product, Category, Supplier, Client, Employee, Batch,
    Order, OrderItem, Inventory
)


class TestProductEdgeCases:
    def test_from_dict_missing_fields(self):
        data = {"id": 1, "name": "Тест"}
        p = Product.from_dict(data)
        assert p.description is None
        assert p.category_id is None
        assert p.color is None
        assert p.stem_length_cm is None
        assert p.purchase_price == Decimal("0.00")

    def test_from_dict_zero_prices(self):
        data = {"id": 1, "name": "Тест", "purchasePrice": "0", "retailPrice": "0"}
        p = Product.from_dict(data)
        assert p.purchase_price == Decimal("0")
        assert p.retail_price == Decimal("0")

    def test_from_dict_large_numbers(self):
        data = {"id": 1, "name": "Тест", "purchasePrice": "999999.99", "retailPrice": "1999999.99"}
        p = Product.from_dict(data)
        assert p.purchase_price == Decimal("999999.99")
        assert p.retail_price == Decimal("1999999.99")

    def test_name_whitespace(self):
        p = Product(id=1, name="  Роза  ")
        data = p.to_dict()
        assert data["name"] == "  Роза  "

    def test_is_active_false(self):
        data = {"id": 1, "name": "Тест", "isActive": False}
        p = Product.from_dict(data)
        assert p.is_active is False

    def test_shelf_life_zero(self):
        data = {"id": 1, "name": "Тест", "shelfLifeDays": 0}
        p = Product.from_dict(data)
        assert p.shelf_life_days == 0

    def test_negative_prices(self):
        data = {"id": 1, "name": "Тест", "purchasePrice": "-50", "retailPrice": "-100"}
        p = Product.from_dict(data)
        assert p.purchase_price == Decimal("-50")
        assert p.retail_price == Decimal("-100")


class TestOrderEdgeCases:
    def test_from_dict_missing_date(self):
        data = {"id": 1, "orderNumber": "ORD-001", "status": "Новый", "totalAmount": "0.00"}
        o = Order.from_dict(data)
        assert o.order_date == date.today()

    def test_from_dict_with_items(self):
        data = {
            "id": 1, "orderNumber": "ORD-001", "orderDate": "2024-01-15T10:00:00",
            "status": "Новый", "totalAmount": "300.00",
            "orderItems": [
                {"id": 1, "orderId": 1, "productId": 1, "quantity": 2, "unitPrice": "150.00"}
            ]
        }
        o = Order.from_dict(data)
        assert o.items_count == 1
        assert o.order_items[0].quantity == 2

    def test_from_dict_employee_as_string(self):
        data = {
            "id": 1, "orderNumber": "ORD-001", "orderDate": "2024-01-15T10:00:00",
            "status": "Новый", "totalAmount": "100.00",
            "employee": "Анна"
        }
        o = Order.from_dict(data)
        assert o.employee is not None

    def test_zero_total(self):
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0.00"))
        d = o.to_dict()
        assert d["totalAmount"] == 0.0

    def test_status_color_all_statuses(self):
        for status, expected in [
            ("Новый", "#2196F3"),
            ("В обработке", "#FF9800"),
            ("Готов к выдаче", "#4CAF50"),
            ("Выполнен", "#9C27B0"),
            ("Отменен", "#F44336"),
        ]:
            o = Order(id=1, order_number="", order_date=date.today(),
                      status=status, total_amount=Decimal("0"))
            assert o.status_color == expected

    def test_add_item_from_empty(self):
        o = Order(id=1, order_number="", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"))
        assert o.order_items is None
        oi = OrderItem(id=1, order_id=1, quantity=2, unit_price=Decimal("50"))
        o.add_item(oi)
        assert o.items_count == 1
        assert o.total_amount == Decimal("100")

    def test_remove_item_not_found(self):
        oi = OrderItem(id=1, order_id=1, product_id=1, quantity=1, unit_price=Decimal("10"))
        o = Order(id=1, order_number="", order_date=date.today(),
                  status="Новый", total_amount=Decimal("10"), order_items=[oi])
        o.remove_item(999)
        assert o.items_count == 1  # unchanged

    def test_recalculate_after_remove(self):
        oi1 = OrderItem(id=1, order_id=1, product_id=1, quantity=2, unit_price=Decimal("100"))
        oi2 = OrderItem(id=2, order_id=1, product_id=2, quantity=3, unit_price=Decimal("50"))
        o = Order(id=1, order_number="", order_date=date.today(),
                  status="Новый", total_amount=Decimal("350"), order_items=[oi1, oi2])
        o.remove_item(1)
        assert o.total_amount == Decimal("150")


class TestEmployeeEdgeCases:
    def test_from_dict_missing_position(self):
        e = Employee.from_dict({"id": 1, "fullName": "Иван"})
        assert e.position is None

    def test_from_dict_missing_phone(self):
        e = Employee.from_dict({"id": 1, "fullName": "Иван"})
        assert e.phone_number is None

    def test_access_level_display_courier(self):
        e = Employee(id=1, full_name="Курьер", access_level="courier")
        assert e.access_level_display == "Курьер"

    def test_can_manage_products_florist(self):
        assert Employee(id=1, full_name="", access_level="florist").can_manage_products is True

    def test_can_manage_orders_seller(self):
        assert Employee(id=1, full_name="", access_level="seller").can_manage_orders is True

    def test_can_manage_orders_admin(self):
        assert Employee(id=1, full_name="", access_level="admin").can_manage_orders is True


class TestInventoryEdgeCases:
    def test_from_dict_no_date(self):
        inv = Inventory.from_dict({"id": 1, "quantity": 10})
        assert inv.receipt_date == date.today()

    def test_from_dict_with_product(self):
        data = {
            "id": 1, "quantity": 10, "receiptDate": "2024-01-10T10:00:00",
            "product": {"id": 1, "name": "Роза", "retailPrice": "150.00"}
        }
        inv = Inventory.from_dict(data)
        assert inv.product is not None
        assert inv.product_name == "Роза"

    def test_zero_quantity(self):
        inv = Inventory(id=1, quantity=0, receipt_date=date.today())
        assert inv.is_low_stock is True
        assert inv.stock_status == "Отсутствует"

    def test_negative_quantity(self):
        inv = Inventory(id=1, quantity=-5, receipt_date=date.today())
        assert inv.is_low_stock is True

    def test_stock_status_critical(self):
        inv = Inventory(id=1, quantity=3, receipt_date=date.today())
        assert inv.stock_status == "Критически низкий"

    def test_stock_status_high(self):
        inv = Inventory(id=1, quantity=100, receipt_date=date.today())
        assert inv.stock_status == "Высокий"

    def test_days_in_stock_negative(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today() + timedelta(days=1))
        assert inv.days_in_stock == -1

    def test_is_expiring_soon_default_threshold(self):
        p = Product(id=1, name="Роза", shelf_life_days=7)
        inv = Inventory(id=1, quantity=10,
                        receipt_date=date.today() - timedelta(days=3), product=p)
        assert inv.is_expiring_soon is True

    def test_is_expiring_soon_not_close(self):
        p = Product(id=1, name="Роза", shelf_life_days=30)
        inv = Inventory(id=1, quantity=10,
                        receipt_date=date.today() - timedelta(days=1), product=p)
        assert inv.is_expiring_soon is False

    def test_is_expiring_soon_no_product(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today())
        assert inv.is_expiring_soon is False

    def test_is_expired_no_product(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today())
        assert inv.is_expired is False

    def test_past_date_receipt(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date(2020, 1, 1))
        assert inv.days_in_stock > 1000


class TestSupplierEdgeCases:
    def test_from_dict_missing_all_optional(self):
        s = Supplier.from_dict({"id": 1, "name": "Тест"})
        assert s.phone_number is None
        assert s.email is None
        assert s.details is None
        assert s.address is None

    def test_contact_info_very_long(self):
        s = Supplier(id=1, name="Тест", phone_number="+7-000-000-00-00", email="very-long-email-address-that-should-still-work@example.com")
        assert "Телефон:" in s.contact_info
        assert "Email:" in s.contact_info


class TestClientEdgeCases:
    def test_from_dict_missing_contacts(self):
        c = Client.from_dict({"id": 1, "fullName": "Иван"})
        assert c.phone_number is None
        assert c.email is None

    def test_contact_info_empty_strings(self):
        c = Client(id=1, full_name="Иван", phone_number="", email="")
        assert c.contact_info == "Нет контактных данных"

    def test_from_dict_with_datetime(self):
        c = Client.from_dict({"id": 1, "fullName": "Иван", "createdAt": "2024-06-15T10:30:00Z"})
        assert c.created_at is not None
        assert c.created_at.month == 6


class TestBatchEdgeCases:
    def test_from_dict_with_supplier(self):
        data = {
            "id": 1, "quantity": 100, "costPrice": "5000.00",
            "supplier": {"id": 1, "name": "ООО Поставщик"}
        }
        b = Batch.from_dict(data)
        assert b.supplier_name == "ООО Поставщик"

    def test_unit_cost_precision(self):
        b = Batch(id=1, quantity=3, cost_price=Decimal("10.00"))
        assert b.unit_cost == Decimal("3.333333333333333333333333333")  # 10/3

    def test_delivery_status_yesterday(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"),
                  delivery_date=date.today() - timedelta(days=1))
        assert b.delivery_status == "Вчера"

    def test_delivery_status_recent(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"),
                  delivery_date=date.today() - timedelta(days=3))
        assert "дней" in b.delivery_status

    def test_delivery_status_old(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"),
                  delivery_date=date.today() - timedelta(days=30))
        assert "дней" in b.delivery_status

    def test_delivery_status_no_date(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"))
        assert b.delivery_status == "Ожидается"


class TestOrderItemEdgeCases:
    def test_from_dict_missing_quantity(self):
        oi = OrderItem.from_dict({"id": 1, "orderId": 1})
        assert oi.quantity == 1
        assert oi.unit_price == Decimal("0.00")

    def test_zero_quantity(self):
        oi = OrderItem(id=1, order_id=1, quantity=0, unit_price=Decimal("100"))
        assert oi.total_price == Decimal("0")

    def test_negative_quantity(self):
        oi = OrderItem(id=1, order_id=1, quantity=-2, unit_price=Decimal("50"))
        assert oi.total_price == Decimal("-100")

    def test_large_quantity(self):
        oi = OrderItem(id=1, order_id=1, quantity=999999, unit_price=Decimal("0.01"))
        assert oi.total_price == Decimal("9999.99")


class TestCategoryEdgeCases:
    def test_empty_name(self):
        c = Category(id=1, name="")
        assert c.name == ""

    def test_very_long_name(self):
        name = "А" * 255
        c = Category(id=1, name=name)
        assert len(c.name) == 255
