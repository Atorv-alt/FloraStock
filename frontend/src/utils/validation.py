"""
Централизованные ограничения целостности данных
для системы автоматизации цветочного склада (FloraStock / Sclad).

Покрывает требования:
1. Целостность: положительные цены, неотрицательные количества,
   корректные даты, положительный срок хранения, статусы заказов,
   уровни доступа сотрудников.
2. Символьные форматы: номер заказа ORD-XXX/ГГГГ, номер накладной
   ХХХ-YYY/ГГГГ, телефон +7XXXXXXXXXX, email, непустой пароль.
3. Уникальность: номера заказов/накладных, email сотрудников/клиентов,
   наименование категории.

Использование:
    from src.utils.validation import validate_product_prices, ValidationError
    validate_product_prices(purchase_price, retail_price)  # raise ValidationError
    # или вариант без исключений:
    errors = validate_product_dict({...})  # -> list[str]
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Optional


class ValidationError(ValueError):
    """Ошибка нарушения ограничения целостности."""
    pass


# ---------------------------------------------------------------------------
# Константы-справочники
# ---------------------------------------------------------------------------

#: Допустимые статусы заказа (п.1 требований)
ORDER_STATUSES = ("Новый", "В обработке", "Выполнен", "Доставлен")

#: Допустимые уровни доступа сотрудника (п.1 требований)
ACCESS_LEVELS = ("admin", "florist", "seller", "purchasing", "courier", "warehouse")

#: Номер заказа: ORD-XXX/ГГГГ (XXX — 3+ цифр порядкового номера)
ORDER_NUMBER_RE = re.compile(r"^ORD-\d{3,}/\d{4}$")

#: Номер накладной: ХХХ-YYY/ГГГГ, где ХХХ — 2-5 букв (кириллица/латиница).
#: Примеры: РОЗ-001/2024, ТЮЛ-002/2024
INVOICE_NUMBER_RE = re.compile(r"^[А-ЯЁA-Z]{2,5}-\d{3,}/\d{4}$", re.IGNORECASE)

#: Телефон строго +7 и 10 цифр: +7XXXXXXXXXX
PHONE_RE = re.compile(r"^\+7\d{10}$")

#: Стандартный email (упрощённый, но достаточный для CHECK-ограничения)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

#: Цвет: только буквы (кириллица/латиница), пробелы и дефисы, без цифр.
#: Примеры: Красный, Светло-розовый, White
COLOR_RE = re.compile(r"^[А-ЯЁA-Zа-яёa-z\s\-]+$")

#: ФИО: буквы, пробелы, дефис и точка, без цифр.
#: Примеры: Иванова Анна Петровна, Соколова Мария Ивановна
PERSON_NAME_RE = re.compile(r"^[А-ЯЁA-Za-zа-яё\s\.\-]+$")

#: Единица измерения: только буквы (без цифр), до 50 символов.
#: Примеры: шт, кг, букет, упаковка
UNIT_RE = re.compile(r"^[А-ЯЁA-Za-zа-яё\s\-]+$")
MAX_UNIT_LENGTH = 50

#: Минимальная длина нового пароля
MIN_PASSWORD_LENGTH = 4

#: Максимальная длина наименований / ФИО (VARCHAR(255) в БД)
MAX_NAME_LENGTH = 255


# ---------------------------------------------------------------------------
# Базовые проверки
# ---------------------------------------------------------------------------

def _to_decimal(value: Any, field: str) -> Decimal:
    try:
        d = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f"{field}: должно быть числом, получено {value!r}")
    return d


def require_positive_price(value: Any, field: str) -> Decimal:
    """Цена (Закупочная_цена, Розничная_цена, Стоимость_партии) > 0."""
    d = _to_decimal(value, field)
    if d <= 0:
        raise ValidationError(f"{field}: должна быть положительным числом, получено {value!r}")
    return d


def require_non_negative_int(value: Any, field: str) -> int:
    """Количество (на складе / в партии / в заказе) — целое >= 0."""
    if isinstance(value, bool):
        raise ValidationError(f"{field}: должно быть целым числом >= 0")
    if isinstance(value, int):
        iv = value
    elif isinstance(value, float):
        if not value.is_integer():
            raise ValidationError(f"{field}: должно быть целым числом >= 0, получено {value!r}")
        iv = int(value)
    elif isinstance(value, str):
        s = value.strip()
        if not re.fullmatch(r"[+-]?\d+", s):
            raise ValidationError(f"{field}: должно быть целым числом >= 0, получено {value!r}")
        iv = int(s)
    else:
        raise ValidationError(f"{field}: должно быть целым числом >= 0, получено {value!r}")
    if iv < 0:
        raise ValidationError(f"{field}: должно быть неотрицательным, получено {value!r}")
    return iv


def require_positive_int(value: Any, field: str) -> int:
    """Срок хранения (дней) — целое > 0."""
    iv = require_non_negative_int(value, field)
    if iv <= 0:
        raise ValidationError(f"{field}: должен быть положительным целым числом, получено {value!r}")
    return iv


def require_order_status(value: Any) -> str:
    """Статус заказа — одно из ORDER_STATUSES."""
    if value not in ORDER_STATUSES:
        raise ValidationError(
            f"Статус заказа должен быть одним из {list(ORDER_STATUSES)}, получено {value!r}"
        )
    return value  # type: ignore[return-value]


def require_access_level(value: Any) -> str:
    """Уровень доступа сотрудника — одно из ACCESS_LEVELS."""
    if value not in ACCESS_LEVELS:
        raise ValidationError(
            f"Уровень доступа должен быть одним из {list(ACCESS_LEVELS)}, получено {value!r}"
        )
    return value  # type: ignore[return-value]


def require_order_number(value: Any) -> str:
    """Номер заказа формата ORD-XXX/ГГГГ."""
    if not isinstance(value, str) or not ORDER_NUMBER_RE.match(value.strip()):
        raise ValidationError(f"Номер заказа должен иметь формат ORD-XXX/ГГГГ, получено {value!r}")
    return value.strip()


def require_invoice_number(value: Any) -> str:
    """Номер накладной формата ХХХ-YYY/ГГГГ (напр. РОЗ-001/2024)."""
    if not isinstance(value, str) or not INVOICE_NUMBER_RE.match(value.strip()):
        raise ValidationError(
            f"Номер накладной должен иметь формат ХХХ-YYY/ГГГГ (напр. РОЗ-001/2024), "
            f"получено {value!r}"
        )
    return value.strip().upper()


def require_phone(value: Any, field: str = "Номер телефона") -> str:
    """Телефон формата +7XXXXXXXXXX."""
    if not isinstance(value, str) or not PHONE_RE.match(value.strip()):
        raise ValidationError(f"{field} должен соответствовать формату +7XXXXXXXXXX, получено {value!r}")
    return value.strip()


def require_email(value: Any, field: str = "Email") -> str:
    """Стандартный формат email."""
    if not isinstance(value, str) or not EMAIL_RE.match(value.strip()):
        raise ValidationError(f"{field} должен соответствовать формату email-адреса, получено {value!r}")
    return value.strip()


def require_non_empty_password(value: Any) -> str:
    """Пароль сотрудника не может быть пустым."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Пароль сотрудника не может быть пустым")
    return value


