"""Тесты ограничений целостности (п.1-3 требований курсовой)."""

import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "frontend"))

from src.utils.validation import (
    ACCESS_LEVELS,
    ORDER_STATUSES,
    ValidationError,
    check_unique,
    require_access_level,
    require_delivery_date,
    require_email,
    require_invoice_number,
    require_non_empty_password,
    require_non_negative_int,
    require_order_date,
    require_order_number,
    require_order_status,
    require_phone,
    require_positive_int,
    require_positive_price,
    require_unique,
    validate_batch_dict,
    validate_client_dict,
    validate_employee_dict,
    validate_order_dict,
    validate_product_dict,
)
from src.models import Batch, Category, Client, Employee, Inventory, Order, OrderItem, Product


# --- 1. Цены положительные ---
@pytest.mark.parametrize("bad", [0, "0", "-1", "-100.50", 0.0])
def test_prices_must_be_positive(bad):
    with pytest.raises(ValidationError):
        require_positive_price(bad, "Розничная цена")


def test_prices_ok():
    assert require_positive_price("300.00", "Розничная цена") == Decimal("300.00")
    assert require_positive_price(150, "Закупочная цена") == 150


# --- Количества неотрицательные целые ---
@pytest.mark.parametrize("bad", [-1, "-5", 1.5, "abc", "3.5", True])
def test_quantity_non_negative_int(bad):
    with pytest.raises(ValidationError):
        require_non_negative_int(bad, "Количество")


def test_quantity_zero_ok():
    assert require_non_negative_int(0, "Количество") == 0
    assert require_non_negative_int("10", "Количество") == 10


# --- Срок хранения положительный ---
@pytest.mark.parametrize("bad", [0, -3, "-1"])
def test_shelf_life_positive(bad):
    with pytest.raises(ValidationError):
        require_positive_int(bad, "Срок хранения")


# --- Даты ---
def test_delivery_date_future_rejected():
    with pytest.raises(ValidationError):
        require_delivery_date(date.today() + timedelta(days=1))


def test_delivery_date_today_and_past_ok():
    require_delivery_date(date.today())
    require_delivery_date("2024-01-15")
    require_delivery_date("15.01.2024")


def test_bad_date_format_rejected():
    with pytest.raises(ValidationError):
        require_order_date("не дата")


def test_order_date_future_rejected():
    with pytest.raises(ValidationError):
        require_order_date(date.today() + timedelta(days=30))


# --- Статусы и уровни доступа ---
def test_order_statuses():
    for s in ("Новый", "В обработке", "Выполнен", "Доставлен"):
        assert require_order_status(s) == s
    assert set(ORDER_STATUSES) == {"Новый", "В обработке", "Выполнен", "Доставлен"}
    with pytest.raises(ValidationError):
        require_order_status("Отменен")
    with pytest.raises(ValidationError):
        require_order_status("New")


def test_access_levels():
    for lvl in ("admin", "florist", "seller", "purchasing", "courier", "warehouse"):
        assert require_access_level(lvl) == lvl
    assert set(ACCESS_LEVELS) == {"admin", "florist", "seller", "purchasing", "courier", "warehouse"}
    with pytest.raises(ValidationError):
        require_access_level("manager")
    with pytest.raises(ValidationError):
        require_access_level("")


# --- 2. Форматы ---
@pytest.mark.parametrize("good", ["ORD-001/2024", "ORD-1234/2025"])
@pytest.mark.parametrize("bad", ["001/2024", "ORD-01/2024", "ORD-001-2024", "ord-001/2024", ""])
def test_order_number_format(good, bad):
    assert require_order_number(good) == good
    with pytest.raises(ValidationError):
        require_order_number(bad)


@pytest.mark.parametrize("good", ["РОЗ-001/2024", "ТЮЛ-002/2024", "ЭКВ-003/2024"])
@pytest.mark.parametrize("bad", ["001/2024", "РОЗ001/2024", "РОЗ-01/24", ""])
def test_invoice_number_format(good, bad):
    require_invoice_number(good)
    with pytest.raises(ValidationError):
        require_invoice_number(bad)


@pytest.mark.parametrize("good", ["+79161234567", "+79999999999"])
@pytest.mark.parametrize("bad", ["89161234567", "+7916123456", "+791612345678", "+7-916", "abc", ""])
def test_phone_format(good, bad):
    assert require_phone(good) == good
    with pytest.raises(ValidationError):
        require_phone(bad)


@pytest.mark.parametrize("good", ["a@b.ru", "ivanova@flowerstore.ru"])
@pytest.mark.parametrize("bad", ["abc", "a@b", "@b.ru", "a b@c.ru", ""])
def test_email_format(good, bad):
    assert require_email(good) == good
    with pytest.raises(ValidationError):
        require_email(bad)


