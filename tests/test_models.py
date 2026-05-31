"""Модульные тесты для моделей данных"""

from decimal import Decimal
from datetime import datetime, date, timedelta
import pytest
from src.models import (
    Product, Category, Supplier, Client, Employee, Batch,
    Order, OrderItem, Inventory
)


class TestCategory:
    def test_from_dict_full(self):
        data = {"id": 1, "name": "Розы", "description": "Срезанные розы"}
        c = Category.from_dict(data)
        assert c.id == 1
        assert c.name == "Розы"
        assert c.description == "Срезанные розы"

    def test_from_dict_minimal(self):
        c = Category.from_dict({"id": 2, "name": "Тюльпаны"})
        assert c.id == 2
        assert c.name == "Тюльпаны"
        assert c.description is None

    def test_to_dict(self):
        c = Category(id=1, name="Розы", description="Описание")
        d = c.to_dict()
        assert d == {"id": 1, "name": "Розы", "description": "Описание"}

    def test_to_dict_with_datetime(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        c = Category(id=1, name="Розы", created_at=dt)
        d = c.to_dict()
        assert d["createdAt"] == "2024-01-01T12:00:00"

    def test_str(self):
        c = Category(id=1, name="Розы")
        assert str(c) == "Category(id=1, name='Розы')"


class TestProduct:
    @pytest.fixture
    def sample_data(self):
        return {
            "id": 1,
            "name": "Роза красная",
            "description": "Красная роза 50см",
            "categoryId": 1,
            "category": {"id": 1, "name": "Розы"},
            "unit": "шт",
            "purchasePrice": "50.00",
            "retailPrice": "150.00",
            "shelfLifeDays": 7,
            "color": "Красный",
            "stemLengthCm": 50,
            "isActive": True
        }

    def test_from_dict(self, sample_data):
        p = Product.from_dict(sample_data)
        assert p.id == 1
        assert p.name == "Роза красная"
        assert p.retail_price == Decimal("150.00")
        assert p.is_active is True
        assert p.category is not None
        assert p.category.name == "Розы"

    def test_from_dict_minimal(self):
        p = Product.from_dict({"id": 1, "name": "Роза"})
        assert p.id == 1
        assert p.name == "Роза"
        assert p.unit == "шт"
        assert p.shelf_life_days == 7

    def test_to_dict(self, sample_data):
        p = Product.from_dict(sample_data)
        d = p.to_dict()
        assert d["name"] == "Роза красная"
        assert d["retailPrice"] == 150.0

    def test_category_name_with_category(self, sample_data):
        p = Product.from_dict(sample_data)
        assert p.category_name == "Розы"

    def test_category_name_without_category(self):
        p = Product(id=1, name="Роза")
        assert p.category_name == "Без категории"

    def test_margin_percentage(self):
        p = Product(id=1, name="Тест", purchase_price=Decimal("100"), retail_price=Decimal("150"))
        assert p.margin_percentage == 50.0

    def test_margin_percentage_zero_purchase(self):
        p = Product(id=1, name="Тест", purchase_price=Decimal("0"), retail_price=Decimal("100"))
        assert p.margin_percentage == 0.0

    def test_margin_amount(self):
        p = Product(id=1, name="Тест", purchase_price=Decimal("100"), retail_price=Decimal("150"))
        assert p.margin_amount == Decimal("50")

    def test_str(self):
        p = Product(id=1, name="Роза", retail_price=Decimal("150"))
        assert "Роза" in str(p)

    def test_from_dict_with_datetime(self):
        data = {"id": 1, "name": "Тест", "createdAt": "2024-01-01T12:00:00Z", "updatedAt": "2024-01-02T12:00:00Z"}
        p = Product.from_dict(data)
        assert p.created_at is not None
        assert p.created_at.year == 2024


class TestSupplier:
    def test_from_dict(self):
        data = {"id": 1, "name": "ООО Цветы", "phoneNumber": "+7-123", "email": "info@flowers.ru"}
        s = Supplier.from_dict(data)
        assert s.name == "ООО Цветы"
        assert s.phone_number == "+7-123"

    def test_to_dict(self):
        s = Supplier(id=1, name="ООО Цветы")
        d = s.to_dict()
        assert d["name"] == "ООО Цветы"

    def test_display_name(self):
        s = Supplier(id=1, name="  ООО Цветы  ")
        assert s.display_name == "ООО Цветы"

    def test_contact_info_full(self):
        s = Supplier(id=1, name="Тест", phone_number="+7-123", email="a@b.ru")
        assert "Телефон:" in s.contact_info and "Email:" in s.contact_info

    def test_contact_info_empty(self):
        s = Supplier(id=1, name="Тест")
        assert s.contact_info == "Нет контактных данных"

    def test_contact_info_phone_only(self):
        s = Supplier(id=1, name="Тест", phone_number="+7-123")
        assert "Телефон:" in s.contact_info
        assert "Email:" not in s.contact_info

    def test_contact_info_email_only(self):
        s = Supplier(id=1, name="Тест", email="a@b.ru")
        assert "Телефон:" not in s.contact_info
        assert "Email:" in s.contact_info

    def test_full_address_default(self):
        s = Supplier(id=1, name="Тест")
        assert s.full_address == "Адрес не указан"

    def test_full_address_custom(self):
        s = Supplier(id=1, name="Тест", address="ул. Цветочная, 1")
        assert s.full_address == "ул. Цветочная, 1"


class TestClient:
    def test_from_dict(self):
        data = {"id": 1, "fullName": "Иван Иванов", "phoneNumber": "+7-999", "email": "ivan@mail.ru"}
        c = Client.from_dict(data)
        assert c.full_name == "Иван Иванов"
        assert c.phone_number == "+7-999"

    def test_to_dict(self):
        c = Client(id=1, full_name="Иван", phone_number="+7-999")
        d = c.to_dict()
        assert d["fullName"] == "Иван"
        assert d["phoneNumber"] == "+7-999"

    def test_display_name(self):
        c = Client(id=1, full_name="  Иван  ")
        assert c.display_name == "Иван"

    def test_contact_info_full(self):
        c = Client(id=1, full_name="Иван", phone_number="+7-999", email="i@m.ru")
        assert "Телефон:" in c.contact_info and "Email:" in c.contact_info

    def test_contact_info_empty(self):
        c = Client(id=1, full_name="Иван")
        assert c.contact_info == "Нет контактных данных"


class TestEmployee:
    def test_from_dict(self):
        data = {"id": 1, "fullName": "Админ", "position": "Директор",
                "accessLevel": "admin", "email": "admin@flora.ru",
                "phoneNumber": "+7-111", "login": "admin"}
        e = Employee.from_dict(data)
        assert e.full_name == "Админ"
        assert e.access_level == "admin"
        assert e.position == "Директор"
        assert e.login == "admin"

    def test_from_dict_default_level(self):
        e = Employee.from_dict({"id": 1, "fullName": "Продавец"})
        assert e.access_level == "seller"

    def test_to_dict(self):
        e = Employee(id=1, full_name="Админ", position="Директор", access_level="admin")
        d = e.to_dict()
        assert d["fullName"] == "Админ"
        assert d["accessLevel"] == "admin"

    def test_display_name(self):
        e = Employee(id=1, full_name="  Сотрудник  ")
        assert e.display_name == "Сотрудник"

    def test_access_level_display_admin(self):
        e = Employee(id=1, full_name="A", access_level="admin")
        assert e.access_level_display == "Администратор"

    def test_access_level_display_warehouse(self):
        e = Employee(id=1, full_name="B", access_level="warehouse")
        assert e.access_level_display == "Кладовщик"

    def test_access_level_display_unknown(self):
        e = Employee(id=1, full_name="C", access_level="unknown")
        assert e.access_level_display == "unknown"

    def test_is_admin(self):
        assert Employee(id=1, full_name="A", access_level="admin").is_admin is True
        assert Employee(id=1, full_name="B", access_level="seller").is_admin is False

    def test_is_manager(self):
        assert Employee(id=1, full_name="A", access_level="admin").is_manager is True
        assert Employee(id=1, full_name="B", access_level="manager").is_manager is True
        assert Employee(id=1, full_name="C", access_level="seller").is_manager is False

    def test_can_manage_products(self):
        assert Employee(id=1, full_name="A", access_level="florist").can_manage_products is True
        assert Employee(id=1, full_name="B", access_level="warehouse").can_manage_products is False

    def test_can_manage_inventory(self):
        assert Employee(id=1, full_name="A", access_level="warehouse").can_manage_inventory is True
        assert Employee(id=1, full_name="B", access_level="seller").can_manage_inventory is False

    def test_can_manage_orders(self):
        assert Employee(id=1, full_name="A", access_level="seller").can_manage_orders is True
        assert Employee(id=1, full_name="B", access_level="warehouse").can_manage_orders is False


class TestBatch:
    def test_from_dict(self):
        data = {"id": 1, "supplierId": 1, "invoiceNumber": "INV-001",
                "deliveryDate": "2024-01-15T10:00:00Z", "quantity": 100, "costPrice": "5000.00"}
        b = Batch.from_dict(data)
        assert b.id == 1
        assert b.invoice_number == "INV-001"
        assert b.quantity == 100
        assert b.cost_price == Decimal("5000.00")

    def test_to_dict(self):
        b = Batch(id=1, supplier_id=1, invoice_number="INV-001",
                  delivery_date=date(2024, 1, 15), quantity=100, cost_price=Decimal("5000.00"))
        d = b.to_dict()
        assert d["invoiceNumber"] == "INV-001"
        assert d["quantity"] == 100

    def test_from_dict_minimal(self):
        b = Batch.from_dict({"id": 1, "quantity": 50, "costPrice": "1000.00"})
        assert b.quantity == 50
        assert b.cost_price == Decimal("1000.00")
        assert b.delivery_date is None

    def test_supplier_name_no_supplier(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"))
        assert b.supplier_name == "Не указан"

    def test_supplier_name_with_supplier(self):
        s = Supplier(id=1, name="ООО Поставщик")
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"), supplier=s)
        assert b.supplier_name == "ООО Поставщик"

    def test_unit_cost(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("500"))
        assert b.unit_cost == Decimal("50.00")

    def test_unit_cost_zero_quantity(self):
        b = Batch(id=1, quantity=0, cost_price=Decimal("500"))
        assert b.unit_cost == Decimal("0.00")

    def test_days_since_delivery_none(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"))
        assert b.days_since_delivery is None

    def test_days_since_delivery_calculated(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"),
                  delivery_date=date.today() - timedelta(days=5))
        assert b.days_since_delivery == 5

    def test_delivery_status_future(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"),
                  delivery_date=date.today() + timedelta(days=1))
        assert b.delivery_status == "Запланирована"

    def test_delivery_status_today(self):
        b = Batch(id=1, quantity=10, cost_price=Decimal("100"),
                  delivery_date=date.today())
        assert b.delivery_status == "Сегодня"


class TestOrderItem:
    def test_from_dict(self):
        data = {"id": 1, "orderId": 1, "productId": 1, "quantity": 5, "unitPrice": "150.00"}
        oi = OrderItem.from_dict(data)
        assert oi.id == 1
        assert oi.quantity == 5
        assert oi.unit_price == Decimal("150.00")

    def test_to_dict(self):
        oi = OrderItem(id=1, order_id=1, product_id=1, quantity=3, unit_price=Decimal("100"))
        d = oi.to_dict()
        assert d["quantity"] == 3
        assert d["unitPrice"] == 100.0

    def test_product_name_with_product(self):
        p = Product(id=1, name="Роза")
        oi = OrderItem(id=1, order_id=1, product=p)
        assert oi.product_name == "Роза"

    def test_product_name_without_product(self):
        oi = OrderItem(id=1, order_id=1, product_id=5)
        assert oi.product_name == "Товар #5"

    def test_total_price(self):
        oi = OrderItem(id=1, order_id=1, quantity=3, unit_price=Decimal("150.50"))
        assert oi.total_price == Decimal("451.50")

    def test_unit_name_with_product(self):
        p = Product(id=1, name="Роза", unit="букет")
        oi = OrderItem(id=1, order_id=1, product=p)
        assert oi.unit_name == "букет"

    def test_unit_name_without_product(self):
        oi = OrderItem(id=1, order_id=1)
        assert oi.unit_name == "шт"


class TestOrder:
    def test_from_dict(self):
        data = {"id": 1, "orderNumber": "ORD-001", "orderDate": "2024-01-15T10:00:00",
                "status": "Новый", "totalAmount": "1500.00", "clientId": 1, "employeeId": 1}
        o = Order.from_dict(data)
        assert o.id == 1
        assert o.order_number == "ORD-001"
        assert o.total_amount == Decimal("1500.00")
        assert o.order_date == date(2024, 1, 15)

    def test_to_dict(self):
        o = Order(id=1, order_number="ORD-001", order_date=date(2024, 1, 15),
                  status="Новый", total_amount=Decimal("1500"),
                  client_id=1, employee_id=1)
        d = o.to_dict()
        assert d["orderNumber"] == "ORD-001"
        assert d["totalAmount"] == 1500.0

    def test_from_dict_with_client_obj(self):
        data = {"id": 1, "orderNumber": "ORD-001", "orderDate": "2024-01-15T10:00:00",
                "status": "Новый", "totalAmount": "500.00",
                "client": {"id": 1, "fullName": "Иван", "phoneNumber": "+7-999"}}
        o = Order.from_dict(data)
        assert o.client is not None
        assert o.client_name == "Иван"

    def test_from_dict_with_client_name_string(self):
        data = {"id": 1, "orderNumber": "ORD-001", "orderDate": "2024-01-15T10:00:00",
                "status": "Новый", "totalAmount": "500.00", "clientName": "Пётр"}
        o = Order.from_dict(data)
        assert o.client_name == "Пётр"

    def test_client_name_fallback(self):
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"))
        assert o.client_name == "Не указан"

    def test_employee_name_fallback(self):
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"))
        assert o.employee_name == "Не указан"

    def test_employee_name_with_employee(self):
        e = Employee(id=1, full_name="Анна")
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"), employee=e)
        assert o.employee_name == "Анна"

    def test_items_count_none(self):
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"))
        assert o.items_count == 0

    def test_items_count_with_items(self):
        items = [OrderItem(id=1, order_id=1), OrderItem(id=2, order_id=1)]
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"), order_items=items)
        assert o.items_count == 2

    def test_status_color_new(self):
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"))
        assert o.status_color == "#2196F3"

    def test_status_color_unknown(self):
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Неизвестный", total_amount=Decimal("0"))
        assert o.status_color == "#757575"

    def test_can_edit(self):
        assert Order(id=1, order_number="", order_date=date.today(),
                     status="Новый", total_amount=Decimal("0")).can_edit is True
        assert Order(id=1, order_number="", order_date=date.today(),
                     status="Выполнен", total_amount=Decimal("0")).can_edit is False

    def test_can_cancel(self):
        assert Order(id=1, order_number="", order_date=date.today(),
                     status="Новый", total_amount=Decimal("0")).can_cancel is True
        assert Order(id=1, order_number="", order_date=date.today(),
                     status="Доставлен", total_amount=Decimal("0")).can_cancel is False

    def test_add_item(self):
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("0"))
        oi = OrderItem(id=1, order_id=1, quantity=2, unit_price=Decimal("100"))
        o.add_item(oi)
        assert o.items_count == 1
        assert o.total_amount == Decimal("200")

    def test_remove_item(self):
        oi1 = OrderItem(id=1, order_id=1, product_id=1, quantity=2, unit_price=Decimal("100"))
        oi2 = OrderItem(id=2, order_id=1, product_id=2, quantity=1, unit_price=Decimal("50"))
        o = Order(id=1, order_number="ORD-001", order_date=date.today(),
                  status="Новый", total_amount=Decimal("250"), order_items=[oi1, oi2])
        o.remove_item(1)
        assert o.items_count == 1


class TestInventory:
    def test_from_dict(self):
        data = {"id": 1, "productId": 1, "quantity": 100, "receiptDate": "2024-01-10T10:00:00",
                "storageLocation": "A-01", "storageTemperature": "+4°C", "humidityLevel": "70%"}
        inv = Inventory.from_dict(data)
        assert inv.id == 1
        assert inv.quantity == 100
        assert inv.storage_location == "A-01"

    def test_to_dict(self):
        inv = Inventory(id=1, quantity=50, receipt_date=date(2024, 1, 10))
        d = inv.to_dict()
        assert d["quantity"] == 50
        assert d["receiptDate"] == "2024-01-10"

    def test_product_name_with_product(self):
        p = Product(id=1, name="Роза")
        inv = Inventory(id=1, quantity=10, receipt_date=date.today(), product=p)
        assert inv.product_name == "Роза"

    def test_product_name_without_product(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today(), product_id=5)
        assert inv.product_name == "Товар #5"

    def test_category_name_with_nested_category(self):
        cat = Category(id=1, name="Розы")
        p = Product(id=1, name="Роза", category=cat)
        inv = Inventory(id=1, quantity=10, receipt_date=date.today(), product=p)
        assert inv.category_name == "Розы"

    def test_category_name_without_category(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today())
        assert inv.category_name == "Без категории"

    def test_total_value(self):
        p = Product(id=1, name="Роза", retail_price=Decimal("150"))
        inv = Inventory(id=1, quantity=10, receipt_date=date.today(), product=p)
        assert inv.total_value == Decimal("1500")

    def test_total_value_no_product(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today())
        assert inv.total_value == Decimal("0")

    def test_days_in_stock(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today() - timedelta(days=3))
        assert inv.days_in_stock == 3

    def test_is_expired(self):
        p = Product(id=1, name="Роза", shelf_life_days=7)
        inv = Inventory(id=1, quantity=10, receipt_date=date.today() - timedelta(days=10), product=p)
        assert inv.is_expired is True

    def test_is_expired_not_expired(self):
        p = Product(id=1, name="Роза", shelf_life_days=14)
        inv = Inventory(id=1, quantity=10, receipt_date=date.today() - timedelta(days=5), product=p)
        assert inv.is_expired is False

    def test_expiry_date(self):
        p = Product(id=1, name="Роза", shelf_life_days=7)
        inv = Inventory(id=1, quantity=10, receipt_date=date(2024, 1, 1), product=p)
        assert inv.expiry_date == date(2024, 1, 8)

    def test_expiry_date_no_product(self):
        inv = Inventory(id=1, quantity=10, receipt_date=date.today())
        assert inv.expiry_date is None

    def test_days_until_expiry(self):
        p = Product(id=1, name="Роза", shelf_life_days=10)
        inv = Inventory(id=1, quantity=10, receipt_date=date.today(), product=p)
        assert inv.days_until_expiry == 10

    def test_is_low_stock(self):
        assert Inventory(id=1, quantity=5, receipt_date=date.today()).is_low_stock is True
        assert Inventory(id=1, quantity=15, receipt_date=date.today()).is_low_stock is False

    def test_stock_status_values(self):
        assert Inventory(id=1, quantity=0, receipt_date=date.today()).stock_status == "Отсутствует"
        assert Inventory(id=1, quantity=3, receipt_date=date.today()).stock_status == "Критически низкий"
        assert Inventory(id=1, quantity=7, receipt_date=date.today()).stock_status == "Низкий"
        assert Inventory(id=1, quantity=30, receipt_date=date.today()).stock_status == "Нормальный"
        assert Inventory(id=1, quantity=100, receipt_date=date.today()).stock_status == "Высокий"