def require_password(value: Any, field: str = "Пароль") -> str:
    """Новый пароль: непустой, без пробелов, длиной не меньше MIN_PASSWORD_LENGTH."""
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} не может быть пустым")
    if len(value) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"{field} должен содержать не менее {MIN_PASSWORD_LENGTH} символов, "
            f"получено {len(value)}"
        )
    if any(ch.isspace() for ch in value):
        raise ValidationError(f"{field} не должен содержать пробелы")
    return value


def require_person_name(value: Any, field: str = "ФИО") -> str:
    """ФИО — только буквы (без цифр)."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} обязательно для заполнения")
    s = value.strip()
    if any(ch.isdigit() for ch in s):
        raise ValidationError(f"{field} не должно содержать цифры, получено {value!r}")
    if not PERSON_NAME_RE.match(s):
        raise ValidationError(
            f"{field} должно содержать только буквы, получено {value!r}"
        )
    if len(s) > MAX_NAME_LENGTH:
        raise ValidationError(f"{field} не должно превышать {MAX_NAME_LENGTH} символов")
    return s


def require_name(value: Any, field: str = "Наименование") -> str:
    """Наименование (товар, категория, поставщик): непустое, длиной до MAX_NAME_LENGTH."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} обязательно для заполнения")
    s = value.strip()
    if len(s) > MAX_NAME_LENGTH:
        raise ValidationError(f"{field} не должно превышать {MAX_NAME_LENGTH} символов")
    return s