def test_password_not_empty():
    with pytest.raises(ValidationError):
        require_non_empty_password("")
    with pytest.raises(ValidationError):
        require_non_empty_password("   ")
    assert require_non_empty_password("secret") == "secret"


@pytest.mark.parametrize("good", ["Красный", "Белый", "Светло-розовый", "White", ""])
@pytest.mark.parametrize("bad", ["123", "5", "красный1", "red2", "к4расный", "Синий!"])
def test_color_no_digits(good, bad):
    from src.utils.validation import require_color
    assert require_color(good) == good.strip()
    with pytest.raises(ValidationError):
        require_color(bad)


def test_color_in_product_model():
    p_bad = Product(id=1, name="Роза", purchase_price=Decimal("150"),
                    retail_price=Decimal("300"), shelf_life_days=10, color="123")
    assert any("цифр" in e for e in p_bad.validate())
    p_good = Product(id=1, name="Роза", purchase_price=Decimal("150"),
                     retail_price=Decimal("300"), shelf_life_days=10, color="Красный")
    assert p_good.validate() == []


def test_supplier_validation():
    from src.models import Supplier
    from src.utils.validation import validate_supplier_dict
    assert validate_supplier_dict({"phone_number": "+74951234567",
                                   "email": "info@dutchroses.ru"}) == []
    assert len(validate_supplier_dict({"phone_number": "123",
                                       "email": "bad"})) == 2
    assert Supplier(id=1, name="ООО", phone_number="+74951234567",
                    email="info@dutchroses.ru").validate() == []
    assert Supplier(id=1, name="ООО", phone_number="123").validate() != []


@pytest.mark.parametrize("bad", ["123", "ab", "a b", " a"])
def test_password_policy(bad):
    from src.utils.validation import require_password
    with pytest.raises(ValidationError):
        require_password(bad)


def test_password_ok():
    from src.utils.validation import require_password
    assert require_password("admin") == "admin"
    assert require_password("ivanova123") == "ivanova123"


@pytest.mark.parametrize("good", ["Иванова Анна Петровна", "Соколова Мария Ивановна", "Анна-Мария"])
@pytest.mark.parametrize("bad", ["Иван123", "Петр5", "123", "Иван!"])
def test_person_name_no_digits(good, bad):
    from src.utils.validation import require_person_name
    assert require_person_name(good) == good.strip()
    with pytest.raises(ValidationError):
        require_person_name(bad)


def test_name_required_and_max_length():
    from src.utils.validation import require_name
    with pytest.raises(ValidationError):
        require_name("   ", "Название товара")
    with pytest.raises(ValidationError):
        require_name("x" * 256, "Название товара")
    assert require_name("Роза Гран При", "Название товара") == "Роза Гран При"


def test_model_name_checks():
    from src.models import Category, Client, Employee
    assert Client(id=1, full_name="Иван123").validate() != []
    assert Employee(id=1, full_name="Петр5", access_level="seller").validate() != []
    assert Category(id=1, name="   ").validate() != []
    assert Product(id=1, name="", purchase_price=Decimal("150"),
                   retail_price=Decimal("300"), shelf_life_days=10).validate() != []


@pytest.mark.parametrize("good", ["шт", "кг", "букет", "упаковка"])
@pytest.mark.parametrize("bad", ["1", "шт2", "2кг", ""])
def test_unit_no_digits(good, bad):
    from src.utils.validation import require_unit
    assert require_unit(good) == good
    with pytest.raises(ValidationError):
        require_unit(bad)


def test_unit_in_product_model():
    p_bad = Product(id=1, name="Роза", purchase_price=Decimal("150"),
                    retail_price=Decimal("300"), shelf_life_days=10, unit="1")
    assert any("цифр" in e for e in p_bad.validate())
    p_good = Product(id=1, name="Роза", purchase_price=Decimal("150"),
                     retail_price=Decimal("300"), shelf_life_days=10, unit="шт")
    assert p_good.validate() == []


@pytest.mark.parametrize("msg", [
    "Ошибка запроса: 409 Client Error: Conflict for url: http://localhost:5000/api/products",
    "Товар с таким названием уже существует",
    'duplicate key value violates unique constraint "uq_category_name"',
    "23505: unique violation",
])
def test_duplicate_error_recognized(msg):
    from src.utils.validation import format_duplicate_error
    text = format_duplicate_error(Exception(msg), "название", "Роза")
    assert text is not None
    assert "уже существует" in text
    assert "Роза" in text


@pytest.mark.parametrize("msg", [
    "Не удалось подключиться к серверу",
    "Товар не найден",
    "Название товара обязательно",
])
def test_duplicate_error_ignores_other_errors(msg):
    from src.utils.validation import format_duplicate_error
    assert format_duplicate_error(Exception(msg), "название", "Роза") is None