def require_unit(value: Any, field: str = "Единица измерения") -> str:
    """Единица измерения — только буквы (без цифр), например: шт, кг, букет."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} обязательна для заполнения")
    s = value.strip()
    if any(ch.isdigit() for ch in s):
        raise ValidationError(f"{field} не должна содержать цифры, получено {value!r}")
    if len(s) > MAX_UNIT_LENGTH:
        raise ValidationError(f"{field} не должна превышать {MAX_UNIT_LENGTH} символов")
    if not UNIT_RE.match(s):
        raise ValidationError(
            f"{field} должна содержать только буквы (например: шт, кг, букет), "
            f"получено {value!r}"
        )
    return s


def require_color(value: Any, field: str = "Цвет") -> str:
    """Цвет — только буквы (без цифр). Пустое значение допустимо (поле необязательное)."""
    if value is None:
        return value  # type: ignore[return-value]
    if not isinstance(value, str):
        raise ValidationError(f"{field} должен содержать только буквы, получено {value!r}")
    s = value.strip()
    if not s:
        return s  # пустое = "не указан", допустимо
    if any(ch.isdigit() for ch in s):
        raise ValidationError(f"{field} не должен содержать цифры, получено {value!r}")
    if not COLOR_RE.match(s):
        raise ValidationError(
            f"{field} должен содержать только буквы (например: красный, белый), "
            f"получено {value!r}"
        )
    return s


def require_delivery_date(value: Any, field: str = "Дата поставки") -> date:
    """Дата поставки: правильный формат и не позже текущей даты."""
    d = _coerce_date(value, field)
    if d > date.today():
        raise ValidationError(f"{field} не может быть позже текущей даты, получено {d.isoformat()}")
    return d


def require_order_date(value: Any, field: str = "Дата заказа") -> date:
    """Дата заказа: правильный формат, логически корректна (не в будущем)."""
    d = _coerce_date(value, field)
    if d > date.today():
        raise ValidationError(f"{field} не может быть позже текущей даты, получено {d.isoformat()}")
    return d


def _coerce_date(value: Any, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        s = value.strip()
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        # ISO с временем: 2024-01-15T10:00:00
        try:
            return datetime.fromisoformat(s).date()
        except ValueError:
            pass
    raise ValidationError(f"{field}: неверный формат даты, получено {value!r}")


def require_unique(value: Any, existing: Iterable[Any], field: str) -> Any:
    """Уникальность значения среди уже существующих (без учёта регистра для строк)."""
    norm = value.strip().lower() if isinstance(value, str) else value
    taken = {v.strip().lower() if isinstance(v, str) else v for v in existing}
    if norm in taken:
        raise ValidationError(f"{field} должен быть уникальным, значение {value!r} уже существует")
    return value


# ---------------------------------------------------------------------------
# Комплексные проверки сущностей (возвращают список ошибок, не бросают)
# ---------------------------------------------------------------------------

def validate_product_dict(d: dict) -> list[str]:
    errors: list[str] = []
    for f in ("purchase_price", "retail_price"):
        if f in d and d[f] is not None:
            try:
                require_positive_price(d[f], f)
            except ValidationError as e:
                errors.append(str(e))
    if "shelf_life_days" in d and d["shelf_life_days"] is not None:
        try:
            require_positive_int(d["shelf_life_days"], "Срок хранения (дней)")
        except ValidationError as e:
            errors.append(str(e))
    if "quantity" in d and d["quantity"] is not None:
        try:
            require_non_negative_int(d["quantity"], "Количество")
        except ValidationError as e:
            errors.append(str(e))
    if "color" in d and d["color"] not in (None, ""):
        try:
            require_color(d["color"])
        except ValidationError as e:
            errors.append(str(e))
    if "unit" in d and d["unit"] not in (None, ""):
        try:
            require_unit(d["unit"])
        except ValidationError as e:
            errors.append(str(e))
    return errors


def validate_batch_dict(d: dict) -> list[str]:
    errors: list[str] = []
    if "cost_price" in d and d["cost_price"] is not None:
        try:
            require_positive_price(d["cost_price"], "Стоимость партии")
        except ValidationError as e:
            errors.append(str(e))
    if "quantity" in d and d["quantity"] is not None:
        try:
            require_non_negative_int(d["quantity"], "Количество в партии")
        except ValidationError as e:
            errors.append(str(e))
    if "delivery_date" in d and d["delivery_date"] is not None:
        try:
            require_delivery_date(d["delivery_date"])
        except ValidationError as e:
            errors.append(str(e))
    if "invoice_number" in d and d["invoice_number"] is not None:
        try:
            require_invoice_number(d["invoice_number"])
        except ValidationError as e:
            errors.append(str(e))
    return errors


def validate_order_dict(d: dict) -> list[str]:
    errors: list[str] = []
    if "status" in d and d["status"] is not None:
        try:
            require_order_status(d["status"])
        except ValidationError as e:
            errors.append(str(e))
    if "order_number" in d and d["order_number"] is not None:
        try:
            require_order_number(d["order_number"])
        except ValidationError as e:
            errors.append(str(e))
    if "order_date" in d and d["order_date"] is not None:
        try:
            require_order_date(d["order_date"])
        except ValidationError as e:
            errors.append(str(e))
    if "quantity" in d and d["quantity"] is not None:
        try:
            require_non_negative_int(d["quantity"], "Количество в заказе")
        except ValidationError as e:
            errors.append(str(e))
    if "total_amount" in d and d["total_amount"] is not None:
        try:
            require_positive_price(d["total_amount"], "Сумма заказа")
        except ValidationError as e:
            errors.append(str(e))
    return errors


def validate_employee_dict(d: dict) -> list[str]:
    errors: list[str] = []
    if "access_level" in d and d["access_level"] is not None:
        try:
            require_access_level(d["access_level"])
        except ValidationError as e:
            errors.append(str(e))
    if "phone_number" in d and d["phone_number"] not in (None, ""):
        try:
            require_phone(d["phone_number"])
        except ValidationError as e:
            errors.append(str(e))
    if "email" in d and d["email"] not in (None, ""):
        try:
            require_email(d["email"])
        except ValidationError as e:
            errors.append(str(e))
    if "password" in d or "login_password" in d:
        try:
            require_non_empty_password(d.get("password", d.get("login_password")))
        except ValidationError as e:
            errors.append(str(e))
    return errors


def validate_client_dict(d: dict) -> list[str]:
    errors: list[str] = []
    if "phone_number" in d and d["phone_number"] not in (None, ""):
        try:
            require_phone(d["phone_number"])
        except ValidationError as e:
            errors.append(str(e))
    if "email" in d and d["email"] not in (None, ""):
        try:
            require_email(d["email"])
        except ValidationError as e:
            errors.append(str(e))
    return errors


def validate_supplier_dict(d: dict) -> list[str]:
    """Проверка поставщика: телефон +7XXXXXXXXXX, email стандартного формата."""
    errors: list[str] = []
    if "phone_number" in d and d["phone_number"] not in (None, ""):
        try:
            require_phone(d["phone_number"])
        except ValidationError as e:
            errors.append(str(e))
    if "email" in d and d["email"] not in (None, ""):
        try:
            require_email(d["email"])
        except ValidationError as e:
            errors.append(str(e))
    return errors


def check_unique_order_numbers(numbers: Iterable[str]) -> Optional[str]:
    """Вернуть дублирующийся номер заказа или None."""
    seen: set[str] = set()
    for n in numbers:
        key = n.strip() if isinstance(n, str) else n
        if key in seen:
            return n  # type: ignore[return-value]
        seen.add(key)
    return None


def check_unique(values: Iterable[Any], case_insensitive: bool = True) -> Optional[Any]:
    """Вернуть первый дубликат в коллекции или None."""
    seen: set[Any] = set()
    for v in values:
        key = v.strip().lower() if (case_insensitive and isinstance(v, str)) else v
        if key in seen:
            return v
        seen.add(key)
    return None


#: Маркеры ошибки дубликата в ответах сервера/БД (409 Conflict, UNIQUE-violation 23505, ...).
DUPLICATE_MARKERS = (
    "unique",
    "duplicate",
    "already exists",
    "23505",
    "conflict",
    "409",
    "уже существует",
)


def format_duplicate_error(exc: BaseException, field_name: str, field_value: Any) -> Optional[str]:
    """Понятный текст ошибки дубликата или None, если это другая ошибка.

    Распознаёт ответы сервера (409 Conflict, «...уже существует»)
    и ошибки БД (UNIQUE-violation 23505).
    """
    msg = str(exc).lower()
    if any(m in msg for m in DUPLICATE_MARKERS):
        return f"❌ Значение «{field_value}» уже существует в поле «{field_name}»."
    return None