def test_widget_duplicate_helpers_delegate():
    from src.ui.widgets.products_widget import _check_duplicate as p_dup
    from src.ui.widgets.batches_widget import _check_duplicate as b_dup
    from src.ui.widgets.orders_widget import _check_duplicate as o_dup
    err = Exception("409 Client Error: Conflict for url: http://localhost:5000/api/products")
    for dup in (p_dup, b_dup, o_dup):
        text = dup(err, "название", "Роза")
        assert text is not None and "уже существует" in text
    assert p_dup(Exception("timeout"), "название", "Роза") is None


# --- 3. Уникальность ---
def test_require_unique():
    with pytest.raises(ValidationError):
        require_unique("ORD-001/2024", ["ORD-001/2024", "ORD-002/2024"], "Номер заказа")
    require_unique("ORD-003/2024", ["ORD-001/2024"], "Номер заказа")
    # email — без учёта регистра
    with pytest.raises(ValidationError):
        require_unique("A@B.ru", ["a@b.RU"], "Email")


def test_check_unique_returns_duplicate():
    assert check_unique(["a", "b", "a"]) == "a"
    assert check_unique(["x", "y"]) is None
    assert check_unique(["A@b.ru", "a@B.RU"]) == "a@B.RU"


# --- Комплексные проверки и модели ---
def test_validate_product_dict_and_model():
    assert validate_product_dict({"purchase_price": 100, "retail_price": 200, "shelf_life_days": 7}) == []
    errs = validate_product_dict({"purchase_price": -5, "retail_price": 0, "shelf_life_days": 0})
    assert len(errs) == 3
    p = Product(id=1, name="Роза", purchase_price=Decimal("-1"), retail_price=Decimal("0"),
                shelf_life_days=0)
    assert len(p.validate()) == 3
    assert Product(id=1, name="Роза", purchase_price=Decimal("150"),
                   retail_price=Decimal("300"), shelf_life_days=10).validate() == []


def test_validate_batch_order_employee_client_category():
    assert validate_batch_dict({"cost_price": 100, "quantity": 5,
                                "delivery_date": "2024-01-15",
                                "invoice_number": "РОЗ-001/2024"}) == []
    assert len(validate_batch_dict({"cost_price": -1, "quantity": -2,
                                    "delivery_date": "2999-01-01",
                                    "invoice_number": "bad"})) == 4

    assert validate_order_dict({"status": "Новый", "order_number": "ORD-001/2024",
                                "order_date": "2024-01-20"}) == []
    assert len(validate_order_dict({"status": "Отменен", "order_number": "bad"})) == 2

    assert validate_employee_dict({"access_level": "florist", "phone_number": "+79161234567",
                                   "email": "a@b.ru", "password": "x"}) == []
    assert len(validate_employee_dict({"access_level": "boss", "phone_number": "123",
                                       "email": "bad", "password": ""})) == 4

    assert validate_client_dict({"phone_number": "+79161234567", "email": "a@b.ru"}) == []

    assert Category(id=1, name="Розы").validate(["Тюльпаны"]) == []
    assert Category(id=1, name="Розы").validate(["розы"]) != []
    assert Category(id=1, name="  ").validate() != []


def test_model_validate_integration():
    o = Order(id=1, order_number="ORD-001/2024", order_date=date(2024, 1, 20),
              status="Доставлен", total_amount=Decimal("100"))
    assert o.validate() == []
    assert o.validate(["ORD-001/2024"]) != []  # дубликат
    assert Order(id=1, order_number="bad", order_date=date.today(),
                 status="???", total_amount=Decimal("1")).validate() != []

    e = Employee(id=1, full_name="А", access_level="courier",
                 phone_number="+79161234567", email="a@b.ru")
    assert e.validate() == []
    assert Employee(id=1, full_name="А", access_level="boss").validate() != []

    c = Client(id=1, full_name="Иван", phone_number="+79031112233", email="x@y.ru")
    assert c.validate() == []
    assert Client(id=1, full_name="И", phone_number="123").validate() != []

    b = Batch(id=1, quantity=10, cost_price=Decimal("100"),
              delivery_date=date(2024, 1, 15), invoice_number="РОЗ-001/2024")
    assert b.validate() == []

    assert Inventory(id=1, quantity=0, receipt_date=date.today()).validate() == []
    assert Inventory(id=1, quantity=-1, receipt_date=date.today()).validate() != []
    assert OrderItem(id=1, order_id=1, quantity=1).validate() == []
    assert OrderItem(id=1, order_id=1, quantity=-2).validate() != []
